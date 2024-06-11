import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from prophet import Prophet

app = Dash(__name__)

# Sample data
data = [
    {"stattime": 1718037360000, "sum": 60},
    {"stattime": 1718037420000, "sum": 60},
    {"stattime": 1718037480000, "sum": 60},
    # Add more data points...
]

# Convert to DataFrame
df = pd.DataFrame(data)
df['ds'] = pd.to_datetime(df['stattime'], unit='ms')
df['y'] = df['sum']
df = df[['ds', 'y']]

# Train the Prophet model
model = Prophet()
model.fit(df)
future = model.make_future_dataframe(periods=24, freq='H')
forecast = model.predict(future)

# Dash layout
app.layout = html.Div([
    html.H1("Occupancy Data Dashboard"),
    dcc.Graph(id='historical-data'),
    dcc.Graph(id='forecast-data'),
    html.Button('Predict Next 24 Hours', id='predict-button', n_clicks=0),
])


@app.callback(
    Output('historical-data', 'figure'),
    Input('predict-button', 'n_clicks')
)
def update_graph(n_clicks):
    fig = px.line(df, x='ds', y='y', title='Historical Occupancy Data')
    return fig


@app.callback(
    Output('forecast-data', 'figure'),
    Input('predict-button', 'n_clicks')
)
def update_forecast(n_clicks):
    if n_clicks > 0:
        fig = px.line(forecast, x='ds', y='yhat',
                      title='Occupancy Prediction for Next 24 Hours')
        return fig
    else:
        return {}


if __name__ == '__main__':
    app.run_server(debug=True)
