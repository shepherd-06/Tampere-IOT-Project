import json
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State, ALL
import plotly.express as px
from utility import process_attribute_name, call_external_api

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
    html.Div(id='attribute-data-graph'),
    html.Button('Fetch Historical Data', id='fetch-button', n_clicks=0),
    dcc.Graph(id='historical-data', style={'display': 'none'}),
    html.Button('Predict Next 24 Hours', id='predict-button', n_clicks=0),
    dcc.Graph(id='forecast-data', style={'display': 'none'})
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
                            'Fetch Data', id={'type': 'fetch-data-button',
                                              'index': attr['id']},
                            n_clicks=0, style={'margin-left': '10px'})
                    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '10px'})
                )
            return html.Div([
                html.H2(product['name']),
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
        return "No button clicked yet.", ""
    button_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if button_id:
        attr_id = json.loads(button_id.split('.')[0])['index']
        data = call_external_api(attr_id)

        if isinstance(data, list) and len(data) > 0 and 'statistics' in data[0]:
            df = pd.DataFrame(data[0]['statistics'])
            df['ds'] = pd.to_datetime(df['stattime'], unit='ms')
            
            # Generate title
            first_time = df['ds'].min().strftime('%Y-%m-%d %H:%M:%S')
            last_time = df['ds'].max().strftime('%Y-%m-%d %H:%M:%S')
            title = f"Bar chart of [add_name_later] from {first_time} to {last_time}"

            # Create a bar chart
            fig = px.bar(df, x='ds', y='sum', title='')  # Empty title for now
            return (html.Div([
                html.P(f"{title}"),
            ]), dcc.Graph(figure=fig))
        else:
            return html.Div([html.P(f"No statistics found for attribute {attr_id}.")]), ""
    return "No button clicked.", ""


@app.callback(
    Output('historical-data', 'figure'),
    Input('fetch-button', 'n_clicks'),
    Input('product-dropdown', 'value')
)
def update_graph(n_clicks, product_id):
    if not product_id or n_clicks == 0:
        return {}

    # Placeholder data; replace with actual data fetching logic
    data = [
        {"stattime": 1718037360000, "sum": 60},
        {"stattime": 1718037420000, "sum": 60},
        {"stattime": 1718037480000, "sum": 60},
        # Add more data points...
    ]

    df = pd.DataFrame(data)
    df['ds'] = pd.to_datetime(df['stattime'], unit='ms')
    df['y'] = df['sum']
    df = df[['ds', 'y']]

    fig_historical = px.line(
        df, x='ds', y='y', title='Historical Occupancy Data')

    return fig_historical


@app.callback(
    Output('forecast-data', 'figure'),
    Input('predict-button', 'n_clicks'),
    Input('product-dropdown', 'value')
)
def update_forecast(n_clicks, product_id):
    if not product_id or n_clicks == 0:
        return {}

    # Placeholder logic for fetching prediction data
    # Replace with actual call to prediction script or API
    # For now, return an empty figure
    return {}


if __name__ == '__main__':
    app.run_server(debug=True)
