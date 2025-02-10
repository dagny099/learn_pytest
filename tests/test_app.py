import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from src.app import initialize_connection, create_histogram, DatabaseConnectionError

@pytest.fixture
def sample_df():
    """Create sample DataFrame for testing."""
    dates = pd.date_range(start='2024-01-01', periods=10)
    return pd.DataFrame({
        'workout_date': dates,
        'distance_mi': np.random.normal(5, 1, 10),
        'duration_sec': np.random.normal(1800, 300, 10),
        'kcal_burned': np.random.normal(300, 50, 10)
    })

@patch('src.app.DatabaseConnection')
def test_initialize_connection_success(mock_db):
    """Test successful database connection initialization."""
    # Set up the mock
    mock_instance = MagicMock()
    mock_instance.test_connection.return_value = True
    mock_db.return_value = mock_instance
    
    # Should return the connection without raising an error
    conn = initialize_connection()
    assert conn is not None

@patch('src.app.DatabaseConnection')
def test_initialize_connection_failure(mock_db):
    """Test database connection failure handling."""
    # Set up the mock to simulate connection failure
    mock_instance = MagicMock()
    mock_instance.test_connection.return_value = False
    mock_db.return_value = mock_instance
    
    # Should raise our custom exception
    with patch('streamlit.error') as mock_error:
        with pytest.raises(DatabaseConnectionError) as exc_info:
            initialize_connection()
        
        # Verify error message was displayed
        assert mock_error.called
        assert "Could not connect to database" in str(exc_info.value)

@patch('src.app.DatabaseConnection')
def test_initialize_connection_exception(mock_db):
    """Test handling of unexpected database exceptions."""
    # Set up the mock to raise an exception
    mock_db.side_effect = Exception("Unexpected database error")
    
    # Should wrap the original exception in our custom exception
    with patch('streamlit.error') as mock_error:
        with pytest.raises(DatabaseConnectionError) as exc_info:
            initialize_connection()
        
        # Verify error was displayed and properly wrapped
        assert mock_error.called
        assert "Unexpected database error" in str(exc_info.value)