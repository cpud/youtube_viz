import numpy as np
import pandas as pd
import plotly.graph_objects as go
from igraph import Graph
from .data import gather_data


def make_df(url):
    rel_df_dict, selected_df = gather_data(url)

    videos = pd.DataFrame()
    for i in range(len(selected_df)):
        # empty lists to store titles and like ratios for layer
        layer_titles = []
        views = []
        likes = []
        length = []

        # add first selected video manually because reasons
        # the other selected videos are in there because they're recommened and
        # due to the sorting for selection. the very first is not so we manually add it
        if i == 0:
            layer_titles.append(selected_df['Title'][0])
            views.append(selected_df['Views'][0])
            likes.append(selected_df['Likes'][0])
            length.append(selected_df['Length'][0])

        layer_titles.extend(rel_df_dict[i]['Title'].tolist()[:10])
        views.extend(rel_df_dict[i]['Views'].tolist()[:10])
        likes.extend(rel_df_dict[i]['Likes'].tolist()[:10])
        length.extend(rel_df_dict[i]['Length'].tolist()[:10])
        #selected.extend([0] * len(rel_df_dict[i]['Title'].tolist()[:10]))

        temp = pd.DataFrame()
        temp['title'] = layer_titles
        temp['layer'] = i
        temp['views'] = views
        temp['likes'] = likes
        temp['length'] = length
        #temp['selected'] = selected

        videos = videos.append(temp)

    videos['length'] = videos['length'].apply(lambda x: convert_time(x))

    return videos
