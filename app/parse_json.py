import datetime
from db import Game, Team, Player, PlayerIn, TeamIn, Play
from sqlalchemy import Column

"""
This file is used to populate the JSON database given JSON data scraped from ESPN
"""


def parse_game(data, session):
    """
    adds an entry to the Game table
    """
    competitions = data["gamepackageJSON"]["header"]["competitions"][0]

    # date of the game in datetime format
    date = competitions["date"]
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%MZ') - datetime.timedelta(hours=4)

    # the id's of the two teams playing
    team_0 = competitions["competitors"][0]["team"]["abbreviation"]
    team_1 = competitions["competitors"][1]["team"]["abbreviation"]

    # parse home and away teams, as well as game score
    if competitions["competitors"][0]["homeAway"] == "home":
        home, visitor = team_0, team_1
        home_score = intf(competitions["competitors"][0]["score"])
        visitor_score = intf(competitions["competitors"][1]["score"])
    else:
        home, visitor = team_1, team_0
        home_score = intf(competitions["competitors"][1]["score"])
        visitor_score = intf(competitions["competitors"][0]["score"])

    # parse winner and loser
    if competitions["competitors"][0]["winner"]:
        winner, loser = team_0, team_1
    else:
        winner, loser = team_1, team_0

    isLeague = competitions["conferenceCompetition"]

    g = session.query(Game).filter_by(date=date,home=home).first()
    if not g:
        g = Game(id=data["gameId"],date=date,home=home,visitor=visitor,winner=winner,
        loser=loser,home_score=home_score,visitor_score=visitor_score,isLeague=isLeague)
        session.add(g)
    # session.commit()


def parse_teams(data, session):
    """
    Adds new teams to the Teams table and stats to the Teamstats table
    """
    game_id = data["gameId"]

    for team in data["gamepackageJSON"]["boxscore"]["players"]:
        team_id = team["team"]["abbreviation"]
        team_name = team["team"]["shortDisplayName"]

        # Only add team if they are not yet in the db
        t = session.query(Team).filter_by(team_id=team_id).first()
        if not t:
            t = Team(team_id=team_id, name=team_name)
            session.add(t)

        s = parse_stats(team["statistics"][0]["totals"])
        team_stats = TeamIn(team=team_id,game=game_id,fgm=s["fgm"],fga=s["fga"],
            fgm3=s["fgm3"],fga3=s["fga3"],ftm=s["ftm"],fta=s["fta"],tp=s["tp"],
            blk=s["blk"],stl=s["stl"],ast=s["ast"],oreb=s["oreb"],dreb=s["dreb"],
            treb=s["treb"],pf=s["pf"],to=s["to"])
        session.add(team_stats)
        # missing technical fouls, can get from team data

    # session.commit()

def parse_players(data, session):
    """
    Adds new players to the Players table and one entry per player to
    the Playerstats table
    """
    game_id = data["gameId"]
    players = data["gamepackageJSON"]["boxscore"]["players"]

    # for each of the two teams
    for team in players:
        team_id = team["team"]["abbreviation"]
        # for every player on that team
        for athlete in team["statistics"][0]["athletes"]:
            athlete_id = intf(athlete["athlete"]["id"])
            athlete_name = athlete["athlete"]["displayName"]
            position = athlete["athlete"]["position"]["displayName"]
            jersey_num = intf(athlete["athlete"]["jersey"])

            # only add player if they are not yet in db, and they played in the game
            p = session.query(Player).filter_by(id=athlete_id).first()
            if (not p) and (not athlete["didNotPlay"]):
                p = Player(id=athlete_id,name=athlete_name, position=position, team=team_id)
                session.add(p)

            # if they played in the game, add their game stats
            if not athlete["didNotPlay"]:
                # s represents the parsed stats
                s = parse_stats(athlete["stats"])
                player_stats = PlayerIn(game=game_id,player=athlete_id,number=jersey_num,
                    mins=s["mins"],fgm=s["fgm"],fga=s["fga"],fgm3=s["fgm3"],
                    fga3=s["fga3"],ftm=s["ftm"],fta=s["fta"],tp=s["tp"],
                    blk=s["blk"],stl=s["stl"],ast=s["ast"],oreb=s["oreb"],
                    dreb=s["dreb"],treb=s["treb"],pf=s["pf"],to=s["to"])
                session.add(player_stats)

    # session.commit()

def parse_plays(data, session):
    game_id = data["gameId"]

    # for every play in the game, extract relevant data
    for play in data["gamepackageJSON"]["plays"]:
        play_id = intf(play["id"])
        period = intf(play["period"]["number"])
        time = play["clock"]["displayValue"]
        scoring_play = play["scoringPlay"]
        shooting_play = play["shootingPlay"]
        score_value = intf(play["scoreValue"])
        home_score = play["homeScore"]
        away_score = play["awayScore"]
        text = play["text"]
        json_type = play["type"]["text"]
        participants = play.get("participants")


        action = ""
        type_ = ""

        if shooting_play:
            if scoring_play:
                action = "GOOD"
            else:
                action = "MISS"
            if score_value == 1:
                type_ = "FT"
            elif score_value == 2:
                type_  = "JUMPER"
            elif score_value == 3:
                type_ = "3PTR"

        # assisted shots have two plays embedded in one JSON play
        if participants and len(participants) > 1:
            # add two plays, one for shot and one for assist
            player_id_0 = intf(participants[0]["athlete"]["id"])
            player_id_1 = intf(participants[1]["athlete"]["id"])

            shooter = player_id_0
            assister = player_id_1

            p0 = Play(game_id=game_id,period=period,time=time,scoring_play=scoring_play,
                shooting_play=shooting_play,score_value=score_value,home_score=home_score,
                away_score=away_score,text=text,action=action,type=type_,player_id=shooter)

            p1 = Play(game_id=game_id,period=period,time=time,scoring_play=scoring_play,
                shooting_play=shooting_play,score_value=score_value,home_score=home_score,
                away_score=away_score,text=text,action="ASSIST",player_id=assister)

            p0.convert_time(period, time)
            p1.convert_time(period, time)
            session.add(p0)
            session.add(p1)

        else:
            # play has 0 or 1 participants
            player_id = None
            if participants:
                player_id = intf(participants[0]["athlete"]["id"])

            # parse action and type
            if json_type == "Lost Ball Turnover":
                action = "TURNOVER"
            elif json_type == "Steal":
                action = "STEAL"
            elif json_type == "Dead Ball Rebound":
                action = "REBOUND"
                type_ = "DEADB"
            elif json_type == "Offensive Rebound":
                action = "REBOUND"
                type_ = "OFF"
            elif json_type == "Defensive Rebound":
                action = "REBOUND"
                type_ = "DEF"
            elif json_type == "Block Shot":
                action = "BLOCK"
            elif json_type == "PersonalFoul":
                action = "FOUL"
            elif json_type == "Technical Foul":
                action = "FOUL"
                type_ = "TECH"

            p = Play(game_id=game_id,period=period,time=time,scoring_play=scoring_play,
                shooting_play=shooting_play,score_value=score_value,home_score=home_score,
                away_score=away_score,text=text,action=action,type=type_,player_id=player_id)

            p.convert_time(period, time)
            session.add(p)

def parse_stats(stats):
    """
    ESPN provides stats in the same format for teams and players, parse that info
    """
    fgm, fga = extract_made_attempted(stats[1])  # Field goals made / attempted
    fgm3, fga3 = extract_made_attempted(stats[2]) # Threes made / attempted
    ftm, fta = extract_made_attempted(stats[3]) # Free throws made / attempted
    mins = intf(stats[0])              # Minutes played
    tp = intf(stats[12])               # Total points
    blk = intf(stats[9])               # Total blocks
    stl = intf(stats[8])               # Total steals
    ast = intf(stats[7])               # Total assists
    oreb = intf(stats[4])              # Total offensive rebounds
    dreb = intf(stats[5])              # Total defensive rebounds
    treb = intf(stats[6])              # Total rebounds (offensive + defensive)
    pf = intf(stats[11])               # Total personal fouls
    to = intf(stats[10])               # Total turnovers

    return {"mins":mins,"fgm":fgm,"fga":fga,"fgm3":fgm3,"fga3":fga3,"ftm":ftm,
        "fta":fta,"tp":tp,"blk":blk,"stl":stl,"ast":ast,"oreb":oreb,"dreb":dreb,
        "treb":treb,"pf":pf,"to":to}

def extract_made_attempted(stat_string):
    """
    Takes as input a string in the format "m-a" where m and a are integers
    representing the number of made and attempted shots, respectively. Returns
    a pair of ints in the form made, attempted.
    """
    split_stats = stat_string.split("-")
    made = split_stats[0]
    attempted = split_stats[1]
    return made, attempted

def intf(s):
    """
    Transforms a string into an int. If the built-in int() function raises an
    error, return 0.
    """
    try:
        num = int(s)
    except:
        num = 0
    return num
