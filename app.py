import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from combine import group
import numpy as np

raw = pd.read_csv('data/whl_game_stat.csv')
whl_stat = group(raw)
games_max = whl_stat['games'].max()
year_lst = np.sort(whl_stat['birthdate_year'].unique())

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

app.layout = dbc.Container([
    html.H1('WHL Player Stat Dashboard',style={
                    'backgroundColor': 'steelblue',
                    'padding': 20,
                    'color': 'white',
                    'margin-top': 20,
                    'margin-bottom': 20,
                    'text-align': 'center',
                    'font-size': '48px',
                    'border-radius': 3}),
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
            dcc.Graph(id = 'scatter_plot',style={'border-width': '0', 'width': '800px', 'height': '700px','margin':'auto'}),
            'Games Played',
            dcc.RangeSlider(
                id='range_slider',
                min=0, max=games_max,value = [15,games_max-5]),
            'Birth Year',
            dcc.Checklist(
                id = 'birthyear_check', options= year_lst,  value = year_lst, inputStyle={"margin-right": "5px", "margin-left":"20px"}
            )
        ])
    ])

])

# Set up callbacks/backend
@app.callback(
    Output('scatter_plot', 'figure'),
    Input('range_slider', 'value'),
    Input('birthyear_check', 'value'),
    #Input('hslider','value')   
)
def update_output(slider_range, birthyear_check):
    whl_stat = group(raw)
    team = raw.groupby('name')['team_name'].max().reset_index()
    whl_stat = pd.merge(whl_stat, team, on = 'name')
    
    low, high = slider_range
    mask = (whl_stat['games'] >= low) & (whl_stat['games'] <= high)
    whl_stat = whl_stat[mask]
    
    whl_stat = whl_stat[whl_stat['birthdate_year'].isin(birthyear_check)]
    
    fig = px.scatter(whl_stat, x = '5v5_GF%', y = 'EVprimarypoints',
                     color = 'team_name', hover_data= ['name'], title = '5v5 GF% and Even Strength Primary Points')
    fig.update_xaxes(range=[0, 100]) 
    fig.add_hline(y=whl_stat['EVprimarypoints'].mean(), line_color = 'grey')
    fig.add_vline(x=whl_stat['5v5_GF%'].mean(), line_color = 'grey')   
    #fig.update_layout(height = 700, width = 800)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)