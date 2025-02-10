# Testing Cheatsheet for Data Science Applications

## Quick Reference

### Basic Test Structure
```python
def test_function_name():
    # Arrange
    expected_result = ...
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_result
```

### Common pytest Decorators
```python
@pytest.fixture  # Create reusable test data
@pytest.mark.parametrize  # Run same test with different inputs
@pytest.mark.skip  # Skip this test
@pytest.mark.xfail  # Expect this test to fail
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_database.py

# Run with coverage report
pytest --cov=src tests/

# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
```

## Testing Patterns for Data Science

### 1. Testing Data Transformations

Testing data transformations requires checking both the transformation logic and the handling of edge cases. Here's a comprehensive example:

```python
import pandas as pd
import pytest

def test_data_transformation():
    # Input data
    input_df = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': ['x', 'y', 'z', None]
    })
    
    # Expected output
    expected_df = pd.DataFrame({
        'A': [1, 2, 0, 4],  # None replaced with 0
        'B': ['x', 'y', 'z', 'missing']  # None replaced with 'missing'
    })
    
    # Perform transformation
    result_df = clean_dataframe(input_df)
    
    # Compare DataFrames
    pd.testing.assert_frame_equal(result_df, expected_df)
```

### 2. Testing Statistical Functions

When testing statistical computations, consider numerical precision and edge cases:

```python
def test_statistical_calculation():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Test mean calculation
    assert abs(calculate_mean(data) - 3.0) < 1e-10
    
    # Test with empty input
    assert calculate_mean([]) is None
    
    # Test with single value
    assert calculate_mean([1.0]) == 1.0
```

### 3. Testing Database Operations

Mock database connections to avoid depending on actual databases during testing:

```python
@pytest.fixture
def mock_db():
    """Create in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

def test_database_query(mock_db):
    # Insert test data
    with mock_db.connect() as conn:
        conn.execute(text("INSERT INTO table_name VALUES (1, 'test')"))
    
    # Test query
    result = run_query(mock_db)
    assert len(result) == 1
```

### 4. Testing Data Quality

Validate data quality checks and cleaning operations:

```python
def test_data_quality_checks():
    df = pd.DataFrame({
        'age': [-5, 25, 150, 30],
        'name': ['John', '', 'Jane', 'Bob']
    })
    
    quality_issues = check_data_quality(df)
    
    assert 'age_out_of_range' in quality_issues
    assert 'empty_name' in quality_issues
```

### 5. Testing Visualizations

Test visualization logic without actually rendering plots:

```python
def test_visualization_data():
    data = prepare_visualization_data(raw_data)
    
    assert 'x' in data
    assert 'y' in data
    assert len(data['x']) == len(data['y'])
    assert all(isinstance(x, (int, float)) for x in data['x'])
```

## Deep Dive: Key Testing Concepts

### Understanding Test Discovery

pytest follows specific patterns to find and execute tests. It looks for:
- Files named test_*.py or *_test.py
- Functions named test_*
- Classes named Test* with methods named test_*

This naming convention helps organize tests and ensures they're automatically discovered. For example, if you have a function called calculate_mean(), your test file might be named test_statistics.py and contain a function called test_calculate_mean().

### Fixture Scoping

Fixtures in pytest can have different scopes that determine how often they're created:

```python
@pytest.fixture(scope="function")  # Default: Created for each test
@pytest.fixture(scope="class")     # Created once per test class
@pytest.fixture(scope="module")    # Created once per module
@pytest.fixture(scope="session")   # Created once per test session
```

Choose fixture scopes based on:
- Setup cost (database connections might use session scope)
- Test isolation needs (test data might use function scope)
- Resource constraints (heavy computations might use module scope)

### Mocking Strategy

Mocking replaces real objects with test doubles. Consider these principles:
1. Mock at the right level (usually at system boundaries)
2. Mock only what's necessary
3. Keep mocks simple and focused

Example of strategic mocking:
```python
# Instead of mocking everything:
@patch('pandas.read_csv')
@patch('pandas.DataFrame')
@patch('numpy.mean')

# Mock only the external dependency:
@patch('requests.get')
def test_data_fetch(mock_get):
    mock_get.return_value.json.return_value = {'data': [1, 2, 3]}
    result = fetch_and_process_data()
    assert result.mean() == 2
```

### Test Parameterization

Parameterization allows testing multiple scenarios efficiently:

```python
@pytest.mark.parametrize("input_data,expected", [
    ([1, 2, 3], 2),
    ([0], 0),
    ([-1, 1], 0),
    ([1.5, 2.5], 2.0)
])
def test_calculate_mean(input_data, expected):
    assert calculate_mean(input_data) == expected
```

This approach:
- Reduces code duplication
- Makes test cases explicit
- Improves test maintenance
- Helps identify edge cases

### Coverage Analysis

Coverage reports help identify untested code, but remember:
- 100% coverage doesn't guarantee perfect testing
- Focus on critical paths and edge cases
- Consider the cost/benefit of testing each component
- Use coverage as a guide, not a goal

### Error Handling Testing

Test both expected and unexpected error conditions:

```python
def test_error_handling():
    # Test expected errors
    with pytest.raises(ValueError) as exc_info:
        process_data(invalid_input)
    assert "Invalid input" in str(exc_info.value)
    
    # Test unexpected errors
    with pytest.raises(Exception) as exc_info:
        process_data(None)
    assert "Unexpected error" in str(exc_info.value)
```

Remember to test:
- Input validation
- Resource availability
- System state changes
- Error recovery mechanisms

This cheatsheet serves as both a quick reference and a learning tool. As you develop your testing skills, you'll find yourself naturally incorporating these patterns and principles into your workflow. Testing becomes more intuitive with practice, and these concepts will help guide your testing strategy in data science applications.