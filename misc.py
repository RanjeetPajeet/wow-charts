"""
misc.py
=======

Functions/classes used elsewhere that didn't have a home.
"""
import pandas as pd




def get_min_max_of_data(
        data: pd.DataFrame, prices: list,
        ma4: bool, ma12: bool, ma24: bool, ma48: bool, hiding_original: bool)  ->  tuple:
    """
    Gets the minimum and maximum values from the given data for use in determining the y-axis chart limits.

    Finds:
        - The minimum of the minimums of each moving average given.
        - The maximum of the maximums of each moving average given.
    
    Parameters
    ----------
    `data` :  The data to be analyzed (can be a single DataFrame or a list of DataFrames [max length of `2`]).
    `prices` :  A list of the prices contained in the data (can be a single list or a list of lists [max length of `2`]).
    `ma4` :  Whether or not to include the 4-day moving average in the analysis.
    `ma12` :  Whether or not to include the 12-day moving average in the analysis.
    `ma24` :  Whether or not to include the 24-day moving average in the analysis.
    `ma48` :  Whether or not to include the 48-day moving average in the analysis.
    `hiding_original` :  Whether or not to include the original data in the analysis.

    Returns
    -------
    A tuple containing the minimum and maximum values of the given data, `(min, max)`.
    """
    # Check proper input of `data` and `prices`
    if isinstance(data, list) and not isinstance(prices[0], list):
        raise ValueError("If `data` is a list, `prices` must be a list of lists.")
    elif not isinstance(data, list) and isinstance(prices[0], list):
        raise ValueError("If `prices` is a list of lists, `data` must be a list.")
    elif isinstance(data, list) and isinstance(prices[0], list) and len(data) != len(prices):
        raise ValueError("If `data` and `prices` are both lists, they must be the same length.")
    elif isinstance(data, list) and isinstance(prices[0], list) and len(data) > 2:
        raise ValueError("If `data` and `prices` are both lists, they must be no longer than 2.")

    if isinstance(data, list):
        min4_a  = min(data[0]["4-hour moving average" ].dropna().tolist()[1:])
        min4_b  = min(data[1]["4-hour moving average" ].dropna().tolist()[1:])
        max4_a  = max(data[0]["4-hour moving average" ].dropna().tolist()[1:])
        max4_b  = max(data[1]["4-hour moving average" ].dropna().tolist()[1:])
        min12_a = min(data[0]["12-hour moving average"].dropna().tolist()[1:])
        min12_b = min(data[1]["12-hour moving average"].dropna().tolist()[1:])
        max12_a = max(data[0]["12-hour moving average"].dropna().tolist()[1:])
        max12_b = max(data[1]["12-hour moving average"].dropna().tolist()[1:])
        min24_a = min(data[0]["24-hour moving average"].dropna().tolist()[1:])
        min24_b = min(data[1]["24-hour moving average"].dropna().tolist()[1:])
        max24_a = max(data[0]["24-hour moving average"].dropna().tolist()[1:])
        max24_b = max(data[1]["24-hour moving average"].dropna().tolist()[1:])
        min48_a = min(data[0]["48-hour moving average"].dropna().tolist()[1:])
        min48_b = min(data[1]["48-hour moving average"].dropna().tolist()[1:])
        max48_a = max(data[0]["48-hour moving average"].dropna().tolist()[1:])
        max48_b = max(data[1]["48-hour moving average"].dropna().tolist()[1:])
        min4  = min(min4_a,  min4_b )
        max4  = max(max4_a,  max4_b )
        min12 = min(min12_a, min12_b)
        max12 = max(max12_a, max12_b)
        min24 = min(min24_a, min24_b)
        max24 = max(max24_a, max24_b)
        min48 = min(min48_a, min48_b)
        max48 = max(max48_a, max48_b)
    else:
        min4  = min(data["4-hour moving average" ].dropna().tolist()[1:])
        max4  = max(data["4-hour moving average" ].dropna().tolist()[1:])
        min12 = min(data["12-hour moving average"].dropna().tolist()[1:])
        max12 = max(data["12-hour moving average"].dropna().tolist()[1:])
        min24 = min(data["24-hour moving average"].dropna().tolist()[1:])
        max24 = max(data["24-hour moving average"].dropna().tolist()[1:])
        min48 = min(data["48-hour moving average"].dropna().tolist()[1:])
        max48 = max(data["48-hour moving average"].dropna().tolist()[1:])

    if hiding_original:
        if ma4 and not ma12 and not ma24 and not ma48:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24 and not ma48:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12 and not ma48:
            minimum = min24
            maximum = max24
        elif ma48 and not ma4 and not ma12 and not ma24:
            minimum = min48
            maximum = max48
        elif ma4 and ma12 and not ma24 and not ma48:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12 and not ma48:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4 and not ma48:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24 and not ma48:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        elif ma4 and ma12 and ma24 and ma48:
            minimum = min(min4, min12, min24, min48)
            maximum = max(max4, max12, max24, max48)
        elif ma4 and not ma12 and ma24 and not ma48:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma4 and not ma12 and not ma24 and ma48:
            minimum = min(min4, min48)
            maximum = max(max4, max48)
        elif ma12 and not ma4 and ma24 and not ma48:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma12 and not ma4 and not ma24 and ma48:
            minimum = min(min12, min48)
            maximum = max(max12, max48)
        elif ma24 and not ma4 and not ma12 and ma48:
            minimum = min(min24, min48)
            maximum = max(max24, max48)
        elif ma4 and not ma12 and ma24 and ma48:
            minimum = min(min4, min24, min48)
            maximum = max(max4, max24, max48)
        elif ma12 and not ma4 and ma24 and ma48:
            minimum = min(min12, min24, min48)
            maximum = max(max12, max24, max48)
        elif ma4 and ma12 and not ma24 and ma48:
            minimum = min(min4, min12, min48)
            maximum = max(max4, max12, max48)
        else:
            if isinstance(data, list):
                minimum = min( min(prices[0]), min(prices[1]) )
                maximum = max( max(prices[0]), max(prices[1]) )
            else:
                minimum = min(prices)
                maximum = max(prices)
    else:
        if isinstance(data, list):
            minimum = min( min(prices[0]), min(prices[1]) )
            maximum = max( max(prices[0]), max(prices[1]) )
        else:
            minimum = min(prices)
            maximum = max(prices)
    return minimum, maximum






def titleize(string: str):
    """
    "Titleizes" the given string.
    
    Basically the built-in `string.title()` method,
    but forces any `s` characters following an `'` character to lower case.
    
    Example:
        string = "mekgineer's chopper"
        string = titleize(string)
        >>> string
            Mekgineer's Chopper
    """
    string = string.title()
    string = string.replace("'S", "'s")
    return string
    




def run_custom_css(css: str):
    """
    Runs the given string as a CSS expression.
    """
    import streamlit as st
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

    
    
def run_custom_javascript(code: str):
    """
    Runs the given Javascript code.
    """
    from streamlit.components.v1 import html
    html(f"<script>{code}</script>")

    
    
def hide_element(element: str, attribute_name: str, attribute_value: str):
    """
    Hides an element with the given identifiers.
    """
    run_custom_css(f'{element}[{attribute_name}="{attribute_value}"]' + '{display: none;}')





def map_value(value, input_range, output_range):
    """
    Maps a value from some specified range to a new range.

    Parameters
    ----------
    `value` :  The value to be mapped.
    `input_range` :  The range that the initial value is a member of.
    `output_range` :  The range that the desired output value should be a member of.

    Returns
    -------
    The mapped equivalent of the given value as an `int` or `float`.

    Examples
    --------
    >>> map_value(10, input_range=[0,100], output_range=[20,50])
        23
    >>> map_value(50, input_range=[0,100], output_range=[20,50])
        35
    >>> map_value(50, input_range=[0,100], output_range=[100,200])
        150
    """
    return (value - input_range[0]) * (output_range[1] - output_range[0]) / (input_range[1] - input_range[0]) + output_range[0]






def weighted_average(values: list, weights: list) -> float:
    """
    Returns the weighted average of a list of values and a list of weights.
    Note:  The weights don't have to sum to 1, but `values` and `weights` must have the same length.

    Parameters
    ----------
    `values` :   The list of values to compute the average of.
    `weights` :   The list of weights to assign to each value.
    
    Examples
    --------
    >>> weighted_average([3, 6, 9],  [1/3, 1/3, 1/3])
        6.0
    >>> weighted_average([4, 4, 8],  [1/4, 1/4, 1/2])
        6.0
    """
    if len(values) != len(weights):
        raise ValueError(f"\n>> `values` and `weights` must have the same length ({len(values)} vs {len(weights)}).\n")
    total = 0
    for value,weight in zip(values,weights):
        total += value*weight
    return total / sum(weights)






def decimal(num: float) -> float:
    """
    Returns just the decimal portion of a number.
    """
    return num - int(num)











def fix_bad_data(data1: list, data2: list, threshold: int = 3) -> list:
    """
    Fixes bad data in a list. `data1` is the good data (server prices), and `data2` is the bad data (region prices).
    `threshold` is the maximum multiple-difference between the two lists before the bad data is fixed.
    """
    import numpy as np
    serverPrices = data1
    regionPrices = data2
    for i in range(len(serverPrices)):
        diff = regionPrices[i] - serverPrices[i]
        if diff > threshold*serverPrices[i] and i > 12:
            lastGoodRegionPrice = regionPrices[i-1]
            last12diffs = [regionPrices[x] - serverPrices[x] for x in range(i-12,i)]
            for j in range(i, len(serverPrices)):
                if (regionPrices[j] - serverPrices[j]) > threshold*serverPrices[j]:
                    plusMinus1Stdev = (np.random.rand() * 2 - 1) * np.std(last12diffs)
                    regionPrices[j] = lastGoodRegionPrice + plusMinus1Stdev
    return regionPrices










# class Datetime:
#     """
#     `datetime`  wrapper with several static methods.
#     """
#     import pytz
#     from datetime import datetime


#     @staticmethod
#     def now(rtype = "string", format = "%m-%d-%Y %H:%M:%S", timezone = "central", _12h = False) -> datetime | str:
#         """
#         Timezone aware version of `datetime.datetime.now()`.
        
#         Parameters
#         ----------
#         `rtype`:   The type to be returned.  Can be `"string"` or `"datetime"`.
#         `format`:   The format for `strftime`,  if `rtype` is `"string"`.  Default format is of the form `09-10-2022 14:21:05`.
#         `timezone`:   The timezone of the returned date & time.  Can be `"central"`, `"eastern"`, `"mountain"`, `"pacific"`, or `"utc"`.
#         `_12h`:   If `True`, will return the time in 12-hour format (`09-10-2022 02:21:05 PM`),  as opposed to 24-hour format (`09-10-2022 14:21:05`).  Overrides `format`.

#         Examples
#         --------
#         >>> Datetime.now()
#             str('09-10-2022 14:21:05')
#         >>> Datetime.now(_12h=True)
#             str('09-10-2022 02:21:05 PM')
#         >>> Datetime.now(timezone="eastern")
#             str('09-10-2022 15:21:05')
#         >>> Datetime.now(rtype="datetime")
#             datetime.datetime('2022-09-10 14:21:05')
#         """
#         if rtype.lower() not in ["string","datetime"]:
#             raise ValueError(f"\n>> `rtype` must be either 'string' or 'datetime', not {rtype}.\n")
#         if timezone.lower() not in ["central","eastern","mountain","pacific","utc"]:
#             raise ValueError(f"\n>> The specified timezone ({timezone}) is invalid.\n")
#         timezone = f"US/{timezone.lower().capitalize()}" if timezone.lower() != "utc" else "UTC"
#         now = Datetime.datetime.now(Datetime.pytz.timezone(timezone))
#         if _12h: return now.strftime("%m-%d-%Y %I:%M:%S %p")
#         if rtype.lower() == "string": return now.strftime(format)
#         return now.replace(tzinfo=None, microsecond=0)
    

#     @staticmethod
#     def change_timezone(dt: datetime, timezone: str, rtype = "string", format = "%m-%d-%Y %H:%M:%S") -> datetime | str:
#         """
#         Converts a `datetime` object into a new `datetime` object in the given timezone.
        
#         Parameters
#         ----------
#         `dt`:   The `datetime` object to be converted.
#         `timezone`:   The timezone to convert to.  Can be `"central"`, `"eastern"`, `"mountain"`, `"pacific"`, or `"utc"`.
#         `rtype`:   The type to be returned.  Can be `"string"` or `"datetime"`.
#         `format`:   The format for `strftime`, if `rtype` is `"string"`.  Default format is of the form `09-10-2022 14:21:05`.
        
#         Examples
#         --------
#         >>> dt = datetime('09-10-2022 14:21:05')
#             str('09-10-2022 14:21:05')
#         >>> dt = Datetime.change_timezone(dt, "eastern")
#             str('09-10-2022 15:21:05')
#         >>> dt = Datetime.change_timezone(dt, "utc", rtype="datetime")
#             datetime.datetime('2022-09-10 19:21:05')
#         """
#         if rtype.lower() not in ["string","datetime"]:
#             raise ValueError(f"\n>> `rtype` must be either 'string' or 'datetime', not {rtype}.\n")
#         if timezone.lower() not in ["central","eastern","mountain","pacific","utc"]:
#             raise ValueError(f"\n>> The specified timezone ({timezone}) is invalid.\n")
#         timezone = f"US/{timezone.lower().capitalize()}" if timezone.lower() != "utc" else "UTC"
#         dt = dt.replace(tzinfo=Datetime.pytz.timezone(timezone))
#         return dt.strftime(format) if rtype.lower() == "string" else dt.replace(tzinfo=None, microsecond=0)
    

#     @staticmethod
#     def seconds_until_next_hour() -> int:
#         """
#         Returns the number of seconds from now until the next hour.
#         """
#         return (60-Datetime.datetime.now().minute)*60 - Datetime.datetime.now().second
    

#     @staticmethod
#     def seconds_until_next_minute() -> int:
#         """
#         Returns the number of seconds from now until the next minute.
#         """
#         return 60-(Datetime.datetime.now().second)
