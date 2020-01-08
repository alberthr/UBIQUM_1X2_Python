# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import datetime
import pickle
from itertools import product, groupby
from random import choices
import os
import pymongo


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# CONNECTION TO MONGO
client = pymongo.MongoClient(
    "mongodb+srv://Albert:madannnn@cluster0-wghee.mongodb.net/test?retryWrites=true&w=majority")
db = client.quiniela
mongo = list(db.teams.find({}))
mongo[0].pop('_id')
teamsmdb = list(mongo[0].keys())


# FIRST QUINIELA WHEN LOADING APP
local =['Barcelona', 'Barcelona', 'Real Madrid', 'Real Betis', 'Sevilla', 'Espanyol', 
        'Real Sociedad', 'Atletico Madrid', 'Real Madrid', 'Atletico Madrid', 
        'Valencia', 'Athletic Club', 'Sevilla', 'Barcelona']
visitante =['Real Madrid', 'Espanyol', 'Barcelona', 'Sevilla', 'Real Betis', 'Barcelona', 
            'Athletic Club', 'Barcelona', 'Atletico Madrid', 'Real Madrid', 
            'Real Madrid', 'Barcelona', 'Barcelona', 'Atletico Madrid']

df = pd.DataFrame(list(zip(local, visitante)), columns =['LOCAL', 'VISITANTE']) 
df['1'] = df['X'] = df['2'] = 0.3333
df_teams = df.iloc[:, :2]
df_probs = df.iloc[:, 2:]



    
app.layout = dcc.Loading([ 
            
html.Div([                    
        html.Div([
                html.Div(children="No file with bets generated yet.")
        ], style={'width':'100%', 'textAlign':'center', 'color':'white'})                    
], style={'backgroundColor':'grey', 'margin':'15px 16px 10px 16px', 'border':'1px solid #d3d3d3', 'lineHeight':'50px'}),
            
html.Div([
        html.Div([
            
            html.Div([                    
                    html.Div([       
                            dash_table.DataTable(
                                    id='tabla-quin', 
                                    columns=[{"name": i, "id": i, 'presentation':'dropdown'} for i in df_teams.columns], 
                                    data=df_teams.to_dict('records'),                                    
                                    editable=True,
                                    dropdown={
                                        'LOCAL': {
                                            'options': [
                                                {'label': i, 'value': i}
                                                for i in teamsmdb
                                            ]
                                        },
                                        'VISITANTE': {
                                             'options': [
                                                {'label': i, 'value': i}
                                                for i in teamsmdb
                                            ]
                                        }
                                    },
                                    style_cell_conditional=[
                                            {'if': {'column_id': 'LOCAL'}, 'width': '50%'},
                                            {'if': {'column_id': 'VISITANTE'},'width': '50%'},
                                            {'textAlign':'center'}
                                    ], 
                                    style_cell={'height': '35px', 'fontFamily':'sans-serif', 'letterSpacing':'0.1rem', 'fontSize':'12px'},
                                    style_header={'height':'30px', 'fontFamily':'sans-serif', 'letterSpacing':'0.1rem', 'fontWeight':600, 'fontSize':'12px'},
                            ),                
                    ], style={'width':'60%', 'padding':'0px 2px 0px 0px'}),
                        
                    html.Div([       
                            dash_table.DataTable(
                                    id='tabla-probs', 
                                    columns=[{"name": i, "id": i} for i in df_probs.columns], 
                                    data=df_probs.to_dict('records'),
                                    editable=False,
                                    style_cell={'height': '35px', 'fontFamily':'sans-serif', 'letterSpacing':'0.1rem', 'fontSize':'12px'},
                                    style_header={'height':'30px', 'fontFamily':'sans-serif', 'letterSpacing':'0.1rem', 'fontWeight':600, 'fontSize':'12px' },                                    
                                    style_cell_conditional=[
                                            {'textAlign':'center'}
                                    ], 
                            ),                
                    ], style={'width':'40%','padding':'0px 0px 0px 2px'}),
                    
                    html.Div([       
                            dash_table.DataTable(
                                    id='tabla-hidden', 
                                    columns=[{"name": i, "id": i} for i in df_probs.columns], 
                                    data=df_probs.to_dict('records'),
                            ),                
                    ], style={'display':'none'}),

            ], style={'display':'flex', 'flexDirection':'row'})
            
        ], style={'width':'50%'}),
        
        html.Div([
            
            html.Div([
                html.Div([html.P('CONFIGURATION', style={'fontWeight':600, 'letterSpacing':'.1rem', 'textTransform':'uppercase', 'lineHeight':'30px', 'textAlign':'center', 'width':'100%', 'backgroundColor':'#e3e3e3', 'margin':0, 'fontSize':'12px'}),], style={'marginBottom':20}),
            
                html.Div([
                
                        html.Div([
                                html.Button(
                                        id='update-button', 
                                        n_clicks=0, 
                                        children='Update', 
                                        style={'width':150, 'marginRight': 10}),
                                html.Div(
                                        id="update-text", 
                                        children="Update database with last games", 
                                        style={'display': 'inline-block'})                        
                                ], style={'marginBottom': 3, 'marginTop': 3, 'fontSize':'small', 'letterSpacing':'0.1rem'}),
                                
                        html.Div([html.Button(id='loadquin-button', n_clicks=0, children='Load', style={'width':150, 'marginRight': 10}),  "Load current Quiniela"], style={'marginBottom': 3, 'marginTop': 3, 'fontSize':'small', 'letterSpacing':'0.1rem'}),
                        html.Div([html.Button(id='probsquin-button', n_clicks=0, children='Probabilities', style={'width':150, 'marginRight': 10}),  "Calculate 1X2 probabilities"], style={'marginBottom': 3, 'marginTop': 3, 'fontSize':'small', 'letterSpacing':'0.1rem'}),
                        html.Div([html.Button(id='limits-button', n_clicks=0, children='Limits', style={'width':150, 'marginRight': 10}),  "Limits on 1X2 results"], style={'marginBottom': 3, 'marginTop': 3, 'fontSize':'small', 'letterSpacing':'0.1rem'}),
                        
                        html.Div([
                                html.Div([html.Div(children='Extreme', style={'float':'left', 'width':150, 'display':'inline-block', 'lineHeight':'38px', 'textAlign':'center', 'fontSize':11, 'letterSpacing':'.1rem', 'textTransform':'uppercase', 'fontWeight':600, 'border':'1px solid #bbb', 'boxSizing':'border-box', 'borderRadius':4, 'color':'#555'}), 
                                          html.Div([dcc.Slider(id='extreme', min=0,max=100, marks={i: 'Label {}'.format(i) if i == 1 else str(i) for i in range(0, 110, 10)}, value=0)], style={'marginLeft':150, 'paddingTop':4})
                                ]),
                        ]),
                               
                        html.Hr(style={'marginTop':24, 'marginBottom':20}),
            
                        html.Div([
                                html.Div([html.Div("", style={'float':'left', 'width':150})], style={'marginRight':10}),
                                html.Div([
                                        html.Div([html.Div('1 results', style={'width':'100%', 'textAlign':'center'})], style={'width':'33%', 'lineHeight':'38px'}),
                                        html.Div([html.Div('X results', style={'width':'100%', 'textAlign':'center'})], style={'width':'33%', 'lineHeight':'38px'}),
                                        html.Div([html.Div('2 results', style={'width':'100%', 'textAlign':'center'})], style={'width':'33%', 'lineHeight':'38px'}),
                                ], style={'display':'flex', 'flexDirection':'row', 'width':'100%', 'letterSpacing':'0.1rem', 'fontSize':'11px', 'textTransform':'uppercase', 'fontWeight':600})
                        ], style={'display':'flex', 'flexDirection':'row'}),
                        
                        html.Div([
                                html.Div([html.Div("Minimum:", style={'lineHeight':'38px', 'textAlign':'center', 'float':'left', 'width':150, 'letterSpacing':'0.1rem', 'fontSize':'11px', 'textTransform':'uppercase', 'fontWeight':600})], style={'marginRight':10}),
                                html.Div([
                                        html.Div([dcc.Input(id="min1", value=0, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),
                                        html.Div([dcc.Input(id="minx", value=0, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                        
                                        html.Div([dcc.Input(id="min2", value=0, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                            
                                ], style={'display':'flex', 'flexDirection':'row', 'width':'100%', 'fontSize':'small'})
                        ], style={'display':'flex', 'flexDirection':'row'}),
                        
                        html.Div([
                                html.Div([html.Div("Maximum:", style={'lineHeight':'38px', 'textAlign':'center', 'float':'left', 'width':150, 'letterSpacing':'0.1rem', 'fontSize':'11px', 'textTransform':'uppercase', 'fontWeight':600})], style={'marginRight':10}),
                                html.Div([
                                        html.Div([dcc.Input(id="max1", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),
                                        html.Div([dcc.Input(id="maxx", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                        
                                        html.Div([dcc.Input(id="max2", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                            
                                ], style={'display':'flex', 'flexDirection':'row', 'width':'100%', 'fontSize':'small'})
                        ], style={'display':'flex', 'flexDirection':'row'}),
            
                        html.Div([
                                html.Div([html.Div("Longest Streak:", style={'lineHeight':'38px', 'textAlign':'center', 'float':'left', 'width':150, 'letterSpacing':'0.1rem', 'fontSize':'11px', 'textTransform':'uppercase', 'fontWeight':600})], style={'marginRight':10}),
                                html.Div([
                                        html.Div([dcc.Input(id="str1", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),
                                        html.Div([dcc.Input(id="strx", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                        
                                        html.Div([dcc.Input(id="str2", value=14, type='number', style={'width':'100%'})], style={'width':'33%', 'padding':2}),                            
                                ], style={'display':'flex', 'flexDirection':'row', 'width':'100%', 'fontSize':'small'})
                        ], style={'display':'flex', 'flexDirection':'row'}),
                    
                ], style={'padding':0})
            ]),
                        
        ], style={'width':'50%', 'paddingLeft':'25px',}),    
], style={'display':'flex', 'flexDirection':'row', 'padding':20, 'margin':'10px 16px 10px 16px', 'border':'1px solid #d3d3d3', 'backgroundColor':'white'}),
                    
html.Div([
        html.Div([
                html.Div([
                        html.Div("Number of bets:", style={'lineHeight':'38px', 'marginRight':10, 'letterSpacing':'0.1rem', 'fontSize':'small', }),
                        dcc.Input(id="nquin", value=25, type='number', style={'width':100, 'height':38, 'fontSize':'small'}),
                        html.Button(id='calc-button', n_clicks=0, children='Calculate', style={'marginLeft': 10}),       
                ], style={'float':'left', 'width':375, 'display':'flex', 'flexDirection':'row'})
        ], style={}),
                    
        html.Div([
                html.Div(children="No file with bets generated yet.", id="status-quin", style={'lineHeight':'38px', 'marginLeft':15, 'fontFamily':'monospace'})
        ], style={'backgroundColor':'#f3f3f3', 'width':'100%'})                    
], style={'display':'flex', 'flexDirection':'row', 'padding':'10px 15px', 'margin':'10px 16px 15px 16px', 'border':'1px solid #d3d3d3', 'backgroundColor':'white'}),


], type='dot', fullscreen=True)



# evaluates streak of serie
def eval_streak(serie, res):
    out = [sum(1 for j in group) for j, group in groupby(serie) if j==res]
    if len(out) < 1:
        return(0)
    else:
        return(max(out))

# max and mins 1X2 of quiniela
def min_max(df, result, threshold=0.2):
    dictionary_p = {'p'+str(i+1): [df[result][i], 1-df[result][i]] for i in range(len(df))}
    df_probs = pd.DataFrame([row for row in product(*dictionary_p.values())], columns=dictionary_p.keys())
    probs = df_probs.apply(lambda x: np.prod(x), axis=1)
    dictionary_c = {'p'+str(i+1): [1, 0] for i in range(len(df))}
    df_cases = pd.DataFrame([row for row in product(*dictionary_c.values())], columns=dictionary_c.keys())
    cases = df_cases.apply(lambda x: sum(x), axis=1)
    df_cp = pd.DataFrame(zip(cases, probs), columns=(['case','prob']))
    arr_probs = []
    for i in range(len(df)):
        arr_probs.append(sum(df_cp[df_cp['case']==i]['prob']))
    df_cp = pd.DataFrame(zip(range(1,15), arr_probs), columns=(['case','prob']))
    df_cp['prob'] = df_cp['prob']
    df_cp = df_cp.sort_values(by=['prob'], ascending=True)
    df_cp['cumsum'] = np.cumsum(df_cp['prob'])
    return(min(df_cp[df_cp['cumsum']> threshold]['case']), max(df_cp[df_cp['cumsum']> threshold]['case']))  

# max streak for 1X2 of quiniela
def max_streak(df, res):
    probs = []
    for streak in range(len(df)):
        max = 0
        for start in range(len(df)-streak):
            value = 1
            for i in range(start, start+streak+1):
                value = value * df[res][i]
            if value > max:
                max = value
        probs.append(max)
    return(probs)

# last n games of home or away team
def last_games(df, league, team, date, season, ngames):
    select = df[(df['LIGA']==league) & ((df['LOCAL']==team) | (df['VISITANTE']==team)) & 
            (df['FECHA'] < date) & (df['TEMPORADA']==season)][-ngames:]
    games = select.shape[0] + 1/2
    WINS = (sum(select['QUINIELA'][select.LOCAL==team]=='1') + sum(select['QUINIELA'][select.VISITANTE==team]=='2') + 1/6)/games
    DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    LOSE = (1 - WINS - DRAW)
    return(WINS, DRAW, LOSE)

# total league. local as a local
def league_local_local(df, league, home_team, date, season):
    select = df[(df['LIGA']==league) & ((df['LOCAL']==home_team)) & 
            (df['FECHA'] < date) & (df['TEMPORADA']==season)]
    games = select.shape[0] + 1/2
    H_WINS = (sum(select['QUINIELA'][select.LOCAL==home_team]=='1') + 1/6)/games
    H_DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    H_LOSE = (1 - H_WINS - H_DRAW)
    return(H_WINS, H_DRAW, H_LOSE)

# total league. visitor as a visitor
def league_visitor_visitor(df, league, away_team, date, season):
    select = df[(df['LIGA']==league) & ((df['VISITANTE']==away_team)) & 
            (df['FECHA'] < date) & (df['TEMPORADA']==season)]
    games = select.shape[0] + 1/2
    V_WINS = (sum(select['QUINIELA'][select.VISITANTE==away_team]=='2') + 1/6)/games
    V_DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    V_LOSE = (1 - V_WINS - V_DRAW)
    return(V_WINS, V_DRAW, V_LOSE)

# h2h last 10 games total
def h2h_10_hda(df, date, home_team, away_team):
    select = df[(df['FECHA'] < date) & (((df['LOCAL']==home_team) & (df['VISITANTE']==away_team)) |  
            ((df['LOCAL']==away_team) & (df['VISITANTE']==home_team)))][-10:]
    games = select.shape[0] + 1/2
    HOME = (sum(select['QUINIELA'][select.LOCAL==home_team]=='1') + 
            sum(select['QUINIELA'][select.VISITANTE==home_team]=='2') + 1/6)/games
    DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    AWAY = (1 - HOME - DRAW)
    return(HOME, DRAW, AWAY)
    
# h2h last 5 games with same home and away
def h2h_5_homeaway(df, date, home_team, away_team):
    select = df[(df['FECHA'] < date) & (df['LOCAL']==home_team) & (df['VISITANTE']==away_team)][-5:]
    games = select.shape[0] + 1/2
    HOME = (sum(select['QUINIELA'][select.LOCAL==home_team]=='1') + 1/6)/games
    DRAW = (sum(select['QUINIELA'][select.LOCAL==home_team]=='X') + 1/6)/games
    AWAY = (1 - HOME - DRAW)
    return(HOME, DRAW, AWAY)
    
# referee: historical results
def ref_team(df, date, team, referee):
    select = df[(df['FECHA'] < date) & ((df['LOCAL']==team) | (df['VISITANTE']==team)) & (df['ARBITRO']==referee)]
    games = select.shape[0] + 1/2
    WINS = (sum(select['QUINIELA'][select.LOCAL==team]=='1') + 
            sum(select['QUINIELA'][select.VISITANTE==team]=='2') + 1/6)/games
    DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    LOSE = (1 - WINS - DRAW)
    return(WINS, DRAW, LOSE)
    
# referee: historical results with home team at home
def ref_home_home(df, date, home_team, referee):
    select = df[(df['FECHA'] < date) & (df['LOCAL']==home_team) & (df['ARBITRO']==referee)]
    games = select.shape[0] + 1/2
    WINS = (sum(select['QUINIELA'][select.LOCAL==home_team]=='1') + 
            sum(select['QUINIELA'][select.VISITANTE==home_team]=='2') + 1/6)/games
    DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    LOSE = (1 - WINS - DRAW)
    return(WINS, DRAW, LOSE)

# referee: historical results with away team playing away
def ref_away_away(df, date, away_team, referee): 
    select = df[(df['FECHA'] < date) & (df['VISITANTE']==away_team) & (df['ARBITRO']==referee)]
    games = select.shape[0] + 1/2
    WINS = (sum(select['QUINIELA'][select.LOCAL==away_team]=='1') + 
            sum(select['QUINIELA'][select.VISITANTE==away_team]=='2') + 1/6)/games
    DRAW = (sum(select['QUINIELA']=='X') + 1/6)/games
    LOSE = (1 - WINS - DRAW)
    return(WINS, DRAW, LOSE)



@app.callback(Output('tabla-quin', 'data'),
              [Input('loadquin-button', 'n_clicks')])
def update_quiniela(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        URL = 'https://resultados.as.com/quiniela/'
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        seccion = soup.find(class_='cont-quiniela')
        equipos = seccion.find_all('', class_='nombre-equipo', )
        quiniela = [equipo.text for equipo in equipos]
        visitor = [equipo for i, equipo in enumerate(quiniela) if i % 2 == 1]
        local = [equipo for i, equipo in enumerate(quiniela) if i % 2 == 0]
        quiniela_df = pd.DataFrame(list(zip(local, visitor)), 
                                   columns =['LOCAL', 'VISITANTE']) 
        with open('./bbdd/teams_dict.json') as json_file:
            teams_dict = json.load(json_file)
        df = quiniela_df.copy()
        df['LOCAL'] = [teams_dict[i] for i in df['LOCAL']]
        df['VISITANTE'] = [teams_dict[i] for i in df['VISITANTE']]
        return(df.to_dict('records'))
    
    
    
@app.callback(Output('update-text', 'children'),
              [Input('update-button', 'n_clicks')],
              [State('tabla-quin', 'data')])
def update_database(n_clicks, df_quin):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        print('abriendo fichero historico de partidos')
        xl = pd.ExcelFile('./bbdd/FULL_BBDD_only_results.xlsx')
        dfr = xl.parse(xl.sheet_names[0])
        maxdate = max(dfr.FECHA)
        print('leído fichero historico de partidos. fecha máxima', maxdate)
        headers = {'x-rapidapi-key': "28d61524ab5698a1f8edb9e9ed577221"}
        league_1 = requests.request("GET", "https://server1.api-football.com/fixtures/league/775", headers=headers).json()
        print('bajados partidos primera division de temporada actual')
        league_2 = requests.request("GET", "https://server1.api-football.com/fixtures/league/776", headers=headers).json()
        print('bajados partidos segunda division de temporada actual')
        FECHA = []
        LOCAL = []
        VISITANTE = []
        ARBITRO = []
        GOL_L = []
        GOL_V = []
        TEMPORADA = []
        LIGA = []
        JORNADA = []  
        QUINIELA = []
        for i in league_1['api']['fixtures']:
            if (datetime.datetime.strptime(i['event_date'][:10], '%Y-%m-%d') > maxdate) and (i['status']=='Match Finished'):
                    FECHA.append(datetime.datetime.strptime(i['event_date'][:10], '%Y-%m-%d'))
                    LOCAL.append(i['homeTeam']['team_name'])
                    VISITANTE.append(i['awayTeam']['team_name'])
                    ARBITRO.append('-') if i['referee'] == None else ARBITRO.append(i['referee'])
                    GOL_L.append(i['goalsHomeTeam'])
                    GOL_V.append(i['goalsAwayTeam'])
                    JORNADA.append(int(i['round'][17:]))
                    LIGA.append(1)
                    TEMPORADA.append(2019)
                    QUINIELA.append('1') if i['goalsHomeTeam'] > i['goalsAwayTeam'] else QUINIELA.append('2') \
                            if i['goalsHomeTeam'] < i['goalsAwayTeam'] else QUINIELA.append('X')
        print('leídos partidos primera division')
        for i in league_2['api']['fixtures']:
            if (datetime.datetime.strptime(i['event_date'][:10], '%Y-%m-%d') > maxdate) and (i['status']=='Match Finished'):
                    FECHA.append(datetime.datetime.strptime(i['event_date'][:10], '%Y-%m-%d'))
                    LOCAL.append(i['homeTeam']['team_name'])
                    VISITANTE.append(i['awayTeam']['team_name'])
                    ARBITRO.append('-') if i['referee'] == None else ARBITRO.append(i['referee'])
                    GOL_L.append(i['goalsHomeTeam'])
                    GOL_V.append(int(i['goalsAwayTeam']))
                    JORNADA.append(int(i['round'][17:]))
                    LIGA.append(2)
                    TEMPORADA.append(2019)
                    QUINIELA.append('1') if i['goalsHomeTeam'] > i['goalsAwayTeam'] else QUINIELA.append('2') \
                            if i['goalsHomeTeam'] < i['goalsAwayTeam'] else QUINIELA.append('X')
        print('leídos partidos segunda division')
        new = pd.DataFrame(list(zip(TEMPORADA, LIGA, JORNADA, FECHA, LOCAL, VISITANTE, GOL_L, GOL_V, ARBITRO, QUINIELA)), 
                       columns =['TEMPORADA', 'LIGA', 'JORNADA', 'FECHA', 'LOCAL', 'VISITANTE', 'GOL L', 'GOL V', 
                                 'ARBITRO', 'QUINIELA'])
        print('numero de partidos a añadir:', len(new))
        if len(new)>0:        
            print('actualizando bbdd de equipos y arbitros')
            with open('./bbdd/teams_dict.json') as json_file:
                teams_dict = json.load(json_file)
            with open('./bbdd/referees_dict.json') as json_file:
                referees_dict = json.load(json_file)
            print('actualizando arbitros')
            save_r = False
            for i in new['ARBITRO']:
                if i not in referees_dict:
                    referees_dict.update({i:i})
                    save_r = True
            save_t = False
            print('actualizando equipos')
            for i in new['LOCAL']:
                if i not in teams_dict:
                    teams_dict.append({i:i})
                    save_t = True            
            for i in new['VISITANTE']:
                if i not in teams_dict:
                    teams_dict.append({i:i})
                    save_t = True
            print('aplicando diccionarios a bbdd de partidos')
            new['LOCAL'] = [teams_dict[i] for i in new['LOCAL']]
            new['VISITANTE'] = [teams_dict[i] for i in new['VISITANTE']]
            new['ARBITRO'] = [referees_dict[i] for i in new['ARBITRO']]
            print('guardando cambios en diccionarios')
            if save_r:
                with open('./bbdd/referees_dict.json', 'w') as outfile:
                        json.dump(referees_dict, outfile)                
            if save_t:
                with open('./bbdd/teams_dict.json', 'w') as outfile:
                        json.dump(teams_dict, outfile)
            print('guardando bbdd con partidos nuevos')
            df_new = dfr.append(new, ignore_index=True, sort=False)
            df_new.to_excel("./bbdd/FULL_BBDD_only_results.xlsx", index=False)
            print('añadiendo informacion sobre ultimos partidos (1/14)')
            new['last2_hometeam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[4], x[3], x[0], 2), axis=1)
            print('añadiendo informacion sobre ultimos partidos (2/14)')
            new['last5_hometeam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[4], x[3], x[0], 5), axis=1)
            print('añadiendo informacion sobre ultimos partidos (3/14)')
            new['last10_hometeam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[4], x[3], x[0], 10), axis=1)
            print('añadiendo informacion sobre ultimos partidos (4/14)')
            new['last2_awayteam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[5], x[3], x[0], 2), axis=1)
            print('añadiendo informacion sobre ultimos partidos (5/14)')
            new['last5_awayteam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[5], x[3], x[0], 5), axis=1)
            print('añadiendo informacion sobre ultimos partidos (6/14)')
            new['last10_awayteam_wdl'] = new.apply(lambda x: last_games(df_new, x[1], x[5], x[3], x[0], 10), axis=1)
            print('añadiendo informacion sobre ultimos partidos (7/14)')
            new['league_local_local_wdl'] = new.apply(lambda x: league_local_local(df_new, x[1], x[4], x[3], x[0]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (8/14)')
            new['league_visitor_visitor_wdl'] = new.apply(lambda x: league_visitor_visitor(df_new, x[1], x[5], x[3], x[0]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (9/14)')
            new['h2h_last_10_hda'] = new.apply(lambda x: h2h_10_hda(df_new, x[3], x[4], x[5]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (10/14)')
            new['h2h_5_homeaway_hda'] = new.apply(lambda x: h2h_5_homeaway(df_new, x[3], x[4], x[5]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (11/14)')
            new['ref_hometeam_wdl'] = new.apply(lambda x: ref_team(df_new, x[3], x[4], x[8]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (12/14)')
            new['ref_awayteam_wdl'] = new.apply(lambda x: ref_team(df_new, x[3], x[5], x[8]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (13/14)')
            new['ref_home_home_wdl'] = new.apply(lambda x: ref_home_home(df_new, x[3], x[4], x[8]), axis=1)
            print('añadiendo informacion sobre ultimos partidos (14/14)')
            new['ref_away_away_wdl'] = new.apply(lambda x: ref_away_away(df_new, x[3], x[5], x[8]), axis=1)            
            print('procesando nueva informacion')
            columns = list(new.columns[[x[-3:] in ['wdl','hda'] for x in new.columns]])            
            for i in columns:
                field_type = i[-3:]
                name1 = i[:-3] + field_type[0]
                name2 = i[:-3] + field_type[1]
                name3 = i[:-3] + field_type[2]
                new[name1] = new[i].apply(lambda x: x[0])
                new[name2] = new[i].apply(lambda x: x[1])
                new[name3] = new[i].apply(lambda x: x[2])
            new.drop(columns, inplace=True, axis=1)
            print('añadiendo informacion a bbdd. abriendo bbdd')
            xl = pd.ExcelFile('./bbdd/FULL_BBDD_with_features.xlsx')
            dfr = xl.parse(xl.sheet_names[0])
            df_new = dfr.append(new, ignore_index=True, sort=False)
            print('guardando fichero con partidos nuevos y todas las características')
            df_new.to_excel("./bbdd/FULL_BBDD_with_features.xlsx", index=False)
            maxdate = max(df_new.FECHA)
        print('proceso finalizado')
        return("Database up to date. Last game: ", str(maxdate)[:10])



@app.callback([Output('tabla-hidden', 'data'), Output('extreme','value')],
              [Input('probsquin-button', 'n_clicks')],
              [State('tabla-quin', 'data')])
def update_probsquin(n_clicks, json_quin):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        df_quin = pd.DataFrame.from_dict(json_quin, orient='columns')
        print('abro bbdd con datos historicos')
        xl = pd.ExcelFile('./bbdd/FULL_BBDD_only_results.xlsx')
        historic = xl.parse(xl.sheet_names[0])
        print('seleccionando datos de temporada actual')
        select_1 = list(historic[(historic['TEMPORADA']==2019) & (historic['LIGA']==1)].LOCAL.unique())
        select_2 = list(historic[(historic['TEMPORADA']==2019) & (historic['LIGA']==2)].LOCAL.unique())
        teams_1 = { i : 1 for i in select_1 }
        teams_2 = { i : 2 for i in select_2 }
        teams_league_dict = {**teams_1, **teams_2}
        print('empezando a construir tablas de datos')
        df_quin['LIGA'] = [teams_league_dict[i] for i in df_quin['LOCAL']]
        df_quin['TEMPORADA'] = 2019
        df_quin['JORNADA'] = 'X'
        df_quin['FECHA'] = datetime.datetime.today().strftime('%Y-%m-%d')
        df_quin = df_quin[['TEMPORADA', 'LIGA', 'JORNADA', 'FECHA', 'LOCAL', 'VISITANTE']]
        print('añadiendo características a cada partido de la quiniela (1/10)')
        df_quin['last2_hometeam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[4], x[3], x[0], 2), axis=1)
        print('añadiendo características a cada partido de la quiniela (2/10)')
        df_quin['last5_hometeam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[4], x[3], x[0], 5), axis=1)
        print('añadiendo características a cada partido de la quiniela (3/10)')
        df_quin['last10_hometeam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[4], x[3], x[0], 10), axis=1)
        print('añadiendo características a cada partido de la quiniela (4/10)')
        df_quin['last2_awayteam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[5], x[3], x[0], 2), axis=1)
        print('añadiendo características a cada partido de la quiniela (5/10)')
        df_quin['last5_awayteam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[5], x[3], x[0], 5), axis=1)
        print('añadiendo características a cada partido de la quiniela (6/10)')
        df_quin['last10_awayteam_wdl'] = df_quin.apply(lambda x: last_games(historic, x[1], x[5], x[3], x[0], 10), axis=1)
        print('añadiendo características a cada partido de la quiniela (7/10)')
        df_quin['league_local_local_wdl'] = df_quin.apply(lambda x: league_local_local(historic, x[1], x[4], x[3], x[0]), axis=1)
        print('añadiendo características a cada partido de la quiniela (8/10)')
        df_quin['league_visitor_visitor_wdl'] = df_quin.apply(lambda x: league_visitor_visitor(historic, x[1], x[5], x[3], x[0]), axis=1)
        print('añadiendo características a cada partido de la quiniela (9/10)')
        df_quin['h2h_last_10_hda'] = df_quin.apply(lambda x: h2h_10_hda(historic, x[3], x[4], x[5]), axis=1)
        print('añadiendo características a cada partido de la quiniela (10/10)')
        df_quin['h2h_5_homeaway_hda'] = df_quin.apply(lambda x: h2h_5_homeaway(historic, x[3], x[4], x[5]), axis=1)
        print('procesando información añadida')
        columns = list(df_quin.columns[[x[-3:] in ['wdl','hda'] for x in df_quin.columns]])
        for i in columns:
            field_type = i[-3:]
            name1 = i[:-3] + field_type[0]
            name2 = i[:-3] + field_type[1]
            name3 = i[:-3] + field_type[2]
            df_quin[name1] = df_quin[i].apply(lambda x: x[0])
            df_quin[name2] = df_quin[i].apply(lambda x: x[1])
            df_quin[name3] = df_quin[i].apply(lambda x: x[2])
        df_quin.drop(columns, inplace=True, axis=1)
        print('información añadida correctamente. preparado para aplicar modelos')
        print('cargando modelo "1"')
        clf_1 = pickle.load(open('./models/model1.sav', 'rb'))
        print('cargando modelo "X"')
        clf_x = pickle.load(open('./models/modelx.sav', 'rb'))
        print('cargando modelo "2"')
        clf_2 = pickle.load(open('./models/model2.sav', 'rb'))
        print('creando variables para ejecutar modelo')
        dummy1 = pd.get_dummies(df_quin.LOCAL)
        dummy2 = pd.get_dummies(df_quin.VISITANTE)
        dummy2.columns = [i+"_2" for i in dummy2.columns]
        df_quin = pd.concat([df_quin, dummy1, dummy2], axis=1)
        variables = pickle.load(open('./models/variables.sav', 'rb'))
        add_col = [i for i in list(variables) if i not in list(df_quin.columns)]
        add_col = [i for i in add_col if i not in ['GOL L', 'GOL V', 'QUINIELA', 'ARBITRO', '1', 'X', '2']]
        for i in add_col:
            df_quin[i] = 0
        training = pickle.load(open('./models/training.sav', 'rb'))
        print('calculando probabilidades "1"')
        probslog_1 = clf_1.predict_proba(df_quin[training])[:,1]
        print('calculando probabilidades "X"')
        probslog_X = clf_x.predict_proba(df_quin[training])[:,1]
        print('calculando probabilidades "2"')
        probslog_2 = clf_2.predict_proba(df_quin[training])[:,1]
        zip_probs = list(zip(probslog_1, probslog_X, probslog_2, df_quin.LOCAL, df_quin.VISITANTE))
        probs_1X2 = pd.DataFrame(zip_probs, columns = ['predslog_1', 'predslog_X', 'predslog_2', 'LOCAL', 'VISITANTE']) 
        print("reajustando resultados")
        probs_1X2['1'] = probs_1X2.apply(lambda x: x[0]/(x[0]+x[1]+x[2]), axis=1)
        probs_1X2['X'] = probs_1X2.apply(lambda x: x[1]/(x[0]+x[1]+x[2]), axis=1)
        probs_1X2['2'] = probs_1X2.apply(lambda x: x[2]/(x[0]+x[1]+x[2]), axis=1)
        probs_1X2.drop(["predslog_1", "predslog_X", "predslog_2"], axis=1, inplace=True)
        dfr = probs_1X2[['1','X','2']]
        dfr = dfr.apply(lambda x: round(100*x, 2))
        print('proceso finalizado')
        return(dfr.to_dict('records'), 0)



@app.callback(
    Output('tabla-probs', 'data'),
    [Input('extreme', 'value')],
    [State('tabla-hidden', 'data')])
def update_tabla_hidden(valor, json_quin):
    probs_1X2 = pd.DataFrame.from_dict(json_quin, orient='columns')
    multiplicador = 1+(valor/100)
    prob_1 = probs_1X2['1'].apply(lambda x: float(x))**multiplicador
    prob_X = probs_1X2['X'].apply(lambda x: float(x))**multiplicador
    prob_2 = probs_1X2['2'].apply(lambda x: float(x))**multiplicador
    probs_1X2['1'] = prob_1 / (prob_1+prob_2+prob_X)
    probs_1X2['X'] = prob_X / (prob_1+prob_2+prob_X)
    probs_1X2['2'] = prob_2 / (prob_1+prob_2+prob_X)
    probs_1X2 = probs_1X2.apply(lambda x: round(100*x, 2))
    return(probs_1X2.to_dict('records'))



@app.callback([Output('min1', 'value'), Output('max1', 'value'),
               Output('minx', 'value'), Output('maxx', 'value'),
               Output('min2', 'value'), Output('max2', 'value'),
               Output('str1', 'value'), Output('strx', 'value'), Output('str2', 'value')],
              [Input('limits-button', 'n_clicks')],
              [State('tabla-probs', 'data')])
def update_limits(n_clicks, json_quin):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        df_quin = pd.DataFrame.from_dict(json_quin, orient='columns')
        df_quin['1'] = df_quin['1'].apply(lambda x: float(x)/100)
        df_quin['X'] = df_quin['X'].apply(lambda x: float(x)/100)
        df_quin['2'] = df_quin['2'].apply(lambda x: float(x)/100)
        print('calculando minimo y maximo de 1')
        min_1, max_1 = min_max(df_quin, '1')
        print('calculando minimo y maximo de X')
        min_x, max_x = min_max(df_quin, 'X')
        print('calculando minimo y maximo de 2')
        min_2, max_2 = min_max(df_quin, '2')
        print("minimo y maximo de 1:", min_1, max_1)
        print("minimo y maximo de X:", min_x, max_x)
        print("minimo y maximo de 2:", min_2, max_2)
        print('calculando maximo de "1" seguidos')
        streak1 = sum(np.array(max_streak(df_quin, '1')) > 0.1)
        print('calculando maximo de "X" seguidos')
        streakx = sum(np.array(max_streak(df_quin, 'X')) > 0.1)
        print('calculando maximo de "2" seguidos')
        streak2 = sum(np.array(max_streak(df_quin, '2')) > 0.1)
        print("maximo de '1' seguidos:", streak1)
        print("maximo de 'X' seguidos:", streakx)
        print("maximo de '2' seguidos:", streak2)
        print('proceso acabado correctamente')
        return(min_1, max_1, min_x, max_x, min_2, max_2, streak1, streakx, streak2)



@app.callback(Output('status-quin', 'children'),
              [Input('calc-button', 'n_clicks')], 
              [State('nquin', 'value'),
               State('min1', 'value'), State('max1', 'value'),
               State('minx', 'value'), State('maxx', 'value'),
               State('min2', 'value'), State('max2', 'value'),
               State('str1', 'value'), State('strx', 'value'), State('str2', 'value'),
               State('tabla-probs', 'data')])
def calcula_quinielas(n_clicks, bets, min_1, max_1, min_x, max_x, min_2, max_2, 
                      streak1, streakx, streak2, json_quin):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        df_quin = pd.DataFrame.from_dict(json_quin, orient='columns')
        df_quin['1'] = df_quin['1'].apply(lambda x: float(x)/100)
        df_quin['X'] = df_quin['X'].apply(lambda x: float(x)/100)
        df_quin['2'] = df_quin['2'].apply(lambda x: float(x)/100)
        df_quin['n1'] = round(bets*df_quin['1'])+1
        df_quin['nx'] = round(bets*df_quin['X'])+1
        df_quin['n2'] = round(bets*df_quin['2'])+1
        q = pd.DataFrame(np.nan, index=range(14), columns=range(bets))
        opcs=0
        for quiniela in range(bets):
            print("calculando quiniela", quiniela)
            correct = False
            while correct == False:
                opcs += 1
                serie = []
                for i in range(14):
                    correct = True
                    rest1 = df_quin['n1'][i] - sum(q.iloc[i]=='1')
                    restx = df_quin['nx'][i] - sum(q.iloc[i]=='X')
                    rest2 = df_quin['n2'][i] - sum(q.iloc[i]=='2')
                    p1 = rest1 / (rest1 + rest2 + restx)
                    p2 = rest2 / (rest1 + rest2 + restx)
                    px = restx / (rest1 + rest2 + restx)
                    serie.append(choices(['1','X','2'], [p1, px, p2])[0])
                    n1 = serie.count('1')
                    n2 = serie.count('2')
                    nx = serie.count('X')
                correct = False if ((n1 > max_1) | (n1 < min_1) | (n2 > max_2) | (n2 < min_2) | (nx > max_x) | (nx < min_x) | 
                                    (eval_streak(serie, '1') > streak1) | (eval_streak(serie, '2') > streak2) | 
                                    (eval_streak(serie, 'X') > streakx)) else True
                #print('calculada quiniela nº', quiniela+1, '| Se han calculado', opcs, 'quinielas')
            q[quiniela] = serie
        print(opcs, "combinations have been calculated and", bets, "have been selected.")
        print(q)
        fileoutput =  os.getcwd() + "\\" +   datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ".xlsx"
        return(fileoutput)



        
if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=True, dev_tools_props_check=True)