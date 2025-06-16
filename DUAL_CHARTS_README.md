# Dual Chart Grid Functionality

This document describes the new dual chart grid functionality that allows displaying two charts side by side with advanced interaction features.

## Features

### 🔄 Side-by-Side Layout
- Two charts displayed horizontally with 50% width each
- Synchronized navigation between charts
- Independent data sources or shared data source

### 🔍 Maximize/Minimize Functionality
- Click the maximize button (⬜) on any chart to expand it to full width
- Click the minimize button (×) to restore the side-by-side view
- Each chart has its own maximize/minimize control

### ⏱️ Timeframe Switching
- Dropdown selector for each chart with timeframes: 1D, 4H, 1H, 15M, 5M, 1M
- Independent timeframe selection for each chart
- Real-time chart updates when timeframe changes

### ⌨️ Keyboard Controls
- **Shift+1**: Navigate to next chart (both charts advance together)
- **Shift+2**: Navigate to previous chart (both charts go back together)
- **Shift+S**: Save screenshots of both charts simultaneously

### 📸 Screenshot Functionality
- Saves separate screenshots for each chart
- Automatic filename generation with ticker, date, and chart identifier
- Screenshots saved to `screenshots/` folder

## Usage

### Basic Usage

```python
from src.models import ChartsDailyData
from src.ui import create_dual_chart_grid
from src.config import config

# Load data
path = config.general.data_path
filename = config.general.data_filename
dict_filename = f"{path}/{filename}"
data_filename = dict_filename.replace(".feather", "_data.feather")

# Create chart data
chart_data = ChartsDailyData(dict_filename, data_filename)

# Create dual chart grid (same data for both charts)
dual_chart = create_dual_chart_grid(chart_data)

# Show the charts
dual_chart.show(block=True)
```

### Advanced Usage with Different Data Sources

```python
# Create separate data sources for each chart
chart_data1 = ChartsDailyData(dict_filename1, data_filename1)
chart_data2 = ChartsDailyData(dict_filename2, data_filename2)

# Create dual chart grid with different data sources
dual_chart = create_dual_chart_grid(chart_data1, chart_data2)

dual_chart.show(block=True)
```

### Integration with Existing Code

Update your `main.py` to use dual charts:

```python
from src.models import ChartsDailyData
from src.ui import create_and_bind_chart, create_dual_chart_grid
from src.config import config

if __name__ == "__main__":
    # ... load data ...
    chart_data = ChartsDailyData(dict_filename, data_filename)
    
    # Choose between single chart or dual chart grid
    use_dual_chart = True  # Set to False for single chart
    
    if use_dual_chart:
        chart = create_dual_chart_grid(chart_data)
    else:
        chart = create_and_bind_chart(chart_data)

    chart.show(block=True)
```

## Demo Scripts

### Run the Demo
```bash
python demo_dual_charts.py
```

### Run Tests
```bash
python test_dual_charts.py
```

## API Reference

### `create_dual_chart_grid(chart_data1, chart_data2=None)`

Creates a grid of 2 charts side by side with advanced functionality.

**Parameters:**
- `chart_data1` (ChartsData): Data for the left chart
- `chart_data2` (ChartsData, optional): Data for the right chart. If None, uses same data as chart_data1

**Returns:**
- `Chart`: The main chart object with dual chart setup

**Features:**
- Side-by-side layout (50% width each)
- Maximize/minimize buttons for each chart
- Timeframe switching (1D, 4H, 1H, 15M, 5M, 1M)
- Navigation hotkeys (Shift+1/2 for next/previous)
- Screenshot functionality (Shift+S)

### Helper Functions

#### `on_maximize(target_chart, charts)`
Handles maximize/minimize functionality for charts.

#### `on_timeframe_change(chart, chart_data, timeframe)`
Handles timeframe switching for a chart.

#### `on_up_dual(chart1, chart2, chart_data1, chart_data2)`
Navigate to next chart for dual chart setup.

#### `on_down_dual(chart1, chart2, chart_data1, chart_data2)`
Navigate to previous chart for dual chart setup.

#### `save_screenshot_dual(chart1, chart2, chart_data1, chart_data2, folder="screenshots")`
Save screenshots for both charts.

## UI Controls

### Top Bar Elements (for each chart)
- **Chart Number**: Displays "Chart 1" or "Chart 2"
- **Timeframe Selector**: Dropdown with available timeframes
- **Maximize Button**: ⬜ to maximize, × to minimize
- **Separator**: Visual separator between controls

### Keyboard Shortcuts
| Key Combination | Action |
|-----------------|--------|
| Shift + 1 | Navigate to next chart (both charts) |
| Shift + 2 | Navigate to previous chart (both charts) |
| Shift + S | Save screenshots of both charts |

## File Structure

```
src/
├── ui.py                    # Contains dual chart functionality
├── models.py               # Chart and data models
├── config.py               # Configuration management
└── data.py                 # Data loading utilities

demo_dual_charts.py         # Demo script
test_dual_charts.py         # Test script
DUAL_CHARTS_README.md       # This documentation
```

## Technical Implementation

### Chart Creation
- Uses `lightweight_charts` library with subchart functionality
- Main chart created with 50% width, subchart positioned to the right
- Both charts inherit from custom `ChartsWMOverride` class for enhanced watermark support

### Event Handling
- Lambda functions capture chart and data references for callbacks
- Hotkeys bound to main chart for global navigation
- Individual chart controls for maximize/timeframe functionality

### Data Management
- Supports independent data sources for each chart
- Fallback to shared data source if only one provided
- Metadata tracking for screenshots and chart identification

### Error Handling
- Graceful fallback for watermark functionality between custom and standard charts
- Exception handling for screenshot operations
- Robust timeframe switching with validation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

2. **Watermark Errors**: The code handles differences between custom and standard chart classes automatically

3. **Screenshot Folder**: The `screenshots/` folder is created automatically if it doesn't exist

4. **Data Loading**: Ensure your data files exist and are in the correct format

### Debug Mode

To enable debug output, modify the functions to include print statements:

```python
def on_timeframe_change(chart, chart_data, timeframe):
    print(f"Switching to timeframe: {timeframe}")
    # ... rest of function
```

## Future Enhancements

Potential improvements for future versions:

1. **More Layout Options**: 2x2 grid, vertical stacking, custom positioning
2. **Synchronized Timeframes**: Option to sync timeframe changes across charts
3. **Chart Linking**: Crosshair synchronization between charts
4. **Custom Indicators**: Per-chart indicator configuration
5. **Export Options**: PDF export, multiple format support
6. **Theme Support**: Dark/light mode, custom color schemes

## Contributing

When contributing to the dual chart functionality:

1. Maintain backward compatibility with existing single chart functionality
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Follow the existing code style and patterns