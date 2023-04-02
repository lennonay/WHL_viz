import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from combine import group
import numpy as np
from PIL import Image
import requests

league_url = 'https://raw.githubusercontent.com/lennonay/WHL_Scraper/main/data/league_info.csv'
league_info = pd.read_csv(league_url)

#read data from github
url = 'https://raw.githubusercontent.com/lennonay/WHL_Scraper/main/data/WHL_2022_23_Regular_Season.csv'
raw = pd.read_csv(url)

#data transformation
game_stat = group(raw)
game_stat = game_stat.rename(columns= {'birthdate_year':'YOB', 'position_str':'POS','plusminus':'+/-'})
game_stat = game_stat.sort_values('points', ascending=False)

#get values for slider and dropdown
games_max = game_stat['games'].max()
name_lst = list(game_stat['name'].unique())
name_lst.insert(0,'All')
year_lst = np.sort(game_stat['YOB'].unique())
pos_lst = np.sort(game_stat['POS'].unique())
col_lst = list(game_stat.columns)
remove = ['name','birthdate_year', 'position_str']
col_lst = list(set(col_lst) - set(remove))

#WHL logo image
image_path = 'image/Western_Hockey_League.png'
pil_image = Image.open(image_path)

bchl_image = 'image/BCHL_Logo.png'
bchl_image = Image.open(bchl_image)

#Get data last updated date
url = 'https://raw.githubusercontent.com/lennonay/WHL_prospect_stat/main/data/update.txt'
response = requests.get(url)
update_text = response.text
last_update = update_text[-25:-1]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    dbc.Col([html.Img(src=pil_image, style ={'width': '100px','display': 'inline-block',}),
             html.Img(src=bchl_image, style ={'width': '100px','display': 'inline-block',}),
             html.H1(' Prospect Stat Dashboard', style={'display': 'inline-block','text-align': 'center','font-size': '48px',"margin-left": "20px"}),
    ],style={
                    'backgroundColor': 'black',
                    'padding': 20,
                    'color': 'white',
                    'margin-top': 20,
                    'margin-bottom': 20,
                    'text-align': 'center',
                    'border-radius': 3}),
    dcc.Store(id = 'data-output'),
    dbc.Col([html.H1('Data ' +  last_update, style = {'font-size': '15px'}),
            dcc.Dropdown(id = 'league', value = league_info.iloc[0]['name'], options = league_info['name'].unique()) ]),
    dcc.Tabs([
        dcc.Tab(label = 'Table', children = [
        dbc.Row([
            dbc.Col(dash_table.DataTable(
            id='table',
            columns=[{'name': i, 'id': i} for i in game_stat.columns],
            sort_action="native",
            filter_action="native",
        )
                
    )])]),
        dcc.Tab(label = 'Viz', children=[
            dbc.Row([dbc.Col([
                'Name',
                dcc.Dropdown(id = 'name',value = 'All', options=[{'label': i, 'value': i} for i in name_lst]),
                'Games Played',
                dcc.RangeSlider(
                    id='range_slider',
                    min=0, max=games_max,value = [0,games_max]),
                'Birth Year',
            dcc.Checklist(
                id = 'birthyear_check', options= year_lst,  value = year_lst, inputStyle={"margin-right": "5px", "margin-left":"20px"}),
                'Position',
                dcc.Checklist(id = 'position', options = pos_lst, value = pos_lst,inputStyle={"margin-right": "5px", "margin-left":"20px"})
            ],md=3,style={
                'background-color': '#e6e6e6',
                'padding': 15,
                'border-radius': 3}),
            dbc.Col([
                'Select Columns:',
                dbc.Col([
                dcc.Dropdown(id = 'x_axis', value ='5v5 Goals For %', options = [{'label': i, 'value': i} for i in col_lst]),
                dcc.Dropdown(id = 'y_axis', value ='5v5 Primary Points', options = [{'label': i, 'value': i} for i in col_lst])
                ]),
                dcc.Graph(id = 'scatter_plot',style={'width': '900px', 'height': '700px'})])])
        ])
    ])

])

# Set up callbacks/backend
@app.callback(
        Output('data-output','data'),
        Input('league', 'value')
)
def league_selected(league):
    url = 'https://raw.githubusercontent.com/lennonay/WHL_Scraper/main/data/{}.csv'.format(league)
    raw = pd.read_csv(url)

    game_stat = group(raw)
    team = raw.groupby('name')['team_name'].max().reset_index()
    #game_stat = pd.merge(game_stat, team, on = 'name')
    game_stat = game_stat.rename(columns= {'birthdate_year':'YOB', 'position_str':'POS','plusminus':'+/-'})
    game_stat = game_stat.sort_values('points', ascending=False)

    return game_stat.to_dict('records')

@app.callback(
        [Output('table','data'),Output('table','columns')],
        Input('data-output','data')
)
def table(data):
    df = pd.DataFrame(data)
    return (data, [{'name': i, 'id': i} for i in df.columns])

@app.callback(
        [Output('name',"options"),Output('name','value')],
        Input('data-output','data')
)
def update_dropdown(data):
    df = pd.DataFrame(data)
    name_lst = list(df['name'].unique())
    name_lst.insert(0,'All')
    return (
        [{"label": i, "value": i} for i in name_lst],'All'
    )

@app.callback(
        [Output('x_axis',"options"),Output('x_axis','value')],
        Input('data-output','data'),
        Input('league', 'value')
)
def update_xaxis(data,league):
    df = pd.DataFrame(data)
    col_lst = list(df.columns)
    remove = ['name','birthdate_year', 'position_str']
    col_lst = list(set(col_lst) - set(remove))
    if league_info[league_info['name'] == league]['league'].item()  !='bchl':
        select = '5v5 Goals For %'
    else: select = 'games'
    return (
        [{"label": i, "value": i} for i in col_lst],select
    )

@app.callback(
        [Output('y_axis',"options"),Output('y_axis','value')],
        Input('data-output','data'),
        Input('league', 'value')
)
def update_yaxis(data,league):
    df = pd.DataFrame(data)
    col_lst = list(df.columns)
    remove = ['name','birthdate_year', 'position_str']
    col_lst = list(set(col_lst) - set(remove))
    if league_info[league_info['name'] == league]['league'].item() !='bchl':
        select = '5v5 Primary Points'
    else: select = 'points'
    return (
        [{"label": i, "value": i} for i in col_lst],select
    )

@app.callback(
        [Output('range_slider', 'max'), Output('range_slider', 'value')],
        Input('data-output','data')
)
def update_slider(data):
    df = pd.DataFrame(data)
    games_max = df['games'].max()
    return (games_max, [0, games_max])

@app.callback(
        [Output('birthyear_check', 'options'), Output('birthyear_check', 'value')],
        Input('data-output','data')
)
def update_birthyear(data):
    df = pd.DataFrame(data)
    year_lst = np.sort(df['YOB'].unique())
    return(year_lst, year_lst)

@app.callback(
        [Output('position', 'options'), Output('position', 'value')],
        Input('data-output','data')
)
def update_position(data):
    df = pd.DataFrame(data)
    pos_lst = np.sort(df['POS'].unique())
    return(pos_lst, pos_lst)



@app.callback(
    Output('scatter_plot', 'figure'),
    Input('name', 'value'),
    Input('range_slider', 'value'),
    Input('birthyear_check', 'value'),
    Input('position','value'),
    Input('data-output', 'data'),
    Input('x_axis','value'),
    Input('y_axis', 'value')
)
def update_output(name, slider_range, birthyear_check, position,data, x_axis, y_axis):

    game_stat = pd.DataFrame(data)

    max_y_axis = game_stat[y_axis].max()
    max_x_axis = game_stat[x_axis].max()
    low, high = slider_range
    mask = (game_stat['games'] >= low) & (game_stat['games'] <= high)
    game_stat = game_stat[mask]
    
    game_stat = game_stat[game_stat['YOB'].isin(birthyear_check)]
    game_stat = game_stat[game_stat['POS'].isin(position)]
    
    fig = px.scatter(game_stat, x = x_axis, y = y_axis,
                     #labels = {x_axis: '5v5 Goals For %', y_axis: '5v5 Primary Points'},
                      hover_name= 'name', title = x_axis + ' and ' + y_axis)
    fig.update_yaxes(range = [-5,max_y_axis+10])
    fig.update_xaxes(range=[-5, max_x_axis+5])
    if len(game_stat) == 0:
        x = 0
        y = 0
    else: 
        x = game_stat[x_axis].mean()
        y = game_stat[y_axis].mean()
    fig.add_hline(y = y, line_color = 'grey', annotation_text = 'average')
    fig.add_vline(x = x, line_color = 'grey', annotation_text = 'average',annotation_position="top left")
    fig.add_vline(x=50, line_color = 'grey',line_dash = 'dash', annotation_text = '50%')
    if name !='All':

        fig.add_traces(
            px.scatter( game_stat[game_stat['name'] == name], x=x_axis, y=y_axis,
                       hover_name= 'name').update_traces(
            marker_size=15, marker_color="red",showlegend = False).data,
        )

    fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Rockwell"
    ))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)