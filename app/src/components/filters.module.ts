import { NgModule} from '@angular/core';
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { PlayersFilterComponent } from "./filter.players.component"
import { TeamsFilterComponent } from "./filter.teams.component"
import { GamesFilterComponent } from "./filter.games.component"

@NgModule({
  imports: [CommonModule, FormsModule],
  exports: [PlayersFilterComponent, TeamsFilterComponent, GamesFilterComponent],
  declarations: [PlayersFilterComponent, TeamsFilterComponent, GamesFilterComponent],
  providers: []
})
export class FiltersModule {}
