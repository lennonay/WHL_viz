import dash
from dash import html, dcc, Input, Output
import altair as alt
import dash_bootstrap_components as dbc
import pandas as pd

alt.data_transformers.enable('data_server')


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([])

# Set up callbacks/backend
@app.callback(
    Output('total_cases', 'srcDoc'),
    Output('total_vaccinations', 'srcDoc'),
    Input('xcol', 'value'),
    Input('xslider', 'value'),
    Input('hslider','value')
)

def update_output(xcol,xslider,hslider):
    return plot_cases(xcol,xslider,hslider), plot_vaccinations(xcol,xslider,hslider)

if __name__ == '__main__':
    app.run_server(debug=True)