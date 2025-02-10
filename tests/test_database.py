import pytest
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from src.database import DatabaseConnection, DatabaseError

@pytest.fixture
def test_db():
    """Create a test database with sample data."""
    # Create SQLite in-memory database
    engine = create_engine('sqlite:///:memory:')
    
    # Create test table and insert data within a transaction
    with engine.begin() as conn:  # Using begin() ensures proper transaction handling
        # First create the table
        print("Creating test table...")
        conn.execute(text("""
            CREATE TABLE workout_summary (
                workout_date DATETIME,
                activity_type VARCHAR(50),
                distance_mi FLOAT
            )
        """))
        
        # Then insert the test data
        print("Inserting test data...")
        conn.execute(text("""
            INSERT INTO workout_summary 
            (workout_date, activity_type, distance_mi)
            VALUES 
            ('2024-01-01 10:00:00', 'run', 3.1)
        """))
        
        conn.execute(text("""
            INSERT INTO workout_summary 
            (workout_date, activity_type, distance_mi)
            VALUES 
            ('2024-01-02 11:00:00', 'run', 5.0)
        """))
    
        # Verify the data was inserted
        result = conn.execute(text("SELECT COUNT(*) FROM workout_summary")).scalar()
        print(f"Number of rows in test database: {result}")
    
    return engine


@pytest.fixture
def db_connection(test_db):
    """Create a database connection using the test database."""
    return DatabaseConnection(test_db)


def test_database_connection(db_connection):
    """Test that database connection can be established."""
    assert db_connection.test_connection() is True





def test_database_error_handling():
    """Test that database errors are caught and wrapped properly."""
    print("\nStarting database error handling test")
    
    # Use a malformed connection string that should definitely fail
    bad_connection = "definitely:not:a:valid:connection:string"
    print(f"Testing with invalid connection string: {bad_connection}")
    
    # This should raise our DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        print("Attempting to create DatabaseConnection...")
        connection = DatabaseConnection(bad_connection)
        print("Warning: Connection creation succeeded when it should have failed")
    
    print(f"Test completed with error: {str(exc_info.value) if 'value' in dir(exc_info) else 'No error caught'}")
    
    assert "Failed to initialize database" in str(exc_info.value)






def test_get_workout_data(db_connection):
    """Test retrieving workout data for date range."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 3)
    
    df = db_connection.get_workout_data(start_date, end_date)

    # Print debug information
    print("\nDebug information:")
    print(f"Number of rows returned: {len(df)}")
    print("\nReturned data:")
    print(df)
    print("\nData types of columns:")
    print(df.dtypes)

    # Original assertions
    assert len(df) == 2
    assert 'workout_date' in df.columns
    assert 'distance_mi' in df.columns
    assert df['distance_mi'].sum() == 8.1  # 3.1 + 5.0