"""
misc.py
=======

Functions/classes used elsewhere that didn't have a home.
"""




def run_custom_css(css: str):
    """
    Runs the given string as a CSS expression.
    """
    import streamlit as st
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)

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
