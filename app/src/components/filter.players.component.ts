import { NgModule, Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from "@angular/common";
import * as globals from './../global.vars';

const ionRangeSlider = require('ion-rangeslider/js/ion.rangeSlider');
const datePicker = require('bootstrap-datepicker/dist/js/bootstrap-datepicker.js');

import * as jquery from 'jquery';
window['$'] = jquery;
window['jQuery'] = jquery;
import * as select2 from 'select2';

@Component({
  selector: 'filter-players',
  templateUrl: 'templates/filter.players.html'
})
export class PlayersFilterComponent implements OnInit {
  // use this to pass data to app.component in applyFilters
  @Output() dataEvent = new EventEmitter<string>();
  @Output() dataEvent_adv = new EventEmitter<string>();

  // Receive the saved filter from the app component
  @Input()
  set savedFilter(savedFilterObj: object) {

    // NOTE: If we want to run a default filter object on opening the file,
    // do it here, remove the if statement and change the blank.data to a filter

    // if a real option has been selected that is not the null value
    if ($('#saved-filters').val() != -1 ) {

      try {
        // apply the saved filters and send to middle stack
        globals.applyFilters(this.currentPageName, savedFilterObj, this.dataEvent, this.dataEvent_adv);

        this.updateFilters(savedFilterObj);
      }
      catch(err) {
        console.log(err)
      }

    }

  }

  currentPageName = "players";

  // Object to save time from sliders
  gametime = {
    pgtSlider:{
      start:{clock: "20:00", sec:-2400},
      end:{clock: "00:00", sec:0}
    },
    pgtSliderExtra:{
      start:{clock: "20:00", sec:-2400},
      end:{clock: "00:00", sec:0}
    },
    pgtSliderOT:{
      start:{clock: "5:00", sec:-300},
      end:{clock: "0:00", sec:0}
    }
  };
  startTime2ndHalf = {
    pgtSlider:false,
    pgtSliderExtra: false,
  }
  endTime2ndHalf = {
    pgtSlider:true,
    pgtSliderExtra: true,
  }

  // 2 way bound filters -- simple inputs
  homeGames:boolean = false;
  awayGames:boolean = false;
  neutralGames:boolean = false;
  wins:boolean = false;
  losses:boolean = false;
  upOrDown:string;
  ot1:boolean = true;
  ot2:boolean = true;
  ot3:boolean = true;
  ot4:boolean = true;
  ot5:boolean = true;
  ot6:boolean = true;
  otAll:boolean = true;
  otNone:boolean = false;
  onlyOT:boolean = false;

  oldFilters = [];

  hidePgtExtra = true;
  hideOvertime = true;

  invalidInput(el) {
    //show a red box around the input box
    console.log("invalid input");
  }

  getAllFilters() {
    var filters = {};
    // set which page we are requesting the filters from
    filters['page'] = this.currentPageName;
    // Gather dropdown data
    $('.players-select2').each(function() {
      // Normalize filter names to send to middle stack
      var id = this.id.split('-')[1];
      filters[id] = $(this).val();
    });

    // Gather data not in dropdowns
    filters.gametime = {};
    filters.gametime.slider = this.gametime.pgtSlider;
    filters.gametime.sliderExtra = this.gametime.pgtSliderExtra;
    filters.gametime.multipleTimeFrames = !this.hidePgtExtra;

    filters.upOrDown = [filters.upOrDown, this.upOrDown];

    if (!this.homeGames && !this.awayGames && !this.neutralGames) {
      filters.location = {
        home:true,
        away:true,
        neutral:true
      }
    }
    else {
      filters.location = {
        home:this.homeGames,
        away:this.awayGames,
        neutral:this.neutralGames
      }
    }

    if (!this.wins && !this.losses) {
      filters.outcome = {
        wins: true,
        losses: true
      }
    }
    else {
      filters.outcome = {
        wins: this.wins,
        losses: this.losses
      }
    }

    filters.overtime = {
        otSliderStart: this.gametime.pgtSliderOT.start.sec + 300,
        otSliderEnd: this.gametime.pgtSliderOT.end.sec + 300,
        ot1: this.ot1,
        ot2: this.ot2,
        ot3: this.ot3,
        ot4: this.ot4,
        ot5: this.ot5,
        ot6: this.ot6,
        onlyQueryOT: this.onlyOT
      }

    filters.dates = {
      start: $("#players-start-date").datepicker('getDate').getTime(),
      end: $("#players-end-date").datepicker('getDate').getTime()
    }

    console.log(filters);

    return filters;
  }
  saveFilters(filters) {
    this.oldFilters.push(filters);
  }
  clearAllFilters() {
    var filters = this.getAllFilters();
    this.saveFilters(filters);
    // clear dropdown inputs
    $('.players-select2').val(null).trigger('change');

    this.homeGames = false;
    this.awayGames = false;
    this.neutralGames = false;
    this.wins = false;
    this.losses = false;
    this.ot1 = true;
    this.ot2 = true;
    this.ot3 = true;
    this.ot4 = true;
    this.ot5 = true;
    this.ot6 = true;
    this.otAll = true;
    this.otNone = false;
    this.onlyOT = false;
    $(upOrDown).val(null);

    globals.clearSliders(this, "pgtSlider");
    globals.clearDates(this.currentPageName);

    console.log("cleared all filters");
  }

  updateFilters(filters) {
    /*
      Changes the filters in the side bar to match the chose saved filter
      Inputs:
        filters: Object that contains all of the filter data
    */

    // set all of the filters with the saved filters
    globals.updateAllSlidersFromSavedFilter(this, 'pgtSlider', filters);
    globals.updateSelect2sFromSavedFilter(this.currentPageName, filters);
    this.updateSimpleInputsFromSavedFilter(filters);
    globals.updateDatesFromSavedFilter(filters);

    // make sure placeholders are visible
    $('.select2-search__field').css('width': '');

  }

  updateSimpleInputsFromSavedFilter(filters) {
    /*
      Changes the checkboxes in the filter to match the filters data
      Sets the non dropdown input values to match the filters data
      Inputs:
        filters: Object that contains all of the filter data

      // NOTE:  this can be component specific because each component has
                a different set of filters
    */

    // set score input
    this.upOrDown = filters.upOrDown[1];

    // set location checkboxes
    this.homeGames = filters.location.home;
    this.awayGames = filters.location.away;
    this.neutralGames = filters.location.neutral;
    if globals.allTrue(filters.location) {
      this.homeGames = false;
      this.awayGames = false;
      this.neutralGames = false;
    }

    // set outcome checkboxes
    this.wins = filters.outcome.wins;
    this.losses = filters.outcome.losses;
    if globals.allTrue(filters.outcome) {
      this.wins = false;
      this.losses = false;
    }

    // set overtime checkboxes
    var otList = ['ot1','ot2','ot3','ot4','ot5','ot6'];
    var anyTrue = [];
    otList.forEach( (ot) => {
      this[ot] = filters.overtime[ot];
      anyTrue.push(filters.overtime[ot]);
    });
    this.otAll = false;
    if (anyTrue.every(function(tf){return tf == true;})) this.otAll = true;

    this.otNone = false;
    if (anyTrue.every(function(tf){return tf == false;})) this.otNone = true;

    this.onlyOT = filters.overtime.onlyQueryOT;

  }

  // For specifications see global.vars
  saveCurrentFilter(inputId, filterName, modalId) {
    // Get all currently set filters
    var filters = this.getAllFilters();
    globals.saveCurrentFilter(modalId, inputId, filterName, filters);
  }


  // Gametime Slider methods -- for specifications look at globals functions
  updateSliderStart(clock, inputId) {
    globals.updateSliderStart(this, clock, inputId);
  }
  updateSliderEnd(clock, inputId) {
    globals.updateSliderEnd(this, clock, inputId);
  }
  changedStartHalf(inputId) {
    globals.changedStartHalf(this, inputId);
  }
  changedEndHalf(inputId) {
    globals.changedEndHalf(this, inputId);
  }

  getPositions() {
    /*
      Returns hard-coded list of 5 positions in basketball
      in the format that select2 needs to create a dropdown menu
    */
    var data = [
      {
          id: 'point-guard',
          text: 'PG'
      },
      {
          id: 'shooting-guard',
          text: 'SG'
      },
      {
          id: 'small-forward',
          text: 'SF'
      },
      {
          id: 'power-forward',
          text: 'PF'
      },
      {
          id: 'center',
          text: 'C'
      }
    ];
    return data;
  }
  getCurrentTeamMembers() {
    var data = [
      {
        id: 'cornell-player1',
          text: '1 Kyle Brown'
      },
      {
        id: 'cornell-player10',
          text: '10 Matt Morgan'
      },
      {
          id: 'cornell-player12',
          text: '12 Jordan Abdur Ra\'oof'
      },
      {
        id: 'cornell-player32',
          text: '32 Jack Gordon'
      }
    ];
    return data;
  }

  // Send and receive data to middle stack

  applyPlayerFilters(){
    var filters = this.getAllFilters();
    // this.saveFilters(filters);
    globals.applyFilters(this.currentPageName, filters, this.dataEvent, this.dataEvent_adv);
  }
  cancelFilterProcess() {
    /*
      Kills the currently running apply filters call on this page
    */
    globals.cancelFilterProcess(this.currentPageName)
  }

  ngOnInit(): void {

    // Setup gametime slider as range slider
    $("#pgtSlider").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -20*2*60,
      max: 0,
      from: -20*2*60,
      to: 0,
      onChange: (data) => {
        this.gametime.pgtSlider.start.sec = data.from;
        this.gametime.pgtSlider.end.sec = data.to;

        this.gametime.pgtSlider.start.clock = globals.secondsToGametime(data.from);
        this.gametime.pgtSlider.end.clock = globals.secondsToGametime(data.to);

        if (data.from >= -1200) this.startTime2ndHalf.pgtSlider = true;
        else this.startTime2ndHalf.pgtSlider = false;
        if (data.to >= -1200) this.endTime2ndHalf.pgtSlider = true;
        else this.endTime2ndHalf.pgtSlider = false;
      }
    });
    $("#pgtSliderExtra").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -20*2*60,
      max: 0,
      from: -20*2*60,
      to: 0,
      onChange: (data) => {
        this.gametime.pgtSliderExtra.start.sec = data.from;
        this.gametime.pgtSliderExtra.end.sec = data.to;

        this.gametime.pgtSliderExtra.start.clock = globals.secondsToGametime(data.from);
        this.gametime.pgtSliderExtra.end.clock = globals.secondsToGametime(data.to);

        if (data.from >= -1200) this.startTime2ndHalf.pgtSliderExtra = true;
        else this.startTime2ndHalf.pgtSliderExtra = false;
        if (data.to >= -1200) this.endTime2ndHalf.pgtSliderExtra = true;
        else this.endTime2ndHalf.pgtSliderExtra = false;
      }
    });
    $("#pgtSliderOT").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -5*60,
      max: 0,
      from: -5*60,
      to: 0,
      onChange: (data) => {
        this.gametime.pgtSliderOT.start.sec = data.from;
        this.gametime.pgtSliderOT.end.sec = data.to;

        this.gametime.pgtSliderOT.start.clock = globals.secondsToGametime(data.from);
        this.gametime.pgtSliderOT.end.clock = globals.secondsToGametime(data.to);
      }
    });

    $(".otButton").change(function () {
      if (this.checked == false) {
        $("#otAll").prop('checked', true).click();
      }
      else {
        $("#otNone").prop('checked', true).click();
      }
    });

    $("#otAll").change(function () {
      if (this.checked == true) {
        $("#ot1").prop('checked', false).click();
        $("#ot2").prop('checked', false).click();
        $("#ot3").prop('checked', false).click();
        $("#ot4").prop('checked', false).click();
        $("#ot5").prop('checked', false).click();
        $("#ot6").prop('checked', false).click();
        $("#otNone").prop('checked', true).click();
      }
    });

    $("#otNone").change(function () {
      if (this.checked== true) {
        $("#ot1").prop('checked', true).click();
        $("#ot2").prop('checked', true).click();
        $("#ot3").prop('checked', true).click();
        $("#ot4").prop('checked', true).click();
        $("#ot5").prop('checked', true).click();
        $("#ot6").prop('checked', true).click();
        $("#otAll").prop('checked', true).click();
      }
    });

    // set up the multiple select dropdowns
    select2();
    globals.createSelect2("#players-position", 'Select Position(s)', this.getPositions);
    globals.createSelect2("#players-team", 'Select Team(s)', function(){ return [] });
    globals.createSelect2("#players-opponent", 'Select Team(s)', function(){ return []; });
    globals.createSelect2("#players-in-lineup", 'Select Player(s)', function(){ return [] });
    globals.createSelect2("#players-out-lineup", 'Select Player(s)', function(){ return [] });
    globals.createSelect2("#players-upOrDown", "Select", globals.getUpOrDown);

    // refresh data for select2's that get dropdowns items from db via middle stack
    globals.getTeams(this.currentPageName);
    globals.getPlayers(this.currentPageName);

    // setup datepickers
    var season = globals.getSeason();
    var startSeason = season[0];
    var today = season[1];

    $("#"+this.currentPageName+"-start-date").find('input').val(startSeason.toLocaleDateString());
    $("#"+this.currentPageName+"-start-date").datepicker({
      title: "Filter Start Date",
      startDate: "11/01/2014",
      endDate : 'now',
      clearBtn: true,
      todayBtn: true,
    });
    $("#"+this.currentPageName+"-start-date").datepicker('update', startSeason);

    $("#"+this.currentPageName+"-end-date").find('input').val(today.toLocaleDateString());
    $("#"+this.currentPageName+"-end-date").datepicker({
      title: "Filter End Date",
      startDate: "11/01/2014",
      endDate : 'now',
      clearBtn: true,
      todayBtn: true,
    });

    // styling on select2s done here after initialization
    $(".select2-selection__rendered").css("overflow-x","scroll");
    $(".select2-selection.select2-selection--multiple").css("line-height","1em");
    $(".select2-selection.select2-selection--multiple").css("min-height","26px");

    // tooltip instatiation
    $(".location-tooltip").tooltip();
    $(".second-half-tooltip").tooltip();
    $(".time-tooltip").tooltip();
  }

}
