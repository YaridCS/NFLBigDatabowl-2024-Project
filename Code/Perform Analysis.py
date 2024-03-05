import pandas as pd
import Circle_Interaction as circles
def square(x):
    return x*x

def add(x):
    return x+x

def analyze():
    play_desc = pd.read_csv('Data/plays.csv')[['playId','gameId','expectedPointsAdded','passResult','penaltyYards','playResult','possessionTeam','defensiveTeam']]
    print('done')
    functions = [circles.interpret_play]
    results = [[]]
    WEEK = []
    GAME = []
    PLAY = []
    RESULT = []
    ENDING_EVENT = []
    EVENT = []
    EPA = []
    YARDS = []
    NEAR_SIDELINE = []
    FINAL_X = []
    FINAL_Y = []
    FRAMES_REMAINING= []
    BC_X = []
    BC_Y = []
    START_X = []
    START_Y = []
    FINAL_X = []
    FINAL_Y = []
    FC_HIT = []
    POSESSION_TEAM = []
    DEFENSIVE_TEAM = []
    FINAL_DANGERS = []
    slices = dict()
    for i in range(36):
        slices[i] = []
    for week in range(1,10):
        current_week = pd.read_csv('Data/Final_Cleaned_{}.csv'.format(week))
        games = list(set(current_week.gameId))
        for game in games:
            current_game = current_week.loc[(current_week['gameId'] == game)]
            plays = list(set(current_game.playId))
            for play in plays:
                current_play = current_game.loc[(current_game['playId'] == play)]
                line = play_desc.loc[(play_desc['playId'] == play) & (play_desc['gameId'] == game)]
                E = list(line.expectedPointsAdded)[0]
                offensive_team = list(line.possessionTeam)[0]
                defensive_team = list(line.defensiveTeam)[0]
                R = list(line.passResult)[0]
                if type(R) == float:
                    R = 'DR'
                Y = list(line.playResult)[0]
                event_list = list(current_play.event)
                event = event_list[len(current_play.event)-1]
                for i in range(len(functions)):
                    print(week, game , play, i)
                    function = functions[i]
                    circle = function(game, play, df = current_week)
                    data = circles.Get_Dangers_And_Centers(circle)
                    final_dangers = circles.Get_Dangers(circle)[1]
                    slicewise_dangers = circles.Get_Dangers(circle)[0]
                    centers = data[1]
                    final = centers[-1]
                    start = centers[0]
                    answer = circles.get_rem_frames_list(data[0],data[1], 36)
                    FC_HIT_LEVER = False
                    for j in range(len(answer[0])):
                        if i == 0:
                            WEEK.append(week)
                            GAME.append(game)
                            PLAY.append(play)
                            EPA.append(E)
                            RESULT.append(R)
                            YARDS.append(Y)
                            ENDING_EVENT.append(event)
                            current_event = event_list[j]
                            if current_event == 'first_contact':
                                FC_HIT_LEVER = True
                            FC_HIT.append(FC_HIT_LEVER)
                            EVENT.append(current_event)
                            FRAMES_REMAINING.append(answer[1][j])
                            BC_X.append(centers[j][0])
                            BC_Y.append(centers[j][1])
                            POSESSION_TEAM.append(offensive_team)
                            DEFENSIVE_TEAM.append(defensive_team)
                            START_X.append(start[0])
                            START_Y.append(start[1])
                            FINAL_X.append(final[0])
                            FINAL_DANGERS.append(final_dangers[j])
                            FINAL_Y.append(final[1])
                        for key in slicewise_dangers:
                            slices[key].append(slicewise_dangers[key][j])
                        results[i].append(answer[0][j])
                        
    datadict = dict()
    for key in slices:
        datadict['Slice_{}'.format(key)] = slices[key]
    datadict['Week'] = WEEK
    datadict['Game'] = GAME
    datadict['Play'] = PLAY
    datadict['Entered_Slice_Danger'] = results[0]
    datadict['Frames_Remaining'] = FRAMES_REMAINING
    datadict['EPA'] = EPA
    datadict['Result'] = RESULT
    datadict['Yards'] = YARDS
    datadict['Ending_Event'] = ENDING_EVENT
    datadict['BC_X'] = BC_X
    datadict['BC_Y'] = BC_Y
    datadict['Final_X'] = FINAL_X
    datadict['Final_Y'] = FINAL_Y
    datadict['Start_X'] = START_X
    datadict['Start_Y'] = START_Y
    datadict['Event'] = EVENT
    datadict['First Contact?'] = FC_HIT
    datadict['Posession Team'] = POSESSION_TEAM
    datadict['Defensive Team'] = DEFENSIVE_TEAM
    datadict['Danger'] = FINAL_DANGERS
    df = pd.DataFrame(datadict)
    df.to_csv('Final_Analysis.csv', index = False)
                    


    
