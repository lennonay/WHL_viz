import pandas as pd

def group(data):
    data['games'] = 1
    data_group = data.groupby(['name','birthdate_year', 'position_str'])[['games','shots', 'goals', 'assists','points','5v5_G','5v5_A1','5v5_A2' ,'5v5primarypoints','plusminus', 'hits', 'pim', 'EV_G', 'EV_A1', 'EV_A2',
       'PP_G', 'PP_A1', 'PP_A2', 'SH_G', 'SH_A1', 'SH_A2', '5v5_GF', '5v5_GA',
        'EVprimarypoints', 'primarypoints']].sum().reset_index()
    
    data_group = data_group.rename(columns= {'5v5primarypoints':'5v5_PP','EVprimarypoints':'EV_PP','primarypoints':'PP'})
    data_group['5v5_GF%'] = (data_group['5v5_GF']/(data_group['5v5_GA']+data_group['5v5_GF']))
    data_group['5v5_GF%'] = data_group['5v5_GF%'].fillna(0.50)
    data_group['5v5_GF%'] = (data_group['5v5_GF%'] * 100).round(2)

    data_group.loc[data_group['position_str'] == 'LW','position_str'] = 'F'
    data_group.loc[data_group['position_str'] == 'RW','position_str'] = 'F'
    data_group.loc[data_group['position_str'] == 'C','position_str'] = 'F'

    data_group.loc[data_group['position_str'] == 'LD','position_str'] = 'D'
    data_group.loc[data_group['position_str'] == 'RD','position_str'] = 'D'   

    return data_group