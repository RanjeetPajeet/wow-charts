"""
api.py
======

Functions that interface with the NexusHub API.
"""
import requests
from urllib.parse import urlparse
from http.client import HTTPConnection





def server_history(itemname: str, realm = "skyfury", faction = "alliance", timerange: int = None, convert_timezone = True, condensed = False, rounded = True) -> list[dict]:
    """
    Get historical price & quantity data for a particular item on a particular server.

    Parameters
    ----------
    `itemname`:   The standard name of the item to get data for.
    `realm`:   The server to get historical price data from.  Default is `skyfury`.
    `faction`:   The faction on the given realm.  Default is `alliance`.
    `timerange`:   The number of days worth of historical price data to retrieve.  If left as `None` (default), its entire history will be retrieved.
    `convert_timezone`:   Whether or not to convert the returned timestamps to the local timezone.  Default is `True`.
    `condensed`:   Whether or not to return the data in a condensed format (i.e., only the `marketValue` and `quantity` fields).  Default is `False`.
    `rounded`:   Whether or not to round the `marketValue`, `minBuyout`, and `quantity` fields to the nearest copper/integer.  Default is `True`.

    Returns
    -------
    List of dictionaries of the form:
    >>> [
    >>>     {
    >>>         "marketValue": 123456,
    >>>         "minBuyout": 123456,
    >>>         "quantity": 123456,
    >>>         "scannedAt": "MM-DD-YYYY HH:MM"
    >>>     },
    >>>     {
    >>>         "marketValue": 234567,
    >>>         "minBuyout": 234567,
    >>>         "quantity": 234567,
    >>>         "scannedAt": "MM-DD-YYYY HH:MM"
    >>>     },
    >>>     ...
    >>> ]
    """
    import datetime, pytz
    if not timerange:
        now = datetime.datetime.now()
        begin = datetime.datetime(year=2022,month=8,day=28,hour=now.hour,minute=now.minute,second=now.second,microsecond=now.microsecond)
        timerange = (now - begin).days
    itemname = itemname.lower().replace(' ', '-').replace("'", '')
    url = f"https://api.nexushub.co/wow-classic/v1/items/{realm.lower()}-{faction.lower()}/{itemname}/prices?timerange={timerange}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        if condensed:
            condensed_data = []
            for i in range(len(data)):
                condensed_data.append({
                    'marketValue': int(round(data[i]['marketValue'],0)) if rounded else data[i]['marketValue'],
                    'quantity': int(round(data[i]['quantity'],0)) if rounded else data[i]['quantity']
                })
            return condensed_data
        if convert_timezone:
            for i in range(len(data)):
                dt = datetime.datetime.strptime(data[i]['scannedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dt = dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
                data[i]['scannedAt'] = dt.strftime("%m-%d-%Y %H:%M")
                data[i]['scannedAt'] = datetime.datetime.strptime(data[i]['scannedAt'],"%m-%d-%Y %H:%M")
        if rounded:
            for i in range(len(data)):
                data[i]['marketValue'] = int(round(data[i]['marketValue'],0))
                data[i]['minBuyout'] = int(round(data[i]['minBuyout'],0))
                data[i]['quantity'] = int(round(data[i]['quantity'],0))
        return data
    else: return {}





def region_history(itemname: str, region = "us", timerange: int = None, convert_timezone = True, condensed = False, rounded = True) -> list[dict]:
    """
    Get historical price & quantity data for a particular item for an entire region.

    Parameters
    ----------
    `itemname`:   The standard name of the item to get data for.
    `region`:   The region to get historical price data for.  Default is `us`.
    `timerange`:   The number of days worth of historical price data to retrieve.  If left as `None`, its entire history will be retrieved.
    `convert_timezone`:   Whether or not to convert the timestamps to the local timezone.  Default is `True`.
    `condensed`:   Whether or not to return the data in a condensed format (i.e., only the `marketValue` and `quantity` fields).  Default is `False`.
    `rounded`:   Whether or not to round the `marketValue`, `minBuyout`, and `quantity` fields to the nearest copper/integer.  Default is `True`.

    Returns
    -------
    List of dictionaries of the form:
    >>> [
    >>>     {
    >>>         "marketValue": 123456,
    >>>         "minBuyout": 123456,
    >>>         "quantity": 123456,
    >>>         "scannedAt": "MM-DD-YYYY HH:MM"
    >>>     },
    >>>     ...
    >>> ]
    """
    import datetime, pytz
    if not timerange:
        now = datetime.datetime.now()
        begin = datetime.datetime(year=2022,month=8,day=28,hour=now.hour,minute=now.minute,second=now.second,microsecond=now.microsecond)
        timerange = (now - begin).days
    itemname = itemname.lower().replace(' ', '-').replace("'", '')
    url = f"https://api.nexushub.co/wow-classic/v1/items/{region.lower()}/{itemname}/prices?timerange={timerange}&region=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        if condensed:
            condensed_data = []
            for i in range(len(data)):
                condensed_data.append({
                    'marketValue': int(round(data[i]['marketValue'],0)) if rounded else data[i]['marketValue'],
                    'quantity': int(round(data[i]['quantity'],0)) if rounded else data[i]['quantity']
                })
            return condensed_data
        if convert_timezone:
            for i in range(len(data)):
                dt = datetime.datetime.strptime(data[i]['scannedAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                dt = dt.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
                data[i]['scannedAt'] = dt.strftime("%m-%d-%Y %H:%M")
                data[i]['scannedAt'] = datetime.datetime.strptime(data[i]['scannedAt'],"%m-%d-%Y %H:%M")
        if rounded:
            for i in range(len(data)):
                data[i]['marketValue'] = int(round(data[i]['marketValue'],0))
                data[i]['minBuyout'] = int(round(data[i]['minBuyout'],0))
                data[i]['quantity'] = int(round(data[i]['quantity'],0))
        return data
    else:
        print(response.status_code)
        return {}



    
def site_is_online(url: str, timeout: int = 2):
    """
    Checks the status of a website.

    Parameters
    ----------
    `url` : str
        The URL of the website to check.
    `timeout` : int
        The number of seconds to wait before timing out.
    
    Returns
    -------
    `status` : bool
        True if the website is online, False otherwise.

    Raises
    ------
    `Exception` if the website is offline.
    """
    error = Exception("< Unknown Error >")
    parser = urlparse(url)
    host = parser.netloc or parser.path.split("/")[0]
    for port in (80,443):
        connection = HTTPConnection(host=host, port=port, timeout=timeout)
        try:
            connection.request("HEAD", "/")
            return True
        except Exception as e:
            error = e
        finally:
            connection.close()
    raise error
    


def api_online() -> bool:
    """
    Checks if the Nexushub API is currently online.

    Parameters
    ----------
    None

    Returns
    -------
    `True` if the API is currently up, `False` otherwise.
    """
    try:
        online = site_is_online("https://api.nexushub.co/wow-classic/v1")
#         online = True   # `online` is only `True` if the `server_history()` call doesn't throw an error
    except:
        online = False  # `online` is only `False` if the `server_history()` call throws an error
    return online





def api_offline() -> bool:
    """
    Checks if the Nexushub API is currently offline.

    Parameters
    ----------
    None

    Returns
    -------
    `True` if the API is currently down, `False` otherwise
    """
    return not api_online()

