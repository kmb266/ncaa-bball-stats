import numpy;
import sys;



def q5(TmAST,AST,TmFGM):
  return float(1.14*((TmAST-AST)/TmFGM))

print q5(10.0,0.0,13.0)

# test result: 87.6923076923%
# exel result: 88% 
# excel location: STAT ANALYSIS(S3)



def FTmPoss(FTM,FTA):
  return float(((1.0-(FTM/FTA))**2.0)*0.4*FTA)

print FTmPoss(0.0,2.0)
# test result: 80.0%
# exel result: 80.0% 
# excel location: STAT ANALYSIS(Y3)




def Usage_Rate(FGA,FTA,TOV,TmMIN,MIN,TmFGA,TmFTA,TmTOV):
  return float(100*((FGA+0.4*FTA+TOV)*(TmMIN/5))/(MIN*(TmFGA+0.4*TmFTA+TmTOV)))

print Usage_Rate(1.0,2.0,1.0,200.0,4.0,52.0,26.0,15.0)
# test result: 36.175
# exel result: 36.7 
# excel location: STAT ANALYSIS(N3)





def AST_perc(AST,MIN,TmMIN,TmFGM,FGM):
    if(((MIN/(TmMIN/5))*TmFGM)-FGM) == 0:
    return 0.0
  else:
    return float(100*AST/(((MIN/(TmMIN/5))*TmFGM)-FGM))

x = AST_perc(747.0,3026.0,19730.0,3429.0,857.0)
print(x)
# test result: 42.14%
# NBA web result: 44.4%
# excel location: cannot find in excel, used NBA data to test




def ASTr(AST,FGM):
  if FGM == 0: 
    return 0.0
  else: 
    return float(AST/FGM)

print ASTr(1.0,0.0)
# test result: 0.0
# exel result: ??????
# excel location: ??????



def AST_Ratio(AST,FGA,FTA,TOV):
  return float((100*AST)/(FGA+(FTA*0.4)+AST+TOV))

print AST_Ratio(2.0,9.0,7.0,5.0)
# test result: 10.63829
# exel result: ??????
# excel location: ??????



def TmPoss(TmFGA, TmOREB,oppDREB,TmFTA,TmFGM,TmTOV):
  return float(TmFGA-(TmOREB/(TmOREB+oppDREB))*(TmFGA-TmFGM)*1.07+TmTOV + 0.4*TmFTA)

print TmPoss(52.0, 9.0, 30.0, 26.0, 13.0, 15.0)
# test result: 67.77
# exel result: 67.8
# excel location: STAT ANALYSIS(C19)



def Pace(TmPoss,OppPoss,TmMIN):
  return float(40*((TmPoss+OppPoss)/(2*(TmMIN/5))))

x =  Pace(8051.97, 8059.5, 19730.0)
print(x)
# test result: 81.65
# NBA web result: 98.0
# excel location: cannot find in excel, used NBA data to test



def DFG_perc(OppFGM,OppFGA):
  if OppFGA == 0:
    return 0.0
  else:
    return float(OppFGM/OppFGA)
  
print DFG_perc(29.0,70.0)
# test result: 41.43%
# exel result: 41.4%
# excel location: OPP BOX(D19)



def DOREB_perc(OppOREB,TmDREB):
  return float(OppOREB/(OppOREB+TmDREB))

print DOREB_perc(17.0,20.0)
# test result: 45.94%
# exel result: 45.9% 
# excel location: STAT ANALYSIS(AC19)
# Note: different fomular from excel sheet, double check? (ask during presentation)





def FMwt(DFG_perc,DOREB_perc):
  return float((DFG_perc*(1-DOREB_perc))/(DFG_perc
      *(1-DOREB_perc)+(1-DFG_perc)*DOREB_perc))

print FMwt(0.4143,0.459)
# test result: 0.4546
# exel result: 0.45 
# excel location: STAT ANALYSIS(AD19)
# Note: this data depends on DOREB, need to check function first 


def Stops_1(STL,BLK,FMwt,DOREB_perc,DREB):
  return float(STL+BLK*FMwt*(1-1.07*DOREB_perc)+DREB*(1-FMwt))

print Stops_1(0.0,1.0,0.45,0.459,2.0)
# test result: 1.328
# exel result: 1.3 
# excel location: STAT ANALYSIS(AE4)



def Stops_2(OppFGA,OppFGM,TmBLK,TmMIN,FMwt,DOREB_perc
      ,OppTOV,TmSTL,MIN,PF,TmPF,OppFTA,OppFTM):
  return  float((((OppFGA-OppFGM-TmBLK)/TmMIN)*FMwt*(1-1.07*DOREB_perc) 
      +((OppTOV-TmSTL)/TmMIN))*MIN+(PF/TmPF) 
      *0.4*OppFTA*(1-(OppFTM/OppFTA))**2)

print Stops_2(70.0,29.0,1.0,200.0,0.45,0.459,8.0,1.0,4.0,0.0,15.0,18.0,13.0)
# test result: 0.323
# exel result: 0.32 
# excel location: STAT ANALYSIS(AF3)

print Stops_2(70.0,29.0,1.0,200.0,0.45,0.459,8.0,1.0,15.0,1.0,15.0,18.0,13.0)
# test result: 1.249
# exel result: 1.25 
# excel location: STAT ANALYSIS(AF4)




def Stops(Stops_1,Stops_2):
  return float(Stops_1+Stops_2)

print Stops(1.3,1.25)
# test result: 2.55
# exel result: 1.9 
# excel location: STAT ANALYSIS(AH4)

# Note: different fomulars(checked. OK) 





def Stop_perc(Stops,OppMIN,TmPoss,MIN):
  if(TmPoss*MIN == 0):
    return 0.0;
  else:
    return float((Stops*OppMIN)/(TmPoss*MIN))
  
print Stop_perc(1.9,200.0,67.77,15.0)
# test result: 0.3739
# exel result: 0.9 
# excel location: STAT ANALYSIS(H4)




def OppPtsPScorPoss(OppPTS,OppFGM,OppFTM,OppFTA):
  return float(OppPTS/(OppFGM+(1-(1-(OppFTM/OppFTA))**2 )*OppFTA*0.4))

print OppPtsPScorPoss(77.0,29.0,17.0,18.0)
# test result: 2.128
# exel result: ???????  
# excel location: ????????



def TmORTG (TmPoints, TmPoss):
  if TmPoss == 0:
    return 0.0
  return float(100*(TmPoints/TmPoss))

print TmORTG(45.0, 67.77)
# test result: 66.4
# exel result: 64.0 
# excel location: STAT ANALYSIS(F19)





def q12(TmAST,TmMIN,MIN,AST,TmFGM,FGM):
  return float(((TmAST/TmMIN)*MIN*5-AST)/((TmFGM/TmMIN)*MIN*5-FGM))

print q12(10.0,200.0,4.0,0.0,13.0,0.0)
# test result: 76.92%
# exel result: 77% 
# excel location: STAT ANALYSIS(T3)




def FGPart(FGM,PTS,FTM,FGA,qAST):
  return float(FGM*(1-0.5*(((PTS-FTM))/(2*FGA))*qAST))

print FGPart(4.0,11.0,2.0,13.0,1.08)
# test result: 325.23%
# exel result: 325% 
# excel location: STAT ANALYSIS(Q5)




def PProdAst(TmFGM, FGM, Tm3PM, TmPTS, TmFTM, PTS, FGA, AST, FGM_3, FTM, TmFGA):
  return float(2*((TmFGM-FGM+0.5*(Tm3PM-FGM_3))/(TmFGM-FGM))*0.5
      *(((TmPTS-TmFTM)-(PTS-FTM))/(2*(TmFGA-FGA) ))*AST)

print PProdAst(13.0,0.0,4.0,45.0,15.0,0.0,3.0,1.0,0.0,0.0,52.0)
# test result: 35.32%
# exel result: 35% 
# excel location: STAT ANALYSIS(AA4)




def PProdFG(FGM,PTS,FTM,FGA,qAST,FGM_3):
  return float(2*(FGM+0.5*FGM_3)*1-0.5*((PTS-FTM)/(2*FGA))*qAST)

print PProdFG(0.0,0.0,0.0,1.0,0.78,0.0)
# test result: 0%
# exel result: 0% 
# excel location: STAT ANALYSIS(Z3)

print PProdFG(4.0,11.0,2.0,13.0,1.08,1.0)
# test result: 881%
# exel result: 732% 
# excel location: STAT ANALYSIS(Z5)




def qAST(MIN,TmMIN,q_12,q_5):
  return float(q_5*(MIN/(TmMIN/5))+(1-(MIN/(TmMIN/5))*q_12))
print qAST(4.0,200.0,0.77,0.88)
# test result: 77% 
# exel result: 78% 
# excel location: STAT ANALYSIS(R3)




def PProdOREB(ORB,TmOREBWgt,TmPlay_pect,TmPTS,
      TmFGM,TmFTM,TmFTA):
  return float(ORB*TmOREBWgt*TmPlay_pect*(TmPTS/(TmFGM+(1-(1-(TmFTM/TmFTA))**2 )
      *0.4*TmFTA)))

print PProdOREB(1.0, 0.56, 0.278, 45.0, 13.0, 15.0, 26.0)
# test result: 32.5%
# exel result: 33% 
# excel location: STAT ANALYSIS(AB9)




def TotPoss(ScPoss,FGmPoss,FTmPoss,TOV):
  return float(ScPoss+FGmPoss+FTmPoss+TOV)

print TotPoss(0.0,0.8,0.75,1.0)
# test result: 2.55
# exel result: 2.6
# excel location: STAT ANALYSIS(C3)


def PProd(PProdFG, PProdAst,FTM,TmOREB,
    TMScorPoss,TmOREBWgt,TmPlay_pect,PProdOREB):
  return float((PProdFG+PProdAst+FTM)*(1-(TmOREB/TMScorPoss)
      *TmOREBWgt*TmPlay_pect)+PProdOREB)

print PProd(0.0,0.35,0.0,9.0,21.5,0.56,0.278,0.0)
# test result: 0.327
# exel result: 0.3
# excel location: STAT ANALYSIS(E4)




def ScPoss(FGPart,ASTPart,FTPart,TmOREB,
      TmScorPoss,TmOREBWgt,TmPlay_pect,OREBPart):
  return float((FGPart+ASTPart+FTPart)*(1-(TmOREB/TmScorPoss)
    *TmOREBWgt*TmPlay_pect)+OREBPart)

print ScPoss(3.25,0.0,0.8,9.0,21.5,0.56,0.278,0.0)
# test result: 3.786
# exel result: 3.8
# excel location: STAT ANALYSIS(D5)




def FTPart(FTM,FTA):
  return float((1-(1-(FTM/FTA))**2 )*0.4*FTA)

print FTPart(6.0,7.0)
# test result: 274.2%
# exel result: 274%
# excel location: STAT ANALYSIS(V8)




def ASTPart(TmPTS,TmFTM,PTS,FTM,TmFGA,FGA,AST):
  return 0.5*(((TmPTS-TmFTM)-(PTS-FTM))/(2*(TmFGA-FGA) ))*AST

print ASTPart(45.0,15.0,0.0,0.0,52.0,3.0,1.0)
# test result: 15.3%
# exel result: 15%
# excel location: STAT ANALYSIS(U4)




def TmScorPoss(TmFGM,TmFTM,TmFTA):
  return float(TmFGM+(1-(1-(TmFTM/TmFTA))**2 )*TmFTA*0.4)

print TmScorPoss(13.0,15.0,26.0)
# test result: 21.53
# exel result: 21.5
# excel location: STAT ANALYSIS(D19)




def TmOREBWgt(TmOREB_pect,TmPlay_pect):
  return float(((1-TmOREB_pect)*TmPlay_pect)/((1-TmOREB_pect)
      *TmPlay_pect+TmOREB_pect*(1-TmPlay_pect)))

print TmOREBWgt(0.231,0.278)
# test result: 56.17%
# exel result: 56%
# excel location: STAT ANALYSIS(P19)



def TmOREB_pect(TmOREB,OppTREB,OppDREB):
  return float(TmOREB/(TmOREB+OppDREB))

print TmOREB_pect(9.0,47.0,30.0)
# test result: 23.07%
# exel result: 23.1%
# excel location: STAT ANALYSIS(019)




def TmPlay(TmFGA,TmFTA,TmTOV):
  return TmFGA+TmFTA*0.4+TmTOV

print TmPlay(52.0,26.0,15.0)
# test result: 77.4
# exel result: 77.4
# excel location: STAT ANALYSIS(L19)



def TmPlay_pect(TmScorPoss, TmFGA,TmFTA,TmTOV):
  return TmScorPoss/(TmFGA+TmFTA*0.4+TmTOV)

print TmPlay_pect(21.5,52.0,26,15)
# test result: 27.8%
# exel result: 27.8%
# excel location: STAT ANALYSIS(M19)




def OREBPart(OREB,TmOREBWgt,TmPlay_pect):
  return float(OREB*TmOREBWgt*TmPlay_pect)

print OREBPart(0.0,0.56,0.278)
# test result: 31.1%
# exel result: 31%
# excel location: STAT ANALYSIS(W12)




def FGmPoss(FGA,FGM,TmOREB_pect):
  return (FGA-FGM)*(1-1.07*TmOREB_pect)

print FGmPoss(1.0,0.0,0.231)
# test result: 75.3%
# exel result: 75%
# excel location: STAT ANALYSIS(X3)




def TmDRTG(OppPTS,TmPoss):
  if TmPoss == 0:
    return 0.0
  else:
    return float(100*(OppPTS/TmPoss))

print TmDRTG(77.0, 67.8)
# test result: 113.57
# exel result: 113.6
# excel location: STAT ANALYSIS(I19)




def Individual_Offensize_Rating(PProd, TotPoss):
  if TotPoss == 0:
    return 0.0
  else:
    return 100*(PProd/TotPoss)
  
print Individual_Offensize_Rating(8.7,10.6)
# test result: 82.1
# exel result: 82.4
# excel location: STAT ANALYSIS(F5)




def Individual_Floor_Percentage(ScPoss,TotPoss):
  if TotPoss == 0:
    return 0.0
  else:
    return float(ScPoss/TotPoss)
  
  print Individual_Floor_Percentage(3.8, 10.6)
# test result: 35.8%
# exel result: 35.8%
# excel location: STAT ANALYSIS(J5)




def Team_Floor_Percentage(TmScorPoss, TmPoss):
  if TmPoss == 0:
    return 0.0
  else:
    return float(TmScorPoss/TmPoss)
    
y = Team_Floor_Percentage(21.5,67.8)
print (y)
# test result: 31.7%
# exel result: 31.8%
# excel location: STAT ANALYSIS(J19)



def DRTG(TmDRTG,OppPtsPScorPoss,Stop_perc):
  return float(TmDRTG+0.2*(100*OppPtsPScorPoss*(1-Stop_perc)-TmDRTG))
  
x = DRTG(113.6,2.16,0)
print(x)
# test result: 134.08
# exel result: 134.1
# excel location: STAT ANALYSIS(I3)





def Game_Score(PTS,FGM,FGA,FTA,FTM,ORE,DREB,STL,AST,BLK,PF,TOV):
  return float(PTS+0.4*FGM-0.7*FGA-0.4 
  *(FTA-FTM)+0.7*ORE-0.3*DREB+STL 
  +0.7*AST+0.7*BLK-0.4*PF-TOV)
  
x = Game_Score(11.0,4.0,13.0,2.0,2.0,0.0,5.0,0.0,0.0,0.0,3.0,0.0)
print(x)
# test result: 0.7999
# exel result: ?????
# excel location: ?????

x = Game_Score(0.0,0.0,1.0,2.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0)
print(x)
# test result: -2.5
# exel result: ?????
# excel location: ?????




def AST_perc(AST,MIN,TmMIN,TmFGM,FGM):
  return float(100*AST/(((MIN/(TmMIN/5))*TmFGM)-FGM))
  
x = AST_perc(747.0,3026.0,19730.0,3311.0,857.0)
print(x)
# test result: 44.41
# NBA web result: 44.4
# excel location: cannot find in excel, used NBA data to test





def Total_REB_pect (TREB,TmMIN,MIN,TmTREB,OppTREB):
  return 100*(TREB*(TmMIN/5))/(MIN*(TmTREB+OppTREB))
  
x = Total_REB_pect(709.0,19730.0,3026.0, 3455.0,3578.0)
print(x)
# test result: 13.1
# NBA web result: 13.1
# excel location: cannot find in excel, used NBA data to test




def STL_perc(STL,TmMIN,MIN,OppPoss):
  return  float(100*(STL*(TmMIN/5))/(MIN*OppPoss))

x = STL_perc(116.0,19730.0,3026.0,8059.5)
print(x)
# test result: 1.876
# NBA web result: 1.9
# excel location: cannot find in excel, used NBA data to test




def BLK_perc(BLK,TmMIN,MIN,OppFGA,Opp3PA):
  return float(100*(BLK*(TmMIN/5))/(MIN*(OppFGA-Opp3PA)))

x = BLK_perc(71.0,19730.0,3026.0,7238.0,2596.0)
print(x)
# test result: 1.99
# NBA web result: 2.0
# excel location: cannot find in excel, used NBA data to test




















