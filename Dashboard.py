from binance.client import Client
import plotly.offline as pyo
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go 
import pandas as pd
from keys import api_key, api_secret
from datetime import datetime
from dash.dependencies import Input, Output
import time
from datetime import timedelta, date


def flexible_lending_values():
    lending = client.get_lending_interest_history(lendingType = "CUSTOMIZED_FIXED")
    cleandf = pd.DataFrame(lending)
    cleandf['time'] = (pd.to_datetime(cleandf['time'], unit='ms'))
    cleandf = cleandf.assign(date_extract = [str(i.date()) for i in cleandf['time']])
    cleandf['time'] =cleandf['date_extract']
    global time2
    time2 =cleandf['time']
    del cleandf['date_extract']
    global total_flexible
    cleandf['interest'] = cleandf['interest'].astype(float)
    total_flexible = cleandf['interest'].sum()

    return cleandf



def fixed_lending_values():
    lending = client.get_lending_interest_history(lendingType = "REGULAR")
    cleandf = pd.DataFrame(lending)
    
    cleandf['time'] = (pd.to_datetime(cleandf['time'], unit='ms'))
    cleandf = cleandf.assign(date_extract = [str(i.date()) for i in cleandf['time']])
    cleandf['time'] =cleandf['date_extract']
    del cleandf['date_extract']
    global total_fixed
    cleandf['interest'] = cleandf['interest'].astype(float)
    total_fixed = cleandf['interest'].sum() 
    return cleandf



def lending_account():
    lending = client.get_lending_account(lendingType = "DAILY")
    cleandf = pd.DataFrame(lending['positionAmountVos'])
    global portfolio_value
    cleandf['amountInUSDT'] = cleandf['amountInUSDT'].astype(float)
    portfolio_value = cleandf['amountInUSDT'].sum()
    portfolio_value = str(round(portfolio_value, 2)) + '$'
    
    return cleandf



def timer():
    lending = client.get_lending_interest_history(lendingType = "DAILY")
    cleandf = pd.DataFrame(lending)
    global time1
    cleandf['time'] = cleandf['time'].astype(float)
    time1 = cleandf['time']
    return cleandf


def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='ms')

def getMarks(start, end, Nth=2):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(time1):
        if(i%Nth == 1):
            result[date] = date

    return result

def dayscount():
    daysmark = {}
    x = 0
    for i in time1:  
        daysmark[x]= i
        x=x+1
    return daysmark


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

start_dt = date(2020, 1, 11)

end_dt = date.today()

milliseconds = int(round(time.time() * 1000))

client = Client(api_key, api_secret)
pd.set_option('float_format', '{:f}'.format)
pd.options.mode.chained_assignment = None

milliseconds = int(round(time.time() * 1000))

#date_range
global final
final = []
for dt in daterange(start_dt, end_dt):
    y = dt.strftime("%Y-%m-%d")
    final.append(y)

sub_final = final[0::int(len(final)/6)]
sub_final.append(final[-1]) 

#flexibel_lending
df = flexible_lending_values()
df0 = pd.DataFrame(final, columns =['time'])
frames = [df, df0]
df_new= pd.concat([df, df0], axis=0, sort=True)
df_new = df_new.sort_values('time')
df_new = df_new.reset_index(drop=True)
global values
values = df_new['interest']
labels = df_new['time']

#fixed_lending
df2 = fixed_lending_values()
df0 = pd.DataFrame(final, columns =['time'])
print(df2)
df_new2= pd.concat([df2, df0], axis=0, sort=True)
df_new2 = df_new2.sort_values('time')
global values2
values2 =df_new2['interest']
labels2 = df_new2['time']


#lending_account
df3 = lending_account()
values3 = []
for interest in df3['amountInUSDT'].unique():
    values3.append(float(interest))

labels3 = []

for time in df3['asset'].unique():
    labels3.append(time)

df_new3= pd.concat([df_new, df_new2], axis=0, sort=True)
df_new3.index = range(len(df_new3.index))
df_new3 = df_new3.fillna(0)
del df_new3['asset']
del df_new3['lendingType']
del df_new3['productName']
df_new3['interest'].astype(float)
df_new3= pd.to_numeric(df_new3.interest).groupby([df_new3.time]).sum()
df_new3= pd.DataFrame(df_new3, columns =['time', 'interest'])
df_new3 = df_new3.fillna(0).copy()
df_new3['interest3']= float(0)
df_new3['interest3'].astype(float)
df_new3.at['2020-01-11', 'interest3'] = float(2224)
df_new3['interest3'].astype(float)
x = 1
df_new3['interest3'].astype(float)

for i in range(len(df_new3['interest3'])-1):
    
    df_new3['interest3'][x]=df_new3['interest3'][x -1].astype(float) + float(df_new3['interest'][x])
    x= x + 1
total_return=round(((df_new3['interest3'][-1]/df_new3['interest3'][0] -1) *100),2)
total_return=f"{total_return}%"


#format_titles
total_fixed = round(float(total_fixed),2)

title1 = '{} {}  {} '.format('Total Interests', total_fixed, '$')

total_flexible = round(float(total_flexible),2)

title2 = '{} {}  {} '.format('Total Interests', total_flexible, '$')

Portfolio_performance = '{} {} '.format('Portfolio Performance:', total_return)


#Layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#1e1e1e',
    'text': '#FDFAF7'
}
farben = ['#f48229', '#2171f3']

app.layout = html.Div(style={'height':'100%','width': '100%','display': 'inline-block','backgroundColor': '#000000' }, children=[
    html.H1(
        children='Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'font-family':'Arial',
            'padding': '0px 0px 2px 2px',
            'backgroundColor': colors['background'],
            'marginLeft': 0, 'marginRight': 0,'marginBottom': 1

        }
    ),
   
    html.Div([
    dcc.Graph(id='Pie1',
        figure=go.Figure(
            data=[go.Pie(labels=labels3,
                        values=values3,
                        hole=.3,
                        textinfo='label+percent',
                        marker=dict(colors=farben),
                        title= str(portfolio_value),
                        
                        
                        )],
            layout=go.Layout(
                    
                    paper_bgcolor = '#1e1e1e',
                    legend=dict(
                    x=1,
                    y=0.4),
                    title= dict(
                        text = 'Portfolio',
                        x = 0.5,
                        y = 0.90),
                    font = dict(
                        color = "#FDFAF7",
                        size = 14,
                        family= 'Arial'
                        
                        

                    )
                    
                    
                    
                    
                    
                    
                    

                    )
            
                           ))],
    style={'display': 'inline-block', 'width': '49.95%', 'height': '490px','vertical-align': 'top', 'marginLeft': 0, 'marginRight': '0.05%',  'marginBottom':'0.05%', 'backgroundColor': colors['background']}), 
    html.Div([

        dcc.Graph(
            id='example-graph',
            
            figure={
                'data': [
                    {'x': labels, 'y': values, 'type': 'bar', 'name': 'Flexible','marker':dict(color='#f48229')},
                    {'x': labels2, 'y': values2, 'type': 'bar', 'name': 'Fixed','marker':dict(color='#2171f3')},
                ],
                
                'layout': {
                    'title': 'Interest payouts ($)',
                    'yaxis' : {
                        'tickformat':'$'},
                    'plot_bgcolor': colors['background'],
                    'colors':'farben',
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text'],
                        'family':'Arial',
                        'size':'14'
                    },
                    'legend': {
                        'x':'1',
                        'y': '0.4'
                    }
                        
                                                


                        
                    }
 
                    
                
                
            }),
        html.Div([
            dcc.RangeSlider(
                            id='year_slider',
                            min = 0,
                            max = len(sub_final)-1,
                            value = [0, 7],
                            marks={i : str(yearm) for i, yearm in enumerate((sub_final))},
                            step = 1,
                            
                            
                        
                            
                )], style= {'width': '80%', 'marginLeft': 30, 'marginBottom':0})

            
            
            
            ],
    style={'display': 'inline-block','width': '49.95%', 'height': '490px','vertical-align': 'top', 'marginLeft': '0.05%','marginRight': 0,'marginBottom': '0.05%', 'backgroundColor': colors['background']}),
    html.H3(children='Interest History: Flexible Products',style={'color': 'white','display': 'inline-block','width': '49.95%','textAlign': 'center','font-size': '18px', 'backgroundColor': colors['background'],'marginLeft': 0,'marginTop':0,'marginBottom':0,'marginRight':'0.05%', 'padding': '2px 0px 2px 0px' }),
    html.H3(children ='Interest History: Fixed Products',style={'color': 'white','display': 'inline-block','width': '49.95%','textAlign': 'center','font-size': '18px', 'backgroundColor': colors['background'],'marginLeft': '0.05%','marginTop':0,'marginBottom':0, 'padding': '2px 0px 2px 0px' }),
    html.H2(children =title2,style={'color': 'white','display': 'inline-block','width': '49.95%','textAlign': 'center','font-size': '18px', 'backgroundColor': colors['background'],'marginRight': '0.05%','marginTop':0,'marginBottom':'0.05%', 'padding': '2px 0px 2px 0px' }),
    html.H2(children =title1,style={'color': 'white','display': 'inline-block','width': '49.95%','textAlign': 'center','font-size': '18px', 'backgroundColor': colors['background'],'marginLeft': '0.05%','marginTop':0,'marginBottom':'0.05%', 'padding': '2px 0px 2px 0px' }),
    
    html.Div([
        
        
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'border': 'thin black solid'

            
        },    
        style_table={
            'height': '100px',
            'marginTop':'3%',
            'marginLeft':'3%',
            'marginRight':'3%',
            'marginBottom':'3%',
            'width': '94.0%'

            
            
            
            
            
            
            }
        
        )],
        style={'overflowX': 'scroll','overflowY': 'scroll','display': 'inline-block','width': '49.95%', 'height': '290px','vertical-align': 'top', 'marginLeft': '0.05%','marginRight': 0,'marginBottom': '0.05%', 'backgroundColor': colors['background']}),

               
    html.Div([
        
        
                  
        dash_table.DataTable(
            id='table2',
            columns=[{"name": i, "id": i} for i in df2.columns],
            data=df2.to_dict('records'),
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            
            style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'border': 'thin black solid'
        },    
        style_table={
            'height': '100px',
            'marginTop':'3%',
            'marginLeft':'3%',
            'marginRight':'3%',
            'marginBottom':'3%',
            'width': '94.0%'
            
            

            
            }
      


    )],
    

    style={'overflowX': 'scroll','overflowY': 'scroll','display': 'inline-block','width': '49.95%', 'height': '290px','vertical-align': 'top', 'marginLeft': '0.05%','marginRight': 0,'marginBottom': '0.05%', 'backgroundColor': colors['background']}),
    html.H3(children='Historical Portfolio Return',style={'color': 'white','display': 'inline-block','width': '100%','textAlign': 'center','font-size': '22px', 'backgroundColor': colors['background'],'marginLeft': 0,'marginTop':0,'marginBottom':0, 'padding': '2px 0px 2px 0px' }),
    html.H2(children =Portfolio_performance,style={'color': 'white','display': 'inline-block','width': '100%','textAlign': 'center','font-size': '18px', 'backgroundColor': colors['background'],'marginRight': '0.05%','marginTop':0,'marginBottom':'0.05%', 'padding': '2px 0px 2px 0px' }),
    html.Div([
        dcc.Graph(
            id='example-graph2',
            
            figure={
                'data': [
                    {'x': df_new3.index, 'y': df_new3['interest3'], 'type': 'line', 'name': 'Portfolio','marker':dict(color='#f48229')}
                    
                ],
                
                'layout': {
                    #'title': Portfolio_performance,
                    'yaxis' : {
                        'tickformat':'$'},
                    'plot_bgcolor': colors['background'],
                    'colors':'farben',
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text'],
                        'family':'Arial',
                        'size':'14'
                    },
                    
                    'legend': {'showlegend':True,'font':'10','x':'3','y': '3', 'title':'asdada'},
                    'xaxis':{
                    'rangeslider':{
                    'visible':True},
                        'rangeselector':{
                            'bgcolor': '#323232',
                            'buttons':[
                                {'count':1,
                                'label':'1m',
                                'step':'month',
                                'stepmode':'backward'

                                },
                                
                                {'count':6,
                                'label':'6m',
                                'step':'month',
                                'stepmode':'backward'},
                                {'count':1,
                                'label':'YTD',
                                'step':'year',
                                'stepmode':'todate'},
                                {'count':1,
                                'label':'1y',
                                'step':'year',
                                'stepmode':'backward'}                                
                                ],
                            'buttonTheme': {    
                                'fill': 'none',
                                'stroke': 'none',
                                'stroke-width': 0,
                                'r': 8,
                                'style': {
                                    'color': '#039',
                                    'fontWeight': 'bold'
                                },
                                'states': {
                                    'hover': {
                                    },
                                    'select': {
                                        'fill: '#039',
                                        'style': {
                                            'color': 'white'
                                        }
                                    }
                                    
                                }
                            }

                    }
                    
                    }
                    
                        


                        
                    

                    
                }
                
            })



    ],
    
    style={'maxWidth': '100%', 'maxHeight': '400px', 'minHeight': '400px', 'padding': '0px 0px 2px 2px', 'backgroundColor': colors['background'], 'marginLeft': 0, 'marginRight': 0,'marginBottom':0}
    
    ),
    #   html.H4(
    #children='Account Summary',
    #style={
    #    'color': 'white',
    #    
    #    'minWidth': '900px',
    #   'textAlign': 'center'}),

])
    
@app.callback(
    Output('example-graph', 'figure'),
    [Input('year_slider', 'value')])

def update_figure(min_date):
    minimum = min_date[0]
    minimum= sub_final[min_date[0]]
    minimum= final.index(minimum)
    maximum = min_date[-1]
    maximum= sub_final[min_date[-1]]
    maximum= final.index(maximum)
    
    
    global labels_new
    global labels2_new
    labels2_new = final[minimum:maximum]
    labels_new = final[minimum:maximum ]
    global values_new
    global values2_new
    values_new = values[minimum:maximum]
    values2_new =values2[minimum:maximum]
    
    return {
            'data': [
                    {'x': labels_new, 'y': values, 'type': 'bar', 'name': 'flexible','marker':dict(color='#f48229')},
                    {'x': labels2_new, 'y': values2, 'type': 'bar', 'name': 'fixed','marker':dict(color='#2171f3')},
                ],
                
             'layout': {
                    'title': 'Interest payouts ($)',
                    'yaxis' : {
                        'tickformat':'$'},
                    'plot_bgcolor': colors['background'],
                    'colors':'farben',
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text'],
                        'family':'Arial',
                        'size':'14',
                    'xaxis': {
                        'range':final[minimum:maximum]
                    }
                    },
                'legend': {
                        'x':'1',
                        'y': '0.4'
                        


                        
                    }
                    
                }}






if __name__ == '__main__':
    app.run_server(debug='False')

