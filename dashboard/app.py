# --------------------------------------------
# Imports at the top - PyShiny EXPRESS VERSION
# --------------------------------------------

from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from collections import deque
import pandas as pd
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats
from faicons import icon_svg

UPDATE_INTERVAL_SECS: int = 3  # Data update every 3 seconds

DEQUE_SIZE: int = 5  # Max number of entries in deque
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

# --------------------------------------------
# Initialize a REACTIVE CALC to generate fake data
# --------------------------------------------

@reactive.calc()
def generate_reactive_data():
    # Invalidate this calculation every UPDATE_INTERVAL_SECS
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    # Simulate new penguin-related data (population, food availability, chick count)
    penguin_population = random.randint(50, 1000)  # Penguin population count
    food_availability = round(random.uniform(10, 100), 1)  # Food availability in tons
    chick_count = random.randint(0, 200)  # Number of chicks
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current timestamp
    
    # New entry to be appended to the deque
    new_data_entry = {
        "penguin_population": penguin_population,
        "food_availability": food_availability,
        "chick_count": chick_count,
        "timestamp": timestamp
    }
    
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
# Define the Shiny UI Page layout with Tabbed Navigation
# --------------------------------------------

ui.page_opts(title="Penguin Monitoring Dashboard", fillable=True)

# Sidebar with links and additional information
with ui.sidebar(open="open"):
    ui.h2("Penguin Population Monitoring", class_="text-center")
    ui.p("Real-time data on penguin populations, food availability, and chick counts.", class_="text-center")
    ui.hr()
    ui.h6("Links:")
    ui.a("GitHub Source", href="https://github.com/denisecase/cintel-05-cintel", target="_blank")
    ui.a("GitHub App", href="https://denisecase.github.io/cintel-05-cintel/", target="_blank")
    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")
    ui.a("PyShiny Express", href="https://shiny.posit.co/blog/posts/shiny-express/", target="_blank")

# Main content with tab navigation
with ui.navset_card_tab(id="tab"):
    # First Tab: Current Data Display
    with ui.nav_panel("Live Data"):
        # Current Penguin Population Box
        with ui.value_box(
            showcase=icon_svg("users"),  # Replaced "user-friends" with "users"
            theme="bg-gradient-blue-green",
        ):
            "Current Penguin Population"
            @render.text
            def display_population():
                """Get the latest penguin population"""
                deque_snapshot, df, latest_data_entry = generate_reactive_data()
                return f"{latest_data_entry['penguin_population']} Penguins"

        # Current Chick Count Box
        with ui.value_box(
            showcase=icon_svg("baby-carriage"),  # Retained "baby-carriage" icon
            theme="bg-gradient-green-yellow",
        ):
            "Current Chick Count"
            @render.text
            def display_chicks():
                """Get the latest chick count"""
                deque_snapshot, df, latest_data_entry = generate_reactive_data()
                return f"{latest_data_entry['chick_count']} Chicks"

        # Current Food Availability Box
        with ui.value_box(
            showcase=icon_svg("fish"),  # Retained "fish" icon for food availability
            theme="bg-gradient-orange-yellow",
        ):
            "Food Availability"
            @render.text
            def display_food():
                """Get the latest food availability"""
                deque_snapshot, df, latest_data_entry = generate_reactive_data()
                return f"{latest_data_entry['food_availability']} Tons"

        # Card for Most Recent Data Readings (DataGrid)
        with ui.card(full_screen=True):
            ui.card_header("Most Recent Data")
            @render.data_frame
            def show_data_frame():
                """Display the current penguin population data as a table"""
                deque_snapshot, df, latest_entry = generate_reactive_data()
                pd.set_option('display.width', None)
                return render.DataGrid(df, width="100%", height=400)

    # Second Tab: Penguin Population Trend
    with ui.nav_panel("Penguin Population Trend"):
        @render_plotly
        def plot_population_trend():
            """Create and return a Plotly chart with a trend line for penguin population"""
            deque_snapshot, df, latest_entry = generate_reactive_data()

            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Create a scatter plot for penguin population over time
                fig = px.scatter(df,
                                 x="timestamp",
                                 y="penguin_population",
                                 title="Penguin Population Trend",
                                 labels={"penguin_population": "Penguin Population", "timestamp": "Time"},
                                 color_discrete_sequence=["forestgreen"])

                # Perform linear regression to create a trend line
                sequence = range(len(df))  # Independent variable (x-values)
                x_vals = list(sequence)
                y_vals = df["penguin_population"]  # Dependent variable (y-values)

                # Using scipy to calculate the regression line (slope, intercept)
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]

                # Add the regression line to the plot
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Trend Line', line=dict(dash='dash', width=3, color='yellow'))

                # Customize plot layout
                fig.update_layout(
                    xaxis_title="Time",
                    yaxis_title="Penguin Population",
                    template="plotly_dark",  # Use dark theme for plot
                    showlegend=True,  # Always show legend
                    xaxis=dict(showline=True, linewidth=1, linecolor='gray', ticks="outside"),
                    yaxis=dict(showline=True, linewidth=1, linecolor='gray', ticks="outside"),
                    plot_bgcolor="#2c2c2c",  # Dark background for the plot area
                    paper_bgcolor="#2c2c2c"  # Dark background for the paper area
                )

                # Prevent flickering by setting smooth transitions
                fig.update_traces(marker=dict(size=8, opacity=0.8), line=dict(width=2))

            return fig
