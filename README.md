# Trend Indicator

<p align="center">
  <img src="Bitcoin Range Filter.png" style="width:100%">
</p>
<p align="center">
  <i>Range Filter applied to BTC-USD</i>
</p>

The **RangeFilter** is designed to smooth out minor fluctuations in financial time series data, such as stock prices or commodity prices. It provides a clearer view of significant trends by filtering out insignificant price movements, allowing to focus on meaningful shifts in the market, while also being relatively robust to trendless markets.

## Mathematical & Statistical Concepts

### 1. Conditional Moving Averages

#### Conditional Exponential Moving Average (EMA)

An **Exponential Moving Average (EMA)** is a type of moving average that places greater weight on recent data points, making it more responsive to new information. The **Conditional EMA** used in the RangeFilter updates its value only when a specific condition is met. This selective updating allows the filter to react to significant changes while ignoring minor, less relevant fluctuations.

#### Conditional Simple Moving Average (SMA)

A **Simple Moving Average (SMA)** calculates the average of a set of data points over a specified period. The **Conditional SMA** computes this average only when certain conditions are met, focusing the smoothing effect on relevant data and improving the accuracy of trend detection.

### 2. Range Size Calculation

The range size is a crucial element in the RangeFilter, acting as a threshold to determine what constitutes a significant price movement. Several statistical measures are employed to calculate the range size:

#### True Range (TR) and Average True Range (ATR)

- **True Range (TR)**: This measures market volatility by considering the largest of three values:
  - The difference between the current period's high and low prices.
  - The absolute difference between the current high and the previous closing price.
  - The absolute difference between the current low and the previous closing price.

- **Average True Range (ATR)**: The ATR is the moving average of the True Range over a specified number of periods. It provides a smoothed measure of volatility, helping to identify when the market is more likely to experience significant price movements.

#### Average Change (AC)

The **Average Change** represents the average of the absolute differences between consecutive mid-price values over a specified period. The mid-price is typically calculated as the average of the high and low prices for each period. This measure helps in assessing the typical price movement magnitude.

#### Standard Deviation (SD)

The **Standard Deviation** quantifies the amount of variation or dispersion in a set of price values. A higher standard deviation indicates that the prices are spread out over a wider range, reflecting higher volatility. This measure is useful for understanding the extent to which prices deviate from the average price.

### 3. Range Filter Calculation

The RangeFilter uses one of two calculation types to determine whether a price movement is significant based on the range size.

#### Filter Types

- **Type 1**:
  - **Upward Movement**: If the current high price minus the range size is greater than the previous filter value, the filter updates to this new higher value.
  - **Downward Movement**: If the current low price plus the range size is less than the previous filter value, the filter updates to this new lower value.
  - **No Significant Movement**: If neither condition is met, the filter value remains unchanged.

- **Type 2**:
  - **Upward Movement**: If the current high price is greater than or equal to the previous filter value plus the range size, the filter increments by the range size. This process can repeat multiple times if the price movement exceeds multiple range sizes.
  - **Downward Movement**: If the current low price is less than or equal to the previous filter value minus the range size, the filter decrements by the range size, potentially multiple times.
  - **No Significant Movement**: The filter remains unchanged if the price does not move beyond the thresholds defined by the range size.

#### Bands Calculation

The **Upper Band** and **Lower Band** are calculated by adding and subtracting the range size from the filter value, respectively. These bands serve as dynamic thresholds that help in identifying when the price has moved significantly enough to consider a trend change.

### 4. Trend Detection

The filter direction is determined by comparing the current filter value with the previous one:

- **Upward Trend**: If the current filter value is greater than the previous filter value, it indicates an upward trend.
- **Downward Trend**: If the current filter value is less than the previous filter value, it indicates a downward trend.
- **Neutral Trend**: If the filter value remains the same, the trend direction is considered unchanged from the previous period.

Based on the filter direction, **Upward** and **Downward** indicators are set, which can be used for generating trading signals or for coloring data visualizations to highlight trends.

## Implementation Details

### Initialization Parameters

When setting up the RangeFilter, several parameters allow customization to fit different analysis needs:

- **Data**: A pandas DataFrame containing the financial time series data with columns named `'open'`, `'high'`, `'low'`, and `'close'`.

- **Filter Type (`f_type`)**: Specifies the filter calculation method to use. Options are `'Type 1'` or `'Type 2'` as described above.

- **Movement Source (`mov_src`)**: Determines the price data to use for detecting movements:
  - `'Close'`: Uses the closing prices.
  - `'Wicks'`: Uses the high and low prices, capturing the full price range of each period.

- **Range Quantity (`rng_qty`)**: A multiplier applied in the range size calculation, influencing the sensitivity of the filter to price movements.

- **Range Scale (`rng_scale`)**: The statistical method used for calculating the range size:
  - **Points**: A fixed value representing price points.
  - **Pips**: A fixed value in pips, commonly used in forex markets.
  - **Ticks**: A fixed tick size, representing the smallest possible price movement.
  - **Percentage of Price**: A percentage of the current closing price.
  - **ATR**: Uses the Average True Range over a specified period.
  - **Average Change**: Uses the average of absolute price changes over a specified period.
  - **Standard Deviation**: Uses the standard deviation of prices over a specified period.
  - **Absolute**: A fixed absolute value.

- **Range Period (`rng_per`)**: The number of periods to use when calculating statistical measures like ATR, Average Change, and Standard Deviation.

- **Smooth Range (`smooth_range`)**: A boolean indicating whether to apply smoothing to the range size using an EMA, which can help reduce noise from volatility spikes.

- **Smoothing Period (`smooth_per`)**: The period used for smoothing the range size if `smooth_range` is enabled.

- **Average Filter Values (`av_vals`)**: A boolean indicating whether to average filter values over several filter changes, providing an additional level of smoothing.

- **Average Samples (`av_samples`)**: The number of filter changes to include when averaging filter values if `av_vals` is enabled.

### Algorithm Steps

1. **Initialization**: Set initial values for all variables, including moving averages, filter values, and counters.

2. **Iterate Over Data**: For each data point in the time series:
   - **Select Movement Source**: Based on `mov_src`, decide whether to use closing prices or high and low prices for calculations.
   - **Calculate Mid-Price**: Compute the average of the selected high and low prices for the period.
   - **Compute Range Size**:
     - Calculate statistical measures (e.g., TR, ATR, Average Change, Standard Deviation) based on the selected `rng_scale`.
     - Apply smoothing to the range size using an EMA if `smooth_range` is enabled.
   - **Calculate Filter Value**:
     - Use the selected filter type (`Type 1` or `Type 2`) to determine the new filter value.
     - If `av_vals` is enabled, average the filter values over the last `av_samples` changes.
   - **Compute Bands**: Determine the upper and lower bands by adding and subtracting the range size from the filter value.
   - **Trend Detection**: Compare the current and previous filter values to establish the filter direction and set trend indicators.
   - **Color Coding**: Assign colors to the filter line and bars for visualization, based on the trend direction.

3. **Store Results**: Append the calculated values to the DataFrame for analysis or visualization.

## Usage

### 1. Prepare Your Data

Ensure your data is in a pandas DataFrame with the following columns:

- `'open'`
- `'high'`
- `'low'`
- `'close'`

The data should be sorted in chronological order, from oldest to newest.

### 2. Initialize the RangeFilter

```python
from range_filter import RangeFilter

# Create an instance of RangeFilter with your data and desired parameters
rf = RangeFilter(
    data=your_dataframe,
    f_type='Type 1',
    mov_src='Close',
    rng_qty=2.618,
    rng_scale='Average Change',
    rng_per=14,
    smooth_range=True,
    smooth_per=27,
    av_vals=False,
    av_samples=2
)
```

### 3. Run the Filter

```python
# Execute the range filter calculations
rf.run()
```

### 4. Retrieve the Results

```python
# Get the modified DataFrame with the filter results
filtered_data = rf.get_data()
```

The resulting DataFrame will include additional columns such as `'filt'`, `'h_band'`, `'l_band'`, `'fdir'`, `'upward'`, `'downward'`, `'filt_color'`, `'bar_color'`, and `'external_trend_output'`.

### 5. Analyze or Visualize

You can analyze the trends or create visualizations to interpret the results. For example, you might plot the closing prices alongside the filter values and bands to see how the filter smooths out minor fluctuations.

## Visual Interpretation

The RangeFilter helps in visualizing significant trends by smoothing out minor price movements:

- **Upward Trends**: Indicated when the filter value increases, suggesting that price movements have exceeded the range size in an upward direction.
- **Downward Trends**: Indicated when the filter value decreases, suggesting that price movements have exceeded the range size in a downward direction.
- **Bands**: The upper and lower bands act as dynamic thresholds for detecting significant price movements, helping to visualize periods of high volatility.

By focusing on movements that exceed the calculated range size, the filter effectively removes noise from the data, allowing for clearer identification of meaningful trends.

## License and Attribution

This project is a Python translation of the original Pine Script by **Donovan Wall**.

- **Original Author**: Donovan Wall
- **Original License**: Mozilla Public License 2.0
- **License**: This project is licensed under the Mozilla Public License 2.0. You can find the full license text at [https://mozilla.org/MPL/2.0/](https://mozilla.org/MPL/2.0/).
