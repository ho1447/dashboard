import dash, json 
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from scrapingstock import saveSp500StocksInfo, getfinancialreportingdf, includecalcvariablesdf, save_self_stocks_info, getetfdf, getbettermentlist, getgTrendsdf, getEconEventdf, getStkdf, getinvestorsdf, getetfdf2, getcandlestickdf, getkddf, getrsidf
from checkeligibility import checkeligibility
from decision import getprice
from pandas_datareader import data
from datetime import datetime as dt
import numpy as np
import dash_table
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = dash.Dash(__name__)
server = app.server

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'color': '#696969',
    'backgroundColor': 'white',
    'fontWeight': 'bold',
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
}

app.layout = html.Div(
    children=[
        html.Header(
            html.H1('ETF Investing'),   
        ),
        html.Div(
            id='app-container',
            children=[
                dcc.Tabs(
                    children=[
                        #first tab
                        dcc.Tab(
                            label='ETF',
                            className='tab',
                            id='tab1',
                            children=[
                                html.Div(
                                    className='row',
                                    children=[
                                       #first tab left column
                                        html.Div(
                                            id='left-col1',
                                            className='six columns',
                                            children=[
                                                #dropdown to choose stk ticker
                                                html.Div(
                                                    children=[    
                                                        html.H2('Choose an ETF ticker'),
                                                        dcc.Dropdown(id='my-dropdown', options=getbettermentlist(), value='VEA'),                            
                                                    ],
                                                    className='etf-dropdown',
                                                ),
                                                html.Div(
                                                    children=[
                                                        #table of critical values and ratios
                                                        html.H2('Critical Values and Ratios'),
                                                        html.Div(
                                                            children=[
                                                                html.Table(id='my-table'),               
                                                            ],
                                                            className='table',
                                                            style={'display': 'inline-block','text-align': 'left'}
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Table(id='my-table1'),               
                                                            ],
                                                            className='table',
                                                        ),
                                                    ],
                                                ),
                                            ],
                                        ),
                                        #first tab right column
                                        html.Div(
                                            id='right-col1',
                                            className='six columns',
                                            children=[
                                                #graph of stk price
                                                html.H2('ETF 5-year Price Graph'),
                                                html.Div(
                                                    children=[
                                                        dcc.Graph(id='my-graph'),
                                                    ],
                                                    className='graph',
                                                ),                            
                                            ]
                                        )
                                    ]
                                )
                            ],
                            style=tab_style, selected_style=tab_selected_style,
                        ),
                        #second tab
                        dcc.Tab(
                            label='Dow Jones 30',
                            id='tab2',
                            className='tab',
                            children=[
                                #left column
                                html.Div(
                                    id='left-col',
                                    className='six columns',
                                    children=[
                                        html.Div(
                                            id='left-col2',
                                            className='six columns',
                                            children=[
                                                #dropdown to choose stk ticker
                                                html.Div(
                                                    children=[
                                                        html.H2('Choose a stock ticker'),
                                                        dcc.Dropdown(id='my-dropdown2', options=save_self_stocks_info(), value='AAPL')
                                                    ],
                                                    className='stk-dropdown',
                                                ),
                                                #basic stock info 
                                                html.H2('Basic Stock Information'),
                                                html.Div(
                                                    children=[
                                                        html.Table(id='my-table2'),
                                                    ],
                                                    className='table',
                                                ),      
                                                # investor 
                                                html.H2('Investors\' Holdings'),
                                                html.Div(
                                                    children=[
                                                        dcc.Graph(id='investor_graph')
                                                        #html.Table(id='my-table4'),
                                                    ],
                                                    className='table',
                                                ),                              
                                            ],
                                        )
                                    ],
                                ),
                                #right column
                                html.Div(
                                    id='right-col',
                                    className='six columns',
                                    children=[ 
                                #second part of right column
                                        html.Div(
                                            id='right-col2',
                                            className='six columns',
                                            children=[  
                                                # google trends
                                                html.H2('Google Trends'),
                                                html.Div(
                                                    children=[
                                                        dcc.Graph(id='my-graph2'),
                                                    ],
                                                    className='graph',
                                                ),          
                                                #econ events table
                                                html.H2('Upcoming Economic Events'),
                                                html.Div(
                                                    children=[
                                                        html.Table(id='my-table3'),
                                                    ],
                                                    className='table',
                                                ),
                                            ],
                                        ), 
                                    ],
                                ), 
                            ],
                            style=tab_style, selected_style=tab_selected_style
                        ),
                        #third tab
                        dcc.Tab(
                            label=('Analysis'),
                            children=[
                                html.Div(
                                    id='whole-page',
                                    className='twelve columns',
                                    children=[
                                        #candlestick chart
                                        html.H2('Technical Analysis'),
                                        html.Div(
                                            children=[
                                                dcc.Graph(id='my-graph3'),
                                            ],
                                            className='graph',
                                        ),   
                                    ],
                                )
                            ],
                            style=tab_style, selected_style=tab_selected_style
                        )
                    ],
                    style={'margin': '0', 'height': '80px'}
                )
            ]
        )        
    ]
)



#stocks graph
@app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
def graphing(selectedValue):
    stockPricedf = data.DataReader(selectedValue.strip(), 'yahoo', dt(2015,1,1), dt.now())
    return {
        'data': [{
            'x': stockPricedf.index,
            'y': stockPricedf.Close
        }]
    }

#first critical values table
@app.callback(Output('my-table', 'children'), [Input('my-dropdown', 'value')])
def generate_table(selectedValue,max_rows=10):
    financialreportingdf = getetfdf(selectedValue.strip().lower()).reset_index()
    # Header
    return [html.Tr([html.Th(col) for col in financialreportingdf.columns])]+ [html.Tr([
        html.Td(financialreportingdf.iloc[i][col]) for col in financialreportingdf.columns
    ]) for i in range(min(len(financialreportingdf), max_rows))]

#second critical values table
@app.callback(Output('my-table1', 'children'), [Input('my-dropdown', 'value')])
def generate_table2(selectedValue,max_rows=10):
    financialreportingdf = getetfdf2(selectedValue.strip().lower()).reset_index()
    # Header
    return [html.Tr([html.Th(col) for col in financialreportingdf.columns])]+ [html.Tr([
        html.Td(financialreportingdf.iloc[i][col]) for col in financialreportingdf.columns
    ]) for i in range(min(len(financialreportingdf), max_rows))]

#visualize google trends table
@app.callback(Output('my-graph2', 'figure'), [Input('my-dropdown', 'value')])
def generate_gTrends_graph(selectedValue):
    gTrendsdf = getgTrendsdf(selectedValue)
    # Header
    return {
        'data':[{
            'x': gTrendsdf.index,
            'y': gTrendsdf[selectedValue],
        }]
    }

#table of basic info
@app.callback(Output('my-table2', 'children'), [Input('my-dropdown2', 'value')])
def generate_basic_table(selectedValue):
    basicdf = getStkdf(selectedValue)
    return [html.Tr([html.Th(col) for col in basicdf.columns])]+[html.Tr([
            html.Td(basicdf.iloc[i][col]) for col in basicdf.columns
        ]) for i in range(min(len(basicdf), 10))]

#table of econ events
@app.callback(Output('my-table3', 'children'), [Input('my-dropdown2', 'value')])
def generate_econ_table(selectedValue):
    econdf = getEconEventdf()
    return [html.Tr([html.Th(col) for col in econdf.columns])]+[html.Tr([
            html.Td(econdf.iloc[i][col]) for col in econdf.columns
        ]) for i in range(min(len(econdf), 10))]

#table of investors
# @app.callback(Output('my-table4', 'children'), [Input('my-dropdown2', 'value')])
# def generate_investor_table(selectedValue):
#     investordf = getinvestorsdf(selectedValue)
#     return [html.Tr([html.Th(col) for col in investordf.columns])]+[html.Tr([
#             html.Td(investordf.iloc[i][col]) for col in investordf.columns
#         ]) for i in range(min(len(investordf), 10))]

#bar chart of investors
@app.callback(Output('investor_graph', 'figure'), [Input('my-dropdown2', 'value')])
def generate_bar(selectedValue):
    investordf = getinvestorsdf(selectedValue)
    inv = go.Bar(
        x=list(investordf['知名投資人']),
        y=list(investordf['股權佔比']),
    )
    print(investordf['知名投資人'])
    print(investordf['股權佔比'])
    return {'data':[inv]}


#candlestick chart
@app.callback(Output('my-graph3', 'figure'), [Input('my-dropdown2', 'value')])
def generate_candlestick(ticker):
    sma_range = 200
    candlestickdf=getcandlestickdf(ticker)
    graph_candlestick = go.Candlestick(
            x=candlestickdf['Date'],
            open=candlestickdf['Open'],
            high=candlestickdf['High'],
            low=candlestickdf['Low'],
            close=candlestickdf['Close'],
            xaxis='x',
            yaxis='y2',
            name=ticker
        )
    #calc sma
    def movingaverage(interval, window_size=10):
        window = np.ones(int(window_size))/float(window_size)
        return np.convolve(interval, window, 'same')
    mv_y = movingaverage(candlestickdf.Close)
    mv_x = list(candlestickdf.index)

    # Clip the ends
    mv_x = mv_x[1:-1]
    mv_y = mv_y[1:-1]

    sma = dict( x=mv_x, y=mv_y, type='scatter', mode='lines', 
                            line = dict( width = 1 ),
                            marker = dict( color = '#E377C2' ),
                            name='Moving Average', yaxis='y2', xaxis='x')

    #volume chart
    colors = []
    increasing_color='#3D9970'
    decreasing_color='#FF4136'
    for i in range(len(candlestickdf.Close)):
        if i != 0:
            if candlestickdf.Close[i] > candlestickdf.Close[i-1]:
                colors.append(increasing_color)
            else:
                colors.append(decreasing_color)
        else:
            colors.append(decreasing_color)
    volume = go.Bar(
        x=candlestickdf.index, y=candlestickdf.Volume, marker_color=colors,                     
        type='bar', xaxis='x', yaxis='y3', name='Volume'
    )

    #calc kd
    kd_df = getkddf(ticker)
    K = dict(
        x=kd_df['Date'],
        y=kd_df['K'],
        name='K',
        xaxis='x',
        mode='lines',
        marker_color='#6B99E5'
    )
    D= dict(
        x=kd_df['Date'],
        y=kd_df['D'],
        name='D',
        xaxis='x',
        mode='lines',
        marker_color='#E58B6B'
    )

    #calc rsi
    rsi_df=getrsidf(ticker)
    rsi = dict(
        x=rsi_df['Date'],
        y=rsi_df['RSI'],
        name='RSI',
        xaxis='x',
        mode='lines',
    )    
    
    #create subplots for all the graphs
    fig = make_subplots(rows=5,subplot_titles=('Volume', 'Candlestick Chart v.s. SMA200', '','RSI Value', 'KD Value'),shared_xaxes=True,vertical_spacing=0.08,\
        #     specs=[[{}],
        #    [{"rowspan": 2}],
        #    [None],
        #    [{}],
        #    [{}]],
        )
    fig.add_trace(volume, row=1,col=1)
    fig.add_trace(graph_candlestick,row=2,col=1)
    fig.add_trace(sma,row=2,col=1)
    fig.add_trace(rsi, row=4, col=1)
    fig.add_trace(K,row=5,col=1)
    fig.add_trace(D,row=5,col=1)
    fig.update_layout(height=1500, width=1200, xaxis_showticklabels=True, xaxis2_showticklabels=True, xaxis3_showticklabels=True, \
        xaxis2_rangeslider_thickness=0.1, xaxis4_rangeslider_thickness=0.1)

    #rangeselector
    rangeselector=dict(
        visible = True,
        x = 0, y = 1.02,
        bgcolor = 'rgba(150, 200, 250, 0.4)',
        font = dict( size = 13 ),
        buttons=list([
            dict(count=1,
                label='reset',
                step='all'),
            dict(count=1,
                label='1yr',
                step='year',
                stepmode='backward'),
            dict(count=3,
                label='3 mo',
                step='month',
                stepmode='backward'),
            dict(count=1,
                label='1 mo',
                step='month',
                stepmode='backward'),
            dict(step='all')
        ]))
    
    #update the rangeselector and hide rangesliders that are not needed
    fig['layout']['xaxis']['rangeselector'] = rangeselector
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.update_xaxes(rangeslider= {'visible':True}, row=2, col=1)
    fig.update_xaxes(rangeslider= {'visible':False}, row=4, col=1)
    fig.update_xaxes(rangeslider= {'visible':True}, row=5, col=1)

    return fig
    # {'data':[graph_candlestick, sma, volume, K, D], 'layout':{'plot_bgcolor': 'rgb(250, 250, 250)',\
    #     'yaxis': dict(tickprefix='$'),'yaxis2':dict(constrain='domain'),'yaxis3':dict(constrain='domain'),\
    #          'legend': dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom')}}
    # https://chart-studio.plotly.com/~jackp/17421/plotly-candlestick-chart-in-python/#/


if __name__ == '__main__':
    app.run_server(debug=True)
