import numpy as np
import pandas as pd
import os
from googleapiclient.discovery import build

api_key = os.environ.get("API_KEY")

def related_ids(url):
    # get video ID
    vid = url.split('=')[-1]

    # build youtube object to access API, then make request
    youtube = build('youtube','v3',developerKey=api_key)
    search_request = youtube.search().list(
        part = 'snippet',
        relatedToVideoId = vid,
        maxResults = 5,
    type = 'video',)

    search_response = search_request.execute()

    # add the selected video to the top so it is included
    # only need video IDs at this point, we request more info
    # in a later API call
    rel_vids = [vid]
    for item in search_response['items']:
        try:
            #rel_titles.append(item['snippet']['title'])
            rel_vids.append(item['id']['videoId'])
        except:
            continue

    return rel_vids



def related_api_requests(video_ids):
    # build youtube resource object
    youtube = build('youtube','v3',developerKey=api_key)

    # video Ids to feed into API
    #related_Ids = list(df['Id'])
    related_Ids = video_ids

    # contentDetails videos request to get video length
    vid_request = youtube.videos().list(
        part = 'contentDetails',
        id = related_Ids,
        maxResults = 5)
    vid_response = vid_request.execute()

    # loop through durations
    durations = []
    for item in vid_response['items']:
        durations.append(item['contentDetails']['duration'])

    # stat request for likes, dislikes, comment counts, and view counts
    stat_request = youtube.videos().list(
        part = 'statistics',
        id = related_Ids,
        maxResults = 5)
    stat_response = stat_request.execute()

    # empty lists to store data
    likes = []
    dislikes = []
    views = []
    comments = []

    # loop through stats
    for stat in stat_response['items']:
        try:
            likes.append(stat['statistics']['likeCount'])
        except KeyError:
            likes.append(0)
        try:
            dislikes.append(stat['statistics']['dislikeCount'])
        except KeyError:
            dislikes.append(0)
        try:
            views.append(stat['statistics']['viewCount'])
        except KeyError:
            views.append(0)
        #comments.append(stat['statistics']['commentCount'])

    # get channel titles
    snip_request = youtube.videos().list(
        part = 'snippet',
        id = related_Ids,
        maxResults = 5)
    snip_response = snip_request.execute()

    # lists for titles
    channels = []
    titles = []
    upload_date = []
    ids = []

    # loop through snippets
    for snip in snip_response['items']:
        channels.append(snip['snippet']['channelTitle'])
        titles.append(snip['snippet']['title'])
        upload_date.append(snip['snippet']['publishedAt'])
        ids.append(snip['id'])

    # add fields to dataframe
    #fields = [durations, likes, dislikes, views, comments]
    df = pd.DataFrame()
    df['Title'] = titles
    df['ID'] = ids
    df['Channel'] = channels
    df['Length'] = durations
    df['Likes'] = likes
    df['Dislikes'] = dislikes
    df['Views'] = views
    #df['Comments'] = comments
    df['Uploaded'] = upload_date

    # convert to int
    #fields = ['Likes', 'Dislikes', 'Views', 'Comments']
    fields = ['Likes', 'Dislikes', 'Views']
    for field in fields:
        df[field] = df[field].apply(lambda x: int(x))

    # create LikeRatio
    df['LikeRatio'] = df['Likes'] / (df['Likes'] + df['Dislikes'])

    # selected vs recommended. the first video is the 'selected', or viewed video.
    selected = [1]
    selected.extend([0] * (len(df) - 1))
    df['Selected'] = selected

    return df

def gather_data(url):
    out = {}
    selected = [url.split('=')[-1]]
    for i in range(0,5):
        url = url.split('=')[-1]
        rel_vids = related_ids(url)
        df = related_api_requests(rel_vids)

        sorted_df = df.sort_values(['LikeRatio', 'Views'], ascending = False)
        out[i] = sorted_df

        # selection logic could use some work...
        url = sorted_df.reset_index()['ID'][0]
        if url in selected:
            filtered = sorted_df[sorted_df['ID'] != url].reset_index()
            url = filtered['ID'][0]

        selected.append(url)

    selected_df = related_api_requests(selected[:5])

    return out, selected_df