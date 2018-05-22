# Cornell Men's Varsity Basketball Statistics Application

This repository contains all of the source code for
an application for the use of the Cornell University men's basketball team coaching staff to more efficiently and intuitively parse through data to make better informed administrative decisions.

## Quick Links
* Setup
  * Developers
    * Requirements
    * Installation
  * Users
* High-Level Implementation
* Low-Level Implementation Details


## Setup

## Developers
TODO: Add information on setting PROD=True or False

### Requirements
1. If you are a developer and would like to make changes to the application, you will need Python 2.7 or higher (3.6+ is preferred). To install all the necessary Python libraries, you can navigate to the cs-5150-basketball-project directory and `pip install -r requirements.txt`.
2. You will also need `npm`.

### Installation
To get a copy of the repository on your local device, begin by `git clone`ing the repository. Once this is complete, navigate into the `app` directory and run `npm install`. After the install process is complete, you can run `npm start` to launch the application. Changing code and refreshing the application window (or relaunching the application by again using `npm start`) will allow you to see your changes in action before you compile the application. In order to compile the application, navigate to the `app` directory and run `electron-forge make`. The compiled application can then be found in `app/out/`.


## Users
End users simply need to download the pre-compiled app, one version of which can be found [here](todo:insert link).


## High-Level Implementation
The application functions by parsing XML game data files provided by the Cornell coaching staff and JSON game data parsed from the ESPN website. The parsed data is then used to populate individual xml and json SQLite databases, which can be found in `app/src/python/backend/`. The database schema definition and initialization functions can be found in `app/db.py`, parsing functions can be found in `app/parser.py` (for XML files) and `app/parse_json.py` (for JSON files). Finally, the database population occurs in and `app/populate_db.py`.

`app/xml_downloader.py` fetches new XML data from a Google Drive account (the necessary credentials should be privately handed over to the coaching staff). Similarly, `app/espn_scraper.py` and `app/espn_to_db.py` contains code to fetch new JSON data.

Dynamically querying the database is handled in `app/data_retriever.py`, while static queries (like obtaining a set of team names or player names) occurs in `app/auto_complete.py`.

Information retrieved from the backend is passed on to the middle stack files for formatting and calculating advanced statistics. The advanced statistics formulas can be found in `app/advanced_stat.py`, and the rest of the middle stack operations take place in `app/data_manager.py`.

Finally, information is presented to the user in the frontend HTML/CSS in the various .html, .css, and .ts files present in `app/src` and `app/src/assets` (the latter of which contains CSS and JavaScript dependencies.)

## Low-Level Implementation
