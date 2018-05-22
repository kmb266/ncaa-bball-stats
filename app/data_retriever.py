from sqlalchemy import create_engine
from db import Game, Team, Player, PlayerIn, TeamIn, Play
import json
import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_, between


from Constants import sqlite_json, sqlite_xml

def getAllTeams():
    """
    Retrieve all the team names and ids. Should return a list of teams with the id and the name of each team.
    """
    which_db = "json"
    # To fetch all team names, we try and use the JSON database. If this does not exist, default to XML

    try:
        # Attempt to connect to the JSON db, which has many more team names than the XML when fully populated
        engine = create_engine(sqlite_json, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        teams = session.query(Team).all()
    except:
        # In the case the JSON db does not exist, default to using the XML db
        which_db = "xml"
        engine = create_engine(sqlite_xml, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        teams = session.query(Team).all()

    if which_db == "json" and len(teams) == 0:
        # If the JSON db exists but is empty, default to using the XML db
            engine = create_engine(sqlite_xml, echo=False)
            Session = sessionmaker(bind=engine)
            session = Session()
            teams = session.query(Team).all()

    # Obtain list of team names and ids
    result = []
    for team in teams:
        team_obj = {"id": team.team_id, "text": team.name}
        result.append(team_obj)

    return json.dumps(result)


def getAllPlayers(teamId):
    """
    Retrieve all players for the team of the given id.
    """
    if teamId == "COR":
        engine = create_engine(sqlite_xml, echo=False)
    else:
        engine = create_engine(sqlite_json, echo=False)

    Session = sessionmaker(bind=engine)
    session = Session()
    players = session.query(Player).filter_by(team=teamId).all()
    result = []

    # Can't give jersey number in return because this is not stored uniquely by player, but rather by game
    for player in players:
        if player.name != "TEAM": # Don't include team's stats, though we might want to include this - check w/ client
            result.append({"id": player.id, "text": player.name})

    return json.dumps(result)

def query_full_length(game_ids, sess, mappings):
    """
    If the information requested is for full length games (with no additional filters), we query the teamstats and
    playersin tables rather than getting all the relevant plays.
    :param data: The dictionary representation of the provided json data
    :param sess: The database session to use
    :return: Box scores in the same format as master_query
    """
    # Get all the team data for the selected games
    teamstats = sess.query(TeamIn).filter(TeamIn.game.in_(game_ids)).all()
    playerstats = sess.query(PlayerIn).filter(PlayerIn.game.in_(game_ids)).all()
    team_dict = {}
    player_dict = {}
    for teamstat in teamstats:
        if teamstat.team not in team_dict:
            team_dict[teamstat.team] = {}
            team_dict[teamstat.team]["games"] = {}
        if teamstat.game not in team_dict[teamstat.team]["games"]:
            game = sess.query(Game).filter_by(id=teamstat.game).first()
            if game.home == teamstat.team:
                score = game.home_score
            else:
                score = game.visitor_score
            team_dict[teamstat.team]["games"][teamstat.game] = {
                "FGA": teamstat.fga,
                "FG": teamstat.fgm,
                "FGA3": teamstat.fga3,
                "3PT": teamstat.fgm3,
                "FTA": teamstat.fta,
                "FT": teamstat.ftm,
                "TP": teamstat.tp,
                "OREB": teamstat.oreb,
                "DREB": teamstat.dreb,
                "REB": teamstat.treb,
                "AST": teamstat.ast,
                "STL": teamstat.stl,
                "BLK": teamstat.blk,
                "TO": teamstat.to,
                "PF": teamstat.pf,
                "PTS": score,
                "home" : game.home,
                "away" : game.visitor
            }

    for player in playerstats:
        if player.player not in player_dict:
            p = sess.query(Player).filter_by(id=player.player).first()
            player_dict[player.player] = {}
            player_dict[player.player]["name"] = p.name
            player_dict[player.player]["team"] = p.team
            player_dict[player.player]["games"] = {}
        game = sess.query(Game).filter_by(id=player.game).first()
        fgm = player.fgm or 0
        ftm = player.ftm or 0
        fgm3 = player.fgm3 or 0
        player_dict[player.player]["games"][player.game] = {
            "FGA": player.fga,
            "FG": player.fgm,
            "FGA3": player.fga3,
            "3PT": player.fgm3,
            "FTA": player.fta,
            "FT": player.ftm,
            "TP": player.tp,
            "OREB": player.oreb,
            "DREB": player.dreb,
            "REB": player.treb,
            "AST": player.ast,
            "STL": player.stl,
            "BLK": player.blk,
            "TO": player.to,
            "PF": player.pf,
            "home" : game.home,
            "away" : game.visitor,
            "PTS": ftm + (fgm - fgm3) * 2 + fgm3 * 3, # TODO: Check this calculation
            "MIN": player.mins or 0 # TODO: Populate db with player minutes
        }

    return player_dict.values(), team_dict, mappings
    # return player_dict, team_dict




def masterQuery(json_form):
    data = json.loads(json.dumps(json_form))
    teamIds = data["team"]
    oppIds = data["opponent"]

    # Pick what DB you're using based on the search criteria
    if (len(teamIds) == 1 and teamIds[0] == "COR") or (len(oppIds) == 1 and oppIds[0] == "COR"):
        engine = create_engine(sqlite_xml, echo=False)
        # print("xml engine")
    else:
        engine = create_engine(sqlite_json, echo=False)
        # print("json engine")

    Session = sessionmaker(bind=engine)
    session = Session()

    # Games query selects all games where teams in team play against teams in opponent
    mappings = {}
    for team in teamIds:
        mappings[team] = team
    for opp in oppIds:
        mappings[opp] = opp

    # print(mappings)

    if teamIds:
        db_contains_team = True
        for team in teamIds:
            t = session.query(Team).filter_by(team_id=team).first()
            if not t:
                j_engine = create_engine(sqlite_json, echo=False)
                JSession = sessionmaker(bind=j_engine)
                j_session = JSession()
                team_name = j_session.query(Team).filter_by(team_id=team).first().name
                translated = session.query(Team).filter_by(name=team_name).first()
                if not translated:
                    # There is no XML data for that team
                    db_contains_opp = False
                    return {}, {}, mappings
                teamIds.remove(team)
                teamIds.append(translated.team_id)
                mappings[team] = translated.team_id


    games_query = session.query(Game).filter(
    or_(
        Game.home.in_(teamIds),
        Game.visitor.in_(teamIds)
    ))


    if oppIds:
        db_contains_opp = True
        for opp in oppIds:
            o = session.query(Team).filter_by(team_id=opp).first()
            if not o:
                j_engine = create_engine(sqlite_json, echo=False)
                JSession = sessionmaker(bind=j_engine)
                j_session = JSession()
                team_name = j_session.query(Team).filter_by(team_id=opp).first().name
                translated = session.query(Team).filter_by(name=team_name).first()
                if not translated:
                    # There is no XML data for that team
                    db_contains_opp = False
                    return {}, {}, mappings
                oppIds.remove(opp)
                oppIds.append(translated.team_id)
                mappings[opp] = translated.team_id

        if db_contains_opp:
            games_query = games_query.filter(
                or_(
                    (and_(Game.home.in_(teamIds), Game.visitor.in_(oppIds))),
                    (and_(Game.visitor.in_(teamIds), Game.home.in_(oppIds)))
                )
            )





    # If there's a season, get all games within that season
    if "season" in data:
        seasons = data["season"]
        if seasons:
            # If the list of seasons isn't empty
            # Make a datetime from the season year number
            datetime_ranges = []
            for season in seasons:
                year = int(season)
                start = datetime.datetime(year-1, 6, 2) # Season starts on June 2 of prior year
                end = datetime.datetime(year, 6, 1)   # Season ends on June 1 of this year
                datetime_ranges.append([start, end])
            conds = []
            for d in datetime_ranges:
                conds.append(and_(Game.date>d[0], Game.date< d[1]))
            games_query = games_query.filter(or_(*conds)) # Pray that this works

    # If there are date filters, use them to restrict the set of filtered games
    if "dates" in data:
        dates = data["dates"]
        start = datetime.datetime.fromtimestamp(dates["start"]/1000.0)
        end = datetime.datetime.fromtimestamp(dates["end"]/1000.0)
        games_query = games_query.filter(and_(Game.date >= start, Game.date <= end))

    # Filter out games based on wins/losses
    outcome = data["outcome"]
    if outcome["wins"] is False:
        # Only show losses
        games_query = games_query.filter(Game.loser.in_(teamIds))
    if outcome["losses"] is False:
        # Only show wins
        games_query = games_query.filter(Game.winner.in_(teamIds))

    # Filter out games based on location
    loc = data["location"]
    if loc["home"] is False:
        # TODO: no support for neutral
        # Filter out any games where the selected team was a home team
        games_query = games_query.filter(Game.visitor.in_(teamIds))
    if loc["away"] is False:
        games_query = games_query.filter(Game.home.in_(teamIds))



    # Get all the game ids of the valid games we've looked at
    selected_game_ids = [game.id for game in games_query.all()]

    # Make the call to query_full_length here if we need it
    ot_stuff = data["overtime"]
    if ot_stuff["onlyQueryOT"] is False and ot_stuff["ot1"] is True and ot_stuff["ot2"] is True \
        and ot_stuff["ot3"] is True and ot_stuff["ot4"] is True and ot_stuff["ot5"] is True and ot_stuff["ot6"] is True \
        and data["gametime"]["multipleTimeFrames"] is False and data["gametime"]["slider"]["start"]["sec"] == -2400 and \
            data["gametime"]["slider"]["end"]["sec"] == 0 \
        and len(data["in"]) == 0 and len(data["out"]) == 0 and data["upOrDown"][1] is None \
        and len(data["position"]) == 0 and ot_stuff["otSliderStart"] == 0 \
        and ot_stuff["otSliderEnd"] == 300:
        #and len(data["position"]) == 0 and ot_stuff["otSlider"]["start"]["sec"] == 0 \
        #and ot_stuff["otSlider"]["end"]["sec"] == 300:
            #print("calling query full length")
            return query_full_length(selected_game_ids, session, mappings)
            # pass

    #print("play query")
    # Get all the plays for this game
    plays_query = session.query(Play).filter(Play.game_id.in_(selected_game_ids))

    # Filter by time periods in regulation time and then OT
    # We begin by collecting the set of times we want to filter by
    time_periods = []
    sec_start = data["gametime"]["slider"]["start"]["sec"]
    sec_end = data["gametime"]["slider"]["end"]["sec"]
    time_periods.append([sec_start, sec_end])

    if data["gametime"]["multipleTimeFrames"] is True:
        sec_start_2 = data["gametime"]["sliderExtra"]["start"]["sec"]
        sec_end_2 = data["gametime"]["sliderExtra"]["start"]["sec"]
        time_periods.append([sec_start_2, sec_end_2])

    # Overtime filter
    if "overtime" in data:
        overtimes = data["overtime"]
        if overtimes["onlyQueryOT"] is True:
            plays_query = plays_query.filter(Play.period > 2)
        valid_ot_periods = []
        for key in overtimes:
            if key != "onlyQueryOT" or key != "otSlider":
                if overtimes[key] is True:
                    valid_ot_periods.append(key[2:])
        if valid_ot_periods:
            for period in valid_ot_periods:
                start = ot_stuff["otSliderStart"] + (int(period) - 1) * 300
                end = ot_stuff["otSliderEnd"] + (int(period) - 1) * 300
                time_periods.append([start, end])

    # Now we apply filters based on the set of times generated above
    time_period_conds = []
    for time in time_periods:
        time_period_conds.append(and_(Play.time_converted >= time[0], Play.time_converted <= time[1]))
    if time_period_conds:
        plays_query = plays_query.filter(or_(*time_period_conds))  # Pray that this works

    # Obtain the actual plays so that we can use python list filtering rather than database querying
    # TODO: Doing this could decrease efficiency
    plays = plays_query.all()

    # Filter the plays based on players in/out
    players_in = data["in"]
    players_out = data["out"]

    def player_in(play, players):
        if play.h1 in players or \
            play.h2 in players or \
            play.h3 in players or \
            play.h4 in players or \
            play.h5 in players or \
            play.v1 in players or \
            play.v2 in players or \
            play.v3 in players or \
            play.v4 in players or \
            play.v5 in players or \
            play.player_id in players:
                return True

    def player_out(play, players):
        if play.h1 not in players and \
            play.h2 not in players and \
            play.h3 not in players and \
            play.h4 not in players and \
            play.h5 not in players and \
            play.v1 not in players and \
            play.v2 not in players and \
            play.v3 not in players and \
            play.v4 not in players and \
            play.v5 not in players and \
            play.player_id not in players:
                return True


    positions = data["position"]

    # Position filter: Only include players with the given positions - expected value is int list
    if positions:
        positions = list(map(lambda p: int(p), positions))
        plays = list(filter(lambda p: session.query(Player).filter_by(id=p.player_id).first().position in positions, plays))

    # Lineup filters: Filter by players in/out of the game
    if players_in:
        players_in = list(map(lambda p: int(p), players_in))
        plays = list(filter(lambda p: player_in(p, players_in), plays))

    if players_out:
        players_out = list(map(lambda p: int(p), players_out))
        plays = list(filter(lambda p: player_out(p, players_out), plays)) # TODO: Verify logic in this line

    # Score filters: Filter by point differentials
    up_or_down = data["upOrDown"]
    if up_or_down[1] is not None:
        def filter_plays_differential(p, up_or_down, amt):
            g = session.query(Game).filter_by(id=p.game_id).first()
            if g.home in teamIds:
                # If the team we're looking for is home team this play, base calculations off that
                if up_or_down == "up":
                    return p.home_score - p.away_score > amt
                elif up_or_down == "down":
                    return p.home_score - p.away_score <= amt
            else:
                # Otherwise the team we're looking for is away team this play
                if up_or_down == "up":
                    return p.away_score - p.home_score > amt
                elif up_or_down == "down":
                    return p.away_score - p.home_score <= amt
            return False

        if up_or_down[0] == "withIn":
            plays = list(filter(lambda p: abs(p.home_score - p.away_score) <= up_or_down[1], plays))
        elif up_or_down[0] == "down":
            plays = list(filter(lambda p: filter_plays_differential(p, "down", up_or_down[1]), plays))
        elif up_or_down[0] == "up":
            plays = list(filter(lambda p: filter_plays_differential(p, "up", up_or_down[1]), plays))

    def generate_box_score(plays):
        """
        Generates a box score for each player involved in the plays listed
        :param plays: The list of plays
        :return: A dict containing box scores for each player
        TODO: this is horribly slow
        """
        players = {}
        teams = {}

        for play in plays:
            # Create player if its not in the list
            player_id = play.player_id
            if player_id is None:
                continue
            if player_id and player_id not in players:
                player = session.query(Player).filter_by(id=play.player_id).first()
                players[player_id] = {
                    "name" : player.name,
                    "team" : player.team,
                    "games": {}
                }

                if player.team not in teams:
                    teams[player.team] = {
                        "games": {}
                    }

            # Create game for the player if its not in the list
            game_id = play.game_id

            g = session.query(Game).filter_by(id=game_id).first()

            if game_id and game_id not in players[player_id]["games"]:
                players[player_id]["games"][game_id] = {
                    "FGA": 0.0,
                    "FG": 0.0,
                    "FGA3": 0.0,
                    "3PT": 0.0,
                    "FTA": 0.0,
                    "FT": 0.0,
                    "TP": 0.0,
                    "OREB": 0.0,
                    "DREB": 0.0,
                    "REB": 0.0,
                    "AST": 0.0,
                    "STL": 0.0,
                    "BLK": 0.0,
                    "TO": 0.0,
                    "PF": 0.0,
                    "PTS": 0.0,
                    "MIN": 0.0,
                    "LAST_IN_OR_OUT": "OUT", # Used to keep track of whether the last sub in this game was in or out
                    "SEEN": False, # Used to keep track of whether the player has been seen yet
                    "last_time": sec_start,
                    "home": g.home,
                    "away": g.visitor
                }

            team = players[player_id]["team"]
            if game_id not in teams[team]["games"]:
                teams[team]["games"][game_id] = {
                    "FGA": 0.0,
                    "FG": 0.0,
                    "FGA3": 0.0,
                    "3PT": 0.0,
                    "FTA": 0.0,
                    "FT": 0.0,
                    "TP": 0.0,
                    "OREB": 0.0,
                    "DREB": 0.0,
                    "REB": 0.0,
                    "AST": 0.0,
                    "STL": 0.0,
                    "BLK": 0.0,
                    "TO": 0.0,
                    "PF": 0.0,
                    "PTS": 0.0,
                    "home": g.home,
                    "away": g.visitor
                }

            if not players[player_id]["games"][game_id]["SEEN"]:
                players[player_id]["games"][game_id]["SEEN"] = True
                if play.action == "SUB" and play.type == "OUT":
                    players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] = "OUT"
                    players[player_id]["games"][game_id]["MIN"] += abs((play.time_converted - sec_start)/60)

                else:
                    players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] = "IN"

            if play.type == "3PTR":
                players[player_id]["games"][game_id]["FGA3"] += 1
                teams[team]["games"][game_id]["FGA3"] += 1
                players[player_id]["games"][game_id]["FGA"] += 1
                teams[team]["games"][game_id]["FGA"] += 1
                if play.action == "GOOD":
                    players[player_id]["games"][game_id]["3PT"] += 1
                    teams[team]["games"][game_id]["3PT"] += 1
                    players[player_id]["games"][game_id]["FG"] += 1
                    teams[team]["games"][game_id]["FG"] += 1
                    players[player_id]["games"][game_id]["PTS"] += 3
                    teams[team]["games"][game_id]["PTS"] += 3
            elif play.action == "SUB":
                if play.type == "IN":
                    # if player_id == 7:
                        # print("Subbing in MCBRIDE at {}".format(play.time_converted))
                    players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] = "IN"
                    players[player_id]["games"][game_id]["SEEN"] = True
                    players[player_id]["games"][game_id]["last_time"] = play.time_converted
                elif play.type == "OUT":
                    now = play.time_converted
                    players[player_id]["games"][game_id]["MIN"] += \
                        abs((now - players[player_id]["games"][game_id]["last_time"])/60)
                    players[player_id]["games"][game_id]["last_time"] = now
                    players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] = "OUT"
            elif play.type == "JUMPER" or play.type == "LAYUP" or play.type == "DUNK":
                players[player_id]["games"][game_id]["FGA"] += 1
                teams[team]["games"][game_id]["FGA"] += 1
                if play.action == "GOOD":
                    players[player_id]["games"][game_id]["FG"] += 1
                    teams[team]["games"][game_id]["FG"] += 1
                    players[player_id]["games"][game_id]["PTS"] += 2
                    teams[team]["games"][game_id]["PTS"] += 2
            elif play.action == "REBOUND":
                players[player_id]["games"][game_id]["REB"] += 1
                teams[team]["games"][game_id]["REB"] += 1
                if play.type == "DEF":
                    players[player_id]["games"][game_id]["DREB"] += 1
                    teams[team]["games"][game_id]["DREB"] += 1
                elif play.type == "OFF":
                    players[player_id]["games"][game_id]["OREB"] += 1
                    teams[team]["games"][game_id]["OREB"] += 1
            elif play.action == "STEAL":
                players[player_id]["games"][game_id]["STL"] += 1
                teams[team]["games"][game_id]["STL"] += 1
            elif play.action == "BLOCK":
                players[player_id]["games"][game_id]["BLK"] += 1
                teams[team]["games"][game_id]["BLK"] += 1
            elif play.action == "TURNOVER":
                players[player_id]["games"][game_id]["TO"] += 1
                teams[team]["games"][game_id]["TO"] += 1
            elif play.type == "FT":
                players[player_id]["games"][game_id]["FTA"] += 1
                teams[team]["games"][game_id]["FTA"] += 1
                if play.action == "GOOD":
                    players[player_id]["games"][game_id]["FT"] += 1
                    teams[team]["games"][game_id]["FT"] += 1
                    players[player_id]["games"][game_id]["PTS"] += 1
                    teams[team]["games"][game_id]["PTS"] += 1
            elif play.action == "ASSIST":
                players[player_id]["games"][game_id]["AST"] += 1
                teams[team]["games"][game_id]["AST"] += 1
            elif play.action == "FOUL":
                players[player_id]["games"][game_id]["PF"] += 1
                teams[team]["games"][game_id]["PF"] += 1

        # If we're done and the player was last subbed in, fix their minutes by subbing them out
        for player_id in players:
            for game_id in players[player_id]["games"]:
                if players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] == "IN":
                    players[player_id]["games"][game_id]["LAST_IN_OR_OUT"] = "OUT"
                    players[player_id]["games"][game_id]["MIN"] += \
                        abs((sec_end - players[player_id]["games"][game_id]["last_time"])/60) # End of normal period game

        return players, teams

    (box_score, teams) = generate_box_score(plays)
    # for key in teams:
    #     print(key)
    return box_score.values(), teams, mappings
    # return box_score, teams


# Test full length games
# import time
# start_time = time.time()
# data = masterQuery({
#   "page": "players",
#   "position": [],
#   "team": ["SYR"],
#   "opponent": ["COR"],
#   "in": [],
#   "out": [],
#   "upOrDown": [
#     "up",
#     10
#   ],
#   "gametime": {
#     "slider": {
#       "start": {
#         "clock": "20:00",
#         "sec": -2400
#       },
#       "end": {
#         "clock": "00:00",
#         "sec": 0
#       }
#     },
#     "sliderExtra": {
#       "start": {
#         "clock": "20:00",
#         "sec": -2400
#       },
#       "end": {
#         "clock": "00:00",
#         "sec": 0
#       }
#     },
#     "multipleTimeFrames": False
#   },
#   "location": {
#     "home": True,
#     "away": True,
#     "neutral": True
#   },
#   "outcome": {
#     "wins": True,
#     "losses": True
#   },
#     "overtime": {
#         "otSliderStart": 0,
#         "otSliderEnd": 300,
#         "ot1": True,
#         "ot2": True,
#         "ot3": True,
#         "ot4": True,
#         "ot5": True,
#         "ot6": True,
#         "onlyQueryOT": False
#     },
#   "dates": {
#      "start": 1509508800000,
#     "end": 1525665600000
#   }
# })[1]
# print("--- %s seconds ---" % (time.time() - start_time))
#
# import pprint
# pprint.pprint(data, width=1)
#
# for player_id in data:
#     sum = 0
#     for game in data[player_id]["games"]:
#         sum += data[player_id]["games"][game]["FGA"]
#     if player_id == 6:
#         print(player_id, sum)
#         print("AVERAGE:", sum/len(data[player_id]["games"]))
