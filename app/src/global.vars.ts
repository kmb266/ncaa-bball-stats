'use strict';

const fs = require('fs');
const path = require('path');

import * as jquery from 'jquery';
window['$'] = jquery;
window['jQuery'] = jquery;

export const saved_filters_file = path.join(__dirname, 'assets', 'saved_filters.json');
export const navHeight: number = 50;
export const pages: Array<string> = ["players", "teams","games"];
export const numPages: number = pages.length;

const PROD = true;

export const getSeason = () => {
  /*
    Returns object with the default start and end of current season
    if in season and most recent season if in offseason
  */
  var today = new Date();
  var year = today.getFullYear();
  var startSeason = new Date('11/1/'+ year);
  if (startSeason > today) {
    year = year - 1;
    startSeason = new Date('11/1/'+ year);
  }
  return [startSeason, today];

}

export const secondsToGametime = (totalSeconds) => {
  if (Math.abs(totalSeconds) > 1200) {
    var s = Math.abs(totalSeconds) - 20*60;
    var minutes = Math.floor(s / 60);
    var seconds = s % 60;
    if (minutes < 10) {minutes = '0'+ minutes;}
    if (seconds < 10) {seconds = '0'+ seconds;}
    return minutes+':'+seconds
  }
  var s = Math.abs(totalSeconds);
  var minutes = Math.floor(s / 60);
  var seconds = s % 60;
  if (minutes < 10) {minutes = '0'+ minutes;}
  if (seconds < 10) {seconds = '0'+ seconds;}
  return minutes+':'+seconds;
}
export const gametimeToSeconds = (gametime, isSecondHalf) => {
  var minSec = gametime.split(":");
  if (isSecondHalf) return parseInt(minSec[0])*60 + parseInt(minSec[1]);
  return parseInt(minSec[0])*60 + parseInt(minSec[1]) + 1200;
}
export const allTrue = (obj) => {
  /*
    Heper function to check if all values of an object are true
    Returns: boolean
  */
  for(var o in obj)
    if(!obj[o]) return false;
  return true;
}

export const createSelect2 = (id, placeholder, getData) => {
  $(id).select2({
    // dropdownCssClass : 'small-dropdown'
    placeholder: placeholder,
    dropdownAutoWidth : true,
    width: 'element',
    allowClear: true,
    data: getData()
  });
}

export const updateSliderStart = (that, clock, inputId) => {
  /*
    Changes the start time of range slider with id:inputId to
    the input clock time

    Inputs:
      clock: string = game time string in format 'MM:SS'
      inputId: string = id of the range slider that corresponds to input
        being changed
  */
  var seconds = - gametimeToSeconds(clock, that.startTime2ndHalf[inputId]);
  if (seconds >= that.gametime[inputId].end.sec) {
    that.invalidInput(event);
    return;
  }

  that.gametime[inputId].start.clock = clock;
  that.gametime[inputId].start.sec = seconds;
  var slider = $("#"+inputId).data("ionRangeSlider");
  slider.update({from: seconds});
}
export const updateSliderEnd = (that, clock, inputId) => {
  /*
    Changes the end time of range slider with id:inputId to
    the input clock time

    Inputs:
      clock: string = game time string in format 'MM:SS'
      inputId: string = id of the range slider to be changed
  */
  var seconds = - gametimeToSeconds(clock, that.endTime2ndHalf[inputId]);
  if (seconds <= that.gametime[inputId].start.sec) {
    that.invalidInput(event);
    return;
  }
  that.gametime[inputId].end.clock = clock;
  that.gametime[inputId].end.sec = seconds;
  var slider = $("#"+inputId).data("ionRangeSlider");
  slider.update({to: seconds});
}
export const changedStartHalf = (that, inputId) => {
  /*
    Changes the slider with id inputId start time to the opposite half of what it
    currently is.
    If the box is currelty not checked, the time is in the first half.
    If you check the box, the time displayed in the text input that corresponds
    to the slider with id:inputId is now in the second half and vice versa.

    Inputs:
      inputId: string = id of range slider to be changed
  */
  var slider = $("#"+inputId).data("ionRangeSlider");
  if (that.startTime2ndHalf[inputId]) {
    that.gametime[inputId].start.sec += 1200;
    slider.update({from: that.gametime[inputId].start.sec});
  }
  else {
    that.gametime[inputId].start.sec -= 1200;
    slider.update({from: that.gametime[inputId].start.sec});
  }

  console.log(that.gametime[inputId].start.sec);
}
export const changedEndHalf = (that, inputId) => {
  /*
    Changes the slider with id inputId end time to the opposite half of what it
    currently is.
    If the box is currelty not checked, the time is in the first half.
    If you check the box, the time displayed in the text input that corresponds
    to the slider with id:inputId is now in the second half and vice versa.

    Inputs:
      inputId: string = id of range slider to be changed
  */
  var slider = $("#"+inputId).data("ionRangeSlider");
  if (that.endTime2ndHalf[inputId]) {
    that.gametime[inputId].end.sec += 1200;
    slider.update({to: that.gametime[inputId].end.sec});
  }
  else {
    that.gametime[inputId].end.sec -= 1200;
    slider.update({to: that.gametime[inputId].end.sec});
  }

  console.log(that.gametime[inputId].end.sec);
}

export const getUpOrDown = () => {
  var data = [
    {
      id: 'up',
      text: 'up by'
    },
    {
      id: 'down',
      text: 'down'
    },
    {
      id: 'withIn',
      text: 'within',
      selected: true
    },
  ];
  return data;
}

export const filters = null;

var active_child_processes = {};

var callAdvancedStats = (page, filters_data, emitter) => {
  /*
    activate a call to get the advanced stats
  */
  console.log('calling advanced_stats')
  filters_data.advanced_stats = true;
  if (PROD) {
    var path_to_exe = path.join(__dirname, 'python', 'middle_stack', 'data_manager'),
        py = require('child_process').execFile(path_to_exe),
        data = filters_data,
        dataString = '';
  }
  else {
    var spawn = require('child_process').spawn,
        py = spawn('python', ['./data_manager.py']),
        data = filters_data,
        dataString = '';
  }
  // Start adv stat loading gif
  $('#'+page+'adv-stat-spinner-wrapper').show();

  //save the python process outside the function to be able to cancel if necessary
  active_child_processes['adv-stats-'+page] = py;
  // console.log(active_child_processes)

  // retrieve the data from the data_manager.py
  py.stdout.on('data', function(data){
    dataString += data.toString();
  });

  // print the data when the child process ends
  py.stdout.on('end', function(){
    if (py.killed) {
      // emitter.emit({})
      console.log('dead py')
    }
    else {
      try {
        var data = JSON.parse(dataString);
        // console.log(data);
        // show table after data loaded -- THIS IS DIFFERENT THAN BEFORE DUE TO TIME CONSTRAINTS
        emitter.emit(dataString.replace(/'/g, ' '));

      }
      catch(err) {
        console.log(err)

        // NOTE: UNCOMMENT THIS LINE TO ALLOW FOR ERROR USER ALERTING FOR ERROR
        alert('There was an unexpected error: \n\n'+err+'\n\nPlease try again.');
      }
    }

    // stop loading gif
    $('#'+page+'adv-stat-spinner-wrapper').hide();

    // remove current process from list of active processes as it is finished
    delete active_child_processes['adv-stats-'+page]

  });

  // if there is an error, print it out
  py.on('error', function(err) {
    console.log("Failed to start child. " + err);
    $('#'+page+'-apply-filters-btn').prop('disabled', function(i, v) { return !v; });
    delete active_child_processes['adv-stats-'+page]
  });

  py.stdin.write(JSON.stringify(data));
  py.stdin.end();
}
export const applyFilters = (page, filters_data, emitter, emitter_adv) => {
  // initial a child process

  this.filters = filters_data;

  // When packaging the app, use pyinstaller to package all of the python files
  // and then put the dist directory in the python folder and the files will run
  // uncomment the next 3 lines to replace spawn and py vars below
  // got ideas from https://github.com/fyears/electron-python-example
  if (PROD) {
    var path_to_exe = path.join(__dirname, 'python', 'middle_stack', 'data_manager'),
        py = require('child_process').execFile(path_to_exe),
        data = filters_data,
        dataString = '';
  }
  else {
    var spawn = require('child_process').spawn,
        py = spawn('python', ['./data_manager.py']),
        data = filters_data,
        dataString = '';
  }
  // Start loading gif
  $('#'+page+'-spinner-wrapper').toggle();
  // disable apply filters button until done loading data
  $('#'+page+'-apply-filters-btn').prop('disabled', function(i, v) { return !v; });
  // hide the table until loaded
  $('#content-'+page).first().hide();

  //save the python process outside the function to be able to cancel if necessary
  active_child_processes[page] = py;
  // console.log(active_child_processes)

  // retrieve the data from the data_manager.py
  py.stdout.on('data', function(data){
    dataString += data.toString();
  });

  // print the data when the child process ends
  py.stdout.on('end', function(){
    if (py.killed) {
      emitter.emit({})
    }
    else {
      try {
        var data = JSON.parse(dataString);
        // console.log(data);
        // send data up to app component
        emitter.emit(dataString.replace(/'/g, ' '));
        //call the advanced stats function
        if (page == "players") callAdvancedStats(page, filters_data, emitter_adv);
      }
      catch(err) {
        console.log(err)

        // NOTE: UNCOMMENT THIS LINE TO ALLOW FOR ERROR USER ALERTING FOR ERROR
        alert('There was an unexpected error while calculating the advanced statistics:\
         \n\n'+err+'\n\nPlease try again.');
      }
    }

    // stop loading gif
    $('#'+page+'-spinner-wrapper').hide();

    //enable apply filters button again
    $('#'+page+'-apply-filters-btn').prop('disabled', function(i, v) { return !v; });

    // show table after data loaded
    $('#content-'+page).first().show()

    // remove current process from list of active processes as it is finished
    delete active_child_processes[page]

  });

  // if there is an error, print it out
  py.on('error', function(err) {
    console.log("Failed to start child. " + err);
    $('#'+page+'-apply-filters-btn').prop('disabled', function(i, v) { return !v; });
    delete active_child_processes[page]
  });

  py.stdin.write(JSON.stringify(data));
  py.stdin.end();

  /*
  const {exec} = require('child_process');
  exec('python ./data_manager.py', (error, stdout, stderr) => {
    if (error) {
      console.log(error);
    } else {
      //console.log(stderr);
      console.log(stdout);
    }
  });
  */
}

export const cancelFilterProcess = (page) => {
  /*
    Cancels the backend python process for specific page this means
    that only one apply filters process can be run for each page (or tab)
  */
  var py_process = active_child_processes[page]
  console.log('killing active process for '+page);
  py_process.kill()
}
export const validateFilterName = (filterName) => {
  /*
    Check if the filter name is valid.
    Valid means the filter name does not already exist

    Input: filterName: string = name of the filter to be saved
    --- Do we need to check anything else? --
  */
  var valid = true;

  // return false if filter name is empty or undefined
  if (filterName == undefined || filterName == '') return false;

  // open the saved filters file and add saved filter objects to list
  var lines = require('fs').readFileSync(saved_filters_file, 'utf-8')
    .split('\n')
    .filter(Boolean);

  // iterate through lines list and see if filtername in list
  lines.forEach(function(line) {
    var filterJson = JSON.parse(line);
    if (filterJson.filterName == filterName) {
      valid = false;
    }
  });
  return valid;
}

export const writeFilterToFile = (data, callback) => {
  /*
    Append data object to file
    Input: data: string = data to be saved to file
  */
  fs.appendFile(saved_filters_file, data, (err) => {
    if (!err) {
      console.log('The filters have been saved!');
      callback();

    }
    else {
      // TODO: display error
      console.log('Failed saving filters');
      console.log(err);
    }
  });
}

export const saveCurrentFilter = (modalId, inputId, filterName, filters) => {
  /*
    Saves current page filters as json object to file
    Input: filter_name: string = user defined name for set filters
  */
  console.log('begin saving filters');

  // check if current filter name already exists
  if validateFilterName(filterName) {

    // add filter name to object
    filters.filterName =  filterName;

    // stringify object to make it savable
    var data = JSON.stringify(filters) + '\n';

    // Save filters' stringified object to file
    writeFilterToFile(data, () => {
      // clear modal input
      $('#'+inputId).val('');

      // close modal
      $('#'+modalId).modal('toggle');

      // refresh the saved filters dropdown
      $('#saved-filters').empty();
      createSelect2("#saved-filters", 'Select Saved Filter', getSavedFilters);


    });
  }
  else {
    // the filter name already exists
    console.log('filtername already exists')
    // TODO: display error
  }
}

export const getSavedFilters = () => {
  /*
    Reads saved filters json objects from file and returns them in correct
    format to be used in select2 dropdown menue
  */
  var savedFilters = [];
  // open the saved filters file and add saved filter objects to list
  var lines = require('fs').readFileSync(saved_filters_file, 'utf-8')
    .split('\n')
    .filter(Boolean);

  // add default option to saved filters to have a null option selected on int
  var blank = {};
  blank.id = -1;
  blank.text='Choose a Filter';
  blank.selected = true;
  blank.data = {};
  savedFilters.push(blank);

  // iterate through lines list and add the formated filter to the filters object
  lines.forEach(function(line, i) {
    var filterJson = JSON.parse(line);
    var dropdownData = {};
    dropdownData.id = i;
    dropdownData.text = filterJson.filterName;
    dropdownData.data = filterJson;
    savedFilters.push(dropdownData);
  });

  return savedFilters;
}

export const clearSliders = (that, sliderId) => {
  /*
    Sets range sliders back to default
    Inputs:
      that: angular component = the component whose sliders that are being reset
      sliderId: string = the base id of the sliders to be changed
  */
  var extra = sliderId + 'Extra';
  var ot = sliderId + 'OT';
  that.gametime = {};
  that.gametime[sliderId] = {
    start:{clock: "20:00", sec:-2400},
    end:{clock: "00:00", sec:0}
  },
  that.gametime[extra] = {
    start:{clock: "20:00", sec:-2400},
    end:{clock: "00:00", sec:0}
  },
  that.gametime[ot] = {
    start:{clock: "5:00", sec:-300},
    end:{clock: "0:00", sec:0}
  }
  that.startTime2ndHalf = {}
  that.startTime2ndHalf[sliderId] = false
  that.startTime2ndHalf[extra] = false

  that.endTime2ndHalf = {}
  that.endTime2ndHalf[sliderId] = true
  that.endTime2ndHalf[extra] = true

  // update slider to match the saved filters gametime
  $("#"+sliderId).data('ionRangeSlider').update({
    from: that.gametime[sliderId].start.sec,
    to: that.gametime[sliderId].end.sec
  });

  // update extra slider to match the saved filters gametime
  $("#"+extra).data('ionRangeSlider').update({
    from: that.gametime[extra].start.sec,
    to: that.gametime[extra].end.sec
  });

    // update OTslider to match the saved filters gametime
  $("#"+ot).data('ionRangeSlider').update({
    from: that.gametime[ot].start.sec,
    to: that.gametime[ot].end.sec
  });

}

export const clearDates = (page) => {
  /*
    clears dates of input page
    Input:
      page: string = page to clear datepickers
  */
  var season = getSeason();
  $("#"+page+"-start-date").datepicker('update', season[0]);
  $("#"+page+"-end-date").find('input').val(season[1].toLocaleDateString());
}

export const updateAllSlidersFromSavedFilter = (that, sliderId, filters) => {
  /*
    Set the range sliders and corresponding data in component to the
    saved filter's data
    Inputs:
      filters: Object that contains all of the filter data
  */
  var sliderIdExtra = sliderId + 'Extra';

  that.gametime[sliderId] = filters.gametime.slider;
  that.gametime[sliderIdExtra] = filters.gametime.sliderExtra;

  // update slider to match the saved filters gametime
  $("#"+sliderId).data('ionRangeSlider').update({
    from: filters.gametime.slider.start.sec,
    to: filters.gametime.slider.end.sec
  });

  // update extra slider to match the saved filters gametime
  $("#"+sliderIdExtra).data('ionRangeSlider').update({
    from: filters.gametime.sliderExtra.start.sec,
    to: filters.gametime.sliderExtra.end.sec
  });

  //set the gamteime data in component to match the filter for both sliders
  that.startTime2ndHalf[sliderId] = filters.gametime.slider.start.sec >= -1200;
  that.endTime2ndHalf[sliderId] = filters.gametime.slider.end.sec >= -1200;

  that.startTime2ndHalf[sliderIdExtra] = filters.gametime.sliderExtra.start.sec >= -1200;
  that.endTime2ndHalf[sliderIdExtra] = filters.gametime.sliderExtra.end.sec >= -1200;

  // show the extra slider if necessary
  that.hidePgtExtra = !filters.gametime.multipleTimeFrames;

}

export const updateSelect2sFromSavedFilter = (page, filters) => {
  /*
    Changes the dropdown menus' values to match the data in the filter
    Inputs:
      page: string = filter's page to edit select2 dropdowns
      filters: Object that contains all of the filter data
  */
  $('.'+page+'-select2').each(function() {
    var id = this.id.split('-')[1];
    if (filters[id] != undefined && filters[id].length > 0) {
      $(this).val(filters[id]).trigger('change');
    }
    else {
      $(this).val(null).trigger('change');
    }
  });

}
export const updateDatesFromSavedFilter = (filters) => {
  /*
  Changes the datepickers to match the data in the filter
  Inputs:
    filters: Object that contains all of the filter data
  */
  var startDate = new Date(filters.dates.start);
  var endDate = new Date(filters.dates.end);
  $("#"+filters.page+"-start-date").datepicker('update', startDate);
  $("#"+filters.page+"-end-date").datepicker('update', endDate);

}
export const getTeams = (page) => {
  /*
    Middle stack:
      Program runs python auto_complete.py and sets the select2s with the id
  */

  if (PROD) {
    // uncomment below to package app after pyinstalling auto_complete
    var path_to_exe = path.join(__dirname, 'python', 'middle_stack', 'auto_complete'),
        py = require('child_process').execFile(path_to_exe),
        data = {'field': 0},
        dataString = '';
  }
  else {
    var spawn = require('child_process').spawn,
        py = spawn('python', ['./auto_complete.py']),
        data = {'field': 0},
        dataString = '';
  }

  // retrieve the data from the data_manager.py
  py.stdout.on('data', function(data){
    dataString += data.toString();
  });

  // print the data when the child process ends
  py.stdout.on('end', function(){
    //console.log("Finished calling get Teams!");
    // console.log(dataString)
    var teams = JSON.parse(dataString)
    var placeholder = 'Select Team(s)';

    $('#'+page+'-opponent').select2({
      placeholder: placeholder,
      dropdownAutoWidth : true,
      width: '115px',
      allowClear: true,
      data: teams.sort(function (a, b) {
            a = a.text.toLowerCase();
            b = b.text.toLowerCase();
            if (a > b) {
                return 1;
            } else if (a < b) {
                return -1;
            }
            return 0;
        });
    });

    teams.forEach(function(teamObj){
      if (teamObj.text == "Cornell") {
        teamObj.selected = true;
      }
    });

    $('#'+page+'-team').select2({
      placeholder: placeholder,
      dropdownAutoWidth : true,
      width: '115px',
      allowClear: true,
      data: teams
    });

    $('.select2-search__field').css('width': '');

  });

  // if there is an error, print it out
  py.on('error', function(err) {
    console.log("Failed to start child. " + err);
  });

  py.stdin.write(JSON.stringify(data));
  py.stdin.end();
}

export const getPlayers = (page) => {
  /*
    Middle stack:
      Program runs python auto_complete.py and sets the select2s with the id
  */
  // uncomment below to package app after pyinstalling auto_complete
  if (PROD) {
    // uncomment below to package app after pyinstalling auto_complete
    var path_to_exe = path.join(__dirname, 'python', 'middle_stack', 'auto_complete'),
        py = require('child_process').execFile(path_to_exe),
        data = {'field': 1},
        dataString = '';
  }
  else {
    var spawn = require('child_process').spawn,
        py = spawn('python', ['./auto_complete.py']),
        data = {'field': 1},
        dataString = '';
  }

  // retrieve the data from the auto_complete.py
  py.stdout.on('data', function(data){
    dataString += data.toString();
  });

  // print the data when the child process ends
  py.stdout.on('end', function(){
    //console.log(typeof(dataString), dataString.replace(/'/g, '"'));
    // console.log("Players: " + dataString)
    var players = JSON.parse(dataString)//.replace(/'/g, '"'))
    var placeholder = 'Select Team(s)';

    $('#'+page+'-out-lineup').select2({
      placeholder: placeholder,
      dropdownAutoWidth : true,
      width: '115px',
      allowClear: true,
      data: players
    });

    $('#'+page+'-in-lineup').select2({
      placeholder: placeholder,
      dropdownAutoWidth : true,
      width: '115px',
      allowClear: true,
      data: players
    });

    $('.select2-search__field').css('width': '');

  });

  // if there is an error, print it out
  py.on('error', function(err) {
    console.log("Failed to start child. " + err);
  });

  py.stdin.write(JSON.stringify(data));
  py.stdin.end();
}
