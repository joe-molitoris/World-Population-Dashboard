import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objs as go
from math import ceil
from dash.exceptions import PreventUpdate
import pathlib

# Sets the relative path
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

# Load the data
df = pd.read_csv(DATA_PATH.joinpath("UN_demographic_data.csv"))
df_pp = pd.read_csv(DATA_PATH.joinpath("UN_population_pyramid_data.csv"))
region_df = pd.read_csv(DATA_PATH.joinpath("Continent Codes.csv"), encoding='latin1')

# Defines functions to create traces and layouts
cols = [col for col in region_df.columns]
region_df = region_df.fillna("nan")
for i in cols:
    continent_dict={i:region_df[i].values.tolist() for i in cols}
for i in cols:
    continent_dict[i]=[val for val in continent_dict[i] if val!="nan"]

input_values=["{}-{}".format(i, i+5) for i in range(1950,2100, 5)]

def create_trace(x, y1, y2, area='World',startdate=1950, enddate=2100):
    trace1=[
            {
            'x':df[(df['Country or Area']==area) & (df['Year']>=startdate) & (df['Year']<=enddate)][x],
            'y':df[(df['Country or Area']==area) & (df['Year']>=startdate) & (df['Year']<=enddate)][y1],
            'mode':'lines',
            'name':area,
            'showlegend':False,
            'hovertemplate':y1+': %{y:.1f}',
            'marker':{'opacity':0.8},
        },
            {
            'x':df[(df['Country or Area']==area) & (df['Year']>=startdate) & (df['Year']<=enddate)][x],
            'y':df[(df['Country or Area']==area) & (df['Year']>=startdate) & (df['Year']<=enddate)][y2],
            'mode':'lines',
            'name':area,
            'showlegend':False,
            'hovertemplate':y2+': %{y:.1f}',
            'marker':{'opacity':0.8, 'color':'#00C15D'},
            'yaxis':'y2'
            }
        ]
    return trace1

def create_layout(y1, y2, startdate=1950, enddate=2100):
    axis_font_style={'size':11, 'family':'Franklin Gothic Medium', 'color':'#999B9A'}
    hover_font_style={'size':11, 'family':'Franklin Gothic Medium', 'color':'rgb(255,255,255)'}
    layout1= dict(
            xaxis={'title':{
                'text':'Year',
            }, 'range':[startdate,enddate], 'gridcolor': '#3a3a3b', 'gridwidth':0.1},
            yaxis={'title':{
                'text':y1,
                'automargin':True,
            }, 'gridcolor': '#3a3a3b', 'gridwidth':0.1,
            },
            yaxis2={'title':{
                'text':y2,
            }, 'gridcolor': '#3a3a3b', 'gridwidth':0.1, 
            'side':'right', 
            'overlaying':'y', 
            'automargin':True},
            font=axis_font_style,
            hoverlabel={'font':hover_font_style},
            paper_bgcolor='#2e2e30',
            plot_bgcolor='#2e2e30',
            margin={'l':40,'b':40,'t':10,'r':20}
        )
    return layout1

def pyramid_trace(area='World', year="2015-2020"):
    df_pp_new=df_pp[(df_pp['Country or Area']==area) & (df_pp['Year(s)']==year)]
    trace=[
            {
            'x': df_pp_new['percent_males']*-1, 
            'y': df_pp_new['Age'], 
            'type': 'bar', 
            'name':'Males', 
            'orientation':'h',
            'showlegend':False,
            'hovertemplate':'%{text}%',
            'text':['{0:.1f}'.format(i*-1) for i in df_pp_new['percent_males']*-1],
            'marker':{'opacity':0.8},
            },
            {
            'x': df_pp_new['percent_females'], 
            'y': df_pp_new['Age'], 
            'type': 'bar', 
            'name':'Females', 
            'orientation':'h',
            'showlegend':False,
            'hovertemplate':'%{x: 0.1f}%',
            'marker':{'opacity':0.8, 'color':'#00C15D'}
            }
        ]
    return trace

def pyramid_layout(area='World', year="2015-2020"):
    df_pp_new=df_pp[(df_pp['Country or Area']==area) & (df_pp['Year(s)']==year)]
    axis_font_style={'size':11, 'family':'Franklin Gothic Medium', 'color':'#999B9A'}
    hover_font_style={'size':11, 'family':'Franklin Gothic Medium', 'color':'rgb(255,255,255)'}
    range_scope=max(int(df_pp_new['percent_males'].max()*-1), int(df_pp_new['percent_females'].max()+1))
    tickvals=[i for i in range(range_scope*-1, range_scope+1)]
    ticktext=[abs(i) for i in tickvals]
    layout=dict(
            xaxis={
                'title':{
                    'text':'Percent',
                    },
                'range':[
                    max(df_pp_new['percent_males'].max().astype(int)+1, df_pp_new['percent_females'].max().astype(int)+1)*-1,
                    max(df_pp_new['percent_females'].max().astype(int)+1 ,df_pp_new['percent_females'].max().astype(int)+1)
                ],
                'tickmode':'array',
                'tickvals': tickvals, 
                'ticktext': ticktext,
                'gridcolor': '#3a3a3b', 'gridwidth':0.1
                },
            yaxis={
                'title':{
                    'text':'Age',
                    }
                },
            barmode='overlay',
            font=axis_font_style,
            hoverlabel={'font':hover_font_style},
            margin={'l':40, 'b':40, 't':10, 'r':10},
            bargap=0.1,
            paper_bgcolor='#2e2e30',
            plot_bgcolor='#2e2e30',
            annotations=[
                dict(
                    x= max([i for i in range(int(df_pp_new['percent_males'].max()*-1), int(df_pp_new['percent_females'].max()+1))]),
                    y=100,
                    text=year,
                    xanchor='right',
                    yanchor='top',
                    showarrow=False,
                    font=dict(
                        color='#38b3d9',
                        family='Franklin Gothic Medium',
                        size=12
                    )
                )
            ]

        )
    return layout    

def create_table(area, year_value):
    test_df=df[(df['Country or Area']==area) & (df['Year(s)']==year_value)][['Total Population', 'Population Change (%)','Total Fertility Rate', 'Life Expectancy at Birth', 'Infant Mortality Rate', 'Net Migration Rate', 'Sex Ratio at Birth']].copy()

    pp_test = df_pp[(df_pp['Country or Area']==area) & (df_pp['Year(s)']==year_value)].copy()

    pp_test['percent_all']=pp_test['percent_males']+pp_test['percent_females']
    pp_test['age_group']=pd.cut(pp_test['Age'], [0, 10, 60, 100], labels=["<15", "15-64", "65+"], include_lowest=True)
    pp_test2=pp_test.groupby(['age_group'])['percent_all'].sum().reset_index()
    test_df['Youth Dependency Ratio']=round(pp_test2.iloc[0,1]/pp_test2.iloc[1,1]*100, 2)
    test_df['Old Age Dependency Ratio']=round(pp_test2.iloc[2,1]/pp_test2.iloc[1,1]*100, 2)
    test_df = test_df.rename(columns={'Total Population':'Total Population (in 1000s)'})
    test_df = test_df.T.reset_index()
    test_df.columns = [area,'Value']

    return test_df

def create_map(country_value=None):
    temp_df=df.groupby('Country or Area').head(1)
    columns = [i for i in temp_df.columns]
    vals = ['Taiwan', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'TWN', 0]
    data = dict(zip(columns,vals))
    taiwan = pd.DataFrame(data, index=[0])
    temp_df=temp_df.append(taiwan)

    if country_value=="World":
        temp_df['shade']=1
    else:
        temp_df['shade']=np.nan
        if country_value in list(continent_dict.keys()):
            temp_df.loc[temp_df['Country or Area'].isin(continent_dict[country_value]), 'shade']=1
        else:
            temp_df.loc[temp_df['Country or Area']==country_value, 'shade']=1
        temp_df['shade']=temp_df['shade'].fillna(-100)
    trace=[go.Choropleth(
        locations=temp_df['iso_alpha'],
        name="Country or Area",
        z=temp_df['shade'],
        text=temp_df['Country or Area'],
        hovertemplate="%{text}",
        autocolorscale=False,
        colorscale=[[0, "gray"],[0.1, '#38b3d9'],[1, '#38b3d9']],
        showscale=False,
        marker_line_width=0.5,
        unselected={'marker':{'opacity': 0.3}}
    )
    ]
    return trace

def map_layout():
    hover_font_style={'size':11, 'family':'Franklin Gothic Medium', 'color':'rgb(255,255,255)'}
    layout=dict(
        geo={'showframe':False,
                'showcoastlines':False,
                'projection':{'type':'miller'},
                'showland':False,
                'showcountries':True,
                'visible':True,
                'countrycolor':'#2e2e30',
                'showocean':True,
                'oceancolor':'#2e2e30',
                'lataxis':{'range':[-40, 90]}},
        margin= {'l':0, 'b':0, 't':0, 'r':0},
        paper_bgcolor='#2e2e30',
        plot_bgcolor='#2e2e30',
        hoverlabel={'font':hover_font_style}
    )
    return layout
######################################################

# Create traces, layouts, and styling
trace1=create_trace('Year', 'Life Expectancy at Birth', 'Infant Mortality Rate')
layout1=create_layout('Life Expectancy at Birth', 'Infant Mortality Rate')

trace2=create_trace('Year', 'Total Population', 'Population Change (%)')
layout2=create_layout('Total Population', 'Population Change (%)')

trace3=pyramid_trace()
layout3=pyramid_layout()

trace4=create_trace('Year', 'Total Fertility Rate', 'Mean Age at Birth')
layout4=create_layout('Total Fertility Rate', 'Mean Age at Birth')

trace5=create_trace('Year', 'Net Migrants', 'Net Migration Rate')
layout5=create_layout('Net Migrants', 'Net Migration Rate')

table = create_table("World", "2015-2020")

trace_map = create_map('World')
layout_map= map_layout()

trace1245_style = {'marginLeft':15, 'marginRight':15}
trace3_style = {'marginLeft':15}

trace_dimensions = {'height':300, 'width':300}
##########################################################

# Creates app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/jmolitoris/pen/BaNpwVy.css'])

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H1(children = "World Demographic Profiles", 
                        style={
                            'fontSize':26,
                            'font-family':'Franklin Gothic Medium', 
                            'font-weight':'normal',
                            'marginLeft':15,
                            'marginTop': 10},
                        className='four columns'
                ),

                html.Div([
                    html.H1(children="", className='one columns')
                ]),


                html.Div([
                    dcc.Markdown(children='''
                        *Use this menu to view data for a specific country or region*
                    ''')
                ], className='two columns', 
                    style={'fontSize':11,
                            'font-family':'Franklin Gothic Medium',
                            'fontWeight':'normal',
                            'marginTop':5,
                            'color':'#a1a1a1'
                        }
                    ),

                html.Div([
                    dcc.Dropdown(
                        id='dropdown',
                        options=[
                            {'label':i, 'value':i} for i in df['Country or Area'].unique()
                        ],
                        multi=False,
                        value='World',
                        placeholder='Select population...',
                        style={'backgroundColor': '#a1e9ff'
                        }
                    )
                ], className='two columns', 
                style={
                    'font-family':'Franklin Gothic Medium',
                    'marginTop': 10
                    }
                ),
                html.Div([
                    html.A(children='Follow me on Twitter', 
                            href="https://twitter.com/JoeMolitoris?ref_src=twsrc%5Etfw",
                            className="twitter-follow-button"),
                    html.Br(),
                    html.A(children="Follow me on ResearchGate", 
                            href="https://www.researchgate.net/profile/Joseph_Molitoris"),
                ], className='two columns', 
                    style={'marginTop':5, 
                            'marginLeft':90, 
                            'font-family':'Franklin Gothic Medium'}),
            ], className='row', 
                style={'background-color':'#383838'
                        }),
            
            html.Div([
                dcc.Markdown(children = '''
                                    *Use this dashboard for a quick overview of the past, present, and future
                                    demographic circumstances of the world's populations.*
                                    ''',
                        style={
                            'fontSize':14,
                            'font-family':'Franklin Gothic Medium', 
                            'font-weight':'normal',
                            'marginLeft':15},
                        className='four columns'
                ),

                html.Div([
                    html.H1(children="", className='one columns')
                ]),

                html.Div([
                    dcc.Markdown(children='''
                        *Use this menu to view the selected population's age structure and statistics for specific years*
                    ''')
                ], className='two columns', 
                    style={'fontSize':11,
                            'font-family':'Franklin Gothic Medium',
                            'fontWeight':'normal',
                            'marginTop':5,
                            'color':'#a1a1a1'
                        }
                    ),

                html.Div([
                    dcc.Dropdown(
                        id='year_input',
                        placeholder='Select a year...',
                        options= [{'label':i, 'value':i} for i in input_values],
                        multi=False,
                        disabled=False,
                        value='2015-2020',
                        style={'backgroundColor': '#a1e9ff'
                                }
                    )
                ], className='two columns', 
                style={'font-family':'Franklin Gothic Medium'}
                ),
            ], className='row', style={'background-color': '#383838'}),
        ]),

        html.Div([
            html.H1(children="", className='twelve columns'),
        ],
            className='row', style={'background-color': '#383838'}),

        html.Div([
            html.Div([
                html.H4(children="Population Overview",
                        className="two columns",
                        style={
                            'text-align':'left',
                            'font-family':'Franklin Gothic Medium',
                            'fontSize':20,
                            'font-weight':'normal',
                            'marginLeft':15
                        }),
                html.H4(children="Age Structure",
                        className='four columns',
                        style={
                            'text-align':'left',
                            'font-family':'Franklin Gothic Medium',
                            'fontSize':20,
                            'font-weight':'normal',
                            'marginLeft':20
                        }
                )
            ], className='row'),
        ], className='row'),

        html.Div([
            html.Div([
                dash_table.DataTable(
                    id='table',
                    columns=[{'name':i, 'id':i} for i in table.columns],
                    data=table.to_dict('records'),
                    style_as_list_view=True,
                    style_cell={'fontSize':12, 
                                'font-family':'Franklin Gothic Medium',
                                'overflow':'hidden',
                                'textOverflow':'ellipses',
                                'minWidth':'0px',
                                'maxWidth':'150px',
                                'backgroundColor':'rgb(50,50,50',
                                'color':'white'
                                },
                    style_cell_conditional=[
                        {
                            'if':{'column_id':'World'},
                            'textAlign':'left'
                    }
                    ],
                    style_data_conditional=[
                        {
                            'if': {'row_index':'odd'},
                            'backgroundColor': 'rgb(100,100,100)'
                        }
                    ],
                    style_header={
                        'backgroundColor':'rgb(76,76,76)',
                        'fontWeight':'bold'
                    }
                )
            ], className= 'four columns', style={'width':200, 'marginLeft':15, 'marginRight':15}),
            
            html.Div([
                dcc.Graph(
                    id='graph-3',
                    style={'height':300},
                    figure={
                        'data': trace3,
                        'layout': layout3
                    }
                )
            ], className='four columns'),

            html.Div([
                dcc.Graph(
                    id='map',
                    style={'height':300, 'width':500},
                    figure={
                        'data':trace_map,
                        'layout':layout_map
                    }
                )
            ], className='four columns')
        ], className='row'),

        html.Br(),
        html.Div([
            html.H4(children='Population Growth',
                    className='three columns',
                    style={
                        'text-align':'left',
                        'font-family':'Franklin Gothic Medium',
                        'fontSize':20,
                        'font-weight':'normal',
                        'marginLeft':15}               
            ),
            html.H4(children='Mortality',
                    className='three columns',
                    style={
                        'text-align':'left',
                        'font-family':'Franklin Gothic Medium',
                        'fontSize':20,
                        'font-weight':'normal',
                        'marginLeft':30}
            ),
            html.H4(children='Fertility',
                    className='three columns',
                    style={
                        'text-align':'left',
                        'font-family':'Franklin Gothic Medium',
                        'fontSize':20,
                        'font-weight':'normal',
                        'marginLeft':30}
            ),
            html.H4(children='Migration',
                    className='three columns',
                    style={
                        'text-align':'left',
                        'font-family':'Franklin Gothic Medium',
                        'fontSize':20,
                        'font-weight':'normal',
                        'marginLeft':30}
            ),            
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id = 'graph-2',
                    style=trace_dimensions,
                    figure={
                        'data': trace2,
                        'layout':layout2
                    }
                )
            ], className= 'three columns', style=trace1245_style),

            html.Div([
                dcc.Graph(
                    id = 'graph-1',
                    style=trace_dimensions,
                    figure={
                        'data':trace1,
                        'layout': layout1
                    }
                )
            ], className= 'three columns', style=trace1245_style),

            html.Div([
                dcc.Graph(
                    id='graph-4',
                    style=trace_dimensions,                
                    figure={
                        'data': trace4,
                        'layout': layout4
                    }
                )
            ], className='three columns', style=trace1245_style),

            html.Div([
                dcc.Graph(
                    id='graph-5',
                    style=trace_dimensions,
                    figure={
                        'data': trace5,
                        'layout': layout5
                    }
                )
            ], className='three columns', style=trace1245_style),
        ], className='row'),

        html.Br(),

        html.Div([
            html.H1(children="",className='two columns'),
            html.P([
                dcc.RangeSlider(
                    id='slider',
                    min=df['Year'].min(),
                    max=2100,
                    step=5,
                    marks={str(i) : {'label' : str(i), 'style':{'color':'#999B9A'}} for i in range(1950,2105,25)},
                    value=[1950,2100],
                    disabled=True
                )
            ], className='eight columns', style={'font-family':'Franklin Gothic Medium'})
        ], className='row'),

        html.Div([
            dcc.Markdown(
                children= '''
                All data used on this page were downloaded from the United Nation's [*World Population Prospects 2019*](https://population.un.org/wpp/).
                '''
            )
        ], style={'fontSize':12,
                'font-family':'Franklin Gothic Medium', 
                'font-weight':'normal'})
    ], className='row')
], style={'backgroundColor':'#2e2e30', 'color':'#38b3d9'}, className='twelve columns')

#Update figures
@app.callback(
    Output(component_id='graph-1', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='slider', component_property='value')]
)

def update_figure1(country_value, slider_value):
    if country_value is None:
        raise PreventUpdate
    new_trace=create_trace('Year', 'Life Expectancy at Birth', 'Infant Mortality Rate',area=country_value, startdate=slider_value[0], enddate=slider_value[1])
    new_layout=create_layout('Life Expectancy at Birth', 'Infant Mortality Rate', startdate=slider_value[0], enddate=slider_value[1])
    df_new=df[(df['Country or Area']==country_value) & (df['Year']>=slider_value[0]) & (df['Year']<=slider_value[1])]
    return{
            'data':new_trace,
            'layout': new_layout
            }

@app.callback(
    Output(component_id='graph-2', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='slider', component_property='value')]
)

def update_figure2(country_value, slider_value):
    if country_value is None:
        raise PreventUpdate
    new_trace=create_trace('Year', 'Total Population', 'Population Change (%)',area=country_value, startdate=slider_value[0], enddate=slider_value[1])
    new_layout=create_layout('Total Population', 'Population Change (%)', startdate=slider_value[0], enddate=slider_value[1])
    df_new=df[(df['Country or Area']==country_value) & (df['Year']>=slider_value[0]) & (df['Year']<=slider_value[1])]
    return{
            'data': new_trace,
            'layout': new_layout
            }

@app.callback(
    Output(component_id='graph-4', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='slider', component_property='value')]
)

def update_figure4(country_value, slider_value):
    if country_value is None:
        raise PreventUpdate
    new_trace=create_trace('Year', 'Total Fertility Rate', 'Mean Age at Birth',area=country_value, startdate=slider_value[0], enddate=slider_value[1])
    new_layout=create_layout('Total Fertility Rate', 'Mean Age at Birth', startdate=slider_value[0], enddate=slider_value[1])
    df_new=df[(df['Country or Area']==country_value) & (df['Year']>=slider_value[0]) & (df['Year']<=slider_value[1])]
    return{
            'data':new_trace,
            'layout':new_layout
            }

@app.callback(
    Output(component_id='graph-5', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='slider', component_property='value')]
)

def update_figure5(country_value, slider_value):
    if country_value is None:
        raise PreventUpdate
    new_trace=create_trace('Year', 'Net Migrants', 'Net Migration Rate',area=country_value, startdate=slider_value[0], enddate=slider_value[1])
    new_layout=create_layout('Net Migrants', 'Net Migration Rate', startdate=slider_value[0], enddate=slider_value[1])
    df_new=df[(df['Country or Area']==country_value) & (df['Year']>=slider_value[0]) & (df['Year']<=slider_value[1])]
    return{
            'data':new_trace,
            'layout':new_layout
            }

@app.callback(
    Output(component_id='graph-3', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='year_input', component_property='value')]
)

def update_figure3(country_value, year_value):
    if country_value is None:
        raise PreventUpdate
    new_trace=pyramid_trace(area=country_value, year=year_value)
    new_layout=pyramid_layout(area=country_value, year=year_value)
    df_pp_new=df_pp[(df_pp['Country or Area']==country_value) & (df_pp['Year(s)']==year_value)]
    return{
            'data':new_trace,
            'layout': new_layout
        }
#Update Table
@app.callback(
    [Output(component_id='table', component_property='data'),
    Output(component_id='table', component_property='columns'),
    Output(component_id='table', component_property='style_cell_conditional')],
    [Input(component_id='dropdown', component_property='value'),
    Input(component_id='year_input', component_property='value')]
)

def update_table(area, year_value):
    if area is None:
        raise PreventUpdate
    new_table=create_table(area, year_value)
    columns=[{'name':i, 'id':i} for i in new_table.columns]
    style=[{'if':{'column_id':area}, 'textAlign':'left'}]
    return new_table.to_dict('records'), columns, style

#Enable slider and year input dropdown
@app.callback(
    [Output(component_id='slider', component_property='disabled'),
    Output(component_id='year_input', component_property='disabled')],
    [Input(component_id='dropdown', component_property='value')]
)

def toggle_on(country_value):
    if country_value is None:
        raise PreventUpdate
    return False, False

#Update available map

@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='dropdown', component_property='value')]
)

def update_map(country_value):
    if country_value is None:
        raise PreventUpdate
    new_trace_map = create_map(country_value)
    new_layout_map= map_layout()
    return {
        'data':new_trace_map,
        'layout':new_layout_map
    }

if __name__=='__main__':
    app.run_server()