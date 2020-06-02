# importing libraries for Dash
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import smtplib  # used for sending emails
import time

# importing libraries for Google api
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# setting up credentials to pull data from the google sheet
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# setting up data for email notifications for growing errors
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
smtp_server = "smtp.gmail.com"
sender_email = "fungalbot@gmail.com"
receiver_email = "rzhang088@gmail.com"
password = 'madpjxlfxcrwytek'


def email_notification():  # function that sends an email to me with error data, for some reason putting the message in a function ruins the email formatting
    server.login(sender_email, password)
    message = """\
    Subject: Growing Unit Error \\
    
    Growing Unit requires attention"""
    server.sendmail(sender_email, receiver_email, message)


# pulling data from the google sheet and updating them in a while true loop

sheet1 = client.open("Logger").sheet1  # Open the spread sheet
row = sheet1.row_values(3)
col = sheet1.col_values(3)
cell = sheet1.cell(1, 2).value
data = sheet1.get_all_records()  # Get a list of all records
x_time = sheet1.col_values(1)
y_temp = sheet1.col_values(2)
y_humid = sheet1.col_values(3)
y_air = sheet1.col_values(4)

sheet2 = client.open("Logger").get_worksheet(1)  # Open the spread sheet
row2 = sheet2.row_values(3)
col2 = sheet2.col_values(3)
cell2 = sheet2.cell(1, 2).value
data2 = sheet2.get_all_records()  # Get a list of all records
x_time2 = sheet2.col_values(1)
y_temp2 = sheet2.col_values(2)
y_humid2 = sheet2.col_values(3)
y_air2 = sheet2.col_values(4)

# Setting up the Dash web page

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# set up colours for backgrounds and text
colors = {
    'background': '#111111',
    'text': '#FFFFFF'
}

# set up style of the tab buttons
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'backgroundColor': '#202224',
    'borderBottom': '1px solid #453c96',
    'padding': '6px',
    'fontWeight': 'bold'

}

tab_selected_style = {
    'borderTop': '1px solid #453c96',
    'borderBottom': '1px solid #453c96',
    'backgroundColor': '#111111',
    'color': 'white',
    'padding': '6px'
}


# create a function to count operation errors
# make this a function later
def error_count():
    temp_error = 0
    timeframe = 300  # set to 336 for a week's worth of data
    max_temp = 30  # set to 30 for oyster mushrooms
    min_temp = 10  # set to 10
    humid_error = 0
    max_hum = 87.5  # set to 90 for oyster mushrooms
    min_hum = 45  # set to 45
    air_error = 0
    min_air = 65
    for i in range((len(y_temp) - timeframe), len(y_temp)):  # 0: for readings in a week
        if round(float(y_temp[i])) >= max_temp or round(float(y_temp[i])) <= min_temp:
            temp_error += 1

    for i in range((len(y_humid) - timeframe), len(y_humid)):
        if round(float(y_humid[i])) >= max_hum or round(float(y_humid[i])) <= min_hum:
            humid_error += 1

    for i in range((len(y_air) - timeframe), len(y_air)):
        if round(float(y_air[i])) <= min_air:
            air_error += 1
    return [temp_error, humid_error, air_error]  # ;

def error_count2():
    temp_error2 = 0
    timeframe = 48  # set to 336 for a week's worth of data
    max_temp = 30  # set to 30 for oyster mushrooms
    min_temp = 10  # set to 10
    humid_error2 = 0
    max_hum = 87.5  # set to 90 for oyster mushrooms
    min_hum = 55  # set to 45
    air_error2 = 0
    min_air = 65
    for i in range((len(y_temp2) - timeframe), len(y_temp2)):  # 0: for readings in a week
        if round(float(y_temp2[i])) >= max_temp or round(float(y_temp2[i])) <= min_temp:
            temp_error2 += 1

    for i in range((len(y_humid2) - timeframe), len(y_humid2)):
        if round(float(y_humid2[i])) >= max_hum or round(float(y_humid2[i])) <= min_hum:
            humid_error2 += 1

    for i in range((len(y_air2) - timeframe), len(y_air2)):
        if round(float(y_air2[i])) <= min_air:
            air_error2 += 1
    return [temp_error2, humid_error2, air_error2]  # ;

error_count()


def error_emailer():
    max_temp = 30  # set to 30 for oyster mushrooms
    min_temp = 10  # set to 10
    max_hum = 87.5  # set to 90 for oyster mushrooms
    min_hum = 45
    min_air = 70
    while True:
        for i in range(len(y_temp)):
            if round(float(y_temp[i])) >= max_temp or round(float(y_temp[i])) <= min_temp or round(
                    float(y_humid[i])) >= max_hum or round(float(y_humid[i])) <= min_hum or round(
                    float(y_air[i])) <= min_air:
                server.login(sender_email, password)
                message = """\
                    Subject: Growing Unit Error \\

                    \n Growing Unit requires attention"""
                server.sendmail(sender_email, receiver_email, message)
            time.sleep(1800)  # wait for the next sheet update in 30 minutes

# webapp design begins here
app.layout = html.Div(style={'backgroundColor': colors['background']},
                      children=[  # here the layout web page is defined by tree components
                          html.H1(
                              children='Mushroom Monitor',
                              style={
                                  'textAlign': 'center',
                                  'color': colors['text']
                              }),

                          html.Div(children='''
        A webapp to monitor environmental data from mushroom growing rigs  
        \ Ric Zhang- SIOT 2020
    ''', style={
                              'textAlign': 'center',
                              'color': colors['text']
                          }),
                          dcc.Tabs(id="tabs", value='tab-1', children=[
                              dcc.Tab(label='Project Overview', value='tab-1', style=tab_style,
                                      selected_style=tab_selected_style),
                              dcc.Tab(label='Grow Unit 1 ', value='tab-2', style=tab_style,
                                      selected_style=tab_selected_style),
                              dcc.Tab(label='Grow Unit 2 ', value='tab-3', style=tab_style,
                                      selected_style=tab_selected_style),
                          ], style=tabs_styles),
                          html.Div(id='tabs-content-example')
                      ])


@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs', 'value')])

def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1('What does Mushroom Monitor do ?', style={
                    'textAlign': 'center', 'color': 'white', 'fontsize': '30'}),
            html.P('Welcome, on this webapp you will be able to monitor the variables of the mushroom growing stacks that Mycobiont uses '
                    '', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '14'}),
            html.H2('Most recent readings', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '24'}),
            html.Div([
                html.H3('Temperature : ', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block', 'vertical-align': 'left'}),
                html.H3(y_temp[-1], style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block', 'vertical-align': 'right'}),
                html.H3('\u00b0C', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'right'})
                ]),
            html.Div([
                html.H3('Humidity : ', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'left'}),
                html.H3( y_humid[-1], style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'right'}),
                html.H3('%', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'right'})
                ]),
            html.Div([
                html.H3('Air Quality : ', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'left'}),
                html.H3( y_air[-1], style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'right'}),
                html.H3('%', style={
                    'textAlign': 'left', 'color': 'white', 'fontsize': '30', 'display': 'inline-block',
                    'vertical-align': 'right'})
                ]
            )
        ])

    elif tab == 'tab-2':
        return html.Div([
            html.Div([
                html.Div([
                    html.H3('Error Counters', style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),

                    dcc.Graph(
                        id='Error Counters',
                        figure={

                        'data': [{
                            'y': ['Total <br> errors', 'Temperature <br> errors', 'Humidity <br> errors', 'Air Quality <br> errors'],
                            'x': [error_count()[0] + error_count()[1] + error_count()[2], error_count()[0],
                                  error_count()[1], error_count()[2]],
                            'type': 'bar', 'orientation': 'h'
                            }],

                            'layout': go.Layout(
                                autosize=True,
                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',

                            )

                        }
                    )], className='six columns'),

                html.Div([
                    html.H3('Air Quality', style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                    dcc.Graph(
                        id='AirQuality1',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=x_time,
                                    y=y_air,
                                    mode='lines+markers'
                                )
                            ],

                            'layout': go.Layout(

                                autosize=True,
                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',
                                title='Grow Unit 1 Data from the past week',
                                xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                       "titlefont": {"color": "white"}, },
                                yaxis={'title': 'Air Quality (%)', 'showgrid': True, "titlefont":{"color": "white"}}
                            )

                        }
                    )], className='six columns')
            ], className='row'),

                # second row of charts
                html.Div([
                    html.Div([
                        html.H3('Temperature', style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                        dcc.Graph(
                            id='temp1',
                            figure={
                                'data': [
                                    go.Scatter(
                                        x=x_time,
                                        y=y_temp,
                                        mode='lines+markers'
                                    )
                                ],

                                'layout': go.Layout(

                                    autosize=True,

                                    paper_bgcolor='#111111',
                                    plot_bgcolor='#111111',
                                    title='Grow Unit 1 Data from the past week',
                                    xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                           "titlefont": {"color": "white"}, },
                                    yaxis={'title': 'Temperature (\u00b0C)', 'showgrid': True,
                                           "titlefont": {"color": "white"}, }
                                )

                            }
                        )], className='six columns'),

                    html.Div([
                        html.H3('Humidity', style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                        dcc.Graph(
                            id='Humidity1',
                            figure={
                                'data': [
                                    go.Scatter(
                                        x=x_time,
                                        y=y_humid,
                                        mode='lines+markers'
                                    )
                                ],

                                'layout': go.Layout(

                                    autosize=True,

                                    paper_bgcolor='#111111',
                                    plot_bgcolor='#111111',
                                    title='Grow Unit 1 Data from the past week',
                                    xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                           "titlefont": {"color": "white"}, },
                                    yaxis={'title': 'Humidity (%)', 'showgrid': True, "titlefont": {"color": "white"}, }
                                )

                            }
                        )], className='six columns')
                ], className='row')
            ])


    elif tab == 'tab-3':
        return html.Div([
            html.Div([
                html.Div([
                    html.H3('Error Counters',style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                    dcc.Graph(
                        id='Error Counters',
                        figure={

                            'data': [{
                                'y': ['Total <br> errors', 'Temperature <br> errors', 'Humidity <br> errors',
                                      'Air Quality <br> errors'],
                                'x': [error_count2()[0] + error_count2()[1] + error_count2()[2], error_count2()[0],
                                      error_count2()[1], error_count2()[2]],
                                'type': 'bar', 'orientation': 'h'
                            }],

                            'layout': go.Layout(
                                autosize=True,
                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',

                            )

                        }
                    )], className='six columns'),

                html.Div([
                    html.H3('Air Quality',style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                    dcc.Graph(
                        id='AirQuality1',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=x_time2,
                                    y=y_air2,
                                    mode='lines+markers'
                                )
                            ],

                            'layout': go.Layout(

                                autosize=True,
                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',
                                title='Grow Unit 2 Data from the past week',
                                xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                       "titlefont": {"color": "white"}, },
                                yaxis={'title': 'Air Quality (%)', 'showgrid': True, "titlefont": {"color": "white"}, }
                            )

                        }
                    )], className='six columns')
            ], className='row'),

            # second row of charts
            html.Div([
                html.Div([
                    html.H3('Temperature',style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                    dcc.Graph(
                        id='temp1',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=x_time2,
                                    y=y_temp2,
                                    mode='lines+markers'
                                )
                            ],

                            'layout': go.Layout(

                                autosize=True,

                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',
                                title='Grow Unit 2 Data from the past week',
                                xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                       "titlefont": {"color": "white"}, },
                                yaxis={'title': 'Temperature (\u00b0C)', 'showgrid': True,
                                       "titlefont": {"color": "white"}, }
                            )

                        }
                    )], className='six columns'),

                html.Div([
                    html.H3('Humidity', style={
                    'textAlign': 'center', 'color': 'gray', 'fontsize': '14'}),
                    dcc.Graph(
                        id='Humidity1',
                        figure={
                            'data': [
                                go.Scatter(
                                    x=x_time2,
                                    y=y_humid2,
                                    mode='lines+markers'
                                )
                            ],

                            'layout': go.Layout(

                                autosize=True,

                                paper_bgcolor='#111111',
                                plot_bgcolor='#111111',
                                title='Grow Unit 2 Data from the past week',
                                xaxis={'title': 'Time (date and time)', 'showgrid': True,
                                       "titlefont": {"color": "white"}, },
                                yaxis={'title': 'Humidity (%)', 'showgrid': True, "titlefont": {"color": "white"}, }
                            )

                        }
                    )], className='six columns')
            ], className='row')
        ])


if __name__ == '__main__':
    app.run_server(debug=True)

error_emailer()

# include a plotly table to show raw data
