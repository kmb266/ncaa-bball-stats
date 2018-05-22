from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey

# Used to keep track of classes and tables
from sqlalchemy.ext.declarative import declarative_base

# Initialize the base
Base = declarative_base()

from Constants import sqlite_json, sqlite_xml

# Define database tables
class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    home = Column(String)
    # Can use date and home as a primary key: A team can only play one game at any given time
    visitor = Column(String)
    winner = Column(String)
    loser = Column(String)
    home_score = Column(Integer)
    visitor_score = Column(Integer)
    isLeague = Column(Boolean)
    isPlayoff = Column(Boolean)
    # How do we store period data - i.e. what if there's 12 OT? Should use PostgreSQL with json


class Team(Base):
    __tablename__ = 'teams'
    team_id = Column(String, primary_key=True)
    name = Column(String)


class TeamIn(Base):
    __tablename__ = 'teamstats'
    team = Column(String, ForeignKey('teams.team_id'), primary_key=True)
    game = Column(Integer, ForeignKey('games.id'), primary_key=True)

    # Box Stats
    fgm = Column(Integer)  # Made field goals
    fga = Column(Integer)  # Attempted field goals

    fgm3 = Column(Integer)  # Made threes
    fga3 = Column(Integer)  # Attempted threes

    ftm = Column(Integer)  # Made free throws
    fta = Column(Integer)  # Attempted free throws

    tp = Column(Integer)  # Total points
    blk = Column(Integer)  # Total blocks
    stl = Column(Integer)  # Total steals
    ast = Column(Integer)  # Total assists
    oreb = Column(Integer)  # Total offensive rebounds
    dreb = Column(Integer)  # Total defensive rebounds
    treb = Column(Integer)  # Total rebounds (offensive + defensive)
    pf = Column(Integer)  # Total personal fouls
    tf = Column(Integer)  # Total team fouls
    to = Column(Integer)  # Total turnovers

    # Special Statistics
    is_home = Column(Boolean)
    pts_to = Column(Integer)  # Points scored off of turnovers
    pts_paint = Column(Integer)  # Points scored in the paint
    pts_ch2 = Column(Integer)  # Points scored within the arc but outside the paint?
    pts_fastb = Column(Integer)  # Points scored on fastbreaks
    pts_bench = Column(Integer)  # Points scored by the bench
    ties = Column(Integer)  # Number of times the team tied the game
    leads = Column(Integer)  # Number of times the team took the lead
    poss_count = Column(Integer)  # Number of possessions
    poss_time = Column(Integer)  # Amount of time the team had the ball
    score_count = Column(Integer)  # Amount of possessions the team scored on
    score_time = Column(Integer)  # Amount of time spent on possessions that resulted in scoring TODO: verify this


class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    position = Column(Integer)
    team = Column(String, ForeignKey('teams.team_id'))


class PlayerIn(Base):
    __tablename__ = 'playersin'
    # temp_id = Column(Integer, primary_key=True)
    game = Column(Integer, ForeignKey('games.id'), primary_key=True)
    player = Column(Integer, ForeignKey('players.id'), primary_key=True)
    number = Column(Integer)  # Jersey number in that game

    # Player Stats
    mins = Column(Integer)  # Minutes played
    fgm = Column(Integer)  # Made field goals
    fga = Column(Integer)  # Attempted field goals

    fgm3 = Column(Integer)  # Made threes
    fga3 = Column(Integer)  # Attempted threes

    ftm = Column(Integer)  # Made free throws
    fta = Column(Integer)  # Attempted free throws

    tp = Column(Integer)  # Total points
    blk = Column(Integer)  # Total blocks
    stl = Column(Integer)  # Total steals
    ast = Column(Integer)  # Total assists
    oreb = Column(Integer)  # Total offensive rebounds
    dreb = Column(Integer)  # Total defensive rebounds
    treb = Column(Integer)  # Total rebounds (offensive + defensive)
    pf = Column(Integer)  # Total personal fouls
    tf = Column(Integer)  # Total team fouls
    to = Column(Integer)  # Total turnovers
    dq = Column(Integer)  # Disqualifications? TODO: review


class Play(Base):
    __tablename__ = 'plays'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    period = Column(Integer)
    time = Column(String)
    scoring_play = Column(Boolean)
    shooting_play = Column(Boolean)
    score_value = Column(Integer)
    home_score = Column(Integer)
    away_score = Column(Integer)
    text = Column(String)
    action = Column(String)
    type = Column(String)
    player_id = Column(Integer, ForeignKey('players.id'))
    # Who's on the court right now?
    h1 = Column(Integer, ForeignKey('players.id'))
    h2 = Column(Integer, ForeignKey('players.id'))
    h3 = Column(Integer, ForeignKey('players.id'))
    h4 = Column(Integer, ForeignKey('players.id'))
    h5 = Column(Integer, ForeignKey('players.id'))

    v1 = Column(Integer, ForeignKey('players.id'))
    v2 = Column(Integer, ForeignKey('players.id'))
    v3 = Column(Integer, ForeignKey('players.id'))
    v4 = Column(Integer, ForeignKey('players.id'))
    v5 = Column(Integer, ForeignKey('players.id'))

    time_converted = Column(Integer)

    def convert_time(self, period, time):
        """
        Converts a period & time representation of time into seconds
        :param period:
        :param time:
        :return:
        """
        colon_idx = time.index(":")
        if period < 3:
            result = -2400 + ((period - 1) * 1200)  # Period 1 -> 2400, period 2 -> 1200
            mins_to_secs = 1200 - int(time[:colon_idx]) * 60  # 20 mins -> 0, 0 mins -> 1200
            secs_to_secs = int(time[colon_idx + 1:])
            self.time_converted = result + mins_to_secs - secs_to_secs
        else:
            # TODO: Check if this works
            result = (period - 3) * 5 * 60
            mins_to_secs = 300 - int(time[:colon_idx]) * 60
            secs_to_secs = int(time[colon_idx + 1:])
            self.time_converted = result + mins_to_secs - secs_to_secs


def create_db(db_name):
    # During initial development, use a sqlite DB held in memory for easy setup/teardown

    engine = create_engine('{}'.format(db_name), echo=False)
    Base.metadata.create_all(engine)


# Initialize xml database
# create_db(sqlite_xml)

# Initialize json database
# create_db(sqlite_json)
