import pandas as pd

def group(data):
    data['game'] = 1
    data_group = data.groupby(['name','birthdate_year', 'position_str'])['game','shots','shots_on', 'goals', 'assists', 'plusminus', 'hits', 'pim', 'EV_G', 'EV_A1', 'EV_A2',
       'PP_G', 'PP_A1', 'PP_A2', 'SH_G', 'SH_A1', 'SH_A2', '5v5_GF', '5v5_GA',
        'EVprimarypoints', 'primarypoints'].sum().reset_index()
    
    data_group['5v5_GF%'] = (data_group['5v5_GF']/(data_group['5v5_GA']+data_group['5v5_GF']))
    data_group['5v5_GF%'] = data_group['5v5_GF%'].fillna(0.50)
    data_group['5v5_GF%'] = (data_group['5v5_GF%'] * 100).round(2)

    return data_group