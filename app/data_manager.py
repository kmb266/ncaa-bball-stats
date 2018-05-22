from __future__ import division
import sys, json
from data_retriever import masterQuery
from stats_results import stats_calculation

def sampleForm():
    form = {
        "page": "players",
        "position": [],
        "team": [
            "SYR"
        ],
        "opponent": [
            "DUKE"
        ],
        "in": [],
        "out": [],
        "upOrDown": [
            "withIn", None
        ],
        "gametime": {
            "slider": {
                "start": {
                    "clock": "20:00",
                    "sec": -2400
                },
                "end": {
                    "clock": "00:00",
                    "sec": 0
                }
            },
            "sliderExtra": {
                "start": {
                    "clock": "20:00",
                    "sec": -2400
                },
                "end": {
                    "clock": "00:00",
                    "sec": 0
                }
            },
            "multipleTimeFrames": False
        },
        "location": {
            "home": True,
            "away": True,
            "neutral": True
        },
        "outcome": {
            "wins": True,
            "losses": True
        },
        "overtime": {
            "otSliderStart": 0,
            "otSliderEnd": 300,
            "ot1": True,
            "ot2": True,
            "ot3": True,
            "ot4": True,
            "ot5": True,
            "ot6": True,
            "onlyQueryOT": False
        },
        "dates": {
            "start": 1509508800000,
            "end": 1525665600000
        }
    }
    return form


def calculatePercentages(box_score):
    # FG% FT% 3PT%
    if "FG" in box_score and "FGA" in box_score and box_score["FGA"] != 0:
        box_score["FGPerc"] = round(box_score["FG"] / box_score["FGA"], 3)
    else:
        box_score["FGPerc"] = 0
    if "3PT" in box_score and "FGA" in box_score and box_score["FGA3"] != 0:
        box_score["FG3Perc"] = round(box_score["3PT"] / box_score["FGA3"], 3)
    else:
        box_score["FG3Perc"] = 0
    if "FT" in box_score and "FTA" in box_score and box_score["FTA"] != 0:
        box_score["FTPerc"] = round(box_score["FT"] / box_score["FTA"], 3)
    else:
        box_score["FTPerc"] = 0

def getAverages(players_score, team_score):
    """
    Name: getAverages
    Returns: the average box score for each player
    Arguments:
    players_score: box score for each player in each game
    team_score: box score for the team in each game
    """
    attributes = ["FG", "FGA", "3PT", "FGA3", "FT", "FTA", "OREB", "DREB", "REB",
    "PF", "AST", "TO", "BLK", "STL", "TP", "PTS", "MIN", "GAMES"]
    advanced_attributes = ["PProdAst", "q5","q12","ASTPart","FTPart","FTmPoss","DOREB_perc","DFG_perc",
    "eFG_perc","Turnover_perc","FTr","FG_2_perc","FG_3_perc","FGr_2","FGr_3",
    "Usage_Rate","ASTPart","ASTr","AST_Ratio","TS_perc","Total_REB_pect","BLK_perc","Game_Score","PIE",
    "qAST", "FGmPoss", "FMwt", "Pace", "STL_perc", "PProdFG", "FGPart", "PProdOREB", "OREBPart","Stops_1", "Stops_2", "Stops",
    "PProd", "ScPoss", "Stop_perc", "TotPoss", "DRTG", "Individual_Offensize_Rating", "Individual_Floor_Percentage"]

    players_boxscore = []
    teams_boxscore = {}

    for values in players_score:
        games = values["games"]
        player = {"name" : values["name"], "team" : values["team"]}
        games_played = len(games)

        for attribute in attributes + advanced_attributes:
            for game, game_boxscore in games.items():
                if attribute in game_boxscore:
                    val = game_boxscore[attribute] or 0
                    val = int (val)
                    if attribute in player:
                        player[attribute] += val
                    else:
                        player[attribute] = val

            if attribute in player:
                player[attribute] = round(player[attribute] / games_played, 2)

        player["GAMES"] = games_played
        calculatePercentages(player)
        players_boxscore.append(player)

    for team_id, values in team_score.items():
        games = values["games"]
        team = {"team_id" : team_id}
        games_played = len(games)

        for attribute in attributes:
            for game, game_boxscore in games.items():
                if attribute in game_boxscore:
                    if attribute in team:
                        team[attribute] += game_boxscore[attribute]
                    else:
                        team[attribute] = game_boxscore[attribute]
            if attribute in team:
                team[attribute] = round(team[attribute] / games_played, 2)
        team["GAMES"] = games_played
        calculatePercentages(team)
        team["MIN"] = 200

        teams_boxscore[team_id] = team

    return (players_boxscore, teams_boxscore)


def getAverageForTeam(team_score):
    # TODO : if wanted to add dates to each game
    attributes = ["FG", "FGA", "3PT", "FGA3", "FT", "FTA", "OREB", "DREB", "REB",
    "PF", "AST", "TO", "BLK", "STL", "TP", "PTS", "MIN"]

    # game_data is a list of all boxscores of teams per game
    # game_data[game_id] has {"home" : home_boxscore, "away" : away_boxscore}
    game_data = {}

    average_box_score = {}

    for team_id, values in team_score.items():
        games = values["games"]
        team = {"team_id" : team_id}
        games_played = len(games)

        for attribute in attributes:
            for game_id, game_boxscore in games.items():
                game_boxscore["team_id"] = team_id
                calculatePercentages(game_boxscore)
                game_boxscore["MIN"] = 200
                key = "home"
                if game_boxscore["away"] == team_id:
                    key = "away"

                if game_id in game_data:
                    game_data[game_id][key] = game_boxscore
                else:
                    game_data[game_id] = {key : game_boxscore}

                if attribute in game_boxscore:
                    if attribute in team:
                        team[attribute] += game_boxscore[attribute]
                    else:
                        team[attribute] = game_boxscore[attribute]
            if attribute in team:
                team[attribute] = round(team[attribute] / games_played, 2)

        calculatePercentages(team)
        team["MIN"] = 200
        average_box_score[team_id] = team

    game_data_list = []

    for game_id, game_boxscores in game_data.items():
        home = game_boxscores["home"]
        away = game_boxscores["away"]
        home["name"] = home["team_id"] #+ " - Game " + str(game_id)
        away["name"] = away["team_id"] #+ " - Game " + str(game_id)

        game_data_list.append(home)
        game_data_list.append(away)

    for team_id, game_boxscore in average_box_score.items():
        game_boxscore["name"] = game_boxscore["team_id"] + " - Average"
        game_data_list.append(game_boxscore)


    return game_data_list



def filterResults(players_score, team_score, form, mappings):
    teamIds = form["team"]
    data = []
    for team in teamIds:
        team_id = mappings[team]
        if team_id in team_score:
            team_boxscore = team_score[team_id]
            team_boxscore["name"] = team_id
            data.append(team_boxscore)
            for player in players_score:
                if player["team"] == team_id:
                    data.append(player)
    return data

def filterTeams(game_data, form, mappings):
    """
    name : filterTeams for games page
    Returns: the box score of the only team without opponent
    Arguments:
    game_data: box score for both team and opponent
    form : the request form from the front end
    """
    teamIds = form["team"]
    data = []
    for team in teamIds:
        team_id = mappings[team]
        for games in game_data:
            if games["team_id"] == team_id:
                # change the name to the opponent team name
                if "Average" not in games["name"]:
                    if games["home"] == team_id:
                        games["name"] = games["away"]
                    if games["away"] == team_id:
                        games["name"] = games["home"]

                data.append(games)
    return data

'''
retrieve the data from the backend
'''
def retrieveData(form):
    page = "players"
    if "page" in form:
        page = form["page"]

    (players_score, team_score, mappings) = masterQuery(form)
    #final = {"dataTab" : "players", "data" : players_score, "teamOverall" : team_score}

    if page == "players":
        if 'advanced_stats' in form:
            final = {"dataTab" : "players", "data" : players_score, "teamOverall" : team_score}
            final = stats_calculation(final)
            players_score = final["data"]
            #p1 = players_score[1]
            #p1_String = json.dumps(p1)
            #raise Exception(p1)
            team_score = final["teamOverall"]

        (players_score, team_score) = getAverages(players_score, team_score)
        players_score = filterResults(players_score, team_score, form, mappings)
        final = {"dataTab" : "players", "data" : players_score, "teamOverall" : team_score}
    elif page == "teams":
        game_data = getAverageForTeam(team_score)
        final = {"dataTab" : "teams", "data" : game_data}
    elif page == "games":
        game_data = getAverageForTeam(team_score)
        data = filterTeams(game_data, form, mappings)
        final = {"dataTab" : "games", "data" : data}

    final = json.dumps(final)
    return final

def tidyForm(form):
    if ('season' in form) == False:
        form['season'] = None

    if ('in' in form) == False:
        form['in'] = []
    if ('out' in form) == False:
        form['out'] = []
    if ('position' in form) == False:
        form['position'] = []

    return form
'''
get the form information from the front end
'''
def getForm():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def main():
    form = getForm()
    # form = sampleForm()

    form = tidyForm(form)
    try:
        data = retrieveData(form)
    except Exception as e:
        data = {"error" : e.message, "doc" : e.__doc__}
        data = json.dumps(data)

    #return what we get
    print(data)
    sys.stdout.flush()

#start process
if __name__ == '__main__':
    main()