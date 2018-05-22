from db import Game, Team, Player, PlayerIn, TeamIn, Play

from parser import parse_game_file
import os
import json

import parse_json

# sqlalchemy imports used to interact with the database
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Get the paths to the databases based on whether we're in debug mode or production mode
from Constants import sqlite_json, sqlite_xml, BACKEND_DIR

sqlite_xml = sqlite_xml[:7] + '/' + sqlite_xml[7:]
sqlite_json = sqlite_json[:7] + '/' + sqlite_json[7:]

# Initialize a session with the xml database
engine = create_engine(sqlite_xml, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


def xml_to_database(xml_file):
    game_info = parse_game_file(xml_file)
    # Extract information for the Game table
    venue = game_info['venue']
    home = venue["home_id"]
    vis = venue["vis_id"]

    # Check if information for this game has already been added - if it has, then exit the function
    if session.query(Game).filter_by(date=venue['date'], home=venue['home_id']).first():
        return "ERR: Game data already documented. Aborting upload"

    g = Game(date=venue['date'], home=venue['home_id'], visitor=venue['vis_id'], isLeague=venue['is_league'],
             isPlayoff=venue['is_playoff'])
    session.add(g)

    # Extract information for Team table, adding the playing teams to the database if they don't already exist
    t1 = session.query(Team).filter_by(team_id=venue['home_id']).first() # Should only be one team with each id, so we can use first()
    t2 = session.query(Team).filter_by(team_id=venue['vis_id']).first()
    if not t1:
        t1 = Team(team_id=venue['home_id'], name=venue['home_name'])
        session.add(t1)
    if not t2:
        t2 = Team(team_id=venue['vis_id'], name=venue['vis_name'])
        session.add(t2)

    # Extract information for the TeamIn table
    """ TODO: Wrap everything in its own adder function, maybe put this in a file like py2db.py, which converts from
    the python dictionary to the database"""
    team1 = game_info['t1']
    spec = team1['special']
    stats = team1['stats']

    p1_vh = True if spec['vh'] == 'H' else False
    plays_in_team_one = TeamIn(team=team1["id"], game=g.id, fgm=stats['fgm'], fga=stats['fga'],
                                fgm3=stats['fgm3'], fga3=stats['fga3'], fta=stats['fta'], ftm=stats['ftm'],
                                tp=stats['tp'], blk=stats['blk'], stl=stats['stl'], ast=stats['ast'],
                                oreb=stats['oreb'], dreb=stats['dreb'], treb=stats['treb'], pf=stats['pf'],
                                tf=stats['tf'], to=stats['to'],
                                is_home=p1_vh, pts_to=spec['pts_to'], pts_paint=spec['pts_paint'],
                                pts_ch2=spec['pts_ch2'], pts_fastb=spec['pts_fastb'], pts_bench=spec['pts_bench'],
                                ties=spec['ties'], leads=spec['leads'], poss_count=spec['poss_count'],
                                poss_time=spec['poss_time'], score_count=spec['score_count'],
                                score_time=spec['score_time'])

    session.add(plays_in_team_one)

    team2 = game_info['t2']
    spec = team2['special']
    stats = team2['stats']

    p2_vh = True if spec['vh'] == 'H' else False

    plays_in_team_two = TeamIn(team=team2["id"], game=g.id, fgm=stats['fgm'], fga=stats['fga'],
                               fgm3=stats['fgm3'], fga3=stats['fga3'], fta=stats['fta'], ftm=stats['ftm'],
                               tp=stats['tp'], blk=stats['blk'], stl=stats['stl'], ast=stats['ast'],
                               oreb=stats['oreb'], dreb=stats['dreb'], treb=stats['treb'], pf=stats['pf'],
                               tf=stats['tf'], to=stats['to'],
                               is_home=p2_vh, pts_to=spec['pts_to'],
                               pts_paint=spec['pts_paint'],
                               pts_ch2=spec['pts_ch2'], pts_fastb=spec['pts_fastb'], pts_bench=spec['pts_bench'],
                               ties=spec['ties'], leads=spec['leads'], poss_count=spec['poss_count'],
                               poss_time=spec['poss_time'], score_count=spec['score_count'],
                               score_time=spec['score_time'])

    session.add(plays_in_team_two)
    session.commit()

    # Put in information on total game scores
    if team1['special']['vh'] == 'H':
        # team1 is the home team
        g.home_score = team1['stats']['score']
        g.visitor_score = team2['stats']['score']
    else:
        g.home_score = team2['stats']['score']
        g.visitor_score = team1['stats']['score']

    if team1['stats']['score'] > team2['stats']['score']:
        g.winner = team1['id']
        g.loser = team2['id']
    else:
        g.winner = team2['id']
        g.loser = team1['id']

    session.add(g)
    session.commit()

    # Loop through Players and add them to the database if they don't already exist, repeat for team2
    starters_team_1 = []
    for player in team1['players']:
        name_formatted = player["checkname"].title()
        if player["checkname"] != "TEAM":
            comma = name_formatted.index(",")
            name_formatted = name_formatted[:comma + 1] + " " + name_formatted[comma + 1:]
        p = session.query(Player).filter_by(name=name_formatted.title(), team=team1["id"]).first()
        if not p:
            # If the player's not already in the database add him
            p = Player(name=name_formatted, team=team1["id"])
            session.add(p)
            session.commit()
        # Some players don't have stats for the game - we ignore those by checking arbitrarily for the fgm stat to exist
        # Example: Keion Green from CENTPENN
        if "fgm" in player:
            game_stats = PlayerIn(player=p.id, game=g.id, fgm=player["fgm"], fga=player["fga"],
                                  fgm3=player["fgm3"], fga3=player["fga3"], ftm=player["ftm"],
                                  fta=player["fta"], tp=player["tp"], blk=player["blk"], stl=player["stl"],
                                  ast=player["ast"], oreb=player["oreb"], dreb=player["dreb"],
                                  treb=player["treb"], pf=player["pf"], tf=player["tf"], to=player["to"],
                                  dq=player["dq"], number=player["uni"], mins=player["min"])
            session.add(game_stats)
            if "gs" in player:
                starters_team_1.append(p.id)
    session.commit()
        # Add stats for the player for the game

    # Now do the same thing for team2
    starters_team_2 = []
    for player in team2['players']:
        name_formatted = player["checkname"].title()
        if player["checkname"] != "TEAM":
            comma = name_formatted.index(",")
            name_formatted = name_formatted[:comma + 1] + " " + name_formatted[comma + 1:]
        p = session.query(Player).filter_by(name=name_formatted, team=team2["id"]).first()
        if not p:
            # If the player's not already in the database add him
            p = Player(name=name_formatted, team=team2["id"])
            session.add(p)
            session.commit()
        # Some players don't have stats for the game - we ignore those by checking arbitrarily for the fgm stat to exist
        # Example: Keion Green from CENTPENN
        if "fgm" in player:
            game_stats = PlayerIn(player=p.id, game=g.id, fgm=player["fgm"], fga=player["fga"],
                                  fgm3=player["fgm3"], fga3=player["fga3"], ftm=player["ftm"],
                                  fta=player["fta"], tp=player["tp"], blk=player["blk"], stl=player["stl"],
                                  ast=player["ast"], oreb=player["oreb"], dreb=player["dreb"],
                                  treb=player["treb"], pf=player["pf"], tf=player["tf"], to=player["to"],
                                  dq=player["dq"], number=player["uni"], mins=player["min"])
            if "gs" in player:
                starters_team_2.append(p.id)
            session.add(game_stats)
    session.commit()
    # print("TEAM ONE STARTERS", starters_team_1)
    # print("TEAM TWO STARTERS", starters_team_2)

    if team1["id"] == home:
        home_on_court = starters_team_1
        away_on_court = starters_team_2
    else:
        home_on_court = starters_team_2
        away_on_court = starters_team_1

    # Now create a dummy play that initializes the starters
    starters_play = Play(game_id=g.id, period=1, time="20:00", scoring_play=False, shooting_play=False, home_score=0,
                         away_score=0, text="Starters", action="Starters", type="",
                         h1=home_on_court[0], h2=home_on_court[1], h3=
                         home_on_court[2], h4=home_on_court[3],
                         h5=home_on_court[4],
                         v1=away_on_court[0], v2=away_on_court[1], v3=away_on_court[2], v4=away_on_court[3],
                         v5=away_on_court[4])
    session.add(starters_play)
    session.commit()


    plays = game_info["plays"]
    last_v_score = 0
    last_h_score = 0
    # TODO: add a dummy play to the start of the second period
    for period in plays:
        if team1["id"] == home:
            home_on_court = starters_team_1
            away_on_court = starters_team_2
        else:
            home_on_court = starters_team_2
            away_on_court = starters_team_1
        for play in plays[period]:
            # print(play)
            name_formatted = play["checkname"].title()
            if play["checkname"] != "TEAM":
                comma = name_formatted.index(",")
                name_formatted = name_formatted[:comma + 1] + " " + name_formatted[comma + 1:]
            player_id = session.query(Player).filter_by(name=name_formatted, team=play["team"]).first().id
            # Update home_on_court and away_on_court as necessary
            if play["action"] == "SUB":
                if play["type"] == "OUT":
                    if player_id in home_on_court:
                        home_on_court.remove(player_id)
                    elif player_id in away_on_court:
                        away_on_court.remove(player_id)
                if play["type"] == "IN":
                    team = session.query(Player).filter_by(id=player_id).first().team
                    # print(team)
                    if team == home:
                        home_on_court.append(player_id)
                    else:
                        away_on_court.append(player_id)

            # TODO: make sure this loops in order of increasing period, dicts are unpredictable
            if play["action"] == "GOOD":
                # Update the last known score after someone scores
                last_v_score = play["vscore"]
                last_h_score = play["hscore"]
            this_play = Play(
                game_id=g.id, period=period, time=play["time"],
                scoring_play=play["action"] == "GOOD",
                shooting_play=(play["type"] == "LAYUP" or play["type"] == "3PTR" or play["type"] == "JUMPER") if "type" in play else False,
                home_score=last_h_score,
                away_score=last_v_score,
                text="",
                action=play["action"],
                type=play["type"] if "type" in play else "",
                player_id=player_id,
                h1=home_on_court[0] if len(home_on_court) > 0 else -1,
                h2=home_on_court[1] if len(home_on_court) > 1 else -1,
                h3=home_on_court[2] if len(home_on_court) > 2 else -1,
                h4=home_on_court[3] if len(home_on_court) > 3 else -1,
                h5=home_on_court[4] if len(home_on_court) > 4 else -1,
                v2=away_on_court[0] if len(away_on_court) > 0 else -1,
                v1=away_on_court[1] if len(away_on_court) > 1 else -1,
                v3=away_on_court[2] if len(away_on_court) > 2 else -1,
                v4=away_on_court[3] if len(away_on_court) > 3 else -1,
                v5=away_on_court[4] if len(away_on_court) > 4 else -1
            )

            this_play.convert_time(int(this_play.period), this_play.time)
            session.add(this_play)
    session.commit()


def fill_all_xml():
    """
    Obtains all the XML files in the xml_data directory and
    populates the database with game information.
    :return: None, database is updated
    """
    # This loops populates the database using all the xml files
    for dir in os.listdir("/{}/xml_data".format(BACKEND_DIR)):
        if os.path.isdir("/{}/xml_data/{}".format(BACKEND_DIR, dir)):
            for filename in os.listdir("/{}/xml_data/{}".format(BACKEND_DIR, dir)):
                if filename.endswith(".xml"):
                    fl = "/{}/xml_data/{}/{}".format(BACKEND_DIR, dir, filename)
                    try:
                        xml_to_database(fl)
                    except AttributeError:
                        print("ERROR: AttributeError in file {}".format(fl))
                    except Exception as ex:
                        print("ERROR: {} in file {} | Arguments: {}".format(type(ex).__name__, fl, ex.args))


def json_to_database(json_file,data=None):
    if data == None:
        with open(json_file) as data_file:
            data = json.load(data_file)

    # Skip files that do not have box score data
    if not data["gamepackageJSON"]["header"]["competitions"][0]["boxscoreAvailable"]:
        return

    json_engine = create_engine(sqlite_json, echo=False)
    JsonSession = sessionmaker(bind=json_engine)
    json_session = JsonSession()

    parse_json.parse_game(data, json_session)
    parse_json.parse_teams(data, json_session)
    parse_json.parse_players(data, json_session)
    parse_json.parse_plays(data, json_session)

    json_session.commit()


def fill_all_json():
    for filename in os.listdir("../cached_json/ncb/playbyplay"):
        if filename != "400990128.json": # TODO: @Dav, why do we have this? (it was because the file has a player playing for both teams) - Sarvar
            json_to_database("../cached_json/ncb/playbyplay/" + filename)


def get_last_scrape_date():
    json_engine = create_engine(sqlite_json, echo=False)
    JsonSession = sessionmaker(bind=json_engine)
    json_session = JsonSession()
    date = json_session.query(Game).order_by(desc(Game.date)).first()
    return date



# COMMENT THE BELOW LINES IN ON INITIAL DB LOAD
# print("Populating XML database...")
# fill_all_xml()
# print("XML database populated\n")

# print("Populating JSON database...")
# fill_all_json()
# print("JSON database populated..")
