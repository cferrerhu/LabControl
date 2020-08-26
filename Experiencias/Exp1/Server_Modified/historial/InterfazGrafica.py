from cliente import Cliente # cliente OPCUA
import threading
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import json
import datetime
from collections import deque
import plotly
from dash.dependencies import Output, Input, State
import time
import os
import pandas as pd
from PID import PID

frecMax = 1 # En Hz
directory = 'HistorialAplicacion'
if not os.path.exists(directory):
        os.makedirs(directory)

eventoColor = 0
eventoTexto = 0
# Función que se suscribe
def funcion_handler(node, val):
    key = node.get_parent().get_display_name().Text
    variables_manipuladas[key] = val # Se cambia globalmente el valor de las variables manipuladas cada vez que estas cambian
    print('key: {} | val: {}'.format(key, val))



class SubHandler(object): # Clase debe estar en el script porque el thread que comienza debe mover variables globales
    def datachange_notification(self, node, val, data):
        thread_handler = threading.Thread(target=funcion_handler, args=(node, val))  # Se realiza la descarga por un thread
        thread_handler.start()

    def event_notification(self, event):
        global eventoColor, eventoTexto
        eventoColor = event
        eventoTexto = event


cliente = Cliente("opc.tcp://192.168.1.23:4840/freeopcua/server/", suscribir_eventos=True, SubHandler=SubHandler)
cliente.conectar()

# Aplicación con Dash
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash()
app.layout = html.Div(style={'backgroundColor': colors['background']},
            children=[html.H1(children='Aplicación de Control', style={'textAlign': 'center','color': colors['text']}),
                      dcc.Interval(id='interval-component', interval=int(1/frecMax*1000), n_intervals=0),
            dcc.Tabs(id='Tabs', children=[
            dcc.Tab(label='Tanques', children=[html.Div(id='live-update-text1', style={'padding':'15px', 'color': colors['text']}),
                dcc.Graph(id='live-update-graph1'), html.Div(id='intermediate', style={'display':'none'}),
                html.Div(id='GuardarDiv', style={'paddingBottom':'30px', 'textAlign': 'center'}, children=[
                    html.Button('Guardar Datos', id='guardar', n_clicks=0),
                    html.Button('Dejar de Guardar', id='Noguardar', n_clicks=0),
                    html.Div(id='indicativoGuardar', children=['No Guardando']),
                    dcc.RadioItems(id='Formato', options=[{'label': '.csv', 'value': 'csv'}, {'label':'.json', 'value': 'json'}, {'label':'.pickle', 'value': 'pickle'}], value='csv')])]),
            dcc.Tab(label='Controlador', children=[
                html.Div(dcc.Graph(id='live-update-graph2')),
                html.Div(id='Modo',style={'textAlign': 'center','color': colors['text']}, children=[html.H2('Modo del controlador'),
                    dcc.RadioItems(id='Eleccion',options=[{'label': 'Modo Manual', 'value': 'Manual'}, {'label': 'Modo Automático', 'value': 'Automatico'}], value='Manual'),
                    html.Div(id='MyDiv')]),
                html.Div(id='Modos',className='row' ,children=[
                    html.Div(id='Manual', className='six columns', style={'color': colors['text'], 'borderStyle': 'solid', 'borderWidth': '5px', 'borderColor': '#B8860B'}, children=[
                        html.H3('Modo Manual', style={'textAlign': 'center'}),
                        html.H4('Valor de las Razones'),
                        html.Div(id='RazonesDiv', className='row', children=[
                            html.Div(id='Razon1Div', style={'paddingBottom':'50px'},className='six columns', children=[
                                html.Label(id='Razon1Label', children='Razon 1'),
                                dcc.Slider(id='Razon1', min=0, max=1, step=0.05, value=0.7)]),
                            html.Div(id='Razon1Div', style={'paddingBottom':'50px'}, className='six columns', children=[
                                html.Label(id='Razon2Label',children='Razon 2'),
                                dcc.Slider(id='Razon2', min=0, max=1, step=0.05, value=0.6)])
                        ]),
                        dcc.RadioItems(id='TipoManual', options=[{'label': 'Sinusoide', 'value': 'sinusoide'}, {'label':'Valor Fijo', 'value':'fijo'}], value='sinusoide'),
                        html.H4('Sinusoide'),
                        html.Div(id='Sliders1', className='row', children=[
                            html.Div(id='Frec', style={'paddingBottom':'50px'}, className='six columns', children=[
                                html.Label(id='1',children='Frec'), dcc.Slider(id='FrecSlider',min=frecMax/25, max=frecMax/2, step=0.1, value=frecMax/4, vertical=False)]),
                            html.Div(id='Amp', className='six columns', children=[
                                html.Label(id='2', children='Amp'), dcc.Slider(id='AmpSlider',min=0.1, max=1, step=0.05, value=1, vertical=False)])]),
                        html.Div(id='Sliders2', className='row', children=[
                            html.Div(id='Fase', style={'paddingBottom':'50px'}, className='six columns', children=[
                                html.Label(id='3', children='Fase'), dcc.Slider(id='FaseSlider',min=0, max=6.28, step=0.1, value=0, vertical=False)]),
                            html.Div(id='Offset', className='six columns', children=[
                                html.Label(id='4', children='Offset'), dcc.Slider(id='OffsetSlider',min=-1, max=1, step=0.05, value=0, vertical=False)])])
                        ,html.H4('Valor fijo'),
                        html.Div(style={'textAlign':'center', 'paddingBottom':'10px'},children=[dcc.Input(id='ManualFijo',placeholder='Ingrese un valor entre -1 y 1 ...', type='text', value='0')])
                    ]),
                    html.Div(id='Automatico', className='six columns', style={'color': colors['text'], 'borderStyle': 'solid', 'borderWidth': '5px', 'borderColor': '#B8860B'}, children=[
                        html.H3('Modo Automatico', style={'textAlign': 'center'}),
                        html.H4('SetPoints'),
                        html.Div(id='SetPoints', className='row', children=[
                            html.Div(id='Tanque1', className='six columns', children=[
                                html.Label('SetPoint Tanque 1'), dcc.Input(id='SPT1', placeholder='Ingrese valor', type='text', value='25')]),
                            html.Div(id='Tanque2', className='six columns', children=[
                                html.Label('SetPoint Tanque 2'), dcc.Input(id='SPT2', placeholder='Ingrese valor', type='text', value='25')])
                        ]),
                        html.H4('Constantes del PID'),
                        html.Div(id='constantes1', className='row', children=[
                            html.Div(id='P', className='six columns', children=[
                                html.Label('Proporcional'),
                                dcc.Input(id='Kp',placeholder='Ingrese un valor', type='text', value='0.1')]),
                            html.Div(id='I', className='six columns', children=[
                                html.Label('Integral'),
                                dcc.Input(id='Ki',placeholder='Ingrese un valor', type='text', value='0.1')])]),
                        html.Div(id='constantes2', className='row',  style={'paddingBottom':'10px'},children=[
                            html.Div(id='D', className='six columns', children=[
                                html.Label('Derivativa'),
                                dcc.Input(id='Kd',placeholder='Ingrese un valor', type='text', value='0')]),
                            html.Div(id='W', className='six columns', children=[
                                html.Label('Anti wind-up'),
                                dcc.Input(id='Kw',placeholder='Ingrese un valor', type='text', value='0')])])
                        ])
                    ]),
                html.Div(id='AlarmaContainer', style={'paddingTop': '20px', 'paddingBottom': '10px'}, children=[
                    html.Div(id='Alarma', style={'backgroundColor': '#006400', 'width': '80%', 'height': '70px', 'paddingTop':'25px', 'margin':'auto','borderStyle': 'solid', 'borderWidth': '5px', 'borderColor': '#B8860B'}, children=[
                        html.H2(id='AlarmaTexto',style={'textAlign':'center', 'color': '#000000', 'paddingBottom':'40px'}, children=['Alarma Inactiva'])
                    ])])

            ])])

])
################################################## Alarma ############################################################
@app.callback(Output('Alarma', 'style'), [Input('interval-component', 'n_intervals')])
def Alarma(n):
    global eventoColor
    if eventoColor != 0:
        style = {'backgroundColor': '#FF0000', 'width': '80%', 'height': '70px', 'paddingTop': '25px', 'margin': 'auto',
                 'borderStyle': 'solid', 'borderWidth': '5px', 'borderColor': '#B8860B'}
    else:
        style = {'backgroundColor': '#006400', 'width': '80%', 'height': '70px', 'paddingTop': '25px', 'margin': 'auto',
                 'borderStyle': 'solid', 'borderWidth': '5px', 'borderColor': '#B8860B'}
    eventoColor = 0
    return style

@app.callback(Output('AlarmaTexto', 'children'), [Input('interval-component', 'n_intervals')])
def TextoAlarma(n):
    global eventoTexto
    if eventoTexto != 0:
        mensaje =eventoTexto.Message.Text.split(':')
        res = 'Alarama Activa: {}: {}'.format(mensaje[1], round(float(mensaje[2]), 2))
    else:
        res = 'Alarma Inactiva'
    eventoTexto = 0
    return res

################################################## Guardar ###########################################################
nGuardar_ant = 0
nNoGuardar_ant = 0
@app.callback(Output('indicativoGuardar', 'children'), [Input('guardar', 'n_clicks'),Input('Noguardar', 'n_clicks')])
def Guardar(nGuardar, nNoGuardar):
    global nGuardar_ant, nNoGuardar_ant
    if nGuardar_ant != nGuardar:
        nGuardar_ant = nGuardar
        return 'Guardando'
    elif nNoGuardar_ant != nNoGuardar:
        return 'No Guardando'
    else:
        return 'No Guardando'






#################################################### Supervisión ######################################################
# Se guardan los valores
@app.callback(Output('intermediate', 'children'), [Input('interval-component', 'n_intervals')])
def UpdateInfo(n):
    global evento
    h1 = cliente.alturas['H1'].get_value()
    h2 = cliente.alturas['H2'].get_value()
    h3 = cliente.alturas['H3'].get_value()
    h4 = cliente.alturas['H4'].get_value()
    alturas = {'h1':h1, 'h2': h2, 'h3': h3, 'h4': h4}
    return json.dumps(alturas)

# Se actualiza el texto
@app.callback(Output('live-update-text1', 'children'), [Input('intermediate', 'children')])
def UpdateText(alturas):
    alturas = json.loads(alturas)
    style = {'padding': '5px', 'fontSize': '16px', 'border': '2px solid powderblue'}
    return [
        html.Span('Tanque 1: {}'.format(round(alturas['h1'], 2)), style=style),
        html.Span('Tanque 2: {}'.format(round(alturas['h2'], 2)), style=style),
        html.Span('Tanque 3: {}'.format(round(alturas['h3'], 2)), style=style),
        html.Span('Tanque 4: {}'.format(round(alturas['h4'], 2)), style=style)
    ]

times = deque(maxlen=100)
h1 = deque(maxlen=100)
h2 = deque(maxlen=100)
h3 = deque(maxlen=100)
h4 = deque(maxlen=100)
V1 = deque(maxlen=100)
V2 = deque(maxlen=100)
# Valores de los estanques
@app.callback(Output('live-update-graph1', 'figure'), [Input('intermediate', 'children')])
def UpdateGraph(alturas):
    global times, h1,h2,h3,h4
    alturas = json.loads(alturas)
    times.append(datetime.datetime.now())
    # Alturas
    h1.append(alturas['h1'])
    h2.append(alturas['h2'])
    h3.append(alturas['h3'])
    h4.append(alturas['h4'])

    plot1 = go.Scatter(x=list(times), y=list(h1), name='Tanque1', mode='lines+markers')
    plot2 = go.Scatter(x=list(times), y=list(h2), name='Tanque2', mode='lines+markers')
    plot3 = go.Scatter(x=list(times), y=list(h3), name='Tanque3', mode='lines+markers')
    plot4 = go.Scatter(x=list(times), y=list(h4), name='Tanque4', mode='lines+markers')

    fig = plotly.tools.make_subplots(rows=2, cols=2, vertical_spacing=0.2,
                                     subplot_titles=('Tanque1', 'Tanque2', 'Tanque3', 'Tanque4'), print_grid=False)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    fig['layout']['plot_bgcolor'] = colors['background']
    fig['layout']['paper_bgcolor'] = colors['background']
    fig['layout']['font']['color'] = colors['text']

    #fig['layout'].update(height=600, width=600, title='Niveles de los Tanques')
    fig.append_trace(plot1, 1, 1)
    fig.append_trace(plot2, 1, 2)
    fig.append_trace(plot3, 2, 1)
    fig.append_trace(plot4, 2, 2)

    return fig

################################################# Control ##############################################################

@app.callback(
    Output(component_id='MyDiv', component_property='children'),
    [Input(component_id='Eleccion', component_property='value')]
)
def update_output_div(input_value):
    return 'Ha seleccionado el modo: {}'.format(input_value)

#################### Modo Manual ##################################
@app.callback(Output('1', 'children'), [Input('FrecSlider', 'value')])
def ActualizaLabels1(n):
    return 'Frec: {} Hz'.format(n)
@app.callback(Output('2', 'children'), [Input('AmpSlider', 'value')])
def ActualizaLabels2(n):
    return 'Amp: {}'.format(n)
@app.callback(Output('3', 'children'), [Input('FaseSlider', 'value')])
def ActualizaLabels3(n):
    return 'Fase: {}'.format(n)
@app.callback(Output('4', 'children'), [Input('OffsetSlider', 'value')])
def ActualizaLabels4(n):
    return 'Offset: {}'.format(n)
@app.callback(Output('Razon1Label', 'children'), [Input('Razon1', 'value')])
def ActualizaRazon1(value):
    return 'Razon 1: {}'.format(value)
@app.callback(Output('Razon2Label', 'children'), [Input('Razon2', 'value')])
def ActualizaRazon1(value):
    return 'Razon 2: {}'.format(value)


#################### Modo Automático ##############################

# PIDS
pid1 = PID()
pid2 = PID()

times_list = deque(maxlen=100)
v1_list = deque(maxlen=100)
v2_list = deque(maxlen=100)
t = 0

memoria = []
T_init = 0

@app.callback(Output('live-update-graph2', 'figure'),
              [Input('intermediate', 'children')],
              [State('Eleccion', 'value'), State('TipoManual', 'value'),
                State('FrecSlider', 'value'),State('AmpSlider', 'value'),
                State('OffsetSlider', 'value'),State('FaseSlider', 'value'),
                State('ManualFijo', 'value'), State('Kp', 'value'),
                State('Ki', 'value'), State('Kd', 'value'), State('Kw','value'),
                State('SPT1', 'value'), State('SPT2', 'value'),
                State('indicativoGuardar', 'children'), State('Formato', 'value'),
                State('Razon1', 'value'), State('Razon2', 'value')])
def SalidaControlador(alturas, eleccion, tipoManual, frec, amp, offset, fase, manualFijo,
                      Kp, Ki, Kd, Kw, SPT1, SPT2, guardando, formato, razon1, razon2):
    global times_list, v1_list, v2_list, t, pid1, pid2, memoria, T_init
    alturas = json.loads(alturas)
    T = datetime.datetime.now()
    v1 = v2 = 0
    cliente.razones['razon1'].set_value(razon1)
    cliente.razones['razon2'].set_value(razon2)
    # Si se elige la sinusoide
    if eleccion == 'Manual' and tipoManual == 'sinusoide':
        v1 = amp*np.cos(2*np.pi*frec*t + fase) + offset
        v2 = amp*np.cos(2*np.pi*frec*t + fase) + offset
        t += 1/frecMax

    # Si se elige el valor fijo
    elif eleccion == 'Manual' and tipoManual == 'fijo':
        v1 = float(manualFijo)
        v2 = float(manualFijo)

    # Modo automático
    elif eleccion == 'Automatico':
        # SetPoints
        pid1.setPoint = float(SPT1)
        pid2.setPoint = float(SPT2)

        # Constantes
        pid1.Kp = float(Kp)
        pid1.Ki = float(Ki)
        pid1.Kd = float(Kd)
        pid1.Kw = float(Kw)

        pid2.Kp = float(Kp)
        pid2.Ki = float(Ki)
        pid2.Kd = float(Kd)
        pid2.Kw = float(Kw)

        v1 = pid1.update(alturas['h1'])
        v2 = pid2.update(alturas['h2'])

    # Guardando
    if guardando == 'Guardando':
        if memoria == []:
            T_init = datetime.datetime.now()

        if eleccion == 'Manual':
            memoria.append({'time':T,'h1': alturas['h1'], 'h2': alturas['h2'], 'h3': alturas['h3'], 'h4': alturas['h4'],
                            'v1': v1, 'v2':v2, 'modo': '{}-{}'.format(eleccion, tipoManual)})
        else:
            memoria.append(
                {'time': T, 'h1': alturas['h1'], 'h2': alturas['h2'], 'h3': alturas['h3'], 'h4': alturas['h4'],
                 'v1': v1, 'v2': v2, 'modo': '{}'.format(eleccion), 'sp1': float(SPT1), 'sp2': float(SPT2),
                 'Ki': float(Ki),'Kd': float(Kd),'Kp': float(Kp),'Kw': float(Kw)})

    elif guardando == 'No Guardando' and memoria != []:
        memoria = pd.DataFrame(memoria)
        memoria = memoria.set_index('time')
        if formato == 'csv':
            memoria.to_csv('{}/{}-{}.csv'.format(directory,T_init, T))
        elif formato == 'json':
            memoria.to_json('{}/{}-{}.json'.format(directory,T_init, T))
        else:
            memoria.to_pickle('{}/{}-{}.pkl'.format(directory,T_init, T))
        memoria = []


    cliente.valvulas['valvula1'].set_value(v1)
    cliente.valvulas['valvula2'].set_value(v2)
    times_list.append(T)
    v1_list.append(v1)
    v2_list.append(v2)

    plot1 = go.Scatter(x=list(times_list), y=list(v1_list), name='Valvula1', mode='lines+markers')
    plot2 = go.Scatter(x=list(times_list), y=list(v2_list), name='Valvula2', mode='lines+markers')


    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2,
                                     subplot_titles=('Valvula1', 'Valvula2'), print_grid=False)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 30
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    fig['layout']['plot_bgcolor'] = colors['background']
    fig['layout']['paper_bgcolor'] = colors['background']
    fig['layout']['font']['color'] = colors['text']

    # fig['layout'].update(height=600, width=600, title='Niveles de los Tanques')
    fig.append_trace(plot1, 1, 1)
    fig.append_trace(plot2, 2, 1)

    return fig


app.run_server()
