import advanced_stat as a_s
import numpy


def stats_calculation(data):
    '''
    Name: getAdvancedData
    Returns: the advanced data for each player and each team
    Arguments:
    FGM : field goal made
    FGA : field goal attempted
    FGM_3 : 3 pointers made
    FGA_3 : 3 pointers attempted
    FGM_2 : 2 pointers made
    FGA_2 : 2 pointers Attempted
    FTM : free throw made
    FTA : free throw attempted
    OREB : offensive rebound
    DREB : deffensive rebound
    TREB : total rebound
    PF : personal foul
    AST : assist
    TOV : turnover
    BLK : block
    STL : steal
    PTS : points
    Tm : Team
    Opp : Opponent
    '''
    #print("Number of players: " + str(len(data["data"])))
    #print("Calculating advanced stats:")
    advanced_data = []
    for player in data["data"]:
        #print("--Calculating stats for " + player["name"])
        games = player["games"]
        team_id = player["team"]

        for game_id, box_score in games.items():
            #print("----Calculating game " + str(game_id))
            # Player values
            try:
                FGM = float(box_score["FG"])
            except:
                FGM = 0.0

            try:
                FGA = float(box_score["FGA"])
            except:
                FGA = 0.0

            try:
                FGM_3 = float(box_score["3PT"])
            except:
                FGM_3 = 0.0

            try:
                FGA_3 = float(box_score["FGA3"])
            except:
                FGA_3 = 0.0

            try:
                FGM_2 = float(FGM - FGM_3)
            except:
                FGM_2 = 0.0
            try:
                FGA_2 = float(FGA - FGM_3)
            except:
                FGA_2 = 0.0

            try:
                FTM = float(box_score["FT"])
            except:
                FTM = 0.0

            try:
                FTA = float(box_score["FTA"])
            except:
                FTA = 0.0
            try:
                OREB = float(box_score["OREB"])
            except:
                OREB = 0.0

            try:
                DREB = float(box_score["DREB"])
            except:
                DREB = 0.0

            try:
                TREB = float(box_score["REB"])
            except:
                TREB = 0.0

            try:
                PF = float(box_score["PF"])
            except:
                PF = 0.0

            try:
                AST = float(box_score["AST"])
            except:
                AST = 0.0

            try:
                TOV = float(box_score["TO"])
            except:
                TOV = 0.0

            try:
                BLK = float(box_score["BLK"])
            except:
                BLK = 0.0

            try:
                STL = float(box_score["STL"])
            except:
                STL = 0.0

            try:
                PTS = float(box_score["PTS"])
            except:
                PTS = 0.0

            try:
                MIN = float(abs(box_score["MIN"]))
            except:
                MIN = 0.0

            opponent_id = box_score["away"]
            if team_id == box_score["away"]:
                opponent_id = box_score["home"]

            # Team values
            team_boxscore = data["teamOverall"][team_id]["games"][game_id]
            TmFGM = float(team_boxscore["FG"])
            TmFGA = float(team_boxscore["FGA"])
            TmFGM_3 = float(team_boxscore["3PT"])
            TmFGA_3 = float(team_boxscore["FGA3"])
            TmFGM_2 = float(TmFGM - TmFGM_3)
            TmFGA_2 = float(TmFGA - TmFGM_3)
            TmFTM = float(team_boxscore["FT"])
            TmFTA = float(team_boxscore["FTA"])
            TmOREB = float(team_boxscore["OREB"])
            TmDREB = float(team_boxscore["DREB"])
            TmTREB = float(team_boxscore["REB"])
            TmPF = float(team_boxscore["PF"])
            TmAST = float(team_boxscore["AST"])
            TmTOV = float(team_boxscore["TO"])
            TmBLK = float(team_boxscore["BLK"])
            TmSTL = float(team_boxscore["STL"])
            TmPTS = float(team_boxscore["PTS"])

            # TODO : TmMIN
            TmMIN = 200.0 #team_boxscore["MIN"]

            # Opponent team values
            opponent_boxscore = data["teamOverall"][opponent_id]["games"][game_id]
            OppFGM = float(opponent_boxscore["FG"])
            OppFGA = float(opponent_boxscore["FGA"])
            OppFGM_3 = float(opponent_boxscore["3PT"])
            OppFGA_3 = float(opponent_boxscore["FGA3"])
            OppFGM_2 = float(OppFGM - OppFGM_3)
            OppFGA_2 = float(OppFGA - OppFGM_3)
            OppFTM = float(opponent_boxscore["FT"])
            OppFTA = float(opponent_boxscore["FTA"])
            OppOREB = float(opponent_boxscore["OREB"])
            OppDREB = float(opponent_boxscore["DREB"])
            OppTREB = float(opponent_boxscore["REB"])
            OppPF = float(opponent_boxscore["PF"])
            OppAST = float(opponent_boxscore["AST"])
            OppTOV = float(opponent_boxscore["TO"])
            OppBLK = float(opponent_boxscore["BLK"])
            OppSTL = float(opponent_boxscore["STL"])
            OppPTS = float(opponent_boxscore["PTS"])

            OppMIN = float(200)

            GmPTS = OppPTS + TmPTS
            GmFGM = OppFGM + TmFGM
            GmFTM = OppFTM + TmFTM
            GmFGA = OppFGA + TmFGA
            GmFTA = OppFTA + TmFTA
            GmDREB = OppDREB + TmDREB
            GmOREB = OppOREB + TmOREB
            GmAST = OppAST + TmAST
            GmSTL = OppSTL + TmSTL
            GmBLK = OppBLK + TmBLK
            GmPF = OppPF + TmPF
            GmTO = OppTOV + TmTOV

            # TODO : Don't know what is this data
            OREB_perc = 0
            if (OppDREB + TmOREB) > 0:
                OREB_perc = TmOREB / (OppDREB + TmOREB)

            #first level calculation
            TmPoss = a_s.TmPoss(TmFGA,TmOREB,OppDREB,TmFTA,TmFGM,TmTOV)
            OppPoss = a_s.OppPoss(OppFGA,OppOREB,TmDREB,OppFTA,OppFGM,OppTOV)
            PProdAst = a_s.PProdAst(TmFGM, FGM, TmFGM_3, TmPTS, TmFTM, PTS, FGA, AST, FGM_3,FTM, TmFGA)
            q5 = a_s.q5(TmAST,AST,TmFGM)
            q12 = a_s.q12(TmAST,TmMIN,MIN,AST,TmFGM,FGM)
            ASTPart =  a_s.ASTPart(TmPTS,TmFTM,PTS,FTM,TmFGA,FGA,AST)
            FTPart = a_s.FTPart(FTM,FTA)
            TmScorPoss = a_s.TmScorPoss(TmFGM,TmFTM,TmFTA)
            TmOREB_pect = a_s.TmOREB_pect(TmOREB,OppTREB,OppDREB)
            TmPlay = a_s.TmPlay(TmFGA,TmFTA,TmTOV)
            FTmPoss = a_s.FTmPoss(FTM,FTA)
            DOREB_perc = a_s.DOREB_perc(OppOREB,TmDREB)
            DFG_perc = a_s.DFG_perc(OppFGM,OppFGA)
            eFG_perc = a_s.eFG_perc(FGM,FGA,FGM_3)
            Turnover_perc = a_s.Turnover_perc(TOV,FGA,FTA)
            FTr = a_s.FTr(FTA,FGA)
            FG_2_perc = a_s.FG_2_perc(FGM_2,FGA_2)
            FG_3_perc = a_s.FG_3_perc(FGM_3,FGA_3)
            FGr_2 = a_s.FGr_2(FGA_2,FGA)
            FGr_3 = a_s.FGr_3(FGA_3,FGA)
            Usage_Rate = a_s.Usage_Rate(FGA,FTA,TOV,TmMIN,MIN,TmFGA,TmFTA,TmTOV)
            ASTPart = a_s.AST_perc(AST,MIN,TmMIN,TmFGM,FGM)
            ASTr = a_s.ASTr(AST,FGM)
            AST_Ratio = a_s.AST_Ratio(AST,FGA,FTA,TOV)
            OppPtsPScorPoss = a_s.OppPtsPScorPoss(OppPTS,OppFGM,OppFTM,OppFTA)
            TS_perc = a_s.TS_perc(PTS,FGA,FTA)
            Total_REB_pect = a_s.Total_REB_pect (TREB,TmMIN,MIN,TmTREB,OppTREB)
            BLK_perc = a_s.BLK_perc(BLK,TmMIN,MIN,OppFGA,OppFGA_3)
            Game_Score = a_s.Game_Score(PTS,FGM,FGA,FTA,FTM,OREB,DREB,STL,AST,BLK,PF,TOV)
            PIE = a_s.PIE(PTS,FGM,FTM,FGA,FTA,DREB,OREB,AST,STL,BLK,PF,TOV,GmPTS,GmFGM,GmFTM,GmFGA,GmFTA,GmDREB,GmOREB,GmAST,GmSTL,GmBLK,GmPF,GmTO)

            # adding results to dictionary
            #box_score["TmPoss"] = TmPoss
            #box_score["OppPoss"] = OppPoss
            box_score["PProdAst"] = PProdAst
            box_score["q5"] = q5
            box_score["q12"] = q12
            box_score["ASTPart"] = ASTPart
            box_score["FTPart"] = FTPart
            #box_score["TmScorPoss"] = TmScorPoss
            #box_score["TmOREB_pect"] = TmOREB_pect
            #box_score["TmPlay"] = TmPlay
            box_score["FTmPoss"] = FTmPoss
            box_score["DOREB_perc"] = DOREB_perc
            box_score["DFG_perc"] = DFG_perc
            box_score["eFG_perc"] = eFG_perc
            box_score["Turnover_perc"] = Turnover_perc
            box_score["FTr"] = FTr
            box_score["FG_2_perc"] = FG_2_perc
            box_score["FG_3_perc"] = FG_3_perc
            box_score["FGr_2"] = FGr_2
            box_score["FGr_3"] = FGr_3
            box_score["Usage_Rate"] = Usage_Rate
            box_score["ASTPart"] = ASTPart
            box_score["ASTr"] = ASTr
            box_score["AST_Ratio"] = AST_Ratio
            #box_score["OppPtsPScorPoss"] = OppPtsPScorPoss
            box_score["TS_perc"] = TS_perc
            box_score["Total_REB_pect"] = Total_REB_pect
            box_score["BLK_perc"] = BLK_perc
            box_score["Game_Score"] = Game_Score
            box_score["PIE"] = PIE

            #second level calculation
            TmORTG = a_s.TmORTG (TmPTS, TmPoss)
            qAST = a_s.qAST(MIN,TmMIN,q12,q5)
            TmPlay_pect = a_s.TmPlay_pect(TmScorPoss, TmFGA,TmFTA,TmTOV)
            FGmPoss = a_s.FGmPoss(FGA,FGM,TmOREB_pect)
            Team_Floor_Percentage = a_s.Team_Floor_Percentage(TmScorPoss, TmPoss)
            TmDRTG = a_s.TmDRTG(OppPTS,TmPoss)
            FMwt = a_s.FMwt(DFG_perc,DOREB_perc)
            STL_perc = a_s.STL_perc(STL,TmMIN,MIN,OppPoss)
            Pace = a_s.Pace(TmPoss,OppPoss,TmMIN)

            #adding results to dictionary
            #box_score["TmORTG"] = TmORTG
            box_score["qAST"] = qAST
            #box_score["TmPlay_pect"] = TmPlay_pect
            box_score["FGmPoss"] = FGmPoss
            #box_score["Team_Floor_Percentage"] = Team_Floor_Percentage
            #box_score["TmDRTG"] = TmDRTG
            box_score["FMwt"] = FMwt
            box_score["Pace"] = Pace
            box_score["STL_perc"] = STL_perc

            #third level calculation
            PProdFG = a_s.PProdFG(FGM,PTS,FTM,FGA,qAST,FGM_3)
            FGPart = a_s.FGPart(FGM,PTS,FTM,FGA,qAST)
            TmOREBWgt = a_s.TmOREBWgt(TmOREB_pect,TmPlay_pect)
            Stops_1 = a_s.Stops_1(STL,BLK,FMwt,DOREB_perc,DREB)
            Stops_2 = a_s.Stops_2(OppFGA,OppFGM,TmBLK,TmMIN,FMwt,DOREB_perc,OppTOV,TmSTL,MIN,PF,TmPF,OppFTA,OppFTM)

            #adding results to dictionary
            box_score["PProdFG"] = PProdFG
            box_score["FGPart"] = FGPart
            #box_score["TmOREBWgt"] = TmOREBWgt
            box_score["Stops_1"] = Stops_1
            box_score["Stops_2"] = Stops_2

            #forth level calculation
            PProdOREB = a_s.PProdOREB(OREB,TmOREBWgt,TmPlay_pect,TmPTS,TmFGM,TmFTM,TmFTA)
            OREBPart = a_s.OREBPart(OREB,TmOREBWgt,TmPlay_pect)
            Stops = a_s.Stops(Stops_1,Stops_2)

            #adding results to dictionary
            box_score["PProdOREB"] = PProdOREB
            box_score["OREBPart"] = OREBPart
            box_score["Stops"] = Stops

            #fifth level calculation
            PProd = a_s.PProd(PProdFG, PProdAst,FTM,TmOREB,TmScorPoss,TmOREBWgt,TmPlay_pect,PProdOREB)
            ScPoss = a_s.ScPoss(FGPart,ASTPart,FTPart,TmOREB,TmScorPoss,TmOREBWgt,TmPlay_pect,OREBPart)
            Stop_perc = a_s.Stop_perc(Stops,OppMIN,TmPoss,MIN)

            #adding results to dictionary
            box_score["PProd"] = PProd
            box_score["ScPoss"] = ScPoss
            box_score["Stop_perc"] = Stop_perc

            #sixth level calculation
            TotPoss = a_s.TotPoss(ScPoss,FGmPoss,FTmPoss,TOV)
            DRTG = a_s.DRTG(TmDRTG,OppPtsPScorPoss,Stop_perc)

            #adding results to dictinory
            box_score["TotPoss"] = TotPoss
            box_score["DRTG"] = DRTG

            #seventh level calculation
            Individual_Offensize_Rating = a_s.Individual_Offensize_Rating(PProd, TotPoss)
            Individual_Floor_Percentage = a_s.Individual_Floor_Percentage(ScPoss,TotPoss)

            #adding results to dictinory
            box_score["Individual_Offensize_Rating"] = Individual_Offensize_Rating
            box_score["Individual_Floor_Percentage"] = Individual_Floor_Percentage

    return data
