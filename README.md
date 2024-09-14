# RangeFilter: Advanced Price Movement Analysis Tool

## Abstract

This document presents the `RangeFilter` class, a sophisticated tool designed for smoothing minor price movements in financial time series data. The `RangeFilter` implements a customizable algorithm that provides a clearer view of underlying trends in market data. This implementation is particularly useful for traders and quantitative analysts seeking to filter out noise and identify significant price movements.

## 1. Introduction

The `RangeFilter` class is implemented in Python, utilizing the pandas, numpy, and matplotlib libraries. It is designed to process financial time series data, typically consisting of open, high, low, and close prices for a given asset.

## 2. Methodology

### 2.1 Initialization

The `RangeFilter` is initialized with several parameters that allow for customization of the filtering process:

- `data`: pandas DataFrame containing price data
- `f_type`: Type of filter calculation ('Type 1' or 'Type 2')
- `mov_src`: Source for movement detection ('Close' or 'Wicks')
- `rng_qty`: Quantity for range size calculation
- `rng_scale`: Scale method for range size
- `rng_per`: Period for range calculations
- `smooth_range`: Boolean to decide if the range should be smoothed
- `smooth_per`: Period for smoothing the range
- `av_vals`: Boolean to decide if filter values should be averaged over filter changes
- `av_samples`: Number of filter changes to average when `av_vals` is True

### 2.2 Core Algorithms

#### 2.2.1 Conditional Exponential Moving Average (EMA)

The Conditional EMA is calculated as follows:

$$ EMA_t = \begin{cases} 
x_t & \text{if } t = 1 \text{ or } \text{prev}_{\text{EMA}} \text{ is NaN} \\
(x_t - \text{prev}_{\text{EMA}}) \cdot k + \text{prev}_{\text{EMA}} & \text{if condition is True} \\
\text{prev}_{\text{EMA}} & \text{otherwise}
\end{cases} $$

where $k = \frac{2}{n+1}$, $n$ is the EMA period, and $x_t$ is the current data point.

#### 2.2.2 Range Size Calculation

The range size is calculated based on the selected scale method. For example, when using the Average True Range (ATR) scale:

$$ \text{Range Size} = q \cdot \text{ATR}_n $$

where $q$ is the range quantity and $\text{ATR}_n$ is the n-period ATR.

#### 2.2.3 Range Filter Calculation

The Range Filter value is calculated using one of two methods:

Type 1:
$$ \text{RFilter}_t = \begin{cases}
h_t - r & \text{if } h_t - r > \text{RFilter}_{t-1} \\
l_t + r & \text{if } l_t + r < \text{RFilter}_{t-1} \\
\text{RFilter}_{t-1} & \text{otherwise}
\end{cases} $$

Type 2:
$$
\text{RFilter}_t = \begin{cases}
\text{RFilter}_{t-1} + \lfloor\frac{|h_t - \text{RFilter}_{t-1}|}{r}\rfloor \cdot r & \text{if } h_t \geq \text{RFilter}_{t-1} + r \\
\text{RFilter}_{t-1} - \lfloor\frac{|l_t - \text{RFilter}_{t-1}|}{r}\rfloor \cdot r & \text{if } l_t \leq \text{RFilter}_{t-1} - r \\
\text{RFilter}_{t-1} & \text{otherwise}
\end{cases}
$$

where $h_t$ is the high price, $l_t$ is the low price, and $r$ is the range size.

## 3. Implementation

The `RangeFilter` class implements the following key methods:

1. `__init__`: Initializes the RangeFilter with user-defined parameters.
2. `Cond_EMA`: Calculates the Conditional Exponential Moving Average.
3. `Cond_SMA`: Calculates the Conditional Simple Moving Average.
4. `Stdev`: Calculates the Standard Deviation.
5. `rng_size`: Calculates the range size based on the selected scale.
6. `rng_filt`: Calculates the Range Filter values.
7. `run`: Executes the Range Filter calculations on the provided data.

## 4. Usage

To use the `RangeFilter`:

1. Initialize the `RangeFilter` with desired parameters.
2. Call the `run()` method to perform calculations.
3. Access the filtered data and additional indicators through the `data` attribute or `get_data()` method.

## 5. Conclusion

The `RangeFilter` class provides a flexible and powerful tool for analyzing price movements in financial time series data. By effectively filtering out minor fluctuations, it allows for clearer identification of significant trends, potentially improving trading and investment decision-making processes.

## References

1. Wilder, J. W. (1978). New Concepts in Technical Trading Systems. Trend Research.
2. Murphy, J. J. (1999). Technical Analysis of the Financial Markets. New York Institute of Finance.
