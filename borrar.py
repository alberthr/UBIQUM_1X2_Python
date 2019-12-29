    html.Div([
        html.H5('QUINIELA', style={'textAlign':'center', 'marginBottom':15}),
        html.Div([       
                dash_table.DataTable(
                        id='tabla-quin', 
                        columns=[{"name": i, "id": i} for i in df_teams.columns], 
                        data=df_teams.to_dict('records'),
                        style_cell_conditional=[
                                {'if': {'column_id': 'LOCAL'}, 'width': '30%', 'textAlign': 'center'},
                                {'if': {'column_id': 'VISITANTE'},'width': '30%'},
                                {'textAlign':'center'}
                        ], 
                ),                
        ], style={'width':'60%'}),
            
        html.Div([       
                dash_table.DataTable(
                        id='tabla-probs', 
                        columns=[{"name": i, "id": i} for i in df_probs.columns], 
                        data=df_probs.to_dict('records'),
                        style_cell_conditional=[
                                {'textAlign':'center'}
                        ], 
                ),                
        ], style={'width':'40%', 'display':'inline-block', 'float':'right'}),

                
                
    ], style={'width': '50%', 'padding':15}),