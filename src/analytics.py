from typing import Tuple, Dict
import pandas as pd
import numpy as np

class WorkoutAnalytics:
    """Handles analysis of workout data."""
    
    @staticmethod
    def aggregate_by_period(
        df: pd.DataFrame,
        metric: str = "distance_mi",
        agg_type: str = "sum",
        period: str = "W"
    ) -> Tuple[pd.DataFrame, Dict]:
        """Aggregate workout data by specified period.
        
        Args:
            df: DataFrame with workout data
            metric: Column to aggregate
            agg_type: Type of aggregation ('sum', 'mean', 'std')
            period: Period for aggregation ('W' for week, 'M' for month)
            
        Returns:
            Tuple of (aggregated DataFrame, summary statistics)
        """
        # Ensure workout_date is datetime
        df['workout_date'] = pd.to_datetime(df['workout_date'])
        
        # Create period grouping
        df['period'] = df['workout_date'].dt.to_period(period)
        
        # Perform aggregation
        agg_map = {
            'sum': 'sum',
            'mean': 'mean',
            'std': 'std',
            'min': 'min',
            'max': 'max',
            'count': 'count',
            'skew': 'skew',
            'median': 'median',
            'kurt': 'kurt'
        }
        
        agg_df = df.groupby('period')[metric].agg(agg_map[agg_type]).reset_index()
        
        # Calculate summary statistics
        summary_stats = {
            'total': df[metric].sum(),
            'mean': df[metric].mean(),
            'std': df[metric].std(),
            'min': df[metric].min(),
            'max': df[metric].max(),
            'count': len(df),
            'skew': df[metric].skew(),
            'median': df[metric].median(),
            'kurt': df[metric].kurt()
        }
        
        return agg_df, summary_stats
    
    @staticmethod
    def prepare_histogram_data(
        df: pd.DataFrame,
        metric: str = "distance_mi",
        bins: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare histogram data for plotting.
        
        Args:
            df: DataFrame with workout data
            metric: Column to analyze
            bins: Number of histogram bins
            
        Returns:
            Tuple of (bin edges, histogram values)
        """
        hist_values, bin_edges = np.histogram(df[metric], bins=bins)
        return bin_edges, hist_values
    
    