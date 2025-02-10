import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.analytics import WorkoutAnalytics

@pytest.fixture
def sample_workout_data():
    """Create sample workout data for testing."""
    dates = pd.date_range(start='2024-01-01', periods=14, freq='D')
    
    return pd.DataFrame({
        'workout_date': dates,
        'distance_mi': [3.1, 5.0, 4.2, 3.8, 6.2, 3.5, 7.0,  # Week 1
                       4.1, 5.5, 3.9, 4.8, 6.0, 3.7, 5.2],  # Week 2
        'duration_sec': np.random.randint(1800, 3600, size=14)
    })

def test_aggregate_by_period_weekly_sum(sample_workout_data):
    """Test weekly sum aggregation."""
    agg_df, stats = WorkoutAnalytics.aggregate_by_period(
        sample_workout_data,
        metric="distance_mi",
        agg_type="sum",
        period="W"
    )
    
    assert len(agg_df) == 2  # Two weeks of data
    assert abs(agg_df[['distance_mi']].sum().values[0] - 
              sample_workout_data['distance_mi'].sum()) < 0.01
    assert 'total' in stats
    assert 'mean' in stats
    assert 'std' in stats

def test_aggregate_by_period_weekly_mean(sample_workout_data):
    """Test weekly mean aggregation."""
    agg_df, stats = WorkoutAnalytics.aggregate_by_period(
        sample_workout_data,
        metric="distance_mi",
        agg_type="mean",
        period="W"
    )
    
    assert len(agg_df) == 2
    assert abs(stats['mean'] - sample_workout_data['distance_mi'].mean()) < 0.01

def test_prepare_histogram_data(sample_workout_data):
    """Test histogram data preparation."""
    bin_edges, hist_values = WorkoutAnalytics.prepare_histogram_data(
        sample_workout_data,
        metric="distance_mi",
        bins=5
    )
    
    assert len(bin_edges) == 6  # n_bins + 1
    assert len(hist_values) == 5  # n_bins
    assert sum(hist_values) == len(sample_workout_data)  # All data points included

def test_empty_dataframe():
    """Test handling of empty DataFrame."""
    empty_df = pd.DataFrame(columns=['workout_date', 'distance_mi'])
    
    agg_df, stats = WorkoutAnalytics.aggregate_by_period(empty_df)
    assert len(agg_df) == 0
    assert stats['count'] == 0
    assert stats['total'] == 0

def test_different_aggregation_periods(sample_workout_data):
    """Test different aggregation periods."""
    weekly_df, _ = WorkoutAnalytics.aggregate_by_period(
        sample_workout_data, period="W")
    monthly_df, _ = WorkoutAnalytics.aggregate_by_period(
        sample_workout_data, period="M")
    
    assert len(weekly_df) > len(monthly_df)  # More weeks than months