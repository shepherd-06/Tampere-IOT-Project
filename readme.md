# Occupancy Data Dashboard with Forecasting

## Project Overview

This project aims to create a comprehensive occupancy data dashboard for Kalevan liikuntapuisto in Tampere City. The dashboard displays historical occupancy data and provides a 30-day forecast using Prophet for predicting future occupancy trends. This project was developed as part of the Tampere City IoT Hackathon on June 11, completed within 6 hours.

## Features

### Data Visualization

Displays historical occupancy data in an interactive bar chart.
Provides clear axis titles for better understanding: "Days" on the x-axis and "Occupancy (Total)" on the y-axis.

### Forecasting

Generates a 30-day occupancy forecast using Prophet.
Forecast data is displayed in a line chart.
A table displays the forecasted occupancy alongside the graph for easy reference.

### Interactive UI

Users can select a specific product to view detailed data and forecasts.
Loading spinner to indicate data fetching.
Bootstrap integration for a responsive and aesthetically pleasing UI.

## Installation

Clone the repository:

```bash
git clone <repository_url>
cd <repository_directory>
```

Create a virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python app.py
```

Open a web browser and go to `http://127.0.0.1:8050/` to view the dashboard.

## How It Works

### Dashboard

* Dropdown Menu: Allows the user to select a specific location's occupancy data.
* Fetch Data Button: Fetches historical occupancy data for the selected location.
* Predict Button: Generates a 30-day forecast based on the fetched historical data.

### Prediction Model

The prediction model uses Prophet to generate forecasts. The model takes the historical data, processes it, and predicts future occupancy for the next 30 days. The results are displayed in both a line chart and a table format.

### Example Graphs

#### Historical Occupancy Data

![Historical Occupancy Data of Beach-Kentaa from Jan 01 to Feb 11](https://github.com/shepherd-06/Tampere-IOT-Project/blob/master/images/plot_1.png)

#### 30-Day Forecast

![30 Day Usage Forecast of Beach-Kentaa from Feb 12 to Mar 12](https://github.com/shepherd-06/Tampere-IOT-Project/blob/master/images/plot_1_prediction.png)

## Acknowledgements

This project was developed for the Tampere City IoT Hackathon on June 11. Special thanks to the organizers and participants for their support and collaboration.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or suggestions, please contact:

* Name: Mohammad Asif Ibtehaz
* Email: `asif.ibtehaz@tuni.fi`
