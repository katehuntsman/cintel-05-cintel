# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

# From shiny, import just reactive and render
from shiny import reactive, render

# From shiny.express, import just ui
from shiny.express import ui

# Imports from Python Standard Library to simulate live data
import random
from datetime import datetime

# --------------------------------------------
# Import icons as you like
# --------------------------------------------

from faicons import icon_svg

# --------------------------------------------
# SET UP THE REACTIVE CONTENT
# --------------------------------------------

# --------------------------------------------
# PLANNING: We want to simulate a fake stock price
# and timestamp every N seconds. 
# For now, we'll avoid storage and just 
# simulate real-time stock data.
# ---------------------------------------------------------

# --------------------------------------------
# First, set a constant UPDATE INTERVAL for all live data
# Constants are usually defined in uppercase letters
# Use a type hint to make it clear that it's an integer (: int)
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 1

# --------------------------------------------
# Initialize a REACTIVE CALC that our display components can call
# to get the latest data and display it.
# The calculation is invalidated every UPDATE_INTERVAL_SECS
# to trigger updates.
# It returns everything needed to display the data.
# Very easy to expand or modify.
# (I originally looked at REACTIVE POLL, but this seems to work better.)
# --------------------------------------------

@reactive.calc()
def reactive_calc_stock():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS to trigger updates
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Simulate stock price generation (e.g., between 100 and 150 USD)
    stock_price = round(random.uniform(100, 150), 2)

    # Get a timestamp for "now" and format it
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a dictionary with the stock data and timestamp
    stock_data_entry = {"price": stock_price, "timestamp": timestamp}

    # Return the latest data as a dictionary
    return stock_data_entry

# ------------------------------------------------
# Define the Shiny UI Page layout - Page Options
# ------------------------------------------------

# Call the ui.page_opts() function
# Set title to a string in quotes that will appear at the top
# Set fillable to True to use the whole page width for the UI

ui.page_opts(title="Live Stock Price Updates", fillable=True)

# ------------------------------------------------
# Define the Shiny UI Page layout - Sidebar
# ------------------------------------------------

# Sidebar is typically used for user interaction/information
# Note the with statement to create the sidebar followed by a colon
# Everything in the sidebar is indented consistently

with ui.sidebar(open="open"):

    ui.h2("Stock Price Monitor", class_="text-center")

    ui.p(
        "A demonstration of live stock price updates.",
        class_="text-center",
    )

    ui.hr()

    ui.h6("Links:")

    ui.a(
        "GitHub Source",
        href="https://github.com/example/stock-price-monitor",
        target="_blank",
    )

    ui.a(
        "Live Demo",
        href="https://example.github.io/stock-price-monitor/",
        target="_blank",
    )

    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")


#---------------------------------------------------------------------
# In Shiny Express, everything not in the sidebar is in the main panel
#---------------------------------------------------------------------
    
ui.h2("Current Stock Price")

@render.text
def display_price():
    """Get the latest stock price and return it as a string"""
    stock_data_entry = reactive_calc_stock()
    return f"${stock_data_entry['price']} USD"

ui.p("stock price is fluctuating")
icon_svg("chart-line")


ui.hr()

ui.h2("Current Date and Time")

@render.text
def display_time():
    """Get the latest timestamp and return it as a string"""
    stock_data_entry = reactive_calc_stock()
    return f"{stock_data_entry['timestamp']}"

with ui.layout_columns():
    with ui.card():
        ui.card_header("Real-Time Stock Price")

with ui.layout_columns():
    with ui.card():
        ui.card_header("Stock Price Chart (placeholder only)")
