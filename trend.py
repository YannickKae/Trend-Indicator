import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class RangeFilter:
    """
    This filter is designed to smooth out minor price movements to provide a clearer view of trends.
    It can be customized with various parameters to suit different trading instruments and preferences.
    """

    def __init__(self, data, f_type='Type 1', mov_src='Close', rng_qty=2.618, rng_scale='Average Change',
                 rng_per=14, smooth_range=True, smooth_per=27, av_vals=False, av_samples=2):
        """
        Initialize the RangeFilter with user-defined parameters.

        Parameters:
        - data: pandas DataFrame with columns ['open', 'high', 'low', 'close']
        - f_type: Type of filter calculation ('Type 1' or 'Type 2')
        - mov_src: Source for movement detection ('Close' or 'Wicks')
        - rng_qty: Quantity for range size calculation
        - rng_scale: Scale method for range size ('Points', 'Pips', 'Ticks', '% of Price', 'ATR', 'Average Change', 'Standard Deviation', 'Absolute')
        - rng_per: Period for range calculations (used in ATR, Average Change, and Standard Deviation)
        - smooth_range: Boolean to decide if the range should be smoothed
        - smooth_per: Period for smoothing the range
        - av_vals: Boolean to decide if filter values should be averaged over filter changes
        - av_samples: Number of filter changes to average when av_vals is True
        """
        # Use the original DataFrame to ensure changes are reflected
        self.data = data  # pandas DataFrame with columns ['open', 'high', 'low', 'close']
        self.data.reset_index(drop=True, inplace=True)  # Reset index in-place if needed
        self.f_type = f_type
        self.mov_src = mov_src
        self.rng_qty = rng_qty
        self.rng_scale = rng_scale
        self.rng_per = rng_per
        self.smooth_range = smooth_range
        self.smooth_per = smooth_per
        self.av_vals = av_vals
        self.av_samples = av_samples

        # Initialize variables to store computation results
        self.fdir = None  # Filter direction
        self.upward = None  # Upward trend indicator
        self.downward = None  # Downward trend indicator
        self.filt = None  # Filtered price
        self.h_band = None  # High band values
        self.l_band = None  # Low band values
        self.filt_color = None  # Colors for the filter line
        self.bar_color = None  # Colors for the bars
        self.external_trend_output = None  # External trend signal

    def Cond_EMA(self, x, cond, n, prev_ema):
        """
        Conditional Exponential Moving Average.

        Updates the EMA value only when the condition is True.

        Parameters:
        - x: Current data point
        - cond: Condition to update the EMA
        - n: Period for EMA calculation
        - prev_ema: Previous EMA value

        Returns:
        - Updated EMA value
        """
        k = 2 / (n + 1)
        if cond:
            if np.isnan(prev_ema):
                ema = x
            else:
                ema = (x - prev_ema) * k + prev_ema
        else:
            ema = prev_ema
        return ema

    def Cond_SMA(self, x_list):
        """
        Conditional Simple Moving Average.

        Calculates the average of the values in the list.

        Parameters:
        - x_list: List of data points

        Returns:
        - SMA value
        """
        if len(x_list) == 0:
            return np.nan
        else:
            return np.mean(x_list)

    def Stdev(self, x_list, mean):
        """
        Standard Deviation calculation.

        Parameters:
        - x_list: List of data points
        - mean: Mean of the data points

        Returns:
        - Standard deviation value
        """
        if len(x_list) == 0:
            return np.nan
        else:
            return np.sqrt(np.mean((x_list - mean) ** 2))

    def rng_size(self, x, i, prev_ac, prev_atr, prev_sd, ac_list, sd_list):
        """
        Calculate the range size based on the selected scale.

        Parameters:
        - x: Current price value
        - i: Current index
        - prev_ac: Previous Average Change value
        - prev_atr: Previous ATR value
        - prev_sd: Previous Standard Deviation value
        - ac_list: List to store changes for Average Change calculation
        - sd_list: List to store values for Standard Deviation calculation

        Returns:
        - Calculated range size
        - Updated prev_ac, prev_atr, prev_sd, ac_list, sd_list
        """
        qty = self.rng_qty
        n = self.rng_per
        scale = self.rng_scale

        # Calculate True Range (TR) for ATR
        if i == 0:
            tr = self.data['high'].iloc[i] - self.data['low'].iloc[i]
        else:
            tr = max(
                self.data['high'].iloc[i] - self.data['low'].iloc[i],
                abs(self.data['high'].iloc[i] - self.data['close'].iloc[i - 1]),
                abs(self.data['low'].iloc[i] - self.data['close'].iloc[i - 1])
            )

        # Update ATR using Conditional EMA
        prev_atr = self.Cond_EMA(tr, True, n, prev_atr)

        # Calculate Absolute Change (AC) for Average Change
        if i == 0:
            ac = 0
        else:
            ac = abs(x - ((self.data['high'].iloc[i - 1] + self.data['low'].iloc[i - 1]) / 2))

        # Update AC using Conditional EMA
        prev_ac = self.Cond_EMA(ac, True, n, prev_ac)

        # Update lists for Standard Deviation
        sd_list.append(x)
        if len(sd_list) > n:
            sd_list.pop(0)
        mean_sd = self.Cond_SMA(sd_list)
        prev_sd = self.Stdev(sd_list, mean_sd)

        # Calculate the range size based on the selected scale
        if scale == 'Pips':
            rng_size = qty * 0.0001
        elif scale == 'Points':
            pointvalue = 1  # Adjust as per instrument
            rng_size = qty * pointvalue
        elif scale == '% of Price':
            rng_size = self.data['close'].iloc[i] * qty / 100
        elif scale == 'ATR':
            rng_size = qty * prev_atr if prev_atr is not None else 0
        elif scale == 'Average Change':
            rng_size = qty * prev_ac if prev_ac is not None else 0
        elif scale == 'Standard Deviation':
            rng_size = qty * prev_sd if prev_sd is not None else 0
        elif scale == 'Ticks':
            mintick = 0.01  # Adjust as per instrument
            rng_size = qty * mintick
        else:  # 'Absolute'
            rng_size = qty

        return rng_size, prev_ac, prev_atr, prev_sd, ac_list, sd_list

    def rng_filt(self, h, l, rng_size_value, i, rfilt_prev, prev_rng_smooth, filt_change_count, filt_change_values):
        """
        Calculate the Range Filter values.

        Parameters:
        - h: High value for the current bar
        - l: Low value for the current bar
        - rng_size_value: Calculated range size
        - i: Current index
        - rfilt_prev: Previous filter value
        - prev_rng_smooth: Previous smoothed range value
        - filt_change_count: Counter for filter changes
        - filt_change_values: List to store filter values for averaging

        Returns:
        - hi_band: High band value
        - lo_band: Low band value
        - rng_filt_value: Filtered price value
        - Updated rfilt_prev, prev_rng_smooth, filt_change_count, filt_change_values
        """
        n = self.rng_per
        f_type = self.f_type
        smooth = self.smooth_range
        sn = self.smooth_per
        av_rf = self.av_vals
        av_n = self.av_samples

        # Smooth the range size if required
        prev_rng_smooth = self.Cond_EMA(rng_size_value, True, sn, prev_rng_smooth)
        r = prev_rng_smooth if smooth else rng_size_value

        # Initialize filter values
        if np.isnan(rfilt_prev):
            rfilt = (h + l) / 2
        else:
            rfilt = rfilt_prev

            # Apply the selected filter type
            if f_type == 'Type 1':
                if h - r > rfilt_prev:
                    rfilt = h - r
                elif l + r < rfilt_prev:
                    rfilt = l + r
            elif f_type == 'Type 2':
                if h >= rfilt_prev + r:
                    rfilt = rfilt_prev + np.floor(abs(h - rfilt_prev) / r) * r
                elif l <= rfilt_prev - r:
                    rfilt = rfilt_prev - np.floor(abs(l - rfilt_prev) / r) * r

        # Calculate the bands
        hi_band = rfilt + r
        lo_band = rfilt - r

        # Handle averaging over filter changes if required
        if av_rf:
            filt_changed = rfilt != rfilt_prev
            if filt_changed:
                filt_change_values.append(rfilt)
                if len(filt_change_values) > av_n:
                    filt_change_values.pop(0)
                filt_change_count += 1
            rng_filt_value = np.mean(filt_change_values) if filt_change_values else rfilt
            hi_band = rng_filt_value + r
            lo_band = rng_filt_value - r
        else:
            rng_filt_value = rfilt

        # Update previous filter value
        rfilt_prev = rfilt

        return hi_band, lo_band, rng_filt_value, rfilt_prev, prev_rng_smooth, filt_change_count, filt_change_values

    def run(self):
        """
        Execute the Range Filter calculations on the provided data.
        """
        # Initialize variables and lists for calculations
        data = self.data
        n = len(data)
        self.filt = np.zeros(n)
        self.h_band = np.zeros(n)
        self.l_band = np.zeros(n)
        self.fdir = np.zeros(n)
        self.upward = np.zeros(n)
        self.downward = np.zeros(n)
        self.filt_color = np.array(['gray'] * n, dtype=object)
        self.bar_color = np.array(['gray'] * n, dtype=object)
        self.external_trend_output = np.zeros(n)

        # Variables for Conditional EMA and SMA calculations
        prev_ac = np.nan  # Previous Average Change EMA
        prev_atr = np.nan  # Previous ATR EMA
        prev_sd = np.nan  # Previous Standard Deviation
        ac_list = []  # List to store changes for Average Change calculation
        sd_list = []  # List to store values for Standard Deviation calculation
        prev_rng_smooth = np.nan  # Previous smoothed range value
        rfilt_prev = np.nan  # Previous filter value
        filt_change_count = 0  # Counter for filter changes
        filt_change_values = []  # List to store filter values for averaging

        # Loop over the data to compute the filter
        for i in range(n):
            # Determine the movement source (high/low or close)
            if self.mov_src == 'Wicks':
                h_val = data['high'].iloc[i]
                l_val = data['low'].iloc[i]
            else:  # 'Close'
                h_val = data['close'].iloc[i]
                l_val = data['close'].iloc[i]

            # Calculate the mid-price
            x = (h_val + l_val) / 2

            # Calculate the range size
            rng_size_value, prev_ac, prev_atr, prev_sd, ac_list, sd_list = self.rng_size(
                x, i, prev_ac, prev_atr, prev_sd, ac_list, sd_list)

            # Calculate the filter and bands
            h_band_i, l_band_i, filt_i, rfilt_prev, prev_rng_smooth, filt_change_count, filt_change_values = self.rng_filt(
                h_val, l_val, rng_size_value, i, rfilt_prev, prev_rng_smooth, filt_change_count, filt_change_values)

            # Store the computed values
            self.h_band[i] = h_band_i
            self.l_band[i] = l_band_i
            self.filt[i] = filt_i

            # Determine the filter direction
            if i == 0:
                self.fdir[i] = 0
            else:
                if self.filt[i] > self.filt[i - 1]:
                    self.fdir[i] = 1
                elif self.filt[i] < self.filt[i - 1]:
                    self.fdir[i] = -1
                else:
                    self.fdir[i] = self.fdir[i - 1]

            # Set upward and downward indicators
            self.upward[i] = 1 if self.fdir[i] == 1 else 0
            self.downward[i] = 1 if self.fdir[i] == -1 else 0

            # Assign colors based on trend direction
            if self.upward[i]:
                self.filt_color[i] = '#05ff9b'  # Bright green
                if data['close'].iloc[i] > self.filt[i]:
                    if i > 0 and data['close'].iloc[i] > data['close'].iloc[i - 1]:
                        self.bar_color[i] = '#05ff9b'  # Bright green
                    else:
                        self.bar_color[i] = '#00b36b'  # Darker green
                else:
                    self.bar_color[i] = 'gray'
            elif self.downward[i]:
                self.filt_color[i] = '#ff0583'  # Bright red
                if data['close'].iloc[i] < self.filt[i]:
                    if i > 0 and data['close'].iloc[i] < data['close'].iloc[i - 1]:
                        self.bar_color[i] = '#ff0583'  # Bright red
                    else:
                        self.bar_color[i] = '#b8005d'  # Darker red
                else:
                    self.bar_color[i] = 'gray'
            else:
                self.filt_color[i] = 'gray'
                self.bar_color[i] = 'gray'

            # External trend output (-1 for bearish, 1 for bullish)
            self.external_trend_output[i] = self.fdir[i]

        # Append the results to the original data DataFrame
        data['filt'] = self.filt
        data['h_band'] = self.h_band
        data['l_band'] = self.l_band
        data['fdir'] = self.fdir
        data['upward'] = self.upward
        data['downward'] = self.downward
        data['filt_color'] = self.filt_color
        data['bar_color'] = self.bar_color
        data['external_trend_output'] = self.external_trend_output

    # Optionally, you can add a method to return the modified DataFrame
    def get_data(self):
        return self.data
