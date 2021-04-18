from datetime import datetime

import os
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_html_components as html
from .make_tree import make_plot, make_df
#from dash.dependencies import Output

#videos = pd.read_csv("data/sy.csv")

def register_callbacks(dashapp):
    @dashapp.callback([Output('tree', 'figure'),
                       Output('likes', 'figure'),
                       Output('minutes', 'figure'),
                       Output('views', 'figure'),
                       Output('channels', 'figure'),
                       Output('table', 'children')],
                     [Input('submit-val', 'n_clicks')],
                     [State('input-on-submit', 'value')])

    def display_plot(n_clicks, value):
        #videos = make_df(value)
        try:
            videos = make_df(value)
        except:
        #    #videos = pd.read_csv('data/sy.csv')
            videos = pd.read_csv('data/tennis.csv')


        # make table of videos
        dataframe = videos
        dataframe = dataframe.reindex(columns = ['Title','Channel', 'Views',
                                                 'Likes','Dislikes', 'LikeRatio', 'Length',
                                                 'Uploaded', 'Polarity',])

        table = html.Table([
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

        fig, fig2, fig3, fig4, fig5 = make_plot(videos)

        # overwrite last users data so default is always sonic youth
        # but first grab the other data if it isn't SY because local baybeee
        title = videos.reset_index()['Title'][0]
        videos.to_csv('data/' + title + '.csv')
        videos = pd.read_csv('data/tennis.csv')
        videos.to_csv('data/videos.csv')
        return fig, fig2, fig3, fig4, fig5, table
