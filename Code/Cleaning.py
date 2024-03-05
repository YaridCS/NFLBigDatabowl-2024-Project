import pandas as pd
def reverse_deg(deg):
    if deg < 180:
        return deg + 180
    if deg >= 180:
        return deg - 180

def switch(f):
    if f == 'left':
        return 'right'
    if f == 'right':
        return 'left'
        
    
def reverse_play_direction(df: pd.DataFrame):
        result_df = df.copy(deep=True)
        
        result_df["o"] = result_df["o"].apply(reverse_deg)
        
        result_df["dir"] = result_df["dir"].apply(reverse_deg)
        
        result_df["x"] = result_df["x"].apply(lambda x: 120 - x)
        
        result_df["y"] = result_df["y"].apply(lambda y: 160/3 - y)

        result_df["playDirection"] = result_df['playDirection'].apply(switch)

        return result_df


def clean():      
    plays = pd.read_csv('Data/plays.csv')
    games = pd.read_csv('Data/games.csv')
    plays = plays.merge(games[['gameId','homeTeamAbbr','visitorTeamAbbr']], how = 'left', on='gameId')
    players = pd.read_csv('Data/players.csv')[['nflId','position']]
    for i in range(1,10):
        print(i)
        df = pd.read_csv('Data/tracking_week_{}.csv'.format(i))
        df = df.loc[df.displayName != 'football']
        df = df.merge(players, how = 'left', on = 'nflId') ##Identify player positions. 
        #We don't want to count QBs as offensive players unless they have the ball
        ###This is because they're largely bystanders.
        ####The Above Code gathers all the data into a single file
        ###Next We will Clean the data to only go until an ending event is found.
        ###We Will also remove all plays with penalties
        ###Then we will identify the ball carrier
        ###We also remove the football
        ###Then we will get yards_to_go using
        df['gameplayId'] = df.playId + df.gameId*100000
        plays['gameplayId'] = plays.playId + plays.gameId*100000  ##Matching up plays and games.
        to_merge = list(plays.columns)
        to_merge.remove('playId')
        to_merge.remove('gameId')
        og = df.copy()
        df = df.merge(plays[to_merge], how='left', on='gameplayId')
        
        df = df.loc[df.playNullifiedByPenalty == 'N'] ##Remove penalties
        df = df.loc[(df.frameId > 5) | (df.passResult.isin(['C','R']))] #If the pass result is a completion or a scramble, include whole play
        #If not, start on ball snap              
        #Now we eliminate all frames after the play is over
        ####Get rid of excess datapoints first
        df = df[['gameId','playId','nflId','displayName','ballCarrierId','frameId','club','playDirection','x','y','s','a',
                 'dis','o','dir','event','possessionTeam','defensiveTeam','position']]
        endings = df.loc[(df.event.isin(['qb_slide','touchdown','out_of_bounds','tackle','safety','fumble', 'pass_outcome_touchdown']))]
        end_games = list(set(endings.gameId))
        for game in end_games:
            big_current = endings.loc[(endings.gameId == game)]
            end_plays = list(set(big_current.playId))
            print(game)
            for play in end_plays:
                current = big_current.loc[(big_current.playId == play)]
                frame = list(set(current.frameId))[0]
                df = df.loc[(df.playId != play) | (df.gameId != game) | (df.frameId <= frame)]
        df['Offensive'] = (df.possessionTeam == df.club)
        ###Now we just need to correct play direction
        ###Code from big data bowl discussion fourms
        left = df[df.playDirection == 'left']
        right = df[df.playDirection == 'right']
        fixed = reverse_play_direction(left)
        df = pd.concat([fixed ,right])
        df = df.sort_values(by=['gameId','playId'])
        df = df.reset_index()
        df['Ball Carrier'] = df['nflId'] == df['ballCarrierId'] ##Identifying Ball Carrer
        df.to_csv('Data/Final_Cleaned_{}.csv'.format(i), index = False)
