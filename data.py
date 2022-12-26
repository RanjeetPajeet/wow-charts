"""
data.py
=======

Functions for getting auction data from the NexusHub API and returning it in more useful forms.
"""
import api





def get_server_history(item: str, server: str = "Skyfury", faction: str = "Alliance", numDays: int = None, avg: bool = True) -> dict:
    """
    Returns the price & quantity history of an item for the specified faction/server.

    Parameters
    ----------
    `item`: The name of the item.
    `server`: The name of the server.  Default is `Skyfury`.
    `faction`: The faction on the given server.  Default is `Alliance`.
    `numDays`: The number of days to get the price history for. If `None`, then the entire history is returned.
    `avg`: Whether or not to average the data over 2 hours.  Default is `True`.

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
    if avg: data = average(data)
    return data










def get_region_history(item: str, region: str = "US", numDays: int = None, avg: bool = True) -> dict:
    """
    Returns the price & quantity history of an item for the US region as a whole.

    Parameters
    ----------
    `item`: The name of the item.
    `region`: The region to get historical price data for.  Default is `US`.
    `numDays`: The number of days to get the price history for. If `None`, then the entire history is returned.
    `avg`: Whether or not to average the data over 2 hours.  Default is `True`.

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
