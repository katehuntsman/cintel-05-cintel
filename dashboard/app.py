# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render

# From shiny.express, import just ui and inputs if needed
from shiny.express import ui

# Import necessary libraries
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats

# Import icons for use in the UI
from faicons import icon_svg

# --------------------------------------------
# Set a constant UPDATE INTERVAL for all live data
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 3  # Data update every 3 seconds

# --------------------------------------------
# Initialize a REACTIVE VALUE with a deque
# This deque will hold the most recent data
# --------------------------------------------

DEQUE_SIZE: int = 5  # Max number of entries in deque
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC to generate fake data
# This function will simulate new data points
# --------------------------------------------

@reactive.calc()
def reactive_calc_combined():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Simulate new data (temperature, humidity, pressure)
    temp = round(random.uniform(-18, -16), 1)  # Temperature in Celsius
    humidity = round(random.uniform(70, 90), 1)  # Humidity in percentage
    pressure = round(random.uniform(980, 1020), 1)  # Pressure in hPa
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
    
    # New entry to be appended to the deque
    new_data_entry = {"temp": temp, "humidity": humidity, "pressure": pressure, "timestamp": timestamp}
    
    # Append the new entry to the deque
    reactive_value_wrapper.get().append(new_data_entry)

    # Snapshot of the current deque
    deque_snapshot = reactive_value_wrapper.get()
    
    # Convert deque to a DataFrame for easier processing
    df = pd.DataFrame(deque_snapshot)
    
    # Return all the data we need for display
    latest_data_entry = new_data_entry
    return deque_snapshot, df, latest_data_entry

# --------------------------------------------
# Define the Shiny UI Page layout
# --------------------------------------------

# Page options like title and filling
ui.page_opts(title="Continuous Intelligence: Live Data Example", fillable=True)

# Sidebar with links and additional information
with ui.sidebar(open="open"):
    ui.h2("Environmental Monitoring", class_="text-center")
    ui.p("A demonstration of real-time environmental data.", class_="text-center")
    ui.hr()
    ui.h6("Links:")
    ui.a("GitHub Source", href="https://github.com/denisecase/cintel-05-cintel", target="_blank")
    ui.a("GitHub App", href="https://denisecase.github.io/cintel-05-cintel/", target="_blank")
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a("PyShiny Express", href="https://shiny.posit.co/blog/posts/shiny-express/", target="_blank")

# Main content section
with ui.layout_columns():
    # Current Temperature Box
    with ui.value_box(
        showcase=icon_svg("sun"), 
        theme="bg-gradient-blue-purple",
    ):
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_data_entry = reactive_calc_combined()
            return f"{latest_data_entry['temp']} °C"

        "warmer than usual"

    # Card for Current Date and Time
    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")
        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_data_entry = reactive_calc_combined()
            return f"{latest_data_entry['timestamp']}"

    # Card for Most Recent Data Readings (DataGrid)
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_data_entry = reactive_calc_combined()
            pd.set_option('display.width', None)  # Use maximum width for display
            return render.DataGrid(df, width="100%")

    # Card for Plotly Chart with Linear Regression Trend
    with ui.card():
        ui.card_header("Chart with Current Trend")
        @render_plotly
        def display_plot():
            """Create and return a Plotly chart with a trend line"""
            deque_snapshot, df, latest_data_entry = reactive_calc_combined()

            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Create a scatter plot for temperature readings over time
                fig = px.scatter(df,
                                 x="timestamp",
                                 y="temp",
                                 title="Temperature Readings with Regression Line",
                                 labels={"temp": "Temperature (°C)", "timestamp": "Time"},
                                 color_discrete_sequence=["blue"])

                # Perform linear regression to create a trend line
                sequence = range(len(df))  # Independent variable (x-values)
                x_vals = list(sequence)
                y_vals = df["temp"]  # Dependent variable (y-values)

                # Using scipy to calculate the regression line (slope, intercept)
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]

                # Add the regression line to the plot
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Trend Line')

                # Customize plot layout
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Temperature (°C)",
                    template="plotly_dark"  # Use dark theme for plot
                )

            return fig