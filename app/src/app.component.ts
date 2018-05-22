import { NgModule, Component, OnInit } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FiltersModule } from './components/filters.module';
import { StatsTableModule } from './components/stats.table.component';
import { MainNavModule } from './components/nav.main.component';
import * as globals from './global.vars';

@Component({
  selector: 'App',
  templateUrl:'templates/app.html',
  host: {
    '(window:resize)': 'onResize($event)'
  }
})
export class AppComponent implements OnInit {
  public readonly title = 'Cornell Basketball Stats';
  contentHeight = window.innerHeight - globals.navHeight;

  currentPage = "players";
  table_data = {
    players: {},
    teams: {},
    games: {}
  };
  table_data_adv = {
    players: {},
    teams: {},
    games: {}
  }

  filter_data = {
    players: "loading players saved filter...",
    teams: "loading teams saved filter...",
    games: "loading games  saved filter..."
  };

  ngOnInit(): void {
    console.log('component initialized');
  }

  receiveData(event) {
    this.table_data[this.currentPage] = event;
    console.log(event);
  }
  receiveAdvData(event) {
    this.table_data_adv[this.currentPage] = event;
    console.log(event);
  }

  onResize(event) {
    this.contentHeight = window.innerHeight - globals.navHeight;
  }

  pageChanged(event) {
    this.currentPage = event;
  }

  savedFilterChanged(event) {
    /*
      Navigate to the saved filters' tab
      and pass filter from nav to correct tab filter
    */

    // change displayed page
    this.currentPage = event.page;

    // pass the data to the filter
    this.filter_data[event.page] = event;

  }

}

@NgModule({
  imports: [BrowserModule, StatsTableModule, FiltersModule, MainNavModule],
  declarations: [AppComponent],
  bootstrap: [AppComponent]
})
export class AppModule {}
