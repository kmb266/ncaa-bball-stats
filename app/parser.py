import xml.etree.ElementTree as ET
import datetime


def parse_venue_info(root_node, dict):
    """
    Retrieves the date, time, and home court information about the game,
    as well as whether or not the game was a leaguegame or a playoff game
    :param root_node:
    :return:
    """
    root = root_node.find('venue')

    # Fetch the id for the home team
    home = root.attrib['homeid']
    home_name = root.attrib['homename']

    # Fetch the id for the visitor team
    vis = root.attrib['visid']
    vis_name = root.attrib['visname']

    # Fetch the date (and time) convert to python datetime
    date = root.attrib['date'] + " " + root.attrib['time'].replace('.', '')
    try:
        date = datetime.datetime.strptime(date, '%m/%d/%Y %I:%M %p')
    except ValueError: # Date is formatted differently
        try:
            date = datetime.datetime.strptime(date, '%m/%d/%Y %I:%M%p')
        except ValueError:
            date = datetime.datetime.strptime(date, '%m/%d/%Y %I %p')




    # Extract information on whether the game is a league game, playoff game
    is_league = False if root.attrib['leaguegame'] == "N" else True
    is_playoff = False if root.attrib['postseason'] == "N" else True
    dict['venue'] = {
        'home_id': home,
        'vis_id': vis,
        'date': date,
        'is_league': is_league,
        'is_playoff': is_playoff,
        'home_name': home_name,
        'vis_name': vis_name,
    }

    return dict


def get_team_info(team_node, dict):
    if 't1' in dict:
        team = 't2'
    else:
        team = 't1'

    # Collecting base information
    id = team_node.attrib['id']
    record = team_node.attrib['record']
    record_divider = record.find('-')
    losses = record[:record_divider]
    wins = record[record_divider + 1:]

    # Information from the linescore node
    linescore = team_node.find('linescore')
    game_score = linescore.attrib['score']
    p1_score = 0
    p2_score = 0
    # TODO: What about OT?
    for lineprd in linescore:
        if lineprd.attrib['prd'] == 1:
            p1_score = lineprd.attrib['score']
        else:
            p2_score = lineprd.attrib['score']

    # Information from the totals node
    totals = team_node.find('totals')
    stats = totals.find('stats')
    stats_dict = {}
    for attrName, attrValue in stats.attrib.items():
        stats_dict[attrName] = attrValue

    stats_dict["score"] = linescore.attrib["score"]
    # print(stats_dict)


    special = totals.find('special')
    spec_dict = {}
    for attrName, attrValue in special.attrib.items():
        spec_dict[attrName] = attrValue
    # print(spec_dict)

    players = team_node.findall("player")
    player_list = []
    for player in players:
        this_player = {}
        for attrName, attrValue in player.attrib.items():
            this_player[attrName] = attrValue
        player_stats = player.find('stats')
        # If the player has saved statistics for the game, extract them
        if player_stats is not None:
            for attrName, attrValue in player_stats.attrib.items():
                this_player[attrName] = attrValue
        player_list.append(this_player)

    dict[team] = {
        'id': id,
        'losses': losses,
        'wins': wins,
        'p1_score': p1_score,
        'p2_score': p2_score,
        'stats': stats_dict,
        'special': spec_dict,
        'players': player_list
    }
    return dict


def get_play_info(root_node, dict):
    plays_node = root_node.find('plays')
    plays = {}
    periods = plays_node.findall("period")
    for period in periods:
        plays[period.attrib['number']] = []
        for play in period.findall("play"):
            this_play = {}
            for attrName, attrValue in play.attrib.items():
                this_play[attrName] = attrValue
            plays[period.attrib['number']].append(this_play)
    dict['plays'] = plays
    return dict


def parse_game_file(filename):
    game_data = ET.parse(filename)
    root = game_data.getroot()

    game_dict = {} # Stores the python dictionary containing the game information
    game_dict = parse_venue_info(root, game_dict)
    # for child in root:
    #     print(child.tag, child.attrib)
    for team in root.findall("team"):
        game_dict = get_team_info(team, game_dict)
    game_dict = get_play_info(root, game_dict)

    return game_dict
