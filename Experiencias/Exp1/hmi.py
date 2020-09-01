import numpy as np
import threading
import dash
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
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
tDeque = deque(maxlen=100)
h1Deque = deque(maxlen=100)
h2Deque = deque(maxlen=100)
h3Deque = deque(maxlen=100)
h4Deque = deque(maxlen=100)
v1Deque = deque(maxlen=100)
v2Deque = deque(maxlen=100)

# Initialize opcua variables
client = Client('opc.tcp://localhost:4840/freeopcua/server/')
client.connect()
objects_node = client.get_objects_node()
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

# Initial conditions
y1 = 0.6
y2 = 0.6
r1.set_value(y1)
r2.set_value(y2)
h1.set_value(20)
h2.set_value(20)
h3.set_value(20)
h4.set_value(20)
v1.set_value(0)
v2.set_value(0)

values = [h1, h2, h3, h4, v1, v2, r1, r2]

data_record = Record(values, 'csv')
run_pid = RunPID(values)


app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


app.layout = html.Div(html.Div(
    [
    html.H2('Dashy: Mining water tank control'),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(id='interval-component',interval=100, n_intervals=0),
    html.Div([
        html.Div([html.H4('Tanque 1', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Tank(id='tank-1', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        html.Div([html.H4('Tanque 2', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Tank(id='tank-2', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        html.Div([html.H4('Tanque 3', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Tank(id='tank-3', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        html.Div([html.H4('Tanque 4', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Tank(id='tank-4', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    ),
    html.Div([
        html.Div([
            html.H4('Válvula 1', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Gauge(
                id='valve-1',
                showCurrentValue=True,
                units="%",
                min=0,
                max=100,
                value=50
                )], style={'display':'inline-block'}),
        html.Div([
            html.H4('Válvula 2', style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
            daq.Gauge(
                id='valve-2',
                showCurrentValue=True,
                units="%",
                min=0,
                max=100,
                value=50
            )], style={'display':'inline-block'})
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    ),
    html.Div([html.Div(id='file-selection', children='Select the file extension'),
        dcc.Dropdown(
            id='file-dropdown',
            style={'height': '40px', 'width': '120px'},
            options=[
            {'label': 'csv file', 'value': 'csv'},
            {'label': 'txt file', 'value': 'txt'},
            {'label': 'npy file', 'value': 'npy'}
            ],
            value='csv'
            ),
        html.Div(id='dd-output-container'),
        html.Div([
            html.Button('Start Recording', id='btn_record', n_clicks=0),
            html.Button('Stop Recording', id='btn_norecord', n_clicks=0),
            html.Div(id='my-button-div', children='No recording')
        ])
    ]),
    html.Div([
        daq.PowerButton(
            id='my-boolean-switch',
            on= not run_pid.stopped
        ),
        html.Div(id='boolean-switch-output', children='Manual Mode'),
        html.I("Set the Setpoints for the tanks."),
        html.Br(),
        dcc.Input(id="setpoint1", type="number", placeholder="SetPoint 1, Default 15", debounce=True),
        dcc.Input(id="setpoint2", type="number", placeholder="SetPoint 2, Default 15", debounce=True),
        html.Div(id="output")
    ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    ),
    html.Div([
        html.I("Set the Voltage for the valves, from 0 to 1 [V]"),
        html.Br(),
        dcc.Input(id="Voltage1", type="number", placeholder="Voltage 1", debounce=True),
        dcc.Input(id="Voltage2", type="number", placeholder="Voltage 2", debounce=True),
        html.Div(id="Voltage-output")
    ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    ),
    html.Div([
        html.I("Set the flux Rate between 0 and 1" ),
        html.Br(),
        dcc.Input(id="Gamma1", type="number", placeholder="Flux Rate 1", debounce=True),
        dcc.Input(id="Gamma2", type="number", placeholder="Flux Rate 2", debounce=True),
        html.Div(id="Gamma-output")
    ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    ),
    html.Div([html.Div(id='Variable-selection', children='Select the variable of the PID'),
        dcc.Dropdown(
            id='k-dropdown',
            style={'height': '40px', 'width': '120px'},
            options=[
            {'label': 'Kp', 'value': 'Kp'},
            {'label': 'Kd', 'value': 'Kd'},
            {'label': 'Ki', 'value': 'Ki'},
            {'label': 'Kw', 'value': 'Kw'}
            ],
            value=''
            ),
        html.Div([
            html.I("Set the variable" ),
            html.Br(),
            dcc.Input(id="K1", type="number", placeholder="K1", debounce=True),
            dcc.Input(id="K2", type="number", placeholder="K2", debounce=True),
            html.Div(id="K-output")
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
        )
    ])
]))




@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def UpdateGraph(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, v1Deque, v2Deque

    tDeque.append(t)
    h1Deque.append(h1.get_value())
    h2Deque.append(h2.get_value())
    h3Deque.append(h3.get_value())
    h4Deque.append(h4.get_value())
    v1Deque.append(v1.get_value())
    v2Deque.append(v2.get_value())
    t += 1

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
                       yaxis_title='Height (cm)')

    return fig

# Tanks
@app.callback(dash.dependencies.Output('tank-1', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque
    value = round(h1Deque[-1], 3)
    return value

@app.callback(dash.dependencies.Output('tank-2', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque
    value = round(h2Deque[-1], 3)
    return value

@app.callback(dash.dependencies.Output('tank-3', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque
    value = round(h3Deque[-1], 3)
    return value

@app.callback(dash.dependencies.Output('tank-4', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque
    value = round(h4Deque[-1], 3)
    return value

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


@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('file-dropdown', 'value')])
def update_output(value):
    #global data_record
    data_record.ext = value
    return 'You have selected "{}" file extension to be storaged'.format(value)


@app.callback(
    dash.dependencies.Output(component_id='my-button-div', component_property='children'),
    [dash.dependencies.Input('btn_record', 'n_clicks'),
     dash.dependencies.Input('btn_norecord', 'n_clicks')])
def record(btn_r, btn_nr):
    ctx = dash.callback_context
    print(f'ctx states:{ctx.states}')
    print(f'ctx triggered:{ctx.triggered}')
    print(f'ctx inputs:{ctx.inputs}')
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





    # return f'{k}, {k1}, {k2}'



if __name__ == '__main__':
    app.run_server(debug=True)
