from sqlalchemy import create_engine
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

# for debugging:
import sys
print("Python is looking for modules in:", sys.path)


from database import DatabaseConnection
from analytics import WorkoutAnalytics

# Configuration
DB_CONNECTION = "mysql+pymysql://barbs:barbs@localhost:3306/sweat"

st.markdown("""
    <style>
        div[data-testid="column"].st-emotion-cache-keje6w.e1f1d6gn3{
            text-align: center;
            background-color: #eeeeee;
            color: #666666;
            border-bottom: 1px dashed #808080;
        }
        div[data-testid="column"].st-emotion-cache-1r6slb0.e1f1d6gn3{
            text-align: center;
            background-color: #eeeeee;
            color: #666666;
            border-bottom: 1px dashed #808080;
        }
        div[data-testid="column"].st-emotion-cache-12w0qpk.e1f1d6gn3{
            text-align: center;
            background-color: #eeeeee;
            border: 2px solid blue;
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""
    pass

def initialize_connection():
    """Initialize database connection with diagnostic information."""
    error_msg = "Could not connect to database. Please check your connection settings."
    try:
        print("\nConnection Initialization Process:")
        print(f"1. Using connection string: {DB_CONNECTION}")
        
        # Try to create engine directly first to test
        print("2. Attempting to create SQLAlchemy engine...")
        test_engine = create_engine(DB_CONNECTION)
        print(f"3. Engine created: {type(test_engine)}")
        
        print("4. Creating DatabaseConnection instance...")
        conn = DatabaseConnection(DB_CONNECTION)
        print("5. Testing connection...")
        
        if not conn.test_connection():
            print("6. Connection test failed")
            st.error(error_msg)
            raise DatabaseConnectionError(error_msg)
        
        print("6. Connection test succeeded")
        return conn
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        full_error_msg = f"{error_msg} Details: {str(e)}"
        st.error(full_error_msg)
        raise DatabaseConnectionError(full_error_msg)    

def create_histogram(df: pd.DataFrame, metric: str, agg_type: str):
    """Create plotly histogram figure with appropriate styling.
    
    Args:
        df: DataFrame containing the workout data
        metric: Name of the metric being plotted
        agg_type: Type of aggregation being displayed
    """
    bin_edges, hist_values = WorkoutAnalytics.prepare_histogram_data(
        df, metric=metric, bins=15
    )
    
    fig = go.Figure(data=[
        go.Bar(
            x=bin_edges[:-1],
            y=hist_values,
            width=bin_edges[1] - bin_edges[0],
            marker_color='rgb(55, 83, 109)'
        )
    ])
    
    fig.update_layout(
        title=f"Distribution of {metric} ({agg_type})",
        xaxis_title=metric,
        yaxis_title="Frequency",
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig


def analyze_workout_distribution(df: pd.DataFrame, metric_name: str):
    """Create a meaningful workout distribution analysis.
    
    Args:
        df: DataFrame with workout data
        metric_name: Name of the metric to analyze
    """
    # Add day of week to the DataFrame
    df['day_of_week'] = df['workout_date'].dt.day_name()
    
    # Create separate traces for each day
    fig = go.Figure()
    
    # Define weekday order
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    for day in weekdays:
        day_data = df[df['day_of_week'] == day][metric_name]
        if not day_data.empty:
            fig.add_trace(go.Histogram(
                x=day_data,
                name=day,
                nbinsx=10,
                opacity=0.7
            ))
    
    fig.update_layout(
        title=f"Distribution of {metric_name} by Day of Week",
        xaxis_title=metric_name,
        yaxis_title="Frequency",
        barmode='overlay',  # Overlapping histograms
        showlegend=True,
        legend_title="Day of Week"
    )
    
    return fig


def main():
    """Main application function that handles the Streamlit interface."""
    st.title("Workout Analysis Dashboard")
    
    # Initialize database connection
    db = initialize_connection()
    
    # Sidebar controls
    st.sidebar.header("Analysis Controls")
    
    # Date range selection with smart defaults
    default_end_date = datetime.now() - timedelta(days=365*4)
    default_start_date = default_end_date - timedelta(days=365*1)
    
    start_date = st.sidebar.date_input(
        "Start Date",
        value=default_start_date,
        max_value=default_end_date,
        format="MM/DD/YYYY"
    )
    
    end_date = st.sidebar.date_input(
        "End Date",
        value=default_end_date,
        min_value=start_date,
        max_value=default_end_date,
        format="MM/DD/YYYY"
    )
    
    # Metric selection
    metric_options = {
        "Distance (miles)": "distance_mi",
        "Duration (seconds)": "duration_sec",
        "Calories Burned": "kcal_burned",
        "Average Pace": "avg_pace",
        "Max Pace": "max_pace",
        "Steps": "steps"
    }
    selected_metric = st.sidebar.selectbox(
        "Select Metric",
        options=list(metric_options.keys())
    )
    
    # Aggregation controls
    agg_period = st.sidebar.selectbox(
        "Aggregation Period",
        options=["Weekly", "Monthly"],
        format_func=lambda x: x
    )
    
    agg_type = st.sidebar.selectbox(
        "Aggregation Type",
        options=["Total", "Average", "Standard Deviation"],
        format_func=lambda x: x
    )
    
    # Convert selections to parameters
    period_map = {"Weekly": "W", "Monthly": "M"}
    agg_map = {
        "Total": "sum",
        "Average": "mean",
        "Standard Deviation": "std"
    }
    
    metric_name = metric_options[selected_metric]
    
    try:
        # Fetch data
        df = db.get_workout_data(
            start_date=start_date,
            end_date=end_date,
            metric_name=metric_name
        )

        if df.empty:
            st.warning("No data available for the selected date range.")
            st.stop()
        
        # Process data
        agg_df, summary_stats = WorkoutAnalytics.aggregate_by_period(
            df,
            metric=metric_name,
            agg_type=agg_map[agg_type],
            period=period_map[agg_period]
        )
        
        # Display summary statistics
        st.subheader(f"{selected_metric} Summary Statistics ")
        col1, col2, col3, col4 = st.columns(4)
        col5, col6, col7 = st.columns(3)
        
        with col1:
            st.metric("Average", f"{summary_stats['mean']:.2f}")
        with col2:
            st.metric("Median", f"{summary_stats['std']:.2f}")
        with col3:
            st.metric("Standard Deviation", f"{summary_stats['std']:.2f}")
        with col4:
            st.metric("Skew", f"{summary_stats['skew']:.2f}")
        with col5:
            st.metric("Earliest Workout Date", f"{df['workout_date'].min().strftime('%m-%d-%Y')}")
        with col6:
            st.metric("Latest Workout Date", f"{df['workout_date'].max().strftime('%m-%d-%Y')}")
        with col7:
            st.metric("# workouts", f"{summary_stats['count']}")

        # Display histogram
        st.subheader("Distribution")
        fig = create_histogram(df, metric_name, agg_type)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display aggregated data table
        st.subheader("Aggregated Data")
        st.dataframe(
            agg_df.style.format({metric_name: "{:.2f}"}),
            use_container_width=True
        )

        # Display histogram
        st.subheader("Day of Week Distribution")
        fig_dow = analyze_workout_distribution(df, metric_name)
        st.plotly_chart(fig_dow, use_container_width=True)


    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your selections and try again.")

if __name__ == "__main__":
    main()