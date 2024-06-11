import pandas as pd
from prophet import Prophet


def make_prediction(data):
    df = pd.DataFrame(data)
    print("DataFrame created:", df)  # Debug print statement

    # Ensure the 'ds' column is in the correct datetime format
    df['ds'] = pd.to_datetime(df['ds'])
    df['y'] = df['y']

    model = Prophet()
    model.fit(df)

    # Generate future dataframe starting from the end of the current data
    last_date = df['ds'].max()
    future = model.make_future_dataframe(periods=7)
    future = future[future['ds'] > last_date]

    forecast = model.predict(future)

    print("Forecast result:", forecast)  # Debug print statement
    return forecast[['ds', 'yhat']]
