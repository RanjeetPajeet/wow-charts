"""
data.py
=======

Functions for getting auction data from the NexusHub API and returning it in more useful forms.
"""
import api
import datetime
import numpy as np
import pandas as pd





def fix_missing_data(data: dict) -> dict:
    """
    Fixes the data missing from Dec.20 -> Dec.25 and returns a new dictionary.
    """
    for i in range(len(data["times"])):
        # remove the minutes and seconds from the time
        data["times"][i] = datetime.datetime(data["times"][i].year, data["times"][i].month, data["times"][i].day, data["times"][i].hour)
    last_okay_index  = -1
    first_okay_index = -1
    last_okay_date  = datetime.datetime(2022, 12, 20, 9)
    first_okay_date = datetime.datetime(2022, 12, 25, 14)
    missing_times = [last_okay_date + datetime.timedelta(hours=i) for i in range(1, int((first_okay_date - last_okay_date).total_seconds() // 3600))]
    
    if data["times"][0] > last_okay_date:
        return data     # no missing data (all data occurs after the last okay date)

    for i in range(len(data["times"])):
        if data["times"][i] >= last_okay_date:
            last_okay_index = i ; break
    for i in range(len(data["times"])):
        if data["times"][i] >= first_okay_date:
            first_okay_index = i ; break
            
    if first_okay_index == -1 or last_okay_index == -1:
        return data     # no missing data (all data occurs before the first okay date)
    
    delta_time = first_okay_date - last_okay_date

    last_okay_price = data["prices"][last_okay_index]
    first_okay_price = data["prices"][first_okay_index]

    delta_price = first_okay_price - last_okay_price
    price_per_hour = delta_price / (delta_time.total_seconds() / 3600)

    missing_prices = [ int(last_okay_price + price_per_hour*(i+1))  for i in range(len(missing_times)) ]

    # add a little bit of randomness to the missing prices
    for i in range(len(missing_prices)):
#         if np.random.random() < 0.3:
#             missing_prices[i] = int(missing_prices[i] * (1 + (np.random.random()/5)*(np.random.random()-0.5)))
        if np.random.random() < 0.2:
            missing_prices[i] = int(missing_prices[i] * (1 + (np.random.random())*(np.random.random()-0.5)))


    last_okay_quantity = data["quantities"][last_okay_index]
    first_okay_quantity = data["quantities"][first_okay_index]

    delta_quantity = first_okay_quantity - last_okay_quantity
    quantity_per_hour = delta_quantity / (delta_time.total_seconds() / 3600)

    missing_quantities = [ int(last_okay_quantity + quantity_per_hour*(i+1))  for i in range(len(missing_times)) ]

    # add a little bit of randomness to the missing quantities
    for i in range(len(missing_quantities)):
        if np.random.random() < 0.5:
#             missing_quantities[i] = int(missing_quantities[i] * (1 + (np.random.random()*15)*(np.random.random()-0.5)))
            missing_quantities[i] = int( (missing_quantities[i]+np.mean(data["quantities"]))  * (1 + (0.3+np.random.random())*(np.random.random()-0.5)))


    fixed_times = data["times"][:last_okay_index+1] + missing_times + data["times"][first_okay_index:]
    fixed_prices = data["prices"][:last_okay_index+1] + missing_prices + data["prices"][first_okay_index:]
    fixed_quantities = data["quantities"][:last_okay_index+1] + missing_quantities + data["quantities"][first_okay_index:]

    return {
        "prices": fixed_prices,
        "quantities": fixed_quantities,
        "times": fixed_times,
    }







def get_server_history(item: str, server: str = "Skyfury", faction: str = "Alliance", numDays: int = None, avg: bool = True, fix: bool = True) -> dict:
    """
    Returns the price & quantity history of an item for the specified faction/server.

    Parameters
    ----------
    `item`: The name of the item.
    `server`: The name of the server.  Default is `Skyfury`.
    `faction`: The faction on the given server.  Default is `Alliance`.
    `numDays`: The number of days to get the price history for. If `None`, then the entire history is returned.
    `avg`: Whether or not to average the data over 2 hours.  Default is `True`.
    `fix`: Whether or not to fix the missing data that occurs between Dec. 20th and Dec. 25th.  Default is `True`.

    Returns
    -------
    Dictionary of lists of the form:
    >>> {
    >>>     "prices": [123456, 123456, ...],
    >>>     "quantities": [123456, 123456, ...],
    >>>     "times": ["MM-DD-YYYY HH:MM", "MM-DD-YYYY HH:MM", ...]
    >>> }
    """
    itemData = api.server_history(item, server, faction, numDays)
    prices = [i["marketValue"] for i in itemData]
    quantities = [i["quantity"] for i in itemData]
    times = [i["scannedAt"] for i in itemData]
    data = {"prices": prices, "quantities": quantities, "times": times}
    if fix: data = fix_missing_data(data)
    if avg: data = average(data)
    return data










def get_server_history_OHLC(item: str, server: str = "Skyfury", faction: str = "Alliance", numDays: int = None, avg: bool = True, fix: bool = True) -> tuple[dict, float, float]:
    """
    Returns the price & quantity history of an item for the specified faction/server,
    for the specified number of days, formatted for the creation of an OHLC-style chart, along with the min and max prices for setting the y-axis limits.
    Parameters
    ----------
    `item`: The name of the item.
    `server`: The name of the server.  Default is `Skyfury`.
    `faction`: The faction on the given server.  Default is `Alliance`.
    `numDays`: The number of days to get the price history for. If `None`, then the entire history is returned.
    `avg`: Whether or not to average the data over 2 hours.  Default is `True`.
    `fix`: Whether or not to fix the missing data that occurs between Dec. 20th and Dec. 25th.  Default is `True`.
    Returns
    -------
    Dictionary of dictionaries of the form:
    ```
    {
        "2023-01-23": {
            "open":   {"price": 0, "quantity": 0},
            "close":  {"price": 0, "quantity": 0},
            "high":   {"price": 0, "quantity": 0},
            "low":    {"price": 0, "quantity": 0},
            "mean":   {"price": 0, "quantity": 0},
            "median": {"price": 0, "quantity": 0},
            "stdev":  {"price": 0, "quantity": 0},
            "percent_change": {"price": 0, "quantity": 0},
            "pct_change": {
                "open":   {"price": 0, "quantity": 0},
                "close":  {"price": 0, "quantity": 0},
                "high":   {"price": 0, "quantity": 0},
                "low":    {"price": 0, "quantity": 0},
                "mean":   {"price": 0, "quantity": 0},
                "median": {"price": 0, "quantity": 0},
                "stdev":  {"price": 0, "quantity": 0},
            }
        },
        "2023-01-24": {
            ...
        },
        ...
    }
    ```
    """
    d = get_server_history(item, server, faction, numDays, avg, fix)
    
    prices = d["prices"]                        # Get the prices
    upper_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  +  
        5*np.std(pd.Series(prices).rolling(2).mean().dropna().tolist()) 
    )
    lower_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  -
        5*np.std(pd.Series(prices).rolling(2).mean().dropna().tolist())
    )
    for i in range(len(d["prices"])):
        if d["prices"][i] > upper_limit: d["prices"][i] = upper_limit
        if d["prices"][i] < lower_limit: d["prices"][i] = lower_limit
    
    minimum = min(d["prices"])                  # Get the minimum price
    maximum = max(d["prices"])                  # Get the maximum price
            
    t = d["times"]                              # Get the times
    t = [t[i].date() for i in range(len(t))]    # Get the dates from the times
    dates = list(set(t))                        # Get the unique dates
    dates.sort()                                # Order the dates
    locs = {}
    for i in range(len(dates)):
        locs[dates[i]] = []
        for j in range(len(t)):
            if t[j] == dates[i]:
                locs[dates[i]].append(j)        # Get the locations of the times that are for this date
    d1 = {}
    for i in range(len(dates)):
    # for date in dates:
        d1[dates[i]] = {
            "prices": [],
            "quantities": [],
        }
        for j in range(len(locs[dates[i]])):
            # append the last price and quantity of the previous day to the first price and quantity of the current day if i > 0
            if i > 0 and j == 0:
                d1[dates[i]]["prices"].append(d1[dates[i-1]]["prices"][-1])
                d1[dates[i]]["quantities"].append(d1[dates[i-1]]["quantities"][-1])
            d1[dates[i]]["prices"].append(d["prices"][locs[dates[i]][j]])
            d1[dates[i]]["quantities"].append(d["quantities"][locs[dates[i]][j]])
        # for loc in locs[date]:
        #     d1[date]["prices"].append(d["prices"][loc])
        #     d1[date]["quantities"].append(d["quantities"][loc])
    d2 = {}
    n = -1
    for date in dates:
        n += 1
        d2[date] = {
            "open":   {"price": 0, "quantity": 0},
            "close":  {"price": 0, "quantity": 0},
            "high":   {"price": 0, "quantity": 0},
            "low":    {"price": 0, "quantity": 0},
            "mean":   {"price": 0, "quantity": 0},
            "median": {"price": 0, "quantity": 0},
            "stdev":  {"price": 0, "quantity": 0},
            "percent_change": {"price": 0, "quantity": 0},
            "pct_change": {
                "open":   {"price": 0, "quantity": 0},
                "close":  {"price": 0, "quantity": 0},
                "high":   {"price": 0, "quantity": 0},
                "low":    {"price": 0, "quantity": 0},
                "mean":   {"price": 0, "quantity": 0},
                "median": {"price": 0, "quantity": 0},
                "stdev":  {"price": 0, "quantity": 0},
            }
        }
        d2[date]["open"]["price"]      = round(d1[date]["prices"][0], 2)
        d2[date]["open"]["quantity"]   = round(d1[date]["quantities"][0])
        d2[date]["close"]["price"]     = round(d1[date]["prices"][-1], 2)
        d2[date]["close"]["quantity"]  = round(d1[date]["quantities"][-1])
        d2[date]["high"]["price"]      = round(max(d1[date]["prices"]), 2)
        d2[date]["high"]["quantity"]   = round(max(d1[date]["quantities"]))
        d2[date]["low"]["price"]       = round(min(d1[date]["prices"]), 2)
        d2[date]["low"]["quantity"]    = round(min(d1[date]["quantities"]))
        d2[date]["mean"]["price"]      = round(np.mean(d1[date]["prices"]), 2)
        d2[date]["mean"]["quantity"]   = round(np.mean(d1[date]["quantities"]))
        d2[date]["median"]["price"]    = round(np.median(d1[date]["prices"]), 2)
        d2[date]["median"]["quantity"] = round(np.median(d1[date]["quantities"]))
        d2[date]["stdev"]["price"]     = round(np.std(d1[date]["prices"]), 2)
        d2[date]["stdev"]["quantity"]  = round(np.std(d1[date]["quantities"]))

        d2[date]["percent_change"]["price"] = round( 100 * ((d2[date]["close"]["price"]-d2[date]["open"]["price"])/(d2[date]["open"]["price"])) , 2 )
        d2[date]["percent_change"]["quantity"] = round( 100 * ((d2[date]["close"]["quantity"]-d2[date]["open"]["quantity"])/(d2[date]["open"]["quantity"])) , 2 )

        try:
            if n > 0:
                d2[date]["pct_change"]["open"]["price"]      = round((d2[date]["open"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["open"]["quantity"]   = round((d2[date]["open"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["close"]["price"]     = round((d2[date]["close"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["close"]["quantity"]  = round((d2[date]["close"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["high"]["price"]      = round((d2[date]["high"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["high"]["quantity"]   = round((d2[date]["high"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["low"]["price"]       = round((d2[date]["low"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["low"]["quantity"]    = round((d2[date]["low"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["mean"]["price"]      = round((d2[date]["mean"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["mean"]["quantity"]   = round((d2[date]["mean"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["median"]["price"]    = round((d2[date]["median"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["median"]["quantity"] = round((d2[date]["median"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
                d2[date]["pct_change"]["stdev"]["price"]     = round((d2[date]["stdev"]["price"] - d2[dates[n-1]]["close"]["price"]) / d2[dates[n-1]]["close"]["price"] * 100, 2)
                d2[date]["pct_change"]["stdev"]["quantity"]  = round((d2[date]["stdev"]["quantity"] - d2[dates[n-1]]["close"]["quantity"]) / d2[dates[n-1]]["close"]["quantity"] * 100, 2)
        except:
            pass
            # print("error on date", date)
    return d2, minimum, maximum











def get_region_history(item: str, region: str = "US", numDays: int = None, avg: bool = True, fix: bool = True) -> dict:
    """
    Returns the price & quantity history of an item for the US region as a whole.

    Parameters
    ----------
    `item`: The name of the item.
    `region`: The region to get historical price data for.  Default is `US`.
    `numDays`: The number of days to get the price history for. If `None`, then the entire history is returned.
    `avg`: Whether or not to average the data over 2 hours.  Default is `True`.
    `fix`: Whether or not to fix the missing data that occurs between Dec. 20th and Dec. 25th.  Default is `True`.

    Returns
    -------
    Dictionary of lists of the form:
    >>> {
    >>>     "prices": [123456, 123456, ...],
    >>>     "quantities": [123456, 123456, ...],
    >>>     "times": ["MM-DD-YYYY HH:MM", "MM-DD-YYYY HH:MM", ...]
    >>> }
    """
    itemData = api.region_history(item, region, numDays)
    prices = [i["marketValue"] for i in itemData]
    quantities = [i["quantity"] for i in itemData]
    times = [i["scannedAt"] for i in itemData]
    data = {"prices": prices, "quantities": quantities, "times": times}
    if fix: data = fix_missing_data(data)
    if avg: data = average(data)
    return data










def average(dataset1: dict, dataset2: dict = None, numHoursToAverage: int = 2) -> dict:
    """
    Averages the given dataset(s) over the given number of hours.

    Parameters
    ----------
    `dataset1`: Dataset #1.
    `dataset2`: Dataset #2. If `None`, then only the `dataset1` is averaged and returned.
    `numHoursToAverage`: The number of hours to average the data over (ex: `2` for 2-hour average, `12` for 12-hour average, etc).

    Returns
    -------
    `averagedDataset1`: The modified version of dataset #1, with the same structure.
    `averagedDataset2`: The modified version of dataset #2, with the same structure, if `dataset2` was given.
    """
    startIndex = len(dataset1["prices"]) % numHoursToAverage
    # if only one dataset is given, then just average that one
    if dataset2 is None:
        # create a new dataset to hold the averaged data
        averagedDataset = {"prices": [], "quantities": [], "times": []}
        # loop through the dataset and average the data
        for i in range(startIndex, len(dataset1["times"]), numHoursToAverage):
            # get the average price and quantity
            avgPrice = sum(dataset1["prices"][i:i+numHoursToAverage]) / numHoursToAverage
            avgQuantity = sum(dataset1["quantities"][i:i+numHoursToAverage]) / numHoursToAverage
            # add the average price and quantity to the new dataset
            averagedDataset["prices"].append(avgPrice)
            averagedDataset["quantities"].append(avgQuantity)
            averagedDataset["times"].append(dataset1["times"][i])
        return averagedDataset
    # if two datasets are given, then average both of them
    else:
        # create new datasets to hold the averaged data
        averagedDataset1 = {"prices": [], "quantities": [], "times": []}
        averagedDataset2 = {"prices": [], "quantities": [], "times": []}
        # loop through the datasets and average the data
        for i in range(startIndex, len(dataset1["times"]), numHoursToAverage):
            avgPrice1 = sum(dataset1["prices"][i:i+numHoursToAverage]) / numHoursToAverage
            avgQuantity1 = sum(dataset1["quantities"][i:i+numHoursToAverage]) / numHoursToAverage
            avgPrice2 = sum(dataset2["prices"][i:i+numHoursToAverage]) / numHoursToAverage
            avgQuantity2 = sum(dataset2["quantities"][i:i+numHoursToAverage]) / numHoursToAverage
            # add the average price and quantity to the new datasets
            averagedDataset1["prices"].append(avgPrice1)
            averagedDataset1["quantities"].append(avgQuantity1)
            averagedDataset1["times"].append(dataset1["times"][i])
            averagedDataset2["prices"].append(avgPrice2)
            averagedDataset2["quantities"].append(avgQuantity2)
            averagedDataset2["times"].append(dataset2["times"][i])
        return averagedDataset1, averagedDataset2










def align(dataset1: dict, dataset2: dict) -> dict:
    """
    Aligns the two given datasets such that the dates of their last elements are within an hour of one another, and their lengths are equal.

    Parameters
    ----------
    `dataset1`: Dataset #1.
    `dataset2`: Dataset #2.

    Returns
    -------
    `alignedDataset1`: The modified version of dataset #1, with the same structure.
    `alignedDataset2`: The modified version of dataset #2, with the same structure.
    """
    len1 = len(dataset1["times"])
    len2 = len(dataset2["times"])
    if len1 > len2:
        dataset1["times"] = dataset1["times"][len1-len2:]
        dataset1["prices"] = dataset1["prices"][len1-len2:]
        dataset1["quantities"] = dataset1["quantities"][len1-len2:]
    elif len2 > len1:
        dataset2["times"] = dataset2["times"][len2-len1:]
        dataset2["prices"] = dataset2["prices"][len2-len1:]
        dataset2["quantities"] = dataset2["quantities"][len2-len1:]
    return dataset1, dataset2






# NOTE: THIS FUNCTION NEEDS WORK
def remove_outliers(lst: list) -> list:
    """
    Replaces any extreme outliers (that are obviously bad data) with the average of the surrounding data.

    Parameters
    ----------
    `lst`: The list to replace outliers in.

    Returns
    -------
    `list`: The modified version of the list, with the same number of elements.
    """
    import statistics
    # get the average and standard deviation of the list
    avg = statistics.mean(lst)
    std = statistics.stdev(lst)
    newLst = []
    # loop through the list and replace any outliers with the average of the surrounding data
    for i in range(len(lst)):
        if lst[i] > avg + 2*std or lst[i] < avg - 2*std:
            newLst.append(avg)
            # lst[i] = avg
            # lst[i] = (lst[i-1] + lst[i+1]) / 2
        else:
            newLst.append(lst[i])
    avg2 = statistics.mean(newLst)
    std2 = statistics.stdev(newLst)
    for i in range(len(lst)):
        if lst[i] > avg2 + 2*std2 or lst[i] < avg2 - 2*std2:
            lst[i] = (avg2+avg)/2
            # lst[i] = (lst[i-1] + lst[i+1]) / 2
    return lst
