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
  selector: 'filter-games',
  templateUrl: 'templates/filter.games.html'
})
export class GamesFilterComponent implements OnInit {
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

      // apply the saved filters and send to middle stack
      globals.applyFilters(this.currentPageName, savedFilterObj, this.dataEvent, this.dataEvent_adv);

      this.updateFilters(savedFilterObj);

    }

  }

  currentPageName = "games";

  // Object to save time from sliders
  gametime = {
    ggtSlider:{
      start:{clock: "20:00", sec:-2400},
      end:{clock: "00:00", sec:0}
    },
    ggtSliderExtra:{
      start:{clock: "20:00", sec:-2400},
      end:{clock: "00:00", sec:0}
    },
    ggtSliderOT:{
      start:{clock: "5:00", sec:-300},
      end:{clock: "0:00", sec:0}
    }
  };
  // Tells if the time referenced in the sliders in the first or second half
  startTime2ndHalf = {
    ggtSlider:false,
    ggtSliderExtra: false,
  }
  endTime2ndHalf = {
    ggtSlider:true,
    ggtSliderExtra: true,
  }

  // 2 way bound filters -- simple checkbox and number inputs
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

  // Tells if the extra slider shown to show two time frames
  hidePgtExtra = true;
  hideOvertime = true;

  invalidInput(el) {
    //show a red box around the input box
    console.log("invalid input");
  }

  getAllFilters() {
    // Initialize filters object to return
    var filters = {};

    // set which page we are requesting the filters from
    filters['page'] = this.currentPageName;

    // Gather dropdown data from .page-select2 class
    $('.games-select2').each(function() {
      // Normalize filter names to send to middle stack by removing page name
      var id = this.id.split('-')[1];
      // add filters to filters object
      filters[id] = $(this).val();
    });

    // Gather game time data from sliders
    filters.gametime = {};
    // Normalize gametime object names for simplicity on backend
    filters.gametime.slider = this.gametime.ggtSlider;
    filters.gametime.sliderExtra = this.gametime.ggtSliderExtra;
    // Include if extra time should even be looked at for backend
    filters.gametime.multipleTimeFrames = !this.hidePgtExtra;

    // Gather game score and recent game filters
    filters.upOrDown = [filters.upOrDown, this.upOrDown];

    // Gather game location filters; default is to include all games (all true)
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
    // Gather game outcome filters; default is both wins and losses = true
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
        otSliderStart: this.gametime.ggtSliderOT.start.sec + 300,
        otSliderEnd: this.gametime.ggtSliderOT.end.sec + 300,
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
    /*
      Save filters to file in order to be able to use
      back and forward button
      Input:
        filters: object containing all of the filters input by the user
    */
    this.oldFilters.push(filters);
  }
  clearAllFilters() {
    /*
      Clears filters by setting checkboxes to false,
      removing all input from dropdowns, set number inputs to null
    */
    var filters = this.getAllFilters();
    this.saveFilters(filters);
    // clear dropdown inputs
    $('.games-select2').val(null).trigger('change');
    $('#games-select-season').val('season17').trigger('change');

    // clear checkboxes and number inputs
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

    globals.clearSliders(this, "ggtSlider");
    globals.clearDates(this.currentPageName);

    console.log("cleared all filters");
  }

  updateFilters(filters) {
    /*
      Changes the filters in the side bar to match the chose saved filter
      Inputs:
        filters: Object that contains all of the filter data
    */

    // clear all filters just to be safe
    this.clearAllFilters();

    // set all of the filters with the saved filters
    globals.updateAllSlidersFromSavedFilter(this, 'ggtSlider', filters);
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


  applyPlayerFilters(){
    /*
      Get all of the filters as an object
      // TODO: Save them to be able to enable back and forward buttons
      and send them to the backend
    */
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

    $("#ggtSlider").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -20*2*60,
      max: 0,
      from: -20*2*60,
      to: 0,
      onChange: (data) => {
        this.gametime.ggtSlider.start.sec = data.from;
        this.gametime.ggtSlider.end.sec = data.to;

        this.gametime.ggtSlider.start.clock = globals.secondsToGametime(data.from);
        this.gametime.ggtSlider.end.clock = globals.secondsToGametime(data.to);

        if (data.from >= -1200) this.startTime2ndHalf.ggtSlider = true;
        else this.startTime2ndHalf.ggtSlider = false;
        if (data.to >= -1200) this.endTime2ndHalf.ggtSlider = true;
        else this.endTime2ndHalf.ggtSlider = false;
      }
    });
    $("#ggtSliderExtra").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -20*2*60,
      max: 0,
      from: -20*2*60,
      to: 0,
      onChange: (data) => {
        this.gametime.ggtSliderExtra.start.sec = data.from;
        this.gametime.ggtSliderExtra.end.sec = data.to;

        this.gametime.ggtSliderExtra.start.clock = globals.secondsToGametime(data.from);
        this.gametime.ggtSliderExtra.end.clock = globals.secondsToGametime(data.to);

        if (data.from >= -1200) this.startTime2ndHalf.ggtSliderExtra = true;
        else this.startTime2ndHalf.ggtSliderExtra = false;
        if (data.to >= -1200) this.endTime2ndHalf.ggtSliderExtra = true;
        else this.endTime2ndHalf.ggtSliderExtra = false;
      }
    });
    $("#ggtSliderOT").ionRangeSlider({
      type: "double",
      hide_min_max: true,
      hide_from_to: true,
      min: -5*60,
      max: 0,
      from: -5*60,
      to: 0,
      onChange: (data) => {
        this.gametime.ggtSliderOT.start.sec = data.from;
        this.gametime.ggtSliderOT.end.sec = data.to;

        this.gametime.ggtSliderOT.start.clock = globals.secondsToGametime(data.from);
        this.gametime.ggtSliderOT.end.clock = globals.secondsToGametime(data.to);
      }
    });

    $(".otButton").change(function () {
      if (this.checked == false) {
        $("#gameOtAll").prop('checked', true).click();
      }
      else {
        $("#gameOtNone").prop('checked', true).click();
      }
    });

    $("#gameOtAll").change(function () {
      if (this.checked == true) {
        $("#gameOt1").prop('checked', false).click();
        $("#gameOt2").prop('checked', false).click();
        $("#gameOt3").prop('checked', false).click();
        $("#gameOt4").prop('checked', false).click();
        $("#gameOt5").prop('checked', false).click();
        $("#gameOt6").prop('checked', false).click();
        $("#gameOtNone").prop('checked', true).click();
      }
    });

    $("#gameOtNone").change(function () {
      if (this.checked== true) {
        $("#gameOt1").prop('checked', true).click();
        $("#gameOt2").prop('checked', true).click();
        $("#gameOt3").prop('checked', true).click();
        $("#gameOt4").prop('checked', true).click();
        $("#gameOt5").prop('checked', true).click();
        $("#gameOt6").prop('checked', true).click();
        $("#gameOtAll").prop('checked', true).click();
      }
    });

    // set up the multiple select dropdowns
    // id of dropdowns pattern is #currentPageName-category eg. #games-opponent
    select2();
    globals.createSelect2("#games-team", 'Select Team(s)', function(){ return [] });
    globals.createSelect2("#games-opponent", 'Select Team(s)', function(){ return [] });
    globals.createSelect2("#games-upOrDown", 'Select', globals.getUpOrDown);

    // refresh data for select2's that get dropdowns items from db via middle stack
    globals.getTeams(this.currentPageName);

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

  }

}
