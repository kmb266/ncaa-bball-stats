import json, datetime, glob, sys
import espn_scraper as espn

import populate_db

# constants
cached_json = None
league = 'ncb'

def getStartYr():
    """get the year of the current season if in season,
    or get the start year of the most recent season if out of season"""

    now = datetime.datetime.now()
    if datetime.datetime(year=now.year,month=11,day=1) < now:
        return now.year
    return now.year - 1

def ppjson(data):
    ''' Pretty print json helper '''
    print(json.dumps(data, indent=2, sort_keys=True))

def url_is_before_today(url):
    """
    Checks to see if a url is for a game in the past
    (espn scoreboards are also for future)
    * Helper function to remove future scoreboard games
    Returns: boolean
    """
    date_string = url[url.rfind('/') + 1: url.rfind('?')]
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[-2:])
    return datetime.datetime(year,month,day).date() < datetime.datetime.now().date()

def url_is_after_last_scrape(url, last_scrape_date):
    """
    Checks to see if a url is for a game is after the last time data was scraped
    * Helper function to avoid duplicating db data from past scoreboard games
    Returns: boolean
    """
    date_string = url[url.rfind('/') + 1: url.rfind('?')]
    year = int(date_string[:4])
    month = int(date_string[4:6])
    day = int(date_string[-2:])
    return datetime.datetime(year,month,day).date() > last_scrape_date.date()

def filter_scoreboards_before_today(scoreboard_url_list, last_scrape_date):
    """
    Takes a list of scoreboard urls which will include all of the scoreboards
    for the NCAA and eliminates urls that are in the future and that have already
    been scraped; returnin the resulting list of urls
    Returns: list of strings
    """
    return [url for url in scoreboard_url_list if url_is_before_today(url) and url_is_after_last_scrape(url, last_scrape_date)]

def scrape_espn_game_ids(withProgress, filtered_scoreboards, start_yr):
    """
    Gets the game ids for the games played in a list of espn scoreboards
    Returns: list of strings
    """
    game_ids = []
    for i, scoreboard_url in enumerate(filtered_scoreboards):
        data = espn.get_url(scoreboard_url, cached_path=cached_json)
        for event in data['content']['sbData']['events']:
            game_id = event['competitions'][0]['id']
            game_ids.append(game_id)
    return game_ids

def scrape_espn_play_by_plays(withProgress, game_ids, start_yr):
    """
    Gets play by play data from ESPN API for the games who's ids are in game_ids
    Returns a list of json objects (containing play-by-plays for each game)
    """
    data = []
    for i,game_id in enumerate(game_ids):
        pbp_url = espn.get_game_url("playbyplay", league, game_id)
        pbp_json = espn.get_url(pbp_url, cached_path=cached_json, game_id=game_id)
        data.append(pbp_json)
    return data

def main():
    # just in case we need the last time the app was opened
    # lines = sys.stdin.readlines()
    # data = json.loads(lines[0])
    # ui_last_open = datetime.datetime.fromtimestamp( int(data['lastOpen']) / 1e3)

    start_yr = getStartYr()
    last_scraped_game_date = populate_db.get_last_scrape_date().date
    print(start_yr, last_scraped_game_date.date())

    scoreboard_urls = espn.get_all_scoreboard_urls(league, start_yr)

    filtered_scoreboards = filter_scoreboards_before_today(scoreboard_urls, last_scraped_game_date)
    print('finished filtered scoreboards')
    game_ids = scrape_espn_game_ids(False, filtered_scoreboards, start_yr)
    print('finished game_ids')
    all_json_data = scrape_espn_play_by_plays(False, game_ids, start_yr)
    print('finished all_json_data')

    for game_json in all_json_data:
        populate_db.json_to_database(None, game_json)
    sys.stdout.flush()

#start process
if __name__ == '__main__':
   main()
