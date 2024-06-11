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
    dcc.Loading(
        id='loading-spinner',
        type='circle',
        children=[
            html.Div(id='attribute-data-graph')
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
            ]), dcc.Graph(figure=fig))
        else:
            return html.Div([html.P(f"No statistics found for attribute {attr_id}.")]), ""
    return "", ""


if __name__ == '__main__':
    app.run_server(debug=True)
