from sqlalchemy import create_engine, Engine, text
import pandas as pd
from datetime import datetime
from typing import Union

class DatabaseError(Exception):
    """A simple wrapper for database-related errors."""
    pass


class DatabaseConnection:
    """Handles database connections and queries for workout data."""
    
    def __init__(self, connection: Union[str, Engine]):
        """Initialize database connection.
        
        Args:
            connection: Either a SQLAlchemy connection string or engine
        """
        try:
            print(f"Attempting to initialize with connection: {connection}")
            if isinstance(connection, Engine):
                print("Connection is an Engine instance")
                self.engine = connection
            else:
                print("Connection is a string, creating engine")
                self.engine = create_engine(connection)
        
            # Determine if we're using SQLite (for testing) or MySQL
            self.is_sqlite = 'sqlite' in str(self.engine.url)
            print(f"Database type: {'SQLite' if self.is_sqlite else 'MySQL'}")

        except Exception as e:
            
            raise DatabaseError(f"Failed to initialize database : {str(e)}")
    
    def test_connection(self) -> bool:
        """Test if database connection is working.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    def get_workout_data(
        self,
        start_date: datetime,
        end_date: datetime,
        metric_name: str = "distance_mi"
    ) -> pd.DataFrame:
        """Retrieve workout data for specified date range.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            metric_name: Column to retrieve (e.g., 'distance_mi')
            
        Returns:
            DataFrame with workout data
        """
        # Adjust table name based on database type
        table_name = "workout_summary" if self.is_sqlite else "sweat.workout_summary"
        
        # Since we can't parameterize column names in SQL, we'll validate the metric_name
        valid_metrics = {'distance_mi', 'duration_sec', 'kcal_burned', 'avg_pace', 'max_pace','steps'}
        if metric_name not in valid_metrics:
            raise ValueError(f"Invalid metric name. Must be one of: {valid_metrics}")
        
        query = text(f"""
            SELECT 
                workout_date,
                activity_type,
                {metric_name} as metric
            FROM {table_name}
            WHERE workout_date BETWEEN :start_date AND :end_date
        """)
        
        with self.engine.connect() as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }  # We removed metric_name from params since it's now part of the query
            )
        
        # Ensure workout_date is datetime
        df['workout_date'] = pd.to_datetime(df['workout_date'])
        
        # Rename the 'metric' column back to its original name
        df = df.rename(columns={'metric': metric_name})
        
        return df
