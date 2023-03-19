import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from combine import group
import numpy as np
from PIL import Image
from datetime import datetime

raw = pd.read_csv('data/whl_game_stat.csv')
whl_stat = group(raw)
whl_stat = whl_stat.rename(columns= {'birthdate_year':'YOB', 'position_str':'POS','plusminus':'+/-'})

games_max = whl_stat['games'].max()
name_lst = list(whl_stat['name'].unique())
name_lst.insert(0,'All')
year_lst = np.sort(whl_stat['YOB'].unique())
pos_lst = np.sort(whl_stat['POS'].unique())

image_path = 'image/Western_Hockey_League.png'
pil_image = Image.open(image_path)

today = datetime.today().strftime('%Y-%m-%d')

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
    html.H1('Data last updated: 2023-03-14' , style = {'font-size': '15px'}),
    dcc.Tabs([
        dcc.Tab(label = 'Table', children = [
        dbc.Row([
            dbc.Col(
                dash_table.DataTable(
                    id = 'table',
                    columns = [{"name": col, "id": col} for col in whl_stat.columns],
                    data = whl_stat.to_dict('records'),
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
                    min=0, max=games_max,value = [15,games_max-5]),
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
    Output('scatter_plot', 'figure'),
    Input('name', 'value'),
    Input('range_slider', 'value'),
    Input('birthyear_check', 'value'),
    Input('position','value')   
)
def update_output(name, slider_range, birthyear_check, position):
    whl_stat = group(raw)
    team = raw.groupby('name')['team_name'].max().reset_index()
    whl_stat_orig = pd.merge(whl_stat, team, on = 'name')
    max_5v5_pp = whl_stat_orig['5v5_PP'].max()
    low, high = slider_range
    mask = (whl_stat['games'] >= low) & (whl_stat['games'] <= high)
    whl_stat = whl_stat[mask]
    
    whl_stat = whl_stat[whl_stat['birthdate_year'].isin(birthyear_check)]

    whl_stat = whl_stat[whl_stat['position_str'].isin(position)]
    
    fig = px.scatter(whl_stat, x = '5v5_GF%', y = '5v5_PP',
                     labels = {'5v5_GF%': '5v5 Goals For %', '5v5_PP': '5v5 Primary Points'},
                      hover_name= 'name', title = '5v5 GF% and Primary Points')
    fig.update_yaxes(range = [-5,max_5v5_pp+10])
    fig.update_xaxes(range=[-5, 100])
    fig.add_hline(y=whl_stat['5v5_PP'].mean(), line_color = 'grey', annotation_text = 'average')
    fig.add_vline(x=whl_stat['5v5_GF%'].mean(), line_color = 'grey', annotation_text = 'average',annotation_position="top left")
    fig.add_vline(x=50, line_color = 'grey',line_dash = 'dash', annotation_text = '50%')
    fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Rockwell"
    ))
    if name !='all':
        fig.add_traces(px.scatter(whl_stat[whl_stat['name'] == name], x="5v5_GF%", y="5v5_PP").update_traces(marker_size=15, marker_color="red").data)
    
    #fig.update_layout(height = 700, width = 800)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)