import numpy as np
import pandas as pd
import plotly.graph_objects as go
from igraph import Graph
from textblob import TextBlob
from datetime import datetime
from .data import gather_data


def make_df(url):
    # gather data for dataframe
    videos = gather_data(url)

    # adjust columns and prepare for plot
    videos['Length'] = videos['Length'].apply(lambda x: convert_time(x))
    videos['Uploaded'] = videos['Uploaded'].apply(lambda x: x.split('T')[0])
    videos['LikeRatio'] = videos['LikeRatio'].apply(lambda x: round(x*100,3))
    videos['Polarity'] = videos['Title'].apply(lambda x: round(TextBlob(x).polarity),3)
    videos['Minutes'] = videos['Length'].apply(lambda x: length_to_min(x))
    videos['views_str'] = videos['Views'].apply(lambda x: str(x))
    videos['likes_str'] = videos['Likes'].apply(lambda x: str(x))
    videos['dislikes_str'] = videos['Dislikes'].apply(lambda x: str(x))
    videos['pol_string'] = videos['Polarity'].apply(lambda x: str(x))
    videos['LikeRatio_str'] = videos['LikeRatio'].apply(lambda x: str(x))
    videos['plot_text'] = videos['Title'] + ' ' + '<br>' + 'Polarity: ' + videos['pol_string'] + '<br>' + \
                        'Views: ' + videos['views_str'] + \
                        '<br>' + 'Likes: ' + videos['likes_str'] + '<br>' + \
                        'LikeRatio: ' + videos['LikeRatio_str'] + '<br>' + 'Length: ' + videos['Length']
    return videos

def prepare_tree(videos):
    layer_lens = []
    for n in range(len(videos['Layer'].unique().tolist())):
        layer_lens.append(len(videos[videos['Layer'] == n]))

    connections = []
    v_label = []
    counter = 0
    sel_idx = [0]

    for i in range(5):
        # get video titles in each layer
        temp_label = videos['Title'].tolist()[counter:counter + layer_lens[i]]

        # generating tuples for node connections
        # we want them in this form:
        # 0, 5, 10 etc are the 'selected' videos and need to connect to each other
        # (0,1), (0,2), (0,3), (0,4), (0, 5)
        # (5, 6), (5, 7), (5, 8), (5, 9), (5, 10)
        for j in range(counter + 1, counter + layer_lens[i] + 1):
            connections.append(((counter, j)))

        counter += layer_lens[i]
        v_label.extend(temp_label)

    return v_label, connections

def make_plot(videos):
    v_label, connections = prepare_tree(videos)

    # make list for coloring the nodes
    coloring = videos['Layer'].tolist()

    videos.to_csv("data/videos.csv")

    v_label, connections = prepare_tree(videos)

    # prepare igraph data for plotly as seen in plotly tree graph docs
    nr_vertices = len(v_label)
    g = Graph(connections)
    #lay = g.layout('fr')
    lay = g.layout('kk')
    #lay = g.layout('circle')

    position = {k: lay[k] for k in range(nr_vertices)}
    Y = [lay[k][1] for k in range(nr_vertices)]
    M = max(Y)

    E = (connections)

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:

        try:
            Xe+=[position[edge[0]][0],position[edge[1]][0], None]
            Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]
        except KeyError:
            continue

    labels = v_label

    # make tree plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                       y=Ye,
                       mode='lines',
                       line=dict(color='rgb(180,180,180)', width=1),
                       hoverinfo='none',
                       showlegend = False
                       ))

    fig.add_trace(go.Scatter(x=Xn,
                      y=Yn,
                      mode='markers',
                      #name='bla',
                      marker=dict(symbol='circle-dot',
                                    size=12,
                                    #color='#6175c1',    #'#DB4551',
                                    color = coloring,
                                    colorbar = dict(
                                        title = 'Layer'),
                                    colorscale = "viridis",
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                      text=videos['plot_text'],
                      hoverinfo='text',
                      opacity=0.8,
                      showlegend = False
                      ))

    fig.update_xaxes(showticklabels = False)
    fig.update_yaxes(showticklabels = False)

    fig2, fig3, fig4, fig5 = make_bars(videos)

    return fig, fig2, fig3, fig4, fig5


def make_bars(videos):

    try:
        videos = pd.read_csv('data/videos.csv')
    except:
        videos = pd.read_csv('data/sy.csv')

    likes_mean = []
    likes_std = []
    mins_mean = []
    mins_std = []
    views_mean = []
    views_std = []
    layers = videos['Layer'].unique().tolist()

    for layer in layers:
        layer_df = videos[videos['Layer'] == layer]
        likes_mean.append(layer_df['Likes'].mean())
        likes_std.append(layer_df['Likes'].std())
        mins_mean.append(layer_df['Minutes'].mean())
        mins_std.append(layer_df['Minutes'].std())
        views_mean.append(layer_df['Views'].mean())
        views_std.append(layer_df['Views'].std())


    fig2 = go.Figure(data = [
            go.Bar(name = 'mean', x = layers, y = likes_mean,
                  #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
                   #marker_color = ['#440154']
                  ),
            go.Bar(name = 'std', x = layers, y = likes_std,
                  #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
                   #marker_color = ['#1f9e89']
                  ),
        ])
    fig2.update_layout(#barmode='group',
                           #font_color = '#3B846D',
                           colorway = ['#3e4989', '#1f9e89'],
                           title = 'Average Video Likes',
                           xaxis_title="Layer",
                           yaxis_title="Likes",)


    fig3 = go.Figure(data = [
        go.Bar(name = 'mean', x = layers, y = mins_mean,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#440154']
              ),
        go.Bar(name = 'std', x = layers, y = mins_std,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#1f9e89']
              ),
    ])
    fig3.update_layout(#barmode='group',
                       #font_color = '#3B846D',
                       colorway = ['#26828e', '#6ece58'],
                       title = 'Average Video Length (Minutes)',
                       xaxis_title="Layer",
                       yaxis_title="Minutes",)


    fig4= go.Figure(data = [
        go.Bar(name = 'mean', x = layers, y = views_mean,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#440154']
              ),
        go.Bar(name = 'std', x = layers, y = views_std,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#1f9e89']
              ),
    ])
    fig4.update_layout(#barmode='group',
                       #font_color = '#3B846D',
                       colorway = ['#440154', '#31688e'],
                       title = 'Average Video Views',
                       xaxis_title="Layer",
                       yaxis_title="Views",)


    fig5 = go.Figure(data = [go.Bar(
        x = videos['Channel'].unique().tolist(),
        y = videos['Channel'].value_counts()
    )])

    fig5.update_layout(#barmode='group',
                           #font_color = '#3B846D',
                           #colorway = ['#3e4989', '#1f9e89'],
                           title = 'Channel Frequency',
                           #font_size = 9,
                           xaxis_title="Channel",
                           yaxis_title="Number of Videos",)

    return fig2, fig3, fig4, fig5


def convert_time(time):
    # it is ugly but it does work

    thing = time.split("T")[1]
    if "H" in time:
        hours = thing.split("H")[0]
        rest = thing.split("H")[1]
        mins = rest.split("M")[0]
        secs = rest.split("M")[1]
        secs = secs.split("S")[0]
    elif "M" not in time:
        secs = thing.split("S")[0]
        hours = ''
        mins = ''
    else:
        mins = thing.split("M")[0]
        rest = thing.split("M")[1]
        secs = rest.split("S")[0]
        hours = ''


    if len(secs) == 1:
        secs = "0" + secs
    if len(mins) == 1:
        mins = "0" + mins
    if secs == '':
        secs = "00"


    if hours != '':
        converted = hours + ":" + mins + ":" + secs
    elif mins == '':
        converted = ":" + secs
    else:
        converted = mins + ":" + secs


    return converted

def length_to_min(time):

    if len(time.split(":")) == 3:
        pt = datetime.strptime(time, '%H:%M:%S')
        total_seconds = pt.second + pt.minute*60 + pt.hour*3600
    elif time.split(":")[0] == '':
        pt = datetime.strptime(time, ':%S')
        total_seconds = pt.second
    else:
        pt = datetime.strptime(time, '%M:%S')
        total_seconds = pt.second + pt.minute*60

    # seems to break if time is an exact number of minutes.

    return round(total_seconds/60,0)
