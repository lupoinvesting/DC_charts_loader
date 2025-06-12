# Tests

This directory contains comprehensive unit tests for the DC Charts Loader application.

## Test Structure

- `test_config.py` - Tests for configuration loading and validation
- `test_data.py` - Tests for data loading and processing functions
- `test_models.py` - Tests for chart data models and navigation
- `test_ui.py` - Tests for UI functions and chart plotting

## Running Tests

To run all tests:
```bash
pytest tests/
```

To run tests with coverage:
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

To run a specific test file:
```bash
pytest tests/test_data.py
```

To run a specific test:
```bash
pytest tests/test_data.py::TestLoadDailyData::test_load_daily_data_basic
```

## Test Coverage

The test suite achieves 100% code coverage across all source modules:

- `src/config.py` - Configuration management
- `src/data.py` - Data loading and processing
- `src/models.py` - Chart data models
- `src/schemas.py` - Data validation schemas
- `src/ui.py` - User interface functions

## Test Features

- **Comprehensive unit tests** for all core functionality
- **Mock-based testing** for external dependencies
- **Edge case testing** for robust error handling
- **Data validation testing** using sample datasets
- **Configuration testing** with various scenarios
- **UI component testing** with proper mocking

## Dependencies

The tests require:
- `pytest>=8.0.0`
- `pytest-cov>=6.0.0`

These are included in the project's `requirements.txt` file.