import os, sys

"""
Auto Complete Target
"""
AC_TEAM = 0
AC_PLAYER = 1
AC_POSITION = 2

"""
Page Constants
"""
Page_Players = 0
Page_Teams = 1
Page_Games = 2


"""
Error Codes
"""
FormMissingElement = 0
InvalidFormValue = 1

"""
Debug Constants
If DEBUG == False, you can run the application via npm start. If DEBUG == True, you can compile the application
into a desktop executable.
"""
DEBUG = False   # Always set DEBUG to false before compiling the application
if DEBUG:
    BASE_DIR = os.getcwd()
    BACKEND_DIR = os.path.join(BASE_DIR, 'src/python/backend')
    db_path_xml = os.path.join(BASE_DIR, 'src/python/backend', "basketball_xml.db")
    db_path_json = os.path.join(BASE_DIR, 'src/python/backend', "basketball_json.db")
else:
    file_dir = sys.argv[0].split('/')[:-2]  # go up one directory to backend
    file_dir += ['backend']
    BASE_DIR = os.path.join(*file_dir)
    BACKEND_DIR = BASE_DIR
    db_path_xml = os.path.join(BASE_DIR, "basketball_xml.db")
    db_path_json = os.path.join(BASE_DIR, "basketball_json.db")


sqlite_xml = 'sqlite:///{}'.format(db_path_xml)
sqlite_json = 'sqlite:///{}'.format(db_path_json)
