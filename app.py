import json
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State, ALL
import plotly.express as px
from utility import process_attribute_name, call_external_api
from predict import make_prediction

app = Dash(__name__, suppress_callback_exceptions=True)

# Load metadata
with open('metadata.json') as f:
    metadata = json.load(f)

# Extracting names, descriptions, and parsed attributes
products = [
    {
        "id": item["productId"],
        "name": item["name"],
        "description": item["description"],
        "attributes": item["attributes"]
    }
    for item in metadata
]

# Dash layout
app.layout = html.Div([
    html.H1("Occupancy Data Dashboard"),
    html.Div(id='metadata'),
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': prod['name'], 'value': prod['id']}
                 for prod in products],
        placeholder='Select a product'
    ),
    html.Div(id='product-info'),
    html.Div(id='attribute-info'),
    # Div to hold the attribute data graph
    dcc.Loading(
        id='loading-spinner',
        type='circle',
        children=[
            html.Div(id='attribute-data-graph'),
            html.Div(id='prediction-graph')  # Div to hold the prediction graph
        ],
        style={'marginTop': 50}
    )
])


@app.callback(
    Output('metadata', 'children'),
    Input('product-dropdown', 'value')
)
def display_metadata(product_id):
    if product_id:
        product = next(
            (prod for prod in products if prod['id'] == product_id), None)
        if product:
            attributes = []
            for attr in product['attributes']:
                processed_name = process_attribute_name(attr['name'])
                attributes.append(
                    html.Li([
                        html.Span(processed_name, style={
                                  'margin-right': '10px'}),
                        html.Button(
                            'Fetch Data', id={'type': 'fetch-data-button', 'index': attr['id']},
                            n_clicks=0, style={'margin-left': '10px'})
                    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'})
                )
            return html.Div([
                html.H2(f"Location: {product['name']}"),
                html.Div([
                    html.Ul(attributes, style={
                            'list-style-type': 'none', 'padding': 0})
                ], style={'max-height': '200px', 'overflow-y': 'auto', 'border': '1px solid #ccc', 'padding': '10px'})
            ])
    return html.P("Select a product to see details.")


@app.callback(
    Output('attribute-info', 'children'),
    Output('attribute-data-graph', 'children'),
    [Input({'type': 'fetch-data-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'fetch-data-button', 'index': ALL}, 'id')]
)
def fetch_data(n_clicks, ids):
    if not any(n_clicks):
        return "", ""
    button_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if button_id:
        attr_id = json.loads(button_id.split('.')[0])['index']
        data = call_external_api(attr_id)

        if isinstance(data, list) and len(data) > 0 and 'statistics' in data[0]:
            df = pd.DataFrame(data[0]['statistics'])
            df['ds'] = pd.to_datetime(df['stattime'], unit='ms')

            # Generate title
            first_time = df['ds'].min().strftime('%Y-%m-%d')
            last_time = df['ds'].max().strftime('%Y-%m-%d')

            title = f"Bar chart of [add_name_later] from {first_time} to {last_time}"

            # Create a bar chart
            fig = px.bar(df, x='ds', y='sum', title=title)
            return (html.Div([
                html.H3(""),
                html.Button('Predict Next 7 Days',
                            id='predict-button', n_clicks=0)
            ]), dcc.Graph(figure=fig))
        else:
            return html.Div([html.P(f"No statistics found for attribute {attr_id}.")]), ""
    return "", ""


@app.callback(
    [Output('prediction-graph', 'children'),
     Output('attribute-data-graph', 'style')],
    Input('predict-button', 'n_clicks'),
    State('attribute-data-graph', 'children')
)
def update_forecast(n_clicks, graph_data):
    if n_clicks == 0:
        return "", {"width": "100%"}

    if graph_data and 'props' in graph_data:
        fig = graph_data['props']['figure']
        df = pd.DataFrame(
            {'ds': fig['data'][0]['x'], 'y': fig['data'][0]['y']})
        forecast = make_prediction(df)
        
        first_time = df['ds'].min()
        last_time = df['ds'].max()
        first_time = first_time[0:-9]
        last_time = last_time[0:-9]

        forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d')
        forecast['yhat'] = forecast['yhat'].round().astype(int)

        fig_forecast = px.line(forecast, x='ds', y='yhat',
                               title=f'7 Days Forecast from {first_time} to {last_time}')

        return html.Div([
            html.Div(dcc.Graph(figure=fig_forecast)),
        ]), {"display": "inline-block"}
    return "", {"width": "100%"}


if __name__ == '__main__':
    app.run_server(debug=True)
