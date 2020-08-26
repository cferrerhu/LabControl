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
values = [h1, h2, h3, h4, v1, v2, r1, r2]

app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


app.layout = html.Div(html.Div(
    [
    html.H2('Dashy: Mining water tank control'),
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(id='interval-component',interval=100, n_intervals=0),
    html.Div([
        html.Div([html.H4('Tanque 1'),
            daq.Tank(id='tank-1', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        html.Div([html.H4('Tanque 2'),
            daq.Tank(id='tank-2', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'})]),
        html.Div([html.H4('Tanque 3'),
            daq.Tank(id='tank-3', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'}),
        html.Div([html.H4('Tanque 4'),
            daq.Tank(id='tank-4', value=5, min=0, max=50,
                showCurrentValue=True, units='cm',
                style={'margin-left': '50px'})], style={'display':
                    'inline-block'})]
        ),
        html.Div([
            daq.Gauge(
                id='valve-1',
                min=-1,
                max=1,
                value=0.5
            ),
            daq.Gauge(
                id='valve-2',
                min=-1,
                max=1,
                value=0.5
            )
        ])
        ], style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
    )
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
    value = round(v1Deque[-1], 3)
    return value

@app.callback(dash.dependencies.Output('valve-2', 'value'), [Input('interval-component', 'n_intervals')])
def update_tank(n):
    global t, tDeque, h1Deque, h2Deque, h3Deque, h4Deque, v2Deque
    value = round(v2Deque[-1], 3)
    return value


if __name__ == '__main__':
    app.run_server(debug=True)

