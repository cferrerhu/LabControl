import numpy as np
from cliente import Cliente # cliente OPCUA
import threading
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import plotly
from collections import deque

T = np.linspace(0,1000, 1001)
sin = np.sin(T)
cos = np.cos(T)
t = 0
sinDeque = deque(maxlen=100)
cosDeque = deque(maxlen=100)
tDeque = deque(maxlen=100)


app = dash.Dash()
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(html.Div([html.H4('Ejemplo'), html.Div(id='live-update-text'), dcc.Graph(id='live-update-graph'),
                                dcc.Interval(id='interval-component', interval=100, n_intervals=0)]))

@app.callback(Output('live-update-text', 'children'), [Input('interval-component', 'n_intervals')])
def updateText(n):
    global t, sinDeque, cosDeque, tDeque
    style = {'padding': '5px', 'fontSize': '16px'}
    sinDeque.append(sin[t])
    cosDeque.append(cos[t])
    tDeque.append(t)
    valores = [html.Span('Seno: {}'.format(round(sin[t], 3)), style=style),
               html.Span('Coseno: {}'.format(round(cos[t], 3)), style=style)]
    t += 1
    return valores


@app.callback(Output('live-update-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def UpdateGraph(n):
    global tDeque, sinDeque, cosDeque
    data = {'time': list(tDeque), 'sin': list(sinDeque), 'cos': list(cosDeque)}
    # Se crea el grafico
    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=2, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}

    fig.append_trace({
        'x': data['time'],
        'y': data['sin'],
        'name': 'Altitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    fig.append_trace({
        'x': data['time'],
        'y': data['cos'],
        'text': data['time'],
        'name': 'Longitude vs Latitude',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 2, 1)

    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
