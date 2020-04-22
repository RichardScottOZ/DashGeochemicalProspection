import base64
import io
import dash
import dash_table
import dash_core_components as dcc  # São componentes interativos gerados com js, html e css através do reactjs
import dash_html_components as html # Possui um componente para cada tag html
from dash.dependencies import Input, Output, State
from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import pandas as pd
import vislogprob
import numpy as np
import plotly.express as px
# Style:
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Empty Graphs
init_fig = px.scatter(x=[], y=[], title='Load Data First', log_x=True, log_y=True, labels={'x':'x axis', 'y':'y axis'})
init_fig.update_layout(margin={'l': 60, 'b': 40, 't': 40, 'r': 60})
map_init_fig = px.choropleth_mapbox(locations=[0], center={"lat": -13.5, "lon": -48.5}, mapbox_style="carto-positron", zoom=4)
map_init_fig.update_layout(margin={"r":10,"t":10,"l":10,"b":10})
app.layout = html.Div(children=[
    html.H1(children='Geochemical Prospection', style={'textAlign': 'left', 'color': '#054b66'}),

    html.Div(children='''
        Workflow for Geochemical Prospection utilyzing Dash and K-means Clustering
    '''),

    html.Hr(), # Linha Divisória -> Começo da aplicação

    html.Div([  # classe ROW -> dois containers
        html.Div([  # classe caixa
            html.Div([  # classe 5 colunas
                html.Div([
                    html.Div([html.H3(children='1. Load table:', style={'textAlign': 'center', 'color': '#054b66'})]),

                    html.Div(dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True
                    )),

                    html.H4('1.2 Select Geochemical Element:', style={'textAlign': 'center', 'font-size':'20px'}),
                    dcc.Dropdown(id='select-element', style={'margin-bottom':'20px'})



                ], className='row'),
                    html.Div([       # Div para as tabs
                        dcc.Tabs(id='tabs', value='tab-1', children=[  # componente tabs
                            dcc.Tab(children=[                              # Data-Table
                                dash_table.DataTable(id='Data Table', columns=[{"name": '', "id": ''} for i in range(0,6)], style_table={'overflowX':'scroll', 'overflowY':'scroll', 'height':'250px'})
                            ], label='Data Table', value='tab-1'),
                            dcc.Tab(children=[
                                dash_table.DataTable(id='Freq Table', columns=[{'name':'Mínimo', 'id':'Mínimo'}, {'name':'Máximo', 'id':'Máximo'}, {'name':'Mínimo (log)', 'id':'Mínimo (log)'}, {'name':'Frequência Absoluta', 'id':'Frequência Absoluta'}, {'name':'Frequência Relativa (%)', 'id':'Frequência Relativa (%)'}, {'name':'Frequência Acumulada', 'id':'Frequência Acumulada'}, {'name':'Frequência Acumulada Direta (%)', 'id':'Frequência Acumulada Direta (%)'}, {'name':'Frequência Acumulada Invertida (%)', 'id':'Frequência Acumulada Invertida (%)'}], style_table={'overflowX':'scroll', 'overflowY':'scroll', 'height':'250px'})
                            ], label='Frequencies Table', value='tab-2')      # Frequency Table
                        ])])
                ], className='three columns', style={'border-style':'solid','margin': '10px', 'border-width':'thin', 'padding':'5px', 'border-radius':'8px', 'height':'auto'})]),

        html.Div([  # Classe Caixa
            html.Div([  # classe 7 colunas
                html.H3(children='2. Number of Clusters by Elbow Method:',
                        style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='cluster-graph', figure=init_fig
                )
            ], className='four columns',
                style={'border-style': 'solid', 'border-width': 'thin', 'margin': '10px', 'border-radius': '8px',
                       'height': '550px'})]),

        html.Div([   # Classe Caixa
            html.Div([   # classe 7 colunas
                html.H3(children='3. Visualize Log-Probability curve:', style={'textAlign': 'center', 'color': '#054b66'}),

                dcc.Graph(
                    id='prob-graph', figure=init_fig
                )
            ], className='five columns', style={'border-style':'solid','border-width':'thin', 'margin': '10px', 'border-radius':'8px', 'height':'550px'})])

    ], className='row'),

    html.Div([
        html.Div([
            dcc.Graph(id='map', figure=map_init_fig)
        ], className='six columns'
    )], className='row', style={'border-style':'solid','border-width':'thin', 'margin': '10px', 'border-radius':'8px'})

])

@app.callback(
    [Output('prob-graph', 'figure'),
     Output('cluster-graph', 'figure')],        # A saída é a figura do gráfico
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela,
def update_graph(element_column, data_dict):
    if element_column == None:
        return init_fig, init_fig
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        x, y = vislogprob.logprob(df[element_column])
        X = np.array([x,y])

        visualizer = KElbowVisualizer(KMeans(), k=(1, 8))
        visualizer.fit(X.transpose())

        df_clustered = vislogprob.clustered_df(X.transpose(), visualizer.elbow_value_)

        probgraf_fig = px.scatter(x=df_clustered.Prob[::-1], y=df_clustered.Value, color=df_clustered.Class, log_y=True, log_x=True,
                                  labels={'x':'Probability (%) ', 'y':str(element_column)+''}, title=str(element_column)+' x Cumulative Probability')
        probgraf_fig.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60})
        probgraf_fig.update_layout(legend_orientation="h")

        cluster_fig = px.line(x=visualizer.k_values_, y=visualizer.k_scores_, labels={'x':'Number of K clusters', 'y':'Distortion Score'}, range_y=[-5, np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_)/3])
        cluster_fig.update_traces(mode="markers+lines", hovertemplate=None)
        cluster_fig.add_shape(dict(type='line',
                                   x0=visualizer.elbow_value_,
                                   y0=-np.mean(visualizer.k_scores_),
                                   x1=visualizer.elbow_value_,
                                   y1=np.max(visualizer.k_scores_)+np.mean(visualizer.k_scores_),
                                   line=dict(dash='dashdot', color='#EF553B')))
        cluster_fig.update_layout(margin={'l': 60, 'b': 30, 't': 40, 'r': 60})
        cluster_fig.update_layout(legend_orientation="h")

        return probgraf_fig, cluster_fig

@app.callback(
    Output('Freq Table', 'data'),                   # A saída são as dados da tabela
    [Input('select-element', 'value'),
     Input('Data Table', 'data')])             # Entrada: valor da tabela
def update_freq(element_column, data_dict):
    if element_column == None:
        return [{"name": '', "id": ''} for i in range(0,6)]
    else:
        df = pd.DataFrame.from_dict(data_dict, 'columns')
        freq_df = vislogprob.tabela_frequencias(df[element_column])
        return freq_df.to_dict('records')

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    data = df.to_dict('records')
    columns = [{'name': i, 'id': i} for i in df.columns]

    return columns, data

@app.callback([Output('Data Table', 'data'),
              Output('Data Table', 'columns'),
              Output('select-element', 'options'),
              Output('select-element', 'value')],   # Output('select-element', 'options')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_output(list_of_contents, list_of_names):
    if list_of_contents is None:
        return [{"name": '', "id": ''} for i in range(0,6)], [{"name": '', "id": ''} for i in range(0,6)], [{"label": '', "value": ''} for i in range(0,6)], None
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        columns, data = children[0]
        values = []
        for i in columns:
            if i['name'][0:7] != 'Unnamed':
                values.append(i['name'])
        markdowns = [{"label": i, "value": i} for i in values]
        columns = [{"name": i, "id": i} for i in values]

        return data, columns, markdowns, None

if __name__ == '__main__':
    app.run_server(debug=True)   # Atualiza a página automaticamente com modificações do código fonte