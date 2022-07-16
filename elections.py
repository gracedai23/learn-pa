# #Imports
# import jwt
# import pandas as pd
# from tqdm import tqdm
# from bs4 import BeautifulSoup
# import requests
# import math
#
#
# #API keys
# # get keys from https://dpn.ceo.getsnworks.com/ceo/developer
# dp_pk = 'pk_h7GGLu5SHOMa1gTJpbCGZgWi1H4iX6'
# dp_secret = 'sk_P62YquYTjiuGLCcTPjoZckjqFk7QBA'
# dp_encoded_jwt = jwt.encode({'pk': dp_pk}, dp_secret, algorithm='HS256')
#
# st_pk = 'pk_cxprrNDEjFDHjZOF1HRxkgnBUOnUiC'
# st_secret = 'sk_085yhKYRPUsQVieJ9ss6ovRfljRMn3'
# st_encoded_jwt = jwt.encode({'pk': st_pk}, st_secret, algorithm='HS256')
#
#
# #Function to get number of items for a given property
# def getItems(endpoint, jwt):
#   per_page=1
#   page = 1
#   endpoint = endpoint.format(page, per_page)
#   headers = {"Authorization": "Bearer " + jwt}
#   response = requests.get(url=endpoint, headers= headers)
#   totalItems = response.json()['total_items']
#   return totalItems
#
# #Item count endpoints
# dp_count_endpoint = """https://dpn.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
#               keywords&order=published_at&page={}&per_page={}&status=published&
#               type=article&workflow"""
# st_count_endpoint = """https://dpn-34s.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
#               keywords&order=published_at&page={}&per_page={}&status=published&
#               type=article&workflow"""
#
# # Get item counts
# dp_items = getItems(dp_count_endpoint, dp_encoded_jwt)
#
# #Endpoints for article scrape
# dp_article_endpoint = """https://dpn.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
#                 keywords&order=published_at&page={}&per_page={}&status=published&
#                 type=article&workflow"""
#
# st_article_endpoint = """https://dpn-34s.ceo.getsnworks.com/v3/content?dir=desc&grid=false&
#                 keywords&order=published_at&page={}&per_page={}&status=published&
#                 type=article&workflow"""
#
#
# # Function to get articles for a given property
# def getArticles(article_endpoint, jwt, numItems, cutoff_date='2022-01-01', source='unknown'):
#     perPage = 100  # Pagesize per request
#     cutoff_date = pd.to_datetime(cutoff_date)  # '2021-11-1' end of dp dump
#
#     # Empty lists for results
#     ids = []
#     titles = []
#     title_url = []
#     content = []
#     slugs = []
#     contentType = []
#     published_dates = []
#     srns = []
#     authorIds = []
#
#     headers = {"Authorization": "Bearer " + jwt}
#
#     # Scrape loop. Progress bar just indicates max duration
#     for i in tqdm(range(math.ceil(numItems / perPage))):
#
#         # Parameters for request
#         endpoint = article_endpoint.format(i + 1, perPage)
#
#         # Request send
#         res = requests.get(url=endpoint, headers=headers).json()
#
#         # Parse response
#         for item in res['items']:
#             ids.append(item['id'])
#             titles.append(item['title'])
#             title_url.append(
#                 item['published_at'][0:4] + "/" +
#                 item['published_at'][5:7] + "/" +
#                 item['title_url'])
#             slugs.append(item['slug'])
#             srns.append(item['srn'].split(":")[3])
#             try:
#                 authorIds.append(item['user_id'])
#             except:
#                 authorIds.append(None)
#             contentType.append(item['type'])
#             soup = BeautifulSoup(item['content'], features="html.parser")
#             for script in soup(['script', 'style']):
#                 script.decompose()
#             content.append(soup.get_text().replace(u'\xa0', u' ').replace("\n", " "))
#             ts = pd.to_datetime(item['published_at'])
#             published_dates.append(ts)
#
#         # Break if cutoff date reached
#         if ts < cutoff_date:
#             break
#
#         articles_df = pd.DataFrame(data={'id': ids,
#                                          'type': contentType,
#                                          'srn': srns,
#                                          'title': titles,
#                                          'slug': slugs,
#                                          'content': content,
#                                          'published_date': published_dates,
#                                          "title_url": title_url})
#         articles_df = articles_df[articles_df['type'] == 'article']
#         articles_df.reset_index(inplace=True, drop=True)
#         articles_df['source'] = source
#
#     return articles_df
#
#
# #Article google analytics pull
# #Imports
# from oauth2client.service_account import ServiceAccountCredentials
# from apiclient.discovery import build
# import httplib2
# import requests
#
# # Get new DP articles
# dp_articles = getArticles(dp_article_endpoint,
#                           dp_encoded_jwt,
#                           dp_items,
#                           '2022-05-01',
#                           'dp')
# articles_df = dp_articles
# urls = ["/article/" + title_url for title_url in articles_df['title_url']]
# articles_df['url'] = ["/article/" + title_url for title_url in articles_df['title_url']]
#
#
# #Get per page statistics
# # Create service credentials
# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     'analytics-api-1581487025251-ac904d31a17e.json',
#     ['https://www.googleapis.com/auth/analytics.readonly'])
#
# # Create a service object
# http = credentials.authorize(httplib2.Http())
# service = build('analytics', 'v4', http=http,
#                 discoveryServiceUrl=('https://analyticsreporting.googleapis.com/$discovery/rest'))
#
#
# def getViews(pages, viewId, startDate='2006-01-01', endDate='today'):
#     response = service.reports().batchGet(
#         body={
#             'reportRequests': [
#                 {
#                     'viewId': viewId,  # Add View ID from GA
#                     'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
#                     'metrics': [{'expression': 'ga:uniquePageviews'},
#                                 {'expression': 'ga:pageviews'},
#                                 {'expression': 'ga:avgTimeOnPage'}],  # If you want to add metrics, add it here!
#                     'dimensions': [{"name": "ga:pagePath"}],  # Get Pages
#                     "dimensionFilterClauses": [{
#                         'filters': {
#                             "dimensionName": "ga:pagePath",
#                             "operator": "IN_LIST",
#                             "expressions": pages
#                         }
#                     }],
#                     'pageSize': 100000
#                 }]
#         }
#     ).execute()
#
#     # create two empty lists that will hold our dimentions and sessions data
#     data = []
#
#     # Extract Data
#     for report in response.get('reports', []):
#
#         rows = report.get('data', {}).get('rows', [])
#
#         for row in rows:
#             url = row['dimensions'][0]
#             uniquePageViews, pageViews, timeOnPage = row['metrics'][0]['values']  # ?? add new metric here
#             data.append((url, uniquePageViews, pageViews, timeOnPage))  # append data here
#
#     return pd.DataFrame(data, columns=['url', 'uniquePageViews', 'pageViews', 'avgTimeOnPage'])  # add new metric here
#
#
#
# #incorporate dates
# import datetime as DT
# today = DT.date.today()
# week_ago = today - DT.timedelta(days=7)
# week_ago_str = str(week_ago)
# month_ago = today - DT.timedelta(days=31)
# month_ago_str = str(month_ago)
#
#
# def get_week_month_engagement(code):
#     engagementDPWeek = getViews(urls, code, week_ago_str)
#     engagementDPWeek['pageViewsWeek'] = pd.to_numeric(
#         engagementDPWeek['pageViews'])  # create column for page views and put in data
#     engagementDPWeek['avgTimeWeek(min)'] = pd.to_numeric(engagementDPWeek['avgTimeOnPage']) / 60
#
#     engagementDPMonth = getViews(urls, code, month_ago_str)
#     engagementDPMonth['pageViewsMonth'] = pd.to_numeric(engagementDPMonth['pageViews'])
#     engagementDPMonth['avgTimeMonth(min)'] = pd.to_numeric(engagementDPMonth['avgTimeOnPage']) / 60
#
#     engagementDPWeek = engagementDPWeek.merge(
#         articles_df[['url', 'title', 'published_date']], on='url')
#     engagementDPMonth = engagementDPMonth.merge(
#         articles_df[['url', 'title', 'published_date']], on='url')
#
#     past_week = engagementDPWeek.sort_values(
#         by='pageViewsWeek', ascending=False).head(
#         20)[['title', 'pageViewsWeek', 'published_date', 'avgTimeWeek(min)']]  # add name of new column here
#
#     past_month = engagementDPMonth.sort_values(
#         by='pageViewsMonth', ascending=False).head(
#         20)[['title', 'pageViewsMonth', 'published_date', 'avgTimeMonth(min)']]
#
#     return past_week, past_month
#
#
# #Overall Statistics
# def getOverallStats(viewId, startDate='2022-01-01', endDate='today'):
#     response = service.reports().batchGet(
#         body={
#             'reportRequests': [
#                 {
#                     'viewId': viewId,  # Add View ID from GA
#                     'dateRanges': [{'startDate': startDate, 'endDate': endDate}],
#                     'metrics': [{'expression': 'ga:uniquePageviews'},
#                                 {'expression': 'ga:pageViews'},
#                                 {'expression': 'ga:bounceRate'},
#                                 {'expression': 'ga:avgTimeOnPage'}],
#                 }]
#         }
#     ).execute()
#
#     # Extract Data
#     for report in response.get('reports', []):
#         results = report.get('data', {}).get('rows', [])[0]['metrics'][0]['values']
#         uniquePageViews, pageViews, bounceRate, avgPageTime = results
#         return uniquePageViews, pageViews, bounceRate, avgPageTime
#
# def getRange(viewId, daySpan, spans):
#   # daySpan: Number of days to aggregate over (eg, 7 for week)
#   # of spans to calculate statistics for (eg, 4 for a month)
#   stats = {}
#   for i in range(spans):
#     start = today - DT.timedelta(days=daySpan * (i+1))
#     end = today - DT.timedelta(days=daySpan * (i))
#     stats[str(end)] = getOverallStats(viewId,
#                                       startDate = str(start),
#                                       endDate = str(end))
#   dpRange = pd.DataFrame(stats)
#   dpRangeT = dpRange.T
#   dpRangeT.columns = ['uniquePageViews', 'pageViews', 'bounceRate', 'avgTimeOnPage']
#   return dpRangeT
#
#
# #Run Program
# if __name__ == '__main__':
#     #print(dp_articles)
#     dp_past_week, dp_past_month = get_week_month_engagement('22050415')
#     print(dp_past_week)
#     print(dp_past_month)
#
#     dpOverallStats = getRange('22050415', 7, 16)
#     print(dpOverallStats)

import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv('politics.csv')
#you can also read your data like this:
# df = pd.read_csv('/home/charmingdata1/demo-app3/politics.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# server = app.server

# radioItem list for the layout (long_code.py lines 13-45)
radio_list = []
for s,v in zip(['AZ','FL','GA','IA','ME','MI','NC','NV','OH','PA','TX','WI'],
               [11,29,16,6,4,16,15,6,18,20,38,10]):
    radio_list.append(
        html.Div([
            html.Label(f'{s}-{v}: ', style={'display':'inline', 'fontSize':15}),
            dcc.RadioItems(
                id=f'radiolist-{s}',
                options=[
                    {"label": "Dem", "value": "democrat"},
                    {"label": "Rep", "value": "republican"},
                    {"label": "NA", "value": "unsure"},
                ],
                value='unsure',
                inputStyle={'margin-left': '10px'},
                labelStyle={'display': 'inline-block'},
                style={'display':'inline'}
            ),
        ], style={'textAlign':'end'})
    )
print(radio_list)


# Input list for the callback (long_code.py lines 48-52)
input_list = []
for x in ['AZ','FL','GA','IA','ME','MI','NC','NV','OH','PA','TX','WI']:
    input_list.append(
        Input(component_id=f'radiolist-{x}', component_property='value')
    )


app.layout = html.Div([
    dbc.Row([
        dbc.Col(html.H1("USA Elections 2020", style={'textAlign':'center'}), width=12)
    ]),
    dbc.Row([
        dbc.Col(radio_list, xs=4, sm=4, md=4, lg=2, xl=2),
        dbc.Col(dcc.Graph(id='my-choropleth', figure={},
                          config={'displayModeBar':False}), xs=8, sm=8, md=8, lg=6, xl=6),
        dbc.Col(dcc.Graph(id='my-bar', figure={},
                          config={'displayModeBar': False}), xs=6, sm=6, md=6, lg=4, xl=4)

    ])
])


# must have Dash version 1.16.0 or higher
@app.callback(
    Output(component_id='my-choropleth', component_property='figure'),
    Output(component_id='my-bar', component_property='figure'),
    input_list
)
def update_graph(az, fl, ga, ia, me, mi, nc, nv, oh, pa, tx, wi):
    dff = df.copy()  # assign party to dataframe (long_code.py lines 55-57)
    for st,radio_value_chosen in zip(
            ['AZ','FL','GA','IA','ME','MI','NC','NV','OH','PA','TX','WI'],
            [az, fl, ga, ia, me, mi, nc, nv, oh, pa, tx, wi]):
        dff.loc[dff.state == st, 'party'] = radio_value_chosen

    # build map figure
    fig_map = px.choropleth(
        dff, locations="state", hover_name='electoral votes',
        locationmode="USA-states", color="party",
        scope="usa", color_discrete_map={'democrat': 'blue',
                                         'republican': 'red',
                                         'unsure': 'grey'})

    # build histogram figure
    dff = dff[dff.party != 'unsure']
    fig_bar = px.histogram(dff, x='party', y='electoral votes', color='party',
                           range_y=[0,350], color_discrete_map={'democrat': 'blue',
                                                                'republican': 'red'}
                           )
    # add horizontal line
    fig_bar.update_layout(showlegend=False, shapes=[
        dict(type='line', yref='paper',y0=0.77,y1=0.77, xref='x',x0=-0.5,x1=1.5)
    ])
    # add annotation text above line
    fig_bar.add_annotation(x=0.5, y=280, showarrow=False, text="270 votes to win")

    return fig_map, fig_bar


if __name__ == '__main__':
    app.run_server(debug=False)