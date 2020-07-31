import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import covid


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "wide-form" data frame with no index
# see https://plotly.com/python/wide-form/ for more options

server = app.server # the Flask app

app.layout = html.Div(children=[
    html.H1(children='Coronavirus Network Analysis of US News'),

    dcc.Graph(
        id='us',
        figure=covid.network_graph("us")
    ),

    html.H1(children='Coronavirus Network Analysis of Korean News'),

    dcc.Graph(
        id='kor',
        figure=covid.network_graph("kor")
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)