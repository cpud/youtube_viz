from datetime import datetime

import pandas as pd
from dash.dependencies import Input, Output, State
import dash_html_components as html
from .make_tree import make_plot, make_df
#from dash.dependencies import Output

videos = pd.read_csv("data/sy.csv")

def register_callbacks(dashapp):
    @dashapp.callback([Output('tree', 'figure'),
                       Output('likes', 'figure'),
                       Output('minutes', 'figure'),
                       Output('views', 'figure')],
                     [Input('submit-val', 'n_clicks')],
                     [State('input-on-submit', 'value')])

    def display_plot(n_clicks, value):
        try:
            videos = make_df(value)
        except:
            videos = pd.read_csv('data/sy.csv')
        fig, fig2, fig3, fig4 = make_plot(videos)
        return fig, fig2, fig3, fig4

    @dashapp.callback(Output('table', 'children'),
                     [Input('submit-val', 'n_clicks')],
                     [State('input-on-submit', 'value')])

    def generate_table(n_clicks, max_rows = 51):
        try:
            dataframe = pd.read_csv('data/videos.csv')
        except:
            dataframe = pd.read_csv('data/sy.csv')
        dataframe = dataframe.reindex(columns = ['title','depth','channel', 'views',
                                                 'likes','dislikes', 'likeRatio', 'length',
                                                 'published'])

        return html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns]),
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(len(dataframe))
            ],#style = {'width': '50%'}
                                    )
        ], style = {#'background-color': '#FFFFFF',
                    'color': '#3B846D',
                    'width': '98%'
                    #'font-style': 'italic'
                    })
