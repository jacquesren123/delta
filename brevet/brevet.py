import sys
import dash
import flask
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px

class BrevetStats():
    START = 'Start'
    STOP  = 'Stop'

    def __init__(self, application = None):
        self.df = pd.read_pickle('data/subWDIdata.pkl')
        self.continent_colors = {'Asia':'gold', 'Europe':'green', 'Africa':'brown', 'Oceania':'red', 
                                 'Americas':'navy'}
        self.french = {'Asia':'Asie', 'Europe':'Europe', 'Africa':'Afrique', 'Oceania':'Océanie', 'Americas':'Amériques'}
        self.years = sorted(set(self.df.index.values))

        self.main_layout = html.Div(children=[
            html.H3(children='Évolution du taux de natalité vs le niveau moyen de revenu par pays'),

            html.Div('Déplacez la souris sur une bulle pour avoir les graphiques du pays en bas.'), 

            html.Div([
                    html.Div([ dcc.Graph(id='wps-main-graph'), ], style={'width':'90%', }),

                    html.Div([
                        html.Div('Continents'),
                        dcc.Checklist(
                            id='wps-crossfilter-which-continent',
                            options=[{'label': self.french[i], 'value': i} for i in sorted(self.continent_colors.keys())],
                            value=sorted(self.continent_colors.keys()),
                            labelStyle={'display':'block'},
                        ),
                        html.Br(),
                        html.Div('Échelle en X'),
                        dcc.RadioItems(
                            id='wps-crossfilter-xaxis-type',
                            options=[{'label': i, 'value': i} for i in ['Linéaire', 'Log']],
                            value='Log',
                            labelStyle={'display':'block'},
                        ),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Button(
                            self.START,
                            id='wps-button-start-stop', 
                            style={'display':'inline-block'}
                        ),
                    ], style={'margin-left':'15px', 'width': '7em', 'float':'right'}),
                ], style={
                    'padding': '10px 50px', 
                    'display':'flex',
                    'justifyContent':'center'
                }),            
            
            html.Div([
                html.Div(
                    dcc.Slider(
                            id='wps-crossfilter-year-slider',
                            min=self.years[0],
                            max=self.years[-1],
                            step = 1,
                            value=self.years[0],
                            marks={str(year): str(year) for year in self.years[::5]},
                    ),
                    style={'display':'inline-block', 'width':"90%"}
                ),
                dcc.Interval(            # fire a callback periodically
                    id='wps-auto-stepper',
                    interval=500,       # in milliseconds
                    max_intervals = -1,  # start running
                    n_intervals = 0
                ),
                ], style={
                    'padding': '0px 50px', 
                    'width':'100%'
                }),

            html.Br(),
            html.Div(id='wps-div-country'),

            html.Div([
                dcc.Graph(id='wps-income-time-series', 
                          style={'width':'33%', 'display':'inline-block'}),
                dcc.Graph(id='wps-fertility-time-series',
                          style={'width':'33%', 'display':'inline-block', 'padding-left': '0.5%'}),
                dcc.Graph(id='wps-pop-time-series',
                          style={'width':'33%', 'display':'inline-block', 'padding-left': '0.5%'}),
            ], style={ 'display':'flex', 
                       'borderTop': 'thin lightgrey solid',
                       'borderBottom': 'thin lightgrey solid',
                       'justifyContent':'center', }),

        ], style={
                #'backgroundColor': 'rgb(240, 240, 240)',
                 'padding': '10px 50px 10px 50px',
                 }
        )
        
        if application:
            self.app = application
            # application should have its own layout and use self.main_layout as a page or in a component
        else:
            self.app = dash.Dash(__name__)
            self.app.layout = self.main_layout

        # I link callbacks here since @app decorator does not work inside a class
        # (somhow it is more clear to have here all interaction between functions and components)

    def update_graph(self, regions, xaxis_type, year):
        dfg = self.df.loc[year]
        dfg = dfg[dfg['region'].isin(regions)]
        fig = px.scatter(dfg, x = "incomes", y = "fertility", 
                         #title = f"{year}", cliponaxis=False,
                         size = "population", size_max=60, 
                         color = "region", color_discrete_map = self.continent_colors,
                         hover_name="Country Name", log_x=True)
        fig.update_layout(
                 xaxis = dict(title='Revenus net par personnes (en $ US de 2020)',
                              type= 'linear' if xaxis_type == 'Linéaire' else 'log',
                              range=(0,100000) if xaxis_type == 'Linéaire' 
                                              else (np.log10(50), np.log10(100000)) 
                             ),
                 yaxis = dict(title="Nombre d'enfants par femme", range=(0,9)),
                 margin={'l': 40, 'b': 30, 't': 10, 'r': 0},
                 hovermode='closest',
                 showlegend=False,
             )
        return fig

    def create_time_series(self, country, what, axis_type, title):
        return {
            'data': [go.Scatter(
                x = self.years,
                y = self.df[self.df["Country Name"] == country][what],
                mode = 'lines+markers',
            )],
            'layout': {
                'height': 225,
                'margin': {'l': 50, 'b': 20, 'r': 10, 't': 20},
                'yaxis': {'title':title,
                          'type': 'linear' if axis_type == 'Linéaire' else 'log'},
                'xaxis': {'showgrid': False}
            }
        }


    def get_country(self, hoverData):
        if hoverData == None:  # init value
            return self.df['Country Name'].iloc[np.random.randint(len(self.df))]
        return hoverData['points'][0]['hovertext']

    def country_chosen(self, hoverData):
        return self.get_country(hoverData)

    # graph incomes vs years
    def update_income_timeseries(self, hoverData, xaxis_type):
        country = self.get_country(hoverData)
        return self.create_time_series(country, 'incomes', xaxis_type, 'PIB par personne (US $)')

    # graph children vs years
    def update_fertility_timeseries(self, hoverData, xaxis_type):
        country = self.get_country(hoverData)
        return self.create_time_series(country, 'fertility', xaxis_type, "Nombre d'enfants par femme")

    # graph population vs years
    def update_pop_timeseries(self, hoverData, xaxis_type):
        country = self.get_country(hoverData)
        return self.create_time_series(country, 'population', xaxis_type, 'Population')

    # start and stop the movie
    def button_on_click(self, n_clicks, text):
        if text == self.START:
            return self.STOP
        else:
            return self.START

    # this one is triggered by the previous one because we cannot have 2 outputs
    # in the same callback
    def run_movie(self, text):
        if text == self.START:    # then it means we are stopped
            return 0 
        else:
            return -1

    # see if it should move the slider for simulating a movie
    def on_interval(self, n_intervals, year, text):
        if text == self.STOP:  # then we are running
            if year == self.years[-1]:
                return self.years[0]
            else:
                return year + 1
        else:
            return year  # nothing changes

    def run(self, debug=False, port=8050):
        self.app.run_server(host="0.0.0.0", debug=debug, port=port)


if __name__ == '__main__':
    ws = BrevetStats()
    ws.run(port=8055)
