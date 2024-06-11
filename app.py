import json
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from utility import parse_attributes
app = Dash(__name__)

# Load metadata
with open('metadata.json') as f:
    metadata = json.load(f)

# Function to parse attributes


def parse_attributes(attributes):
    pattern = re.compile(
        r"Kaleva sports park ➞ (Entire area|Whole area) ➞ (.*?) ➞")
    parsed_output = []
    for attribute in attributes:
        match = pattern.search(attribute['name'])
        if match:
            area = match.group(2)
            parsed_output.append(f"Kaleva sports park ({area})")
    return parsed_output


# Extracting names, descriptions, and parsed attributes
products = [
    {
        "id": item["productId"],
        "name": item["name"],
        "description": item["description"],
        "attributes": item["attributes"]}
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
            attributes = html.Ul([html.Li(attr['name'])
                                 for attr in product['attributes']])
            return html.Div([
                html.H2(product['name']),
                html.P(product['description']),
                html.H3("Attributes:"),
                attributes
            ])
    return html.P("Select a product to see details.")


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
