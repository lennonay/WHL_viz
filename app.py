import dash
from dash import html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from combine import group

raw = pd.read_csv('data/whl_game_stat.csv')
whl_stat = group(raw)


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
        dcc.Tab(label = 'Viz', children=[])
    ])

])

# Set up callbacks/backend
@app.callback(
    Output('total_cases', 'srcDoc'),
    #Input('xcol', 'value'),
    #Input('xslider', 'value'),
    #Input('hslider','value')   
)

def update_output(xcol,xslider,hslider):
    return plot_cases(xcol,xslider,hslider)

if __name__ == '__main__':
    app.run_server(debug=True)