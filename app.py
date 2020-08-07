import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import covid
from dash.dependencies import Input, Output
import dash_daq as daq



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "wide-form" data frame with no index
# see https://plotly.com/python/wide-form/ for more options

server = app.server # the Flask app

app.layout = html.Div(children=[
    html.H1(children='Coronavirus Network Analysis of US News'),
    # daq.Slider(
    #     min=0, max=100, value=30, step=1,
    #     marks={str(val): str(val) for val in range(0,101,10)},
    # ),
    dcc.Slider(
        id='slider_us',
        min=200,
        max=400,
        value=400,
        marks={str(val): str(val) for val in range(200,401,50)},
        step=50
    ),

    dcc.Graph(
        id='us',
        # figure=covid.network_graph("us")
    ),

    # html.Br(),
    # html.Br(),

    # html.H1(children='Coronavirus Network Analysis of Korean News'),

    # dcc.Slider(
    #     id='slider_kor',
    #     min=10,
    #     max=100,
    #     value=50,
    #     marks={str(val): str(val) for val in range(0,101,10)},
    #     step=1
    # ),

    # dcc.Graph(
    #     id='kor',
    #     # figure=covid.network_graph("us")
    # ),


    # dcc.Graph(
    #     id='kor',
    #     figure=covid.network_graph("kor")
    # )
])

@app.callback(
    Output('us', 'figure'),
    [Input('slider_us', 'value')])
def update_graph(slider_us):
    return covid.network_graph("us", slider_us)

# @app.callback(
#     Output('kor', 'figure'),
#     [Input('slider_kor', 'value')])
# def update_graph2(slider_kor):
#     return covid.network_graph("us", 10)
#     # return covid.network_graph("kor", slider_kor)


if __name__ == '__main__':
    app.run_server(debug=True)