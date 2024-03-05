import Sidelining_Standard_Circles as standard_circles
import pandas as pd
endings = ['qb_slide','touchdown','out_of_bounds','tackle','safety']

def get_play(df, gameID, playID):
    return df.loc[(df['gameId'] == gameID) & (df['playId'] == playID)]


def get_frame(df, frame):
    return df.loc[(df['frameId'] == frame)]

def get_players(df, gameID, playID, frame):
    play = get_frame(get_play(df, gameID, playID), frame)
    return play

def get_player_on_play(df, gameID, playID, nflID):
    return df.loc[(df['gameId'] == gameID) & (df['playId'] == playID) & (df['nflId'] == nflID)]

def get_bc_locs(df, gameId, playId):
    return df.loc[(df['gameId'] == gameId) & (df['playId'] == playId) & (df['Ball Carrier'] == 1)]
    
    

def frame_to_circle(df, gameID, playID, frame):
    play = get_players(df, gameID, playID, frame)
    offensive = []
    defensive = []
    for item in list(play.index):
        c == df.loc()[item]

def get_frames(df):
    return list(set(df.frameId))

def get_cropped_play(df, gameID, playId):
    play = get_play(df, gameID, playId)
    frames = play.loc[play['event'].isin(['qb_slide','touchdown','out_of_bounds','tackle','safety','fumble', 'pass_outcome_touchdown'])]
    frame = list(set(frames['frameId']))
    if len(frame) == 0:
        return False
    else:
        frame.sort()
        ending = frame[0]
    answer = play.loc[(play['frameId'] <= ending)]
    return answer

def get_play_items(df):
    frames = get_frames(df)
    oracle = dict()
    for frame in frames:
        curr = get_frame(df, frame)
        Offensive = []
        Defensive = []
        for index in curr.index:
            player = curr.loc()[index]
            if player['Ball Carrier'] == 0:
                ID = player.nflId
                team = player.club
                x = player.x
                y = player.y
                name = player.displayName
                if player['Offensive'] == 1:
                    ###Offensive Player
                    p = circles.Offensive_Player(ID, 0, 0, 'HB', x, y, team, name)
                    Offensive.append(p)
                elif player['Offensive'] == 0:
                    p = circles.Defensive_Player(ID, 0, 0, 'LB', x, y, team, name)
                    Defensive.append(p)
            elif player['Ball Carrier'] == 1:
                BC_Coords = [player.x, player.y]
        oracle[frame] = [BC_Coords, Offensive, Defensive]
    return oracle

def chart_play(df, gameID, playID, radius = 10, slices = 4, rotations = 4):
    play = get_play(df, gameID, playID)
    frames = get_play_items(play)
    pictures = []
    i = 0
    for frame in frames:
        o = frames[frame][1]
        d = frames[frame][2]
        center_coords = frames[frame][0]
        curr = circles.make_big_circ(offensive = o, defensive = d, radius = radius, startx = 0, starty = 0,
                  slices = slices, rotations = rotations,start_angle = 0, center_x = center_coords[0], center_y = center_coords[1])
        photo = curr.plot_circle(alpha = 2, show_line = False, show = False)
        photo.savefig('Slides2/{}_{}_Frame{}.jpg'.format(gameID,playID,i))
        i += 1
        pictures.append(photo)


###These might start getting a little tricky

###Each of these will return the respective circle object
###Use that circle object in the functions below

def interpret_play(game, play, df = False, week = False, slices = 6, rotations = 6):
    if df is False and week == False:
        print('Specify a week or pass in a pre-trimmed frame')
        return False
    elif df is False:
        df = pd.read_csv('Data/Final_Cleaned_{}.csv'.format(week))
    df = get_play(df, game, play)
    circle = standard_circles.play_circle(df, slices = slices, rotations = rotations)
    return circle

####The Functions you're familiar with. They input a circle object, rather than a week, play, gameid, etc.

def Get_Dangers(circle, weights = False):
    'Input a created circle, and this will return a dictionary of slices, where the ith index is the danger of that slice at frame i'
    'The second item returned is the weighted dangers. This is NOT what is shown when you plot the circle. That total danger is unweighted for now'
    'Once we find ideal weights, we can hardcode them.'
    dictionary = dict()
    num_slices = circle.slices*circle.rotations
    if weights == False:
        weights = [1 for i in range(num_slices)]
    for i in range(num_slices):
        dictionary[i] = []
    frames = circle.circles
    num_frames = len(frames)
    for frame in frames:
        slices = frame.Slice
        for i in range(num_slices):
            dictionary[i].append(slices[i].danger)
    lst = []
    for i in range(num_frames):
        lst.append(0)
        for SLICE in dictionary:
            lst[i] += dictionary[SLICE][i]*weights[SLICE]
        lst[i] = lst[i]/num_slices
    return(dictionary, lst)

def Get_Dangers_And_Centers(circle):
    danger = Get_Dangers(circle)[0]
    centers = []
    for C in circle.circles:
        centers.append([C.center_x, C.center_y])
    return(danger, centers)

def Scatterplot_Dangers(circle):
    circle.scatter_plot()

def plot_frame(circle, frame, alpha = 1, show_d = False, show_line = True, show_coords = False, show = True):
    circle.circles[frame].plot_circle(alpha, show_d, show_line, show_coords, show)

def animate_play(circle, alpha = 2, show_d = False, show_line = False, show_coords = False,
                 show = True, saveframes = False, savegif = False, floc = False, gloc = False):
    circle.plot_play(alpha, show_d, show_line, show_coords, show,
                     saveframes, savegif, floc, gloc)


def get_effective_danger(dangers, centers, num_slices):
    cumulative = 0
    for i in range(len(centers)-1):
        first_coords = centers[i]
        second_coords = centers[i+1]
        third_coords = [first_coords[0]+10, first_coords[0]]
        angle = standard_circles.getAngle(third_coords,first_coords,second_coords)
        angle = standard_circles.normalize_angle(angle)
        slice_loc = standard_circles.get_slice_loc(angle, num_slices)
        #print(cumulative, third_coords, first_coords, second_coords, angle, slice_loc)
        cumulative += dangers[slice_loc][i]
    return cumulative/(len(centers)-1)

def get_rem_frames_list(dangers, centers, num_slices):
    cumulative = []
    for i in range(len(centers)-1):
        first_coords = centers[i]
        second_coords = centers[i+1]
        third_coords = [first_coords[0]+10, first_coords[0]]
        angle = standard_circles.getAngle(third_coords,first_coords,second_coords)
        angle = standard_circles.normalize_angle(angle)
        slice_loc = standard_circles.get_slice_loc(angle, num_slices)
        #print(cumulative, third_coords, first_coords, second_coords, angle, slice_loc)
        cumulative.append(dangers[slice_loc][i])
    return cumulative, [i for i in range(len(cumulative)-1,-1,-1)] 
