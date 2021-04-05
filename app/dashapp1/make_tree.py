import numpy as np
import pandas as pd
import plotly.graph_objects as go
from igraph import Graph
from datetime import datetime
from .data import gather_data


def make_df(url):
    rel_df_dict, selected_df = gather_data(url)

    videos = pd.DataFrame()
    for i in range(len(selected_df)):
        # empty lists to store titles and like ratios for layer
        layer_titles = []
        views = []
        likes = []
        dislikes = []
        likeRatio = []
        length = []
        channel = []
        published = []

        # add first selected video manually because reasons
        # the other selected videos are in there because they're recommened and
        # due to the sorting for selection. the very first is not so we manually add it
        if i == 0:
            layer_titles.append(selected_df['Title'][0])
            views.append(selected_df['Views'][0])
            likes.append(selected_df['Likes'][0])
            dislikes.append(selected_df['Dislikes'][0])
            likeRatio.append(selected_df['LikeRatio'][0])
            length.append(selected_df['Length'][0])
            channel.append(selected_df['Channel'][0])
            published.append(selected_df['Uploaded'][0])

        layer_titles.extend(rel_df_dict[i]['Title'].tolist()[:10])
        views.extend(rel_df_dict[i]['Views'].tolist()[:10])
        likes.extend(rel_df_dict[i]['Likes'].tolist()[:10])
        dislikes.extend(rel_df_dict[i]['Dislikes'].tolist()[:10])
        likeRatio.extend(rel_df_dict[i]['LikeRatio'].tolist()[:10])
        length.extend(rel_df_dict[i]['Length'].tolist()[:10])
        channel.extend(rel_df_dict[i]['Channel'].tolist()[:10])
        published.extend(rel_df_dict[i]['Uploaded'].tolist()[:10])
        #selected.extend([0] * len(rel_df_dict[i]['Title'].tolist()[:10]))

        temp = pd.DataFrame()
        temp['title'] = layer_titles
        temp['channel'] = channel
        temp['layer'] = i
        temp['views'] = views
        temp['likes'] = likes
        temp['dislikes'] = dislikes
        temp['likeRatio'] = likeRatio
        temp['length'] = length
        temp['published'] = published
        #temp['selected'] = selected

        videos = videos.append(temp)

    videos['length'] = videos['length'].apply(lambda x: convert_time(x))
    videos['published'] = videos['published'].apply(lambda x: x.split('T')[0])
    videos['likeRatio'] = videos['likeRatio'].apply(lambda x: round(x*100,3))
    videos.to_csv("data/videos.csv")

    return videos

def prepare_tree(videos):
    """This function creates the connections and labels used to make the
    tree plot."""
    layer_lens = []
    for n in range(len(videos['layer'].unique().tolist())):
        layer_lens.append(len(videos[videos['layer'] == n]))

    connections = []
    v_label = []
    counter = 0
    sel_idx = [1]

    for i in range(5):
        temp_label = videos['title'].tolist()[counter:counter + layer_lens[i]]

        for j in range(counter, counter + layer_lens[i]):
            if i == 0:
                connections.append((0, j))
            else:
                connections.append((sel_idx[i-1], j))
                #connections.append((counter, j))

        counter += layer_lens[i]
        sel_idx.append(counter)

        v_label.extend(temp_label)

    return v_label, connections

def make_plot(videos):
    #videos = make_df(url)

    v_label, connections = prepare_tree(videos)

    # make list for coloring the nodes
    coloring = videos['layer'].tolist()
    for i in range(1, len(videos)):
        coloring[i] = coloring[i] + 1

    # prepare text for plot
    videos['depth'] = coloring
    videos['minutes'] = videos['length'].apply(lambda x: length_to_min(x))
    videos['views_str'] = videos['views'].apply(lambda x: str(x))
    videos['likes_str'] = videos['likes'].apply(lambda x: str(x))
    videos['dislikes_str'] = videos['dislikes'].apply(lambda x: str(x))
    videos['likeRatio_str'] = videos['likeRatio'].apply(lambda x: str(x))
    videos['plot_text'] = videos['title'] + ' ' + '<br>' + 'Views: ' + videos['views_str'] + \
                        '<br>' + 'Likes: ' + videos['likes_str'] + '<br>' + \
                        'LikeRatio: ' + videos['likeRatio_str'] + '<br>' + 'Length: ' + videos['length']

    # resort because wrong before??
    depths = [0,1,2,3,4,5]
    proper_sort = pd.DataFrame()
    for depth in depths:
        temp = videos[videos['depth'] == depth]
        temp = temp.sort_values(by = ['likeRatio', 'views'], ascending = False)
        proper_sort = proper_sort.append(temp)

    videos = proper_sort
    videos.to_csv("data/videos.csv")

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
                                        title = 'Depth'),
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

    fig2, fig3, fig4 = make_bars(videos)

    return fig, fig2, fig3, fig4


def make_bars(videos):
    depths = [0,1,2,3,4,5]
    videos = pd.read_csv('data/videos.csv')
    likes_mean = []
    likes_std = []
    mins_mean = []
    mins_std = []
    views_mean = []
    views_std = []
    for depth in depths:
        depth_df = videos[videos['depth'] == depth]
        likes_mean.append(depth_df['likes'].mean())
        likes_std.append(depth_df['likes'].std())
        mins_mean.append(depth_df['minutes'].mean())
        mins_std.append(depth_df['minutes'].std())
        views_mean.append(depth_df['views'].mean())
        views_std.append(depth_df['views'].std())

    fig2 = go.Figure(data = [
        go.Bar(name = 'mean', x = depths, y = likes_mean,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#440154']
              ),
        go.Bar(name = 'std', x = depths, y = likes_std,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#1f9e89']
              ),
    ])
    fig2.update_layout(#barmode='group',
                       #font_color = '#3B846D',
                       colorway = ['#26828e', '#6ece58'],
                       title = 'Average Video Likes',
                       xaxis_title="Depth",
                       yaxis_title="Likes",)


    fig3 = go.Figure(data = [
        go.Bar(name = 'mean', x = depths, y = mins_mean,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#440154']
              ),
        go.Bar(name = 'std', x = depths, y = mins_std,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#1f9e89']
              ),
    ])
    fig3.update_layout(#barmode='group',
                       #font_color = '#3B846D',
                       colorway = ['#440154', '#31688e'],
                       title = 'Average Video Length (minutes)',
                       xaxis_title="Depth",
                       yaxis_title="Minutes",)


    fig4 = go.Figure(data = [
        go.Bar(name = 'mean', x = depths, y = views_mean,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#440154']
              ),
        go.Bar(name = 'std', x = depths, y = views_std,
              #marker_color = ['#440154', '#3e4989', '#26828e', '#1f9e89', '#6ece58', '#fde725']
               #marker_color = ['#1f9e89']
              ),
    ])
    fig4.update_layout(#barmode='group',
                       #font_color = '#3B846D',
                       colorway = ['#3e4989', '#26828e'],
                       title = 'Average Video Views',
                       xaxis_title="Depth",
                       yaxis_title="Views",)

    return fig2, fig3, fig4


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
        secs = thing.split[0]
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

    return round(total_seconds/60,0)
