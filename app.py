import json
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State, ALL
import plotly.express as px
import seaborn as sns
from utility import process_attribute_name, call_external_api
from predict import make_prediction

# Add external stylesheet for Bootstrap
external_stylesheets = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']

app = Dash(__name__, suppress_callback_exceptions=True,
           external_stylesheets=external_stylesheets)

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

# Seaborn color palette
seaborn_palette = sns.color_palette("Set2").as_hex()

# Dash layout
app.layout = html.Div([
    html.H1("Occupancy Data Dashboard", className="text-center my-4"),
    html.Div(id='metadata', className="container"),
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': prod['name'], 'value': prod['id']}
                 for prod in products],
        placeholder='Select a product',
        className="form-control my-3"
    ),
    html.Div(id='product-info', className="container"),
    html.Div(id='attribute-info', className="container"),
    # Div to hold the attribute data graph
    dcc.Loading(
        id='loading-spinner',
        type='circle',
        children=[
            html.Div(id='attribute-data-graph', className="container"),
            # Div to hold the prediction graph
            html.Div(id='prediction-graph', className="container mt-4")
        ],
        style={'marginTop': 50}
    )
], className="container")


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
                # processed_name = process_attribute_name(attr['name'])
                processed_name = attr['name']
                attributes.append(
                    html.Li([
                        html.Span(processed_name, className="mr-3"),
                        html.Button(
                            'Fetch Data', id={'type': 'fetch-data-button', 'index': attr['id']},
                            n_clicks=0, className="btn btn-primary ml-3")
                    ], className="d-flex align-items-center mb-2")
                )
            return html.Div([
                html.H4(f"Location: {product['name']}",
                        className="my-3 text-center"),
                html.Div([
                    html.Ul(attributes, className="list-unstyled p-2", style={
                            'max-height': '200px', 'overflow-y': 'auto', 'border': '1px solid #ccc'})
                ], className="p-3 border")
            ])
    return html.P("Select a product to see details.", className="text-muted")


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

            # Create a bar chart with Seaborn color palette
            fig = px.bar(df, x='ds', y='sum', title=title,
                         labels={'ds': 'Days', 'sum': 'Occupancy (Total)'},
                         color_discrete_sequence=seaborn_palette)
            return (html.Div([
                html.H3("", className="mt-4"),
                html.Button('Predict Next 7 Days', id='predict-button',
                            n_clicks=0, className="btn btn-primary mt-3")
            ]), dcc.Graph(figure=fig))
        else:
            return html.Div([html.P(f"No statistics found for attribute {attr_id}.", className="text-danger")]), ""
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

        forecast['ds'] = forecast['ds'].dt.strftime('%Y-%m-%d')
        forecast['yhat'] = forecast['yhat'].round().astype(int)

        first_time = forecast['ds'].min()
        last_time = forecast['ds'].max()

        fig_forecast = px.line(forecast, x='ds', y='yhat',
                               title=f'7 Days Forecast from {first_time} to {last_time}',
                               labels={'ds': 'Days', 'yhat': 'Occupancy (Total)'},
                               color_discrete_sequence=seaborn_palette)

        return html.Div([
            html.Div(dcc.Graph(figure=fig_forecast)),
        ]), {"display": "inline-block"}
    return "", {"width": "100%"}


if __name__ == '__main__':
    app.run_server(debug=True)
