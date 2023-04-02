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
whl_stat = group(raw)
whl_stat = whl_stat.rename(columns= {'birthdate_year':'YOB', 'position_str':'POS','plusminus':'+/-'})
whl_stat = whl_stat.sort_values('points', ascending=False)

#get values for slider and dropdown
games_max = whl_stat['games'].max()
name_lst = list(whl_stat['name'].unique())
name_lst.insert(0,'All')
year_lst = np.sort(whl_stat['YOB'].unique())
pos_lst = np.sort(whl_stat['POS'].unique())

#WHL logo image
image_path = 'image/Western_Hockey_League.png'
pil_image = Image.open(image_path)

#Get data last updated date
url = 'https://raw.githubusercontent.com/lennonay/WHL_prospect_stat/main/data/update.txt'
response = requests.get(url)
update_text = response.text
last_update = update_text[-25:-1]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    dbc.Col([html.Img(src=pil_image, style ={'width': '100px','display': 'inline-block',},),
             html.H1(' WHL Player Stat Dashboard', style={'display': 'inline-block','text-align': 'center','font-size': '48px',"margin-left": "20px"}),
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
            columns=[{'name': i, 'id': i} for i in whl_stat.columns]
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
            dbc.Col(dcc.Graph(id = 'scatter_plot',style={'width': '900px', 'height': '700px'}))])
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

    whl_stat = group(raw)
    team = raw.groupby('name')['team_name'].max().reset_index()
    #whl_stat = pd.merge(whl_stat, team, on = 'name')
    whl_stat = whl_stat.rename(columns= {'birthdate_year':'YOB', 'position_str':'POS','plusminus':'+/-'})
    whl_stat = whl_stat.sort_values('points', ascending=False)

    return whl_stat.to_dict('records')

@app.callback(
        Output('table','data'),
        Input('data-output','data')
)
def table(data):
    return data

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
    Input('data-output', 'data')
)
def update_output(name, slider_range, birthyear_check, position,data):

    whl_stat = pd.DataFrame(data)

    max_5v5_pp = whl_stat['5v5_PP'].max()
    low, high = slider_range
    mask = (whl_stat['games'] >= low) & (whl_stat['games'] <= high)
    whl_stat = whl_stat[mask]
    
    whl_stat = whl_stat[whl_stat['YOB'].isin(birthyear_check)]
    whl_stat = whl_stat[whl_stat['POS'].isin(position)]
    
    fig = px.scatter(whl_stat, x = '5v5_GF%', y = '5v5_PP',
                     labels = {'5v5_GF%': '5v5 Goals For %', '5v5_PP': '5v5 Primary Points'},
                      hover_name= 'name', title = '5v5 GF% and Primary Points')
    fig.update_yaxes(range = [-5,max_5v5_pp+10])
    fig.update_xaxes(range=[-5, 100])
    fig.add_hline(y=whl_stat['5v5_PP'].mean(), line_color = 'grey', annotation_text = 'average')
    fig.add_vline(x=whl_stat['5v5_GF%'].mean(), line_color = 'grey', annotation_text = 'average',annotation_position="top left")
    fig.add_vline(x=50, line_color = 'grey',line_dash = 'dash', annotation_text = '50%')
    if name !='All':

        fig.add_traces(
            px.scatter( whl_stat[whl_stat['name'] == name], x="5v5_GF%", y="5v5_PP",
                       labels = {'5v5_GF%': '5v5 Goals For %', '5v5_PP': '5v5 Primary Points'},
                       hover_name= 'name').update_traces(
            marker_size=20, marker_color="red",showlegend = False).data,
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