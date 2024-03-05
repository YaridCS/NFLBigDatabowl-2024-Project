import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
def get_correlation():
    data = pd.read_csv('Final_Analysis.csv')
    data = data.loc[(data['Start_X'] <= 100)]
    data['YardsLeft'] = data['Final_X'] - data['BC_X']
    events = list(set(data.Ending_Event))
    events.remove('touchdown')
    new_data = data.loc[data.Ending_Event.isin(events)].copy()
    new_data['Immediate_Yards_Left'] = new_data['YardsLeft'].apply(lambda x: x if x <= 10 else 10)
    X = np.array(new_data['Danger']).reshape(-1,1)
    Y = np.array(new_data['Immediate_Yards_Left'])
    reg = LinearRegression().fit(X,Y)
    #print(reg.coef_)
    print('r-squared for comparing Frame-Danger to Trimmed Yards Left is {}'.format(reg.score(X,Y)))


    
    
    
