import Constants
from data_retriever import getAllTeams, getAllPlayers
import sys, json

def getErrorForm(code, msg):
    data = {"error" : {"code" : code, "message" : msg}}
    return data

def retrieveData(form):
    # print(type(form))
    target = form["field"]
    if target is None:
        return getErrorForm(Constants.FormMissingElement, "Missing value for the key 'field'")
    else:
      # team drop down menu
      if target == Constants.AC_TEAM:
        data = getAllTeams()
        return data
            # player drop down menu
      elif target == Constants.AC_PLAYER:
        # don't need id for now just Cornell basketball
        cornell_id = "COR"
        data = getAllPlayers(cornell_id)
        return data
      else:
        return getErrorForm(Constants.InvalidFormValue, "Wrong value for key 'field'")

    return ["ASD"]

def getForm():
    lines = sys.stdin.readlines()
    # Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def main():
    try:
        form = getForm()
        # form = {"field" : 1}
        data = retrieveData(form)
    except Exception as e:
        data = {"error" : e.message, "doc" : e.__doc__, "dir": sys.argv[0]}
        data = json.dumps(data)

    #return what we get
    print(data)
    sys.stdout.flush()

#start process
if __name__ == '__main__':
    main()
