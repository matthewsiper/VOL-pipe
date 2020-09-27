import datetime as dt
import pandas as pd
import math

from handlers.surface_worker import SurfaceWorker
from adapters.mongo_adapter import MongoAdapter
from constants import dash_tickers
from utils.helpers import get_data_for_graph

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

surf_worker = SurfaceWorker()
MONGO_ADAPTER = MongoAdapter()

tickers = dash_tickers
tickers = [{"label": t, "value": t} for t in tickers]

global REPLAY_IDX
global REPLAY_RECORDS

REPLAY_IDX = -1

REPLAY_RECORDS = MONGO_ADAPTER.get_docs_by_match("main_db", "surfaces", match_dict={"symbol": tickers[0]["value"]},
                                                 greedy=True)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Div([
        dcc.Store(
            id='replay_idx',
            storage_type='session',
        )
    ]),
    html.Div([
        html.Label('Select ticker:'),
        dcc.Dropdown(id='ticker_dropdown',
                     options=tickers,
                     value=tickers[0]["value"]
                     )
        ],
        style={"width": "20"}),
    html.Div([
                html.Label('Graph Mode:'),
                dcc.RadioItems(
                    id='mode_selector',
                    options=[
                        {'label': 'live', 'value': 'live'},
                        {'label': 'replay', 'value': 'replay'},
                    ],
                    value='replay',
                    labelStyle={'display': 'inline-block'},
                )
            ]
    ),
    html.Div([
                html.Label('Option Type:'),
                dcc.RadioItems(
                    id='option_selector',
                    options=[
                        {'label': 'calls', 'value': 'calls'},
                        {'label': 'puts', 'value': 'puts'},
                    ],
                    value='calls',
                    labelStyle={'display': 'inline-block'},
                ),
            ],
    ),
    html.Div([
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1000,
            n_intervals=0
        )]
    )
        ]
)


@app.callback(output=Output('replay_idx', 'data'), inputs=[Input('ticker_dropdown', 'value')])
def update_replay_idx(ticker):
    global REPLAY_IDX
    REPLAY_IDX = -1
    return REPLAY_IDX


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('ticker_dropdown', 'value'),
               Input('mode_selector', 'value'),
               Input('option_selector', 'value')])
def update_graph_live(n, ticker, mode, option_type):
    if mode == 'live':
        raw_data = surf_worker.get_opt_data(ticker=ticker)
    else:
        global REPLAY_IDX
        REPLAY_IDX += 1
        REPLAY_RECORDS = MONGO_ADAPTER.get_docs_by_match("main_db", "surfaces", match_dict={"symbol": ticker}, greedy=True)
        if REPLAY_IDX >= len(REPLAY_RECORDS) - 1:
            REPLAY_IDX = 0
        raw_data = REPLAY_RECORDS[REPLAY_IDX]

    data = get_data_for_graph(raw_data, option_type=option_type)

    df = pd.DataFrame([data['strikes'], data['expiries'], data['ivs']]).T

    trace1 = {
        "type": "mesh3d",
        'x': [math.log10(v) for v in df[0].values],
        'y': [i/100.0 for i in range(len(df[1].values))],
        'z': df[2],
        'intensity': df[2],
        'autocolorscale': False,
        "colorscale": [
            [0, "rgb(244,236,21)"], [0.3, "rgb(249,210,41)"], [0.4, "rgb(134,191,118)"], [
                0.5, "rgb(37,180,167)"], [0.65, "rgb(17,123,215)"], [1, "rgb(54,50,153)"],
        ],
        "lighting": {
            "ambient": 1,
            "diffuse": 0.9,
            "fresnel": 0.5,
            "roughness": 0.9,
            "specular": 2
        },
        "reversescale": False,
    }

    layout = {
        "title": "{} Volatility Surface | {}".format(ticker, str(dt.datetime.now() if mode == 'live' else str(dt.datetime.fromtimestamp(data["datetime"]/1000)))),
        'margin': {
            'l': 15,
            'r': 15,
            'b': 15,
            't': 60,
        },
        'paper_bgcolor': '#FAFAFA',
        "hovermode": "closest",
        "scene": {
            "aspectmode": "manual",
            "aspectratio": {
                "x": 1.5,
                "y": 3.1,
                "z": 2
            },
            'camera': {
                'up': {'x': 0, 'y': 0, 'z': 1},
                'center': {'x': -1, 'y': -.5, 'z': -1},
                'eye': {'x': 3, 'y': 2, 'z': 1.75},
            },
            "xaxis": {
                "title": "Strike ($)",
                "showbackground": True,
                "backgroundcolor": "rgb(230, 230,230)",
                "gridcolor": "rgb(255, 255, 255)",
                "zerolinecolor": "rgb(255, 255, 255)"
            },
            "yaxis": {
                "title": "Expiry (days)",
                "showbackground": True,
                "backgroundcolor": "rgb(230, 230,230)",
                "gridcolor": "rgb(255, 255, 255)",
                "zerolinecolor": "rgb(255, 255, 255)"
            },
            "zaxis": {
                # "rangemode": "tozero",
                "title": "IV (σ)",
                "type": "log",
                "showbackground": True,
                "backgroundcolor": "rgb(230, 230,230)",
                "gridcolor": "rgb(255, 255, 255)",
                "zerolinecolor": "rgb(255, 255, 255)"
            }
        },
    }

    data = [trace1]
    figure = dict(data=data, layout=layout)
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)