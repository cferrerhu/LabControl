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

y1 = 0.7
y2 = 0.6
r1.set_value(y1)
r2.set_value(y2)

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
     daq.BooleanSwitch(
        id='my-boolean-switch',
        on=False
    ),
    html.Div(id='boolean-switch-output', children='Manual Mode')
    ])
    ]
))



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
    if on:
        run_pid.start()
        return 'Automatic Mode'
    else:
        run_pid.stop()
        return 'Manual mode'



if __name__ == '__main__':
    app.run_server(debug=True)
