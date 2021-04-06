import dash_core_components as dcc
import dash_html_components as html
import dash_table
#from .make_tree import make_df

default_url = "https://www.youtube.com/watch?v=XcOG5iZpV-k"
#videos = make_df(default_url)
#videos.to_csv("data/videos.csv")


layout = html.Div([

    #html.Div([]),
    html.Div([
    html.H3("Enter a link to a Youtube video and click submit to create the charts!"),
    dcc.Input(id = 'input-on-submit', type = 'text',
             #value = 'https://www.youtube.com/watch?v=Q8C7Ke-62ok',
             style = {'width': '70%'}),
    html.Button('Submit', id = 'submit-val', n_clicks = 0),
    ], style = {#'width': '49%',
                #'display': 'inline-block',
                #'padding-left': '80px',
                #'padding-top': '20px',
               }),

    html.Div(id='container-button-basic',
    children=[html.Ul(children = [
                  html.Li('The video you submitted will have a "depth" of 0. The node will be \
                  dark purple, so please locate that node to properly follow the graph. \
                  It is most likely near the bottom left corner.'),
                  html.Li('The nodes with multiple connections are "selected" videos, while \
              the other videos will be related videos that were not "selected".'),
                  html.Li('The colors represent the "depth" of each video. The video you entered would  \
                  have a depth of 0, and every video directly related to it would have a depth of 1, \
                  because it is one step further down the rabbit hole.'),
                  html.Li('Selection is based on the "polarity" of the title. The\
                  absolute value of each polarity score is compared, and then the \
                  video with the greatest "polarity" is selected. Polarity is \
                  generally on a scale from -1.0 to 1.0.'),
                  html.Li("I'd like to include more videos per node, but this app uses up youtube's API \
                  quota quickly, so I've limited it to 5."),
                  html.Li("I've included a default dataset (Sonic Youth) to display in the case that the API quota \
                  has been maxed out, so if you submit a link and it doesn't change, you can assume \
                  that the API quota limit has been exceeded."),
            ]),
        ],
    style = {#'padding-left': '80px',
             #'width': '49%',
             #'display': 'inline-block'
            }),

    # tree plot
    html.Div([
        #dcc.Graph(figure=fig),
        dcc.Graph(id = 'tree'),
        dcc.Graph(id = 'polarity'),
        dcc.Graph(id = 'likes'),
        dcc.Graph(id = 'minutes'),
        dcc.Graph(id = 'views')
        #dcc.Graph(figure = fig),
    ], style = {'width': '98%',
                #'display': 'inline-block'
               }
    ),

    html.Div(id = 'table',
             style = {'width': '98%',
                #'display': 'inline-block'
                }
    ),
    #html.Div([
    #dash_table.DataTable(
    #    id = 'datatable',
    #    columns = [{"name": i, "id": i} for i in videos.columns],
    #    data = videos.to_dict('records'))
    #], style = {'width': '49%',
                #'display': 'inline-block'
    #            }
    #),





], style = {'columnCount': '2'}
)
