import numpy as np
import threading
import dash
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash.dependencies import Input, Output

import plotly
import plotly.graph_objects as go
from collections import deque
from opcua import Client
from opcua import ua
from Record import Record
from runpid import RunPID

T = np.linspace(0,1000, 1001)
t = 0
tDeque = deque(maxlen=1000)
h1Deque = deque(maxlen=1000)
h2Deque = deque(maxlen=1000)
h3Deque = deque(maxlen=1000)
h4Deque = deque(maxlen=1000)
v1Deque = deque(maxlen=1000)
v2Deque = deque(maxlen=1000)

tDeque.append(0)
h1Deque.append(0)
h2Deque.append(0)
h3Deque.append(0)
h4Deque.append(0)
v1Deque.append(0)
v2Deque.append(0)

alarmas = [0, 0, 0, 0]
alarma_texto = ''

style_global = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}

class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        thread_handler = threading.Thread(target=funcion_handler, args=(node, val))  # Se realiza la descarga por un thread
        thread_handler.start()

    def event_notification(self, event):
        global alarma_texto
        index = str(event.Message).find('Tanque')
        tank = int(str(event.Message)[61])
        alarmas[tank-1] = 1
        alarma_texto = 'Warning in Tank {}'.format(tank)


# Initialize opcua variables
client = Client('opc.tcp://localhost:4840/freeopcua/server/')
client.connect()
objects_node = client.get_objects_node()
root_node = client.get_root_node()
# Heights
h1 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque1', '2:h'])
h2 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque2', '2:h'])
h3 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque3', '2:h'])
h4 = objects_node.get_child(['2:Proceso_Tanques', '2:Tanques', '2:Tanque4', '2:h'])
# Valves
v1 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula1', '2:u'])
v2 = objects_node.get_child(['2:Proceso_Tanques', '2:Valvulas', '2:Valvula2', '2:u'])
# Ratios
r1 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon1', '2:gamma'])
r2 = objects_node.get_child(['2:Proceso_Tanques', '2:Razones', '2:Razon2', '2:gamma'])
# Alarmas
myevent = root_node.get_child(["0:Types", "0:EventTypes", "0:BaseEventType", "2:Alarma_nivel"])#Tipo de evento
obj_event = objects_node.get_child(['2:Proceso_Tanques', '2:Alarmas', '2:Alarma_nivel'])#Objeto Evento
handler_event = SubHandler()
sub_event = client.create_subscription(100, handler_event)#Subscripción al evento
handle_event = sub_event.subscribe_events(obj_event, myevent)

# Initial conditions
y1 = 0.6
y2 = 0.6
r1.set_value(y1)
r2.set_value(y2)
h1.set_value(40) # initial condition
h2.set_value(40) # initial condition
h3.set_value(40) # initial condition
h4.set_value(40) # initial condition
v1.set_value(0)
v2.set_value(0)

values = [h1, h2, h3, h4, v1, v2, r1, r2]

run_pid = RunPID(values)
data_record = Record(values, run_pid, 'csv')


app = dash.Dash()
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})
#app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/dZVMbK.css"})
app.css.append_css({"external_url": "https://github.com/plotly/dash-core-components/blob/master/dash_core_components/react-select@1.0.0-rc.3.min.css"})


app.layout = html.Div([
    html.H2(children="Dashboard Control de Tanques", style={'text-align':
        'center'}),
    html.P(id='placeholder'),
    html.Div([
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(id='interval-component',interval=2000, n_intervals=0),
        dcc.Interval(id='interval-fast',interval=500, n_intervals=0)
        ], style={'margin-top': '10px', 'margin-bottom': '10px', 'margin-left':
            '10px', 'margin-right': '10px', 'background': '#D3D3D3'}),
        html.Div([
            html.Div(
            [
                html.Div([
                        daq.Tank(id='tank-1', value=5, min=0, max=50,
                            showCurrentValue=True, units='cm',
                            label='Tank 1',
                            labelPosition='top',
                            style={'margin-left': '50px'}),
                        daq.Tank(id='tank-2', value=5, min=0, max=50,
                            showCurrentValue=True, units='cm',
                            label='Tank 2',
                            labelPosition='top',
                            style={'margin-left': '50px'}),
                        daq.Tank(id='tank-3', value=5, min=0, max=50,
                            showCurrentValue=True, units='cm',
                            label='Tank 3',
                            labelPosition='top',
                            style={'margin-left': '50px'}),
                        daq.Tank(id='tank-4', value=5, min=0, max=50,
                            showCurrentValue=True, units='cm',
                            label='Tank 4',
                            labelPosition='top',
                            style={'margin-left': '50px'}),
                    ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
                ),
                html.Div([
                    html.Div([
                        html.H4('Valve 1', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                        daq.Gauge(
                            id='valve-1',
                            showCurrentValue=True,
                            units="%",
                            min=0,
                            max=100,
                            value=50
                            )], style={'display':'inline-block'}),
                    html.Div([
                        html.H4('Valve 2', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                        daq.Gauge(
                            id='valve-2',
                            showCurrentValue=True,
                            units="%",
                            min=0,
                            max=100,
                            value=50
                        )], style={'display':'inline-block'})
                    ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'})
                ], style={'background': '#D3D3D3', 'margin-right': '10px',
                    'margin-top':'10px', 'margin-left': '10px'}),
            # Right panel
            html.Div([
                html.Div([
                    daq.PowerButton(
                        id='my-boolean-switch',
                        on= not run_pid.stopped
                    ),
                    html.Div(id='boolean-switch-output',
                        children='Manual Mode')], style={'width': '100%',
                            'display': 'flex', 'align-items': 'center',
                            'justify-content': 'center', 'margin-top': '10px',
                            'margin-bottom': '10px'}),
                dbc.Col([
                    dbc.Row([
                        html.Div(id='file-selection', children='Select the file extension'),
                        dbc.Col([
                            dcc.Dropdown(
                                id='file-dropdown',
                                style={'height': '40px', 'width': '120px'},
                                options=[
                                {'label': 'csv file', 'value': 'csv'},
                                {'label': 'txt file', 'value': 'txt'},
                                {'label': 'npy file', 'value': 'npy'}
                                ],
                                value='csv'
                                )
                        ]),
                    ], justify='center'),
                    dbc.Row([
                        html.Div(id='dd-output-container'),
                        dbc.Col([
                            html.Div([
                                html.Button('Start Recording', id='btn_record', n_clicks=0),
                                html.Button('Stop Recording', id='btn_norecord', n_clicks=0),
                                html.Div(id='my-button-div', children='No recording')
                            ])
                        ]),
                    ], justify='center'),
                    dbc.Row([
                        html.P("Set the Tanks Setpoints."),
                        dbc.Col([
                            dcc.Input(id="setpoint1", type="number", placeholder="SetPoint 1, Default 15", debounce=True),
                            dcc.Input(id="setpoint2", type="number", placeholder="SetPoint 2, Default 15", debounce=True),
                        ]),
                        html.Div(id="output")
                    ], justify='center'),
                    dbc.Row([
                        html.P("Set the Valves Voltage from 0 to 1 [V]"),
                        dbc.Col([
                            dcc.Input(id="Voltage1", type="number", placeholder="Voltage 1", debounce=True),
                            dcc.Input(id="Voltage2", type="number", placeholder="Voltage 2", debounce=True),
                        ]),
                            html.Div(id="Voltage-output")
                    ], justify='center'),
                    dbc.Row([
                        html.P("Set the flux Rate from 0 to 1" ),
                        dbc.Col([
                            dcc.Input(id="Gamma1", type="number", placeholder="Flux Rate 1", debounce=True),
                            dcc.Input(id="Gamma2", type="number", placeholder="Flux Rate 2", debounce=True),
                        ]),
                            html.Div(id="Gamma-output")
                    ], justify='center'),
                    dbc.Row([
                        html.Div([html.Div(id='Variable-selection',
                            children='Select the variable of the PID')]),
                        dbc.Col([
                            dcc.Dropdown(
                                id='k-dropdown',
                                style={'height': '40px', 'width': '120px'},
                                options=[
                                    {'label': 'Kp', 'value': 'Kp'},
                                    {'label': 'Kd', 'value': 'Kd'},
                                    {'label': 'Ki', 'value': 'Ki'},
                                    {'label': 'Kw', 'value': 'Kw'},
                                    {'label': 'fc', 'value': 'Pole'}
                                ],
                                value='')
                        ])], justify='center'),
                    dbc.Row([
                        html.I("Set the variable" ),
                        dbc.Col([
                            dcc.Input(id="K1", type="number", placeholder="K1", debounce=True),
                            dcc.Input(id="K2", type="number", placeholder="K2", debounce=True),
                            html.Div(id="K-output")
                        ])], align='center')]),
                        html.Br(),
                        html.Div(children='Last Warning:'),
                        html.Div(id='alarm-item',
                            children='No events reported', style={'background':
                                '#E3E3E3', 'text-align': 'center'})
                ], style={'background': '#D3D3D3', 'margin-left': '10px', 'margin-top':
                    '10px', 'margin-right': '10px'})
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'top','justify-content': 'center', 'background': '#C3C3C3'})
    ], style={'align-items': 'center', 'background': '#B3B3B3'})

@app.callback(Output('placeholder', 'children'), [Input('interval-fast', 'n_intervals')])
def UpdateGraph(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, v1Deque, v2Deque

    tDeque.append(t)
    h1Deque.append(h1.get_value())
    h2Deque.append(h2.get_value())
    h3Deque.append(h3.get_value())
    h4Deque.append(h4.get_value())
    v1Deque.append(v1.get_value())
    v2Deque.append(v2.get_value())
    t += 0.1

    return ''

@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def UpdateGraph(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, v1Deque, v2Deque

    data = {'time': list(tDeque), 'h1': list(h1Deque), 'h2': list(h2Deque),
            'h3': list(h3Deque), 'h4': list(h4Deque)}
    # Se crea el grafico
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=data['time'], y=data['h1'],
        name='Tank 1 height', mode = 'lines+markers'))
    fig.add_trace(go.Scatter(x=data['time'], y=data['h2'],
        name='Tank 2 height', mode = 'lines+markers'))
    fig.add_trace(go.Scatter(x=data['time'], y=data['h3'],
        name='Tank 3 height', mode = 'lines+markers'))
    fig.add_trace(go.Scatter(x=data['time'], y=data['h4'],
        name='Tank 4 height', mode = 'lines+markers'))

    fig.update_layout(title='Tank heights',
                       xaxis_title='Time (s)',
                       yaxis_title='Height (cm)',
                       plot_bgcolor="#F3F6FA",
                       paper_bgcolor='rgba(0,0,0,0)')

    return fig

# Tanks
@app.callback([Output('tank-1', 'value'), Output('tank-1', 'color'),
    Output('tank-1', 'label')], [Input('interval-component', 'n_intervals'), Input('my-boolean-switch', 'on')])
def update_tank(n, on):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, alarmas
    value = round(h1Deque[-1], 3)
    color = '#FF0000' if value < 10 else '#ADE2FA'
    label = 'Tank 1' if not on else 'Tank 1 ({}cm)'.format(run_pid.setpoint1)
    return value, color, label

@app.callback([Output('tank-2', 'value'), Output('tank-2', 'color'),
    Output('tank-2', 'label')], [Input('interval-component', 'n_intervals'), Input('my-boolean-switch', 'on')])
def update_tank(n, on):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, alarmas
    value = round(h2Deque[-1], 3)
    color = '#FF0000' if value < 10 else '#ADE2FA'
    label = 'Tank 2' if not on else 'Tank 2 ({}cm)'.format(run_pid.setpoint1)
    return value, color, label

@app.callback([Output('tank-3', 'value'), Output('tank-3', 'color')], [Input('interval-component', 'n_intervals'), Input('my-boolean-switch', 'on')])
def update_tank(n, on):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, alarmas
    value = round(h3Deque[-1], 3)
    color = '#FF0000' if value < 10 else '#ADE2FA'
    return value, color

@app.callback([Output('tank-4', 'value'), Output('tank-4', 'color')], [Input('interval-component', 'n_intervals'), Input('my-boolean-switch', 'on')])
def update_tank(n, on):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, alarmas
    value = round(h4Deque[-1], 3)
    color = '#FF0000' if value < 10 else '#ADE2FA'
    return value, color

@app.callback(dash.dependencies.Output('valve-1', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, v1Deque
    value = round(v1Deque[-1], 3)*100
    return value

@app.callback(dash.dependencies.Output('valve-2', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, v2Deque
    value = round(v2Deque[-1], 3)*100
    return value

@app.callback(Output('alarm-item', 'children'), [Input('interval-component', 'n_intervals')])
def update_text(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, v2Deque, alarma_texto
    value = alarma_texto
    return value

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('file-dropdown', 'value')])
def update_output(value):
    #global data_record
    data_record.ext = value
    return 'You have selected "{}" file extension to be stored'.format(value)


@app.callback(
    dash.dependencies.Output(component_id='my-button-div', component_property='children'),
    [dash.dependencies.Input('btn_record', 'n_clicks'),
     dash.dependencies.Input('btn_norecord', 'n_clicks')])
def record(btn_r, btn_nr):
    ctx = dash.callback_context
    # print(f'ctx states:{ctx.states}')
    # print(f'ctx triggered:{ctx.triggered}')
    # print(f'ctx inputs:{ctx.inputs}')
    if 'btn_record.n_clicks' in ctx.triggered[0].values():
        if data_record.stopped:

            data_record.start()

        return 'Starting to record as '+str(data_record.ext)
    elif 'btn_norecord.n_clicks' in ctx.triggered[0].values():

        if not data_record.stopped:

            data_record.stop()

        if data_record.ext == 'npy':
            return 'Stop recording, saved at wd with name '+str(data_record.namenpy)+'.'+str(data_record.ext)

        return 'Stop recording, saved at wd with name '+str(data_record.name)+'.'+str(data_record.ext)

@app.callback(
    dash.dependencies.Output('boolean-switch-output', 'children'),
    [dash.dependencies.Input('my-boolean-switch', 'on')])
def update_output(on):
    if on == True:
        run_pid.start()
        return 'Automatic Mode'
    elif on == False:
        run_pid.stop()
        return 'Manual mode'



@app.callback(
    Output("output", "children"),
    [Input("setpoint1", "value"), Input("setpoint2", "value")],
)
def update_output(input1, input2):
    # ctx = dash.callback_context
    # if input1 is not None and input2 is not None:
    #     run_pid.setpoint1 = input1
    #     run_pid.setpoint2 = input2
    #     run_pid.setPoint_pid()
    #
    #     return f'SetPoint Tank 1: {input1}, SetPoint Tank 2: {input2}'
    # return f'Nothing set'
    ctx = dash.callback_context
    if 'setpoint1.value' in ctx.triggered[0].values() and input1 is not None:
        if input1 <= 50 and input1 >=0:
            run_pid.setpoint1 = input1
            run_pid.setPoint_pid()
            print('Set point 1 changed to', run_pid.H1.setPoint)
            return f'SetPoint Tank 1: {input1}'
        else:
            return 'Set the SetPoint of Tank 1 between 0 and 50'

    if 'setpoint2.value' in ctx.triggered[0].values() and input2 is not None:
        if input2 <= 50 and input2 >=0:
            run_pid.setpoint2 = input2
            run_pid.setPoint_pid()
            print('Set point 2 changed to', run_pid.H2.setPoint)
            return f'SetPoint Tank 2: {input2}'
        else:
            return 'Set the SetPoint of Tank 2 between 0 and 50'


    if input1 is not None and input2 is not None:
        return f'Nothing set'






@app.callback(
    [Output("Voltage-output", "children"), Output('my-boolean-switch', 'on')],
    [Input("Voltage1", "value"), Input("Voltage2", "value")],
)
def update_output(input1, input2):
    ctx = dash.callback_context
    if 'Voltage1.value' in ctx.triggered[0].values() and input1 is not None:
        if input1 <= 1 and input1 >=0:
            v1 = values[4]
            v1.set_value(input1)

            return f'Voltage 1: {input1}', False
        else:
            return 'Set voltage 1 between 0 and 1 [V]', None

    if 'Voltage2.value' in ctx.triggered[0].values() and input2 is not None:
        if input2 <= 1 and input2 >=0:
            v2 = values[5]
            v2.set_value(input2)
            return f'Voltage 2: {input2}', False
        else:
            return 'Set voltage 2 between 0 and 1 [V]', None


    if input1 is not None and input2 is not None:
        return f'Nothing set', None

    return '', None


@app.callback(
    Output("Gamma-output", "children"),
    [Input("Gamma1", "value"), Input("Gamma2", "value")],
)
def update_output(input1, input2):
    ctx = dash.callback_context
    if 'Gamma1.value' in ctx.triggered[0].values() and input1 is not None:
        if input1 <= 1 and input1 >=0:
            r1 = values[6]
            r1.set_value(input1)
            return f'Flux Rate 1: {input1}'
        else:
            return 'Set the Flux Rate 1 between 0 and 1'

    if 'Gamma2.value' in ctx.triggered[0].values() and input2 is not None:
        if input2 <= 1 and input2 >=0:
            r2 = values[7]
            r2.set_value(input2)
            return f'Flux Rate  2: {input2}'
        else:
            return 'Set Flux Rate 2 between 0 and 1 '


    if input1 is not None and input2 is not None:
        return f'Nothing set'



@app.callback(
    dash.dependencies.Output('K-output', 'children'),
    [dash.dependencies.Input('k-dropdown', 'value'),
    dash.dependencies.Input("K1", "value"),
    dash.dependencies.Input("K2", "value")])
def update_output(k, k1, k2):
    ctx = dash.callback_context

    if k == 'Kp':
        if 'K1.value' in ctx.triggered[0].values() and k1 is not None:
            run_pid.H1.Kp = k1
            return f'{k}1 set to {k1}'
        if 'K2.value' in ctx.triggered[0].values() and k2 is not None:
            run_pid.H2.Kp = k2
            return f'{k}2 set to {k2}'

    elif k == 'Kd':
        if 'K1.value' in ctx.triggered[0].values() and k1 is not None:
            run_pid.H1.Kd = k1
            return f'{k}1 set to {k1}'
        if 'K2.value' in ctx.triggered[0].values() and k2 is not None:
            run_pid.H2.Kd = k2
            return f'{k}2 set to {k2}'

    elif k == 'Ki':
        if 'K1.value' in ctx.triggered[0].values() and k1 is not None:
            run_pid.H1.Ki = k1
            return f'{k}1 set to {k1}'
        if 'K2.value' in ctx.triggered[0].values() and k2 is not None:
            run_pid.H2.Ki = k2
            return f'{k}2 set to {k2}'

    elif k == 'Kw':
        if 'K1.value' in ctx.triggered[0].values() and k1 is not None:
            run_pid.H1.Kw = k1
            return f'{k}1 set to {k1}'
        if 'K2.value' in ctx.triggered[0].values() and k2 is not None:
            run_pid.H2.Kw = k2
            return f'{k}2 set to {k2}'

    elif k == 'Pole':
        if 'K1.value' in ctx.triggered[0].values() and k1 is not None:
            run_pid.H1.pole = k1
            return f'fc1 set to {k1} Hz'
        if 'K2.value' in ctx.triggered[0].values() and k2 is not None:
            run_pid.H2.pole = k2
            return f'fc2 set to {k2} Hz'





    # return f'{k}, {k1}, {k2}'



if __name__ == '__main__':
    app.run_server(debug=True)
