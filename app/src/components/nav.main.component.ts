const {app} = require('electron').remote;
import { NgModule, Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from "@angular/common";
const ipcRenderer = require('electron').ipcRenderer;
const fs = require('fs');

import * as globals from './../global.vars';
const noUiSlider = require('nouislider/distribute/nouislider');
import * as jquery from 'jquery';
window['$'] = jquery;
window['jQuery'] = jquery;
import * as select2 from 'select2';

var jsPDF = require('jspdf');
require('jspdf-autotable');

@Component({
  selector: 'main-nav',
  templateUrl: 'templates/nav.main.html'
})

export class MainNavComponent {
  @Output() pageChanged = new EventEmitter<string>();
  @Output() savedFilterChanged = new EventEmitter<string>();
  currentPage = "players";
  savedFiltersFromFile = this.getSavedFilters();

  app_version = "1.0"

  quitAndInstall() {
    ipcRenderer.send('quitAndInstall');
  }

  getSavedFilters() {
    /*
      return the saved filters from the file
      minus the default filters
    */
    var filtersFromFile = globals.getSavedFilters();
    return filtersFromFile.slice(1);
  }

  showSaveModal(){
    /*
      Show current page's save filter modal
    */
    var modalId = "#" + this.currentPage + "-save-filters-modal";
    $(modalId).modal('toggle');

  }

  showEditSavedFiltersModal(modal) {
    /*
      Shows the edit filters modal
    */
    $(modal).modal('toggle');
    this.savedFiltersFromFile = this.getSavedFilters();

  }
  jsonStringify(data) {
    /*
      Returns stringified data
      Inputs:
        data: obj = filter object data
    */
    return JSON.stringify(data);
  }
  saveFilterChanges(modal) {
    /*
      Saves the changed filters in edit saved filter modal
    */
    var new_filters = "";
    $('.input-filter-names').each(function(){
      if ($(this).data('include')) {
        var current_filter = $(this).data('filter');
        console.log(current_filter)
        current_filter.filterName = $(this).val();
        new_filters += JSON.stringify(current_filter) + '\n';
      }
    });
    console.log(new_filters);
    // not checking for duplicates, if they want to make a filter the same name
    // we are going to let them do it here..
    fs.writeFile(globals.saved_filters_file, new_filters, function (err) {
      if (err) throw err;
      $(modal).modal('toggle');

      // refresh the saved filters dropdown
      $('#saved-filters').empty();
      globals.createSelect2("#saved-filters", 'Select Saved Filter', globals.getSavedFilters);

      console.log('Saved!');

    });

  }

  deleteFilter(event, index) {
    /*
      delete selected filter
    */
    var isDisabled = $('#filter-names-'+index).prop('disabled');
    $('#filter-names-'+index).prop('disabled', !isDisabled);
    $('#filter-names-'+index).attr('data-include', isDisabled);
    $('#btn-filter-'+index).toggle();
    $('#btn-filter-undo-'+index).toggle();

  }


  ngOnInit(): void {

    // get filter names and data and add them to savedFiltersFromFile

    select2();
    globals.createSelect2("#saved-filters", 'Select Saved Filter', globals.getSavedFilters);
    $('#saved-filters').on("change", (e) => {
      console.log(e.target.value);
      // if you select the null value, do nothing
      if (e.target.value == -1 || e.target.value == '') return;

      // get the data from the saved filter object
      var filterData = $('#saved-filters').select2('data')[0].data;

      // send the data to the app component
      // to be able to pass it to the correct filter
      this.savedFilterChanged.emit(filterData);

      // change the currently selected to match selected saved filter
      this.currentPage = filterData.page;

    });
    $("#print-tooltip").tooltip();
    $("#saved-filters-wrapper").tooltip();
    $("#save-filter-tooltip").tooltip();
    $(".nav-tooltip").tooltip();
    $("#version").tooltip();

    // set app Version
    this.app_version = app.getVersion();
    $('#version').click(function(){
      ipcRenderer.send('checkForUpdate');
    })
    ipcRenderer.on('updateReady', function(event, text) {
      if (confirm("An update needs to be installed.\nDownload and Install Update?")) {
        ipcRenderer.send('quitAndInstall');
      }
    })
  }

  pageClicked(event){
    if (event.target.id == this.currentPage) return
    this.currentPage = event.target.id;
    this.pageChanged.emit(this.currentPage);
  }

  printMsg(event): void {
    console.log('Cornell Basketball Logo');
  }

  printPage(event) {
    // Create PDF and add table
    var doc = new jsPDF('l');
    var elem = document.getElementById(this.currentPage+"-table");
    var res = doc.autoTableHtmlToJson(elem);
    doc.autoTable(res.columns, res.data, {
       startY: 20,
       tableWidth: 'wrap',
       styles: {overflow: 'linebreak', columnWidth: 'wrap', fontSize: 10},
       margin: {left: 10}
     });

    var filters = globals.filters;

    // Add filter to PDF if there is one
    if (filters != null) {
      doc.setFontSize(12);
      doc.text("Filters Applied:", 14, doc.autoTable.previous.finalY + 10);

      var filterStrings = [];

      // TEAM
      var team = "Teams: All";
      if (filters.team.length > 0) {
        team = "Teams: " + filters.team.toString();
      }
      filterStrings.push(team);

      // OPPONENT
      var opponent = "Opponent: All";
      if (filters.opponent.length > 0) {
        opponent = "Opponents: " + filters.opponent.toString();
      }
      filterStrings.push(opponent);

      // Format the fields specific to Players
      if (filters.page == "players") {
        if (filters.position.length > 0) {
          var position = "Positions: " + filters.position.toString();
          filterStrings.push(position);
        }
        if (filters.in.length > 0) {
          var inLineup = "Players In Lineup: " + filters.in.toString();
          filterStrings.push(inLineup);
        }
        if (filters.out.length > 0) {
          var outLineup = "Players Out Of Lineup: " + filters.out.toString();
          filterStrings.push(outLineup);
        }
      }

      // LOCATION
      var location = "Location: ";
      if (filters.location.away) { location = location + "Away, "; }
      if (filters.location.home) { location = location + "Home, "; }
      if (filters.location.neutral) { location = location + "Neutral, "; }
      location = location.slice(0, -2);
      if (location == "Location" || location == "Location: Away, Home, Neutral") { location = "Location: All"; }
      filterStrings.push(location);

      // OUTCOME
      var outcome = "Outcome: ";
      if (filters.outcome.wins) { outcome = outcome + "Wins, "; }
      if (filters.outcome.losses) { outcome = outcome + "Losses, "; }
      outcome = outcome.slice(0, -2);
      if (outcome == "Outcome" || outcome == "Outcome: Wins, Losses") { outcome = "Outcome: All"; }
      filterStrings.push(outcome);

      // SCORE DIFFERENCE
      if (filters.upOrDown[1] != null) {
        var upOrDown = "Point Difference: " + filters.upOrDown[0] + " " + String(filters.upOrDown[1]);
        filterStrings.push(upOrDown);
      }

      // MAIN GAMETIME
      var min = NaN;
      var sec = NaN;
      var secStr = "";

      var mainSlider = ""
      if (!filters.overtime.onlyQueryOT) {

          // Get beginning in seconds and half
          var sliderStart = -1*filters.gametime.slider.start.sec;
          var startFirstHalf = true;
          if sliderStart > 1200 {
            sliderStart = sliderStart - 1200;
            startFirstHalf = true;
          }
          else { startFirstHalf = false; }

          // Create string for beginning
          min = Math.floor(sliderStart/60);
          sec = sliderStart % min;
          secStr = "";
          if (isNaN(sec)) {secStr = "00";}
          else if (sec < 10) {secStr = "0" + String(sec);}
          else {secStr = String(sec);}
          var mainStartString = String(min) + ":" + secStr;
          mainStartString = startFirstHalf ? mainStartString + " (First Half)" : mainStartString + " (Second Half)";

          // Get end in seconds and half
          var sliderEnd = -1*filters.gametime.slider.end.sec;
          var endFirstHalf = true;
          if sliderEnd > 1200 {
            sliderEnd = sliderEnd - 1200;
            endFirstHalf = true;
          }
          else { endFirstHalf = false; }

          // Create string for end
          min = Math.floor(sliderEnd/60);
          sec = sliderEnd % min;
          secStr = "";
          if (isNaN(sec)) {secStr = "00";}
          else if (sec < 10) {secStr = "0" + String(sec);}
          else {secStr = String(sec);}
          var mainEndString = String(min) + ":" + secStr;
          mainEndString = endFirstHalf ? mainEndString + " (First Half)" : mainEndString + " (Second Half)";

          // Create gametime string with beginning and end
          mainSlider = "Gametime: " + mainStartString + " - " + mainEndString;

          // If there are multiple time frames, add the extra slider
          if (filters.gametime.multipleTimeFrames) {

              // Get beginning of extra time period in seconds and half
              sliderStart = -1*filters.gametime.sliderExtra.start.sec;
              startFirstHalf = true;
              if sliderStart > 1200 {
                sliderStart = sliderStart - 1200;
                startFirstHalf = true;
              }
              else { startFirstHalf = false; }

              // Create string
              min = Math.floor(sliderStart/60);
              sec = sliderStart % min;
              secStr = "";
              if (isNaN(sec)) {secStr = "00";}
              else if (sec < 10) {secStr = "0" + String(sec);}
              else {secStr = String(sec);}
              var extraStartString = String(min) + ":" + secStr;
              extraStartString = startFirstHalf ? extraStartString + " (First Half)" : extraStartString + " (Second Half)";


              // Get end of extra time period in seconds and half
              sliderEnd = -1*filters.gametime.sliderExtra.end.sec;
              endFirstHalf = true;
              if sliderEnd > 1200 {
                sliderEnd = sliderEnd - 1200;
                endFirstHalf = true;
              }
              else { endFirstHalf = false; }

              // Create string
              min = Math.floor(sliderEnd/60);
              sec = sliderEnd % min;
              secStr = "";
              if (isNaN(sec)) {secStr = "00";}
              else if (sec < 10) {secStr = "0" + String(sec);}
              else {secStr = String(sec);}
              var extraEndString = String(min) + ":" + secStr;
              extraEndString = endFirstHalf ? extraEndString + " (First Half)" : extraEndString + " (Second Half)";

              // Add onto the main slider
              mainSlider = mainSlider + " and " + extraStartString + " - " + extraEndString;
          }

          filterStrings.push(mainSlider);
      }

      // OVERTIME
      // Convert start time into string
      var otStart = 300 - filters.overtime.otSliderStart;
      min = Math.floor(otStart/60);
      sec = otStart % min;
      secStr = "";
      if (isNaN(sec)) {secStr = "00";}
      else if (sec < 10) {secStr = "0" + String(sec);}
      else {secStr = String(sec);}
      var otStartString = String(min) + ":" + secStr;

      // Convert end time into string
      var otEnd = 300 - filters.overtime.otSliderEnd;
      min = Math.floor(otEnd/60);
      sec = otEnd % min;
      if (isNaN(sec)) {secStr = "00";}
      else if (sec < 10) {secStr = "0" + String(sec);}
      else {secStr = String(sec);}
      var otEndString = String(min) + ":" + secStr;

      var onlyOT = filters.overtime.onlyQueryOT ? ", Only Query OT" : "";
      var otSlider = "Overtime: " + otStartString + " - " + otEndString + onlyOT;

      // Create overtime period string
      var periods = "";
      if (filters.overtime.ot1 && filters.overtime.ot2 && filters.overtime.ot3 && filters.overtime.ot4 && filters.overtime.ot5 && filters.overtime.ot6) {
        periods = "Overtime Periods: All";
      }
      else if (!filters.overtime.ot1 && !filters.overtime.ot2 && !filters.overtime.ot3 && !filters.overtime.ot4 && !filters.overtime.ot5 && !filters.overtime.ot6) {
        periods = "";
        otSlider = "";
      }
      else {
        periods = "Overtime Periods: ";
        if (filters.overtime.ot1) { periods = periods + "OT1, "; }
        if (filters.overtime.ot2) { periods = periods + "OT2, "; }
        if (filters.overtime.ot3) { periods = periods + "OT3, "; }
        if (filters.overtime.ot4) { periods = periods + "OT4, "; }
        if (filters.overtime.ot5) { periods = periods + "OT5, "; }
        if (filters.overtime.ot6) { periods = periods + "OT6+, "; }
        periods = periods.slice(0, -2);
      }
      if (otSlider) {
        filterStrings.push(otSlider);
        filterStrings.push(periods);
      }


      // DATES
      var startDate = new Date(filters.dates.start);
      var startString = String(startDate.getMonth() + 1) + "/" + String(startDate.getDate()) + "/" + String(startDate.getFullYear());
      var endDate = new Date(filters.dates.end);
      var endString = String(endDate.getMonth() + 1) + "/" + String(endDate.getDate()) + "/" + String(endDate.getFullYear());
      var date = "Dates: " + startString + " - " + endString;
      filterStrings.push(date);

      doc.setFontSize(10);
      for (var i = 0; i < filterStrings.length; i++) {
        var string = filterStrings[i];
        doc.text(doc.splitTextToSize(string, doc.internal.pageSize.width - 35, {}), 14, doc.autoTable.previous.finalY + 10 + 5*(i+1));
      }

    }

    doc.save("results.pdf");
  }

}

@NgModule({
   imports: [CommonModule],
   exports: [MainNavComponent],
   declarations: [MainNavComponent]
})

export class MainNavModule {
}
