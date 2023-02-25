import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from misc import map_value
from data import get_server_history, get_region_history, remove_outliers



MOUSEOVER_LINE_THICKNESS = 15.0     # the stroke width of the zero opacity line added to charts to assist in tooltip visibility when mousing over price lines


def mouseover_line(data: pd.DataFrame, color: str, y_label: str, yaxis_title: str, 
                   chart_ylimits: tuple, opacity: float = 0.0, xaxis_datetime_format: tuple = ("%b %d")) -> alt.Chart:
    """
    Generates a line equivalent to what is used for an item's price,
    except the stroke width (thickness) is much larger and it has zero opacity.
    This creates a region around the visible line where the mouse will generate a tooltip.
    """
    return alt.Chart(data).mark_line(
        color = color,
        strokeWidth = MOUSEOVER_LINE_THICKNESS,
        opacity = opacity,
    ).encode(
        x=alt.X("Time", axis=alt.Axis(title="Date", format=xaxis_datetime_format)),
        y=alt.Y(y_label, axis=alt.Axis(title=yaxis_title), scale=alt.Scale(domain=chart_ylimits)),
        tooltip=["Time", y_label],
    )





def enforce_upper_limit(prices: list, num_std_deviations: int = 3) -> list:
    """
    Defines an upper limit as `mean(prices) + num_std_deviations*std_dev(prices)`,
    then iterates through the given list of prices, setting any values larger than this value equal to it.
    
    Parameters
    ----------
    `prices`: The list to set an upper limit on.
    `num_std_deviations`: The number of standard deviations away from the mean to define the upper limit as.
    
    Returns
    -------
    A new list with any values too high replaced with the upper limit.
    """
    upper_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  +  
        num_std_deviations * np.std(pd.Series(prices).rolling(2).mean().dropna().tolist()) 
    )
    for i in range(len(prices)):
        if prices[i] > upper_limit:
            prices[i] = upper_limit
    return prices

  


def enforce_lower_limit(prices: list, num_std_deviations: int = 3) -> list:
    """
    Defines a lower limit as `mean(prices) - num_std_deviations*std_dev(prices)`,
    then iterates through the given list of prices, setting any values smaller than this value equal to it.
    
    Parameters
    ----------
    `prices`: The list to set an upper limit on.
    `num_std_deviations`: The number of standard deviations away from the mean to define the lower limit as.
    
    Returns
    -------
    A new list with any values too low replaced with the lower limit.
    """
    lower_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  -  
        num_std_deviations * np.std(pd.Series(prices).rolling(2).mean().dropna().tolist()) 
    )
    for i in range(len(prices)):
        if prices[i] < lower_limit:
            prices[i] = lower_limit
    return prices
        
    

    
    
    
    
    
    
def create_OHLC_chart(OHLC_data: dict, minimum: float, maximum: float, show_quantity: bool = False) -> alt.Chart:
    """
    `OHLC_data`, `minimum`, and `maximum` come from `data.get_server_history_OHLC()`.
    `show_quantity` determines whether or not an area is drawn to the plot showing quantities.
    """
    df = pd.DataFrame({
        'median_price': [OHLC_data[date]["median"]["price"] for date in OHLC_data],
    })
    SCALE = 100 if df["median_price"].mean() < 10000 else 10000
    YLABEL = "Price (silver)" if SCALE==100 else "Price (gold)"
    chart_ylims = (int(minimum/1.25/SCALE), int(maximum*1.1/SCALE))
    if minimum < 1 and maximum < 2 and SCALE != 100:
        chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))

    OHLC_df = pd.DataFrame({
        'date': list(OHLC_data.keys()),
        'open_price': [round(OHLC_data[date]["open"]["price"]/SCALE,2) for date in OHLC_data],
        'close_price': [round(OHLC_data[date]["close"]["price"]/SCALE,2) for date in OHLC_data],
        'high_price': [round(OHLC_data[date]["high"]["price"]/SCALE,2) for date in OHLC_data],
        'low_price': [round(OHLC_data[date]["low"]["price"]/SCALE,2) for date in OHLC_data],
        'open_quantity': [OHLC_data[date]["open"]["quantity"] for date in OHLC_data],
        'close_quantity': [OHLC_data[date]["close"]["quantity"] for date in OHLC_data],
        'high_quantity': [OHLC_data[date]["high"]["quantity"] for date in OHLC_data],
        'low_quantity': [OHLC_data[date]["low"]["quantity"] for date in OHLC_data],
        'mean_price': [round(OHLC_data[date]["mean"]["price"]/SCALE,2) for date in OHLC_data],
        'mean_quantity': [OHLC_data[date]["mean"]["quantity"] for date in OHLC_data],
        'median_price': [round(OHLC_data[date]["median"]["price"]/SCALE,2) for date in OHLC_data],
        'median_quantity': [OHLC_data[date]["median"]["quantity"] for date in OHLC_data],
        'pct_change_mean_price': [OHLC_data[date]["pct_change"]["mean"]["price"] for date in OHLC_data],
        'pct_change_mean_quantity': [OHLC_data[date]["pct_change"]["mean"]["quantity"] for date in OHLC_data],
        'pct_change_median_price': [OHLC_data[date]["pct_change"]["median"]["price"] for date in OHLC_data],
        'pct_change_median_quantity': [OHLC_data[date]["pct_change"]["median"]["quantity"] for date in OHLC_data],
    })
    
    
    range_quantity = [OHLC_df["mean_quantity"].min(), OHLC_df["mean_quantity"].max()]
    quantities = [ map_value(x, range_quantity, [chart_ylims[0],minimum/SCALE]) for x in OHLC_df["mean_quantity"] ]
    OHLC_df.insert(2, "quantities", quantities, True)

    
    OHLC_df['date'] = pd.to_datetime(OHLC_df['date'])
    OHLC_df = OHLC_df.sort_values(by='date')
    OHLC_df = OHLC_df.reset_index(drop=True)
    OHLC_df['pct_change_mean_price'] = OHLC_df['pct_change_mean_price'].apply(lambda x: x / 100)
    OHLC_df['pct_change_mean_quantity'] = OHLC_df['pct_change_mean_quantity'].apply(lambda x: x / 100)
    OHLC_df['pct_change_median_price'] = OHLC_df['pct_change_median_price'].apply(lambda x: x / 100)
    OHLC_df['pct_change_median_quantity'] = OHLC_df['pct_change_median_quantity'].apply(lambda x: x / 100)

    
    
    
    

    XAXIS_DATETIME_FORMAT = ( "%b %d" )
    chart = alt.Chart(OHLC_df).mark_rule().encode(
        x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
        y=alt.Y('low_price', axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
        y2='high_price',
        color=alt.condition('datum.open_price <= datum.close_price', alt.value('#06982d'), alt.value('#ae1325')),    # color green (#06982d) if open <= close, else red (#ae1325)
        tooltip=[
            alt.Tooltip('date' , title='Date'),
            alt.Tooltip('open_price' , title='Open' , format='.2f',),
            alt.Tooltip('close_price', title='Close', format='.2f',),
            alt.Tooltip('high_price' , title='High' , format='.2f',),
            alt.Tooltip('low_price'  , title='Low'  , format='.2f',),
            # alt.Tooltip('mean_price' , title='Mean' , format='.2f',),
            # alt.Tooltip('median_price'  , title='Median'  , format='.2f',),
            alt.Tooltip('pct_change_mean_price'  , title='Pct Change'  , format='.2%',),
        ]
    ).properties(
        #width=600,
        height=600
    )
    chart += alt.Chart(OHLC_df).mark_bar().encode(
        x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
        y='open_price',
        y2='close_price',
        # size=alt.value(8),
        # stroke=alt.value('black'), strokeWidth=alt.value(0.25),
        color=alt.condition('datum.open_price <= datum.close_price', alt.value('#06982d'), alt.value('#ae1325')),
        tooltip=[
            alt.Tooltip('date' , title='Date'),
            alt.Tooltip('open_price' , title='Open' , format='.2f',),
            alt.Tooltip('close_price', title='Close', format='.2f',),
            alt.Tooltip('high_price' , title='High' , format='.2f',),
            alt.Tooltip('low_price'  , title='Low'  , format='.2f',),
            # alt.Tooltip('mean_price' , title='Mean' , format='.2f',),
            # alt.Tooltip('median_price'  , title='Median'  , format='.2f',),
            alt.Tooltip('pct_change_mean_price'  , title='Pct Change'  , format='.2%',),
        ]
    ).properties(
        #width=600,
        height=600
    )
    
    
    if show_quantity:
        quantity_chart = alt.Chart(OHLC_df).mark_area(
              color=alt.Gradient(
                  gradient="linear",
                  stops=[alt.GradientStop(color="#83c9ff", offset=0),     # bottom color
                        alt.GradientStop(color="#52A9FA", offset=0.4)],  # top color
                  x1=1, x2=1, y1=1, y2=0,
              ),
              opacity = 0.2,
              strokeWidth=2,
              interpolate="monotone",
              clip=True,
          ).encode(
              x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
              y=alt.Y("quantities", axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
              tooltip=[
                  alt.Tooltip('date' , title='Date'),
                  alt.Tooltip('mean_quantity' , title='Quantity')
              ]
          )
        chart = chart + quantity_chart
    
    
    
    chart = chart.properties(height=600)
    chart = chart.properties(width=700)
    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    return chart
    
    
    
    







def plot_saronite_value_history(server: str, faction: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    gems = {
        "Scarlet Ruby": get_server_history("Scarlet Ruby", server, faction, num_days),
        "Bold Scarlet Ruby": get_server_history("Bold Scarlet Ruby", server, faction, num_days),
        "Runed Scarlet Ruby": get_server_history("Runed Scarlet Ruby", server, faction, num_days),
        "Monarch Topaz": get_server_history("Monarch Topaz", server, faction, num_days),
        "Durable Monarch Topaz": get_server_history("Durable Monarch Topaz", server, faction, num_days),
        "Accurate Monarch Topaz": get_server_history("Accurate Monarch Topaz", server, faction, num_days),
        "Luminous Monarch Topaz": get_server_history("Luminous Monarch Topaz", server, faction, num_days),
        "Autumns Glow": get_server_history("Autumns Glow", server, faction, num_days),
        "Mystic Autumns Glow": get_server_history("Mystic Autumns Glow", server, faction, num_days),
        "Brilliant Autumns Glow": get_server_history("Brilliant Autumns Glow", server, faction, num_days),
    }
    earth = {
        "Eternal": get_server_history("Eternal Earth", server, faction, num_days),
        "Crystallized": get_server_history("Crystallized Earth", server, faction, num_days),
    }
    de_mats = {
        "Dream Shard": get_server_history("Dream Shard", server, faction, num_days),
        "Infinite Dust": get_server_history("Infinite Dust", server, faction, num_days),
        "Greater Cosmic Essence": get_server_history("Greater Cosmic Essence", server, faction, num_days),
    }
    
    scarlet_ruby_prices = []
    for i in range( min(  len(gems["Scarlet Ruby"]["prices"]), len(gems["Bold Scarlet Ruby"]["prices"]), len(gems["Runed Scarlet Ruby"]["prices"])  ) ):
        scarlet_ruby_prices.append( (gems["Scarlet Ruby"]["prices"][i] + gems["Bold Scarlet Ruby"]["prices"][i] + gems["Runed Scarlet Ruby"]["prices"][i]) / 3 )
    monarch_topaz_prices = []
    for i in range( min(  len(gems["Monarch Topaz"]["prices"]), len(gems["Durable Monarch Topaz"]["prices"]), len(gems["Accurate Monarch Topaz"]["prices"]), len(gems["Luminous Monarch Topaz"]["prices"]) )  ):
        monarch_topaz_prices.append( (gems["Monarch Topaz"]["prices"][i] + gems["Durable Monarch Topaz"]["prices"][i] + gems["Accurate Monarch Topaz"]["prices"][i] + gems["Luminous Monarch Topaz"]["prices"][i]) / 4 )
    autumns_glow_prices = []
    for i in range( min(  len(gems["Autumns Glow"]["prices"]), len(gems["Mystic Autumns Glow"]["prices"]), len(gems["Brilliant Autumns Glow"]["prices"])  ) ):
        autumns_glow_prices.append( (gems["Autumns Glow"]["prices"][i] + gems["Mystic Autumns Glow"]["prices"][i] + gems["Brilliant Autumns Glow"]["prices"][i]) / 3 )

    crystallized_earth_prices = []
    for i in range( min(  len(earth["Crystallized"]["prices"]), len(earth["Eternal"]["prices"])  ) ):
        crystallized_earth_prices.append( (earth["Crystallized"]["prices"][i] + (earth["Eternal"]["prices"][i] / 10)) / 2 )
    
    dream_shard_prices = [ p for p in de_mats["Dream Shard"]["prices"] ]
    infinite_dust_prices = [ p for p in de_mats["Infinite Dust"]["prices"] ]
    greater_cosmic_essence_prices = [ p for p in de_mats["Greater Cosmic Essence"]["prices"] ]
    
    shortest_list = min(  len(scarlet_ruby_prices), len(monarch_topaz_prices), len(autumns_glow_prices), len(crystallized_earth_prices), len(dream_shard_prices), len(infinite_dust_prices), len(greater_cosmic_essence_prices)  )
    
    values = {
        "blueGems": [ 0.04 * (scarlet_ruby_prices[i] + autumns_glow_prices[i] + monarch_topaz_prices[i]) + 0.12*(4.5)  for i in range(shortest_list) ],
        "greenGems": [ 0.72 * ( 1.84*infinite_dust_prices[i] + 0.12*greater_cosmic_essence_prices[i] + 0.008*dream_shard_prices[i] - 2*crystallized_earth_prices[i] ) + 0.072*(1.0) + 0.0288*(0.5)  for i in range(shortest_list) ],
    }
    
    values_per_prospect = [ values["blueGems"][i] + values["greenGems"][i]  for i in range(len(values["blueGems"])) ]
    values = [ values_per_prospect[i]/5  for i in range(len(values_per_prospect)) ]     # per saronite ore
    values = [ value/100 for value in values ]  # gold -> silver
    
    values = enforce_upper_limit(values)
    values = enforce_lower_limit(values,2)
    
    saronite_ore_data = get_server_history("Saronite Ore", server, faction, num_days)
    scale = 100 if saronite_ore_data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in saronite_ore_data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    if fix_outliers:
        prices = remove_outliers(prices)
    
    prices = enforce_upper_limit(prices)
    prices = prices[-len(values):]
    
    saronite_ore_data["times"] = [time.replace(minute=0) for time in saronite_ore_data["times"]]
    saronite_ore_data["times"] = saronite_ore_data["times"][-len(prices):]
    
    saronite_data = pd.DataFrame(
        {
            "Time": saronite_ore_data["times"], ylabel: prices,
            "4-hour moving average":  pd.Series(prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(prices).rolling(12).mean(),
        }
    )
    value_data = pd.DataFrame(
        {
            "Time": saronite_ore_data["times"], ylabel: values,
            "4-hour moving average":  pd.Series(values).rolling(2).mean(),
            "12-hour moving average": pd.Series(values).rolling(6).mean(),
            "24-hour moving average": pd.Series(values).rolling(12).mean(),
        }
    )
    
    
    
    if hide_original:
        min4_prices  = min(saronite_data["4-hour moving average" ].dropna().tolist()[1:])
        min4_values  = min(value_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_prices  = max(saronite_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_values  = max(value_data["4-hour moving average" ].dropna().tolist()[1:])
        min12_prices = min(saronite_data["12-hour moving average"].dropna().tolist()[1:])
        min12_values = min(value_data["12-hour moving average"].dropna().tolist()[1:])
        max12_prices = max(saronite_data["12-hour moving average"].dropna().tolist()[1:])
        max12_values = max(value_data["12-hour moving average"].dropna().tolist()[1:])
        min24_prices = min(saronite_data["24-hour moving average"].dropna().tolist()[1:])
        min24_values = min(value_data["24-hour moving average"].dropna().tolist()[1:])
        max24_prices = max(saronite_data["24-hour moving average"].dropna().tolist()[1:])
        max24_values = max(value_data["24-hour moving average"].dropna().tolist()[1:])
        min4  = min(min4_prices,  min4_values )
        max4  = max(max4_prices,  max4_values )
        min12 = min(min12_prices, min12_values)
        max12 = max(max12_prices, max12_values)
        min24 = min(min24_prices, min24_values)
        max24 = max(max24_prices, max24_values)

        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min( min(prices), min(values) )
            maximum = max( max(prices), max(values) )
    else:
        minimum = min( min(prices), min(values) )
        maximum = max( max(prices), max(values) )
    
    try: chart_ylims = (int(minimum/1.25), int(maximum*1.2))
    except Exception as e:
        chart_ylims = (
            int(min( min(prices), min(values) )/1.25),
            int(max( max(prices), max(values) )*1.20),
        )
        st.markdown(f"**Error:** {e}")
    
    
    


    
    if not hide_original:
        chart = alt.Chart(saronite_data).mark_line(
            # color="#83c9ff" if not hide_original else "#0e1117",
            color="#3aa9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        ) + alt.Chart(value_data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",                                            #  <------ NOTE: "#ff6f83" can be changed
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        )
        chart = chart.properties(height=600)

        
    if ma4:
        if hide_original:
            chart = alt.Chart(saronite_data).mark_line(
                        # color="#7defa1",strokeWidth=2).encode(
                        color="#0ce550",strokeWidth=2).encode(
                        x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            ) + alt.Chart(value_data).mark_line(
                        color="#7defa1",strokeWidth=2).encode(                     #  <------ NOTE: "#7defa1" can be changed
                        x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            )
        else:
            chart = chart + alt.Chart(saronite_data).mark_line(
                                # color="#7defa1").encode(
                                color="#0ce550").encode(
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average")
            ) + alt.Chart(value_data).mark_line(
                                color="#7defa1").encode(                                    #  <------ NOTE: "#7defa1" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average"))
    
    
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(saronite_data).mark_line(
                                    # color="#6d3fc0",strokeWidth=2.1).encode(
                                    color="#6029c1",strokeWidth=2.1).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(value_data).mark_line(
                                    color="#9670dc",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
            else:
                chart = alt.Chart(saronite_data).mark_line(
                            # color="#6d3fc0",strokeWidth=2.1).encode(
                            color="#6029c1",strokeWidth=2.1).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(value_data).mark_line(
                            color="#9670dc",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
        else:
            chart = chart + alt.Chart(saronite_data).mark_line(
                                # color="#6d3fc0").encode(
                                color="#6029c1").encode(
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average")
            ) + alt.Chart(value_data).mark_line(
                                color="#9670dc").encode(                                    #  <------ NOTE: "#6d3fc0" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average"))

    
    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(saronite_data).mark_line(
                                    # color="#bd4043",strokeWidth=2.2).encode(
                                    color="#ba191c",strokeWidth=2.2).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(value_data).mark_line(
                                    color="#ff5169",strokeWidth=2.2).encode(                 #  <------ NOTE: "#bd4043" can be changed
                                    x=alt.X("Time", axis=alt.Axis(title="Date")),
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
            else:
                chart = alt.Chart(saronite_data).mark_line(
                            # color="#bd4043",strokeWidth=2.2).encode(
                            color="#ba191c",strokeWidth=2.2).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(value_data).mark_line(
                            color="#ff5169",strokeWidth=2.2).encode(                 #  <------ NOTE: "#ff6f83" can be changed
                            x=alt.X("Time", axis=alt.Axis(title="Date")),
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
        else:
            chart = chart + alt.Chart(saronite_data).mark_line(
                # color="#bd4043").encode(
                color="#ba191c").encode(
                x=alt.X("Time"),
                y=alt.Y("24-hour moving average")
            ) + alt.Chart(value_data).mark_line(
                color="#ff5169").encode(                                    #  <------ NOTE: "#bd4043" can be changed
                x=alt.X("Time"),
                y=alt.Y("24-hour moving average"))


    chart = chart.properties(height=600)
    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    
    
    
    
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        
        chart = chart.properties(title=f"{item} {ylabel.replace('(', '(in ')}")
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center'
        )
        
        chart = chart.properties(height=400)

    return chart

            
            
            
            
            
            
            


def plot_price_history(item: str, server: str, faction: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    data = get_server_history(item, server, faction, num_days)
    scale = 100 if data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    # run the remove_outliers function
    if fix_outliers:
        prices = remove_outliers(prices)
        
        
    upper_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  +  
        3*np.std(pd.Series(prices).rolling(2).mean().dropna().tolist()) 
    )
    
    for i in range(len(prices)):
        if prices[i] > upper_limit:
            prices[i] = upper_limit
        

    data = pd.DataFrame(
        {
            "Time": data["times"], ylabel: prices,
            "4-hour moving average":  pd.Series(prices).rolling(2).mean().round(2),
            "12-hour moving average": pd.Series(prices).rolling(6).mean().round(2),
            "24-hour moving average": pd.Series(prices).rolling(12).mean().round(2),
        }
    )
    
 
    
    if hide_original:
        min4  = min(data["4-hour moving average" ].dropna().tolist()[1:])
        max4  = max(data["4-hour moving average" ].dropna().tolist()[1:])
        min12 = min(data["12-hour moving average"].dropna().tolist()[1:])
        max12 = max(data["12-hour moving average"].dropna().tolist()[1:])
        min24 = min(data["24-hour moving average"].dropna().tolist()[1:])
        max24 = max(data["24-hour moving average"].dropna().tolist()[1:])
        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min(prices)
            maximum = max(prices)
    else:
        minimum = min(prices)
        maximum = max(prices)
        
    try: chart_ylims = (int(minimum/1.25), int(maximum*1.2))
    except Exception as e:
        chart_ylims = (int(min(prices)/1.25), int(max(prices)*1.2))
        st.markdown(f"**Error:** {e}")
        st.markdown(f"**min4  = ** {min(data['4-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max4  = ** {max(data['4-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**min12 = ** {min(data['12-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max12 = ** {max(data['12-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**min24 = ** {min(data['24-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max24 = ** {max(data['24-hour moving average'].dropna().tolist()[1:])}")
        
        
    
    # fix the issue with chart y-limit scaling when
    # the price of something is barely over a gold (saronite ore)
    if minimum < 1 and maximum < 2 and scale != 100:
        try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))
        except: pass
        
        

    XAXIS_DATETIME_FORMAT = ( "%b %d" )
        
    if not hide_original:
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover = mouseover_line(data=data, color="#83c9ff", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0.0)
        
        chart = alt.Chart(data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(  title="Date", format=XAXIS_DATETIME_FORMAT  )),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        )
        chart = chart + price_line_mouseover
        chart = chart.properties(height=600)

    if ma4:
        if hide_original:
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover = mouseover_line(data=data, color="#7defa1", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0.0)
            chart = alt.Chart(data).mark_area(fill='red', opacity=0, strokeWidth=2, clip=True, line=True).encode(
                        color=alt.value("#7defa1"),
                        x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))) + price_line_mouseover
        else:
            chart = chart + alt.Chart(data).mark_line(color="#7defa1").encode(x=alt.X("Time"), y=alt.Y("4-hour moving average"))
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(data).mark_area(fill='red', opacity=0, strokeWidth=2, clip=True, line=True).encode(
                                    color=alt.value("#6d3fc0"),
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
#                 chart = chart + alt.Chart(data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
#                                     x=alt.X("Time", axis=alt.Axis(  title="Date", format=XAXIS_DATETIME_FORMAT  )), 
#                                     y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
            else:
                chart = alt.Chart(data).mark_area(fill='red', opacity=0, strokeWidth=2, clip=True, line=True).encode(
                            color=alt.value("#6d3fc0"),
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
#                 chart = alt.Chart(data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
#                         x=alt.X("Time", axis=alt.Axis(  title="Date", format=XAXIS_DATETIME_FORMAT  )), 
#                         y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
        else:
            chart = chart + alt.Chart(data).mark_line(color="#6d3fc0").encode(x=alt.X("Time"), y=alt.Y("12-hour moving average"))
    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
                                    x=alt.X("Time", axis=alt.Axis(  title="Date", format=XAXIS_DATETIME_FORMAT  )), 
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
            else:
                chart = alt.Chart(data).mark_area(fill='red', opacity=0, strokeWidth=2, clip=True, line=True).encode(
                            color=alt.value("#bd4043"),
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
#                 chart = alt.Chart(data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
#                             x=alt.X("Time", axis=alt.Axis(  title="Date", format=XAXIS_DATETIME_FORMAT  )), 
#                             y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
        else:
            chart = chart + alt.Chart(data).mark_line(color="#bd4043").encode(x=alt.X("Time"), y=alt.Y("24-hour moving average"))
    

    
    
    
    def mouseover_stuff(line: alt.Chart) -> alt.Chart:
        nearest = alt.selection(
            type="single",
            nearest=True,
            on="mouseover",
            fields=["Time"],
            empty="none",
        )
        selectors = alt.Chart(data).mark_point().encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            opacity=alt.value(0),
        ).add_selection(nearest)
        points = line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )
        text = line.mark_text(align="left", dx=5, dy=-5, color="#ffffff").encode(
            text=alt.condition(nearest, ylabel, alt.value(' '))
        )
        rules = alt.Chart(data).mark_rule(color="gray").encode(
            x="Time",
        ).transform_filter(nearest)
        return alt.layer(area, line, selectors, points, rules, text)
    
    

    
    

    chart = chart.properties(height=600)

    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",  tickOpacity=0.9,
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        
        chart = chart.properties(title=f"{item} {ylabel.replace('(', '(in ')}")
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center'
        )
        
        chart = chart.properties(height=400)
    
    
#     TEXT   = lambda t: st.markdown(t)
#     SMALL  = lambda t: st.markdown(f"### {t}")
#     MEDIUM = lambda t: st.markdown( f"## {t}")
#     LARGE  = lambda t: st.markdown(  f"# {t}")
    
    return chart










def plot_price_and_quantity_history(item: str, server: str, faction: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    data = get_server_history(item, server, faction, num_days)
    scale = 100 if data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    if fix_outliers:
        prices = remove_outliers(prices)
        
    
    upper_limit  =  (
        np.mean(pd.Series(prices).rolling(2).mean().dropna().tolist())  +  
        3*np.std(pd.Series(prices).rolling(2).mean().dropna().tolist()) 
    )
    
    for i in range(len(prices)):
        if prices[i] > upper_limit:
            prices[i] = upper_limit
    
    
    data = pd.DataFrame(
        {
            "Time": data["times"], ylabel: prices,
            "Quantity": data["quantities"],
            "Quantity  4hMA": pd.Series(data["quantities"]).rolling( 2).mean(),
            "Quantity 12hMA": pd.Series(data["quantities"]).rolling( 6).mean(),
            "Quantity 24hMA": pd.Series(data["quantities"]).rolling(12).mean(),
            "4-hour moving average":  pd.Series(prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(prices).rolling(12).mean().round(2),
            "4h Avg Quantity":  pd.Series(data["quantities"]).rolling( 2).mean().dropna().apply(lambda x: int(x)),
            "12h Avg Quantity": pd.Series(data["quantities"]).rolling( 6).mean().dropna().apply(lambda x: int(x)),
            "24h Avg Quantity": pd.Series(data["quantities"]).rolling(12).mean().dropna().apply(lambda x: int(x)),
        }
    )
    
    

    
#     base = alt.Chart(data).encode(x="Time")
#     bar = base.mark_bar().encode(y="Quantity")
#     line = base.mark_line(color="red").encode(y=ylabel)
#     if not hide_original:
#         base = alt.Chart(data).encode(x="Time")
#         bar = base.mark_bar().encode(y="Quantity")
#         line = base.mark_line(color="red").encode(y=ylabel)
#     if ma4:
#         base = alt.Chart(data).encode(x="Time")
#         bar = base.mark_bar().encode(y="Quantity 4hMA")
#         line = base.mark_line(color="red").encode(y="4-hour moving average")
#     if ma12:
#         base = alt.Chart(data).encode(x="Time")
#         bar = base.mark_bar().encode(y="Quantity 12hMA")
#         line = base.mark_line(color="red").encode(y="12-hour moving average")
#     if ma24:
#         base = alt.Chart(data).encode(x="Time")
#         bar = base.mark_bar().encode(y="Quantity 24hMA")
#         line = base.mark_line(color="red").encode(y="24-hour moving average")
#     chart = (bar + line).properties(height=600)
#     return chart


    if hide_original:
        min4  = min(data["4-hour moving average" ].dropna().tolist()[1:])
        max4  = max(data["4-hour moving average" ].dropna().tolist()[1:])
        min12 = min(data["12-hour moving average"].dropna().tolist()[1:])
        max12 = max(data["12-hour moving average"].dropna().tolist()[1:])
        min24 = min(data["24-hour moving average"].dropna().tolist()[1:])
        max24 = max(data["24-hour moving average"].dropna().tolist()[1:])
        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min(prices)
            maximum = max(prices)
    else:
        minimum = min(prices)
        maximum = max(prices)
    
    
    try: chart_ylims = (int(minimum/1.25), int(maximum*1.1))
    except Exception as e:
        chart_ylims = (
            int(min(prices)/1.25),
            int(max(prices)*1.10),
        )
        st.markdown(f"**Error:** {e}")
    
    
    # fix the issue with chart y-limit scaling when
    # the price of something is barely over a gold (saronite ore)
    if minimum < 1 and maximum < 2 and scale != 100:
        try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))
        except: pass
    
    
    if not hide_original:
        range_quantity = [data["Quantity"].min(), data["Quantity"].max()]
        data["Quantity"] = data["Quantity"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
    if ma4:
        range_quantity = [data["Quantity  4hMA"].min(), data["Quantity  4hMA"].max()]
        data["Quantity  4hMA"] = data["Quantity  4hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
    if ma12:
        range_quantity = [data["Quantity 12hMA"].min(), data["Quantity 12hMA"].max()]
        data["Quantity 12hMA"] = data["Quantity 12hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
    if ma24:
        range_quantity = [data["Quantity 24hMA"].min(), data["Quantity 24hMA"].max()]
        data["Quantity 24hMA"] = data["Quantity 24hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
    
    
    
    XAXIS_DATETIME_FORMAT = ( "%b %d" )
    
    
    if not hide_original:
        price_line = alt.Chart(data).mark_line(
            color="#3aa9ff",
            strokeWidth = 2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
        )
        quantity_line = alt.Chart(data).mark_area(
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#83c9ff", offset=0),     # bottom color
                       alt.GradientStop(color="#0068c9", offset=1)],  # top color
                x1=1, x2=1, y1=1, y2=0,
            ),
            opacity = 0.5,
            strokeWidth=2,
            interpolate="monotone",
            clip=True,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("Quantity", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
        )
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover = mouseover_line(data=data, color="#3aa9ff", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        chart = quantity_line + price_line + price_line_mouseover
        chart = chart.properties(height=600)
            
        
    if ma4:
        price_line_ma4 = alt.Chart(data).mark_line(
            color="#0ce550",
            strokeWidth = 2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "4-hour moving average"],
        )
        quantity_line_ma4 = alt.Chart(data).mark_area(
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#7defa1", offset=0),     # bottom color
                       alt.GradientStop(color="#29b09d", offset=0.4)],  # top color
                x1=1, x2=1, y1=1, y2=0,
            ),
            opacity = 0.5,
            strokeWidth=2,
            interpolate="monotone",
            clip=True,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("Quantity  4hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "4h Avg Quantity"]
        )
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover = mouseover_line(data=data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        if hide_original:
#             chart = quantity_line_ma4 + price_line_ma4
            chart = quantity_line_ma4 + price_line_ma4 + price_line_mouseover
        else:
#             chart = chart + quantity_line_ma4 + price_line_ma4
            chart = chart + quantity_line_ma4 + price_line_ma4 + price_line_mouseover
    

    if ma12:
        price_line_ma12 = alt.Chart(data).mark_line(
            color = "#6029c1",
            strokeWidth = 2.1,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "12-hour moving average"],
        )
        
        
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_ma12_mouseover = alt.Chart(data).mark_line(
            color = "#6029c1",
            strokeWidth = MOUSEOVER_LINE_THICKNESS,
            opacity = 0,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
#             tooltip=["Time", "12-hour moving average"],
#             tooltip=[alt.Tooltip("Time",title="Time",format=("%b %d  %I %p")), alt.Tooltip("12-hour moving average",title="Price (12h avg)",format=".2f")],
            tooltip=(
              [alt.Tooltip("Time",title="Time",format=("%b %d, %I %p")), alt.Tooltip("12-hour moving average",title="Price (12h avg)",format=".2f")] if
              scale!=100 else [alt.Tooltip("Time",title="Time",format=("%b %d, %I %p")), alt.Tooltip("12-hour moving average",title="Price (12h avg)",format=".0f")]
            ),
        )
#         price_line_ma12_shadow = alt.Chart(data).mark_line(
#             color = "#CCCCCC",
#             strokeWidth = 4.1,
#             opacity = 0.1,
#         ).encode(
#             x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
#             y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
#             tooltip=["Time", "12-hour moving average"],
#         )
        
        
        quantity_line_ma12 = alt.Chart(data).mark_area(
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#9670dc", offset=0.3),     # bottom color
                       alt.GradientStop(color="#5728ae", offset=0.7)],  # top color
                x1=1, x2=1, y1=1, y2=0,
            ),
            opacity = 0.5,
            strokeWidth=1,
            interpolate="monotone",
            clip=True,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("Quantity 12hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "12h Avg Quantity"],
#             tooltip=alt.Tooltip(["Time", "12h Avg Quantity"], title="Asdf", format=".0f")
        )
#         ).interactive()
        if hide_original:
            if ma4:
                chart = chart + quantity_line_ma12 + price_line_ma12 + price_line_ma12_mouseover
            else:
                chart = quantity_line_ma12 + price_line_ma12 + price_line_ma12_mouseover
        else:
            chart = chart + quantity_line_ma12 + price_line_ma12 + price_line_ma12_mouseover
    
    
    if ma24:
        price_line_ma24 = alt.Chart(data).mark_line(
            color = "#ba191c",
            strokeWidth = 2.2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "24-hour moving average"],
        )
        quantity_line_ma24 = alt.Chart(data).mark_area(
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#ff5169", offset=0),     # bottom color
                       alt.GradientStop(color="#d71b35", offset=0.4)],  # top color
                x1=1, x2=1, y1=1, y2=0,
            ),
            opacity = 0.5,
            strokeWidth=2.2,
            interpolate="monotone",
            clip=True,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("Quantity 24hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
            tooltip=["Time", "24h Avg Quantity"]
        )
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover = mouseover_line(data=data, color="#ba191c", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        if hide_original:
            if ma4 or ma12:
#                 chart = chart + quantity_line_ma24 + price_line_ma24
                chart = chart + quantity_line_ma24 + price_line_ma24 + price_line_mouseover
            else:
#                 chart = quantity_line_ma24 + price_line_ma24
                chart = quantity_line_ma24 + price_line_ma24 + price_line_mouseover
        else:
#             chart = chart + quantity_line_ma24 + price_line_ma24
            chart = chart + quantity_line_ma24 + price_line_ma24 + price_line_mouseover


    chart = chart.properties(height=600)
    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        
        chart = chart.properties(title=f"{item} {ylabel.replace('(', '(in ')}")
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center'
        )
        
        chart = chart.properties(height=400)

    return chart










def plot_price_and_region_history(item: str, server: str, faction: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    server_data = get_server_history(item, server, faction, num_days)
    region_data = get_region_history(item, numDays=num_days)
    if server_data["prices"][-1] < 10000 or region_data["prices"][-1] < 10000:
        scale = 100
    else: scale = 10000
    # scale = 100 if server_data["prices"][-1] < 10000 else 10000
    server_prices = [round(price/scale,2) for price in server_data["prices"]]
    region_prices = [round(price/scale,2) for price in region_data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"

    # set the minute to 0 for all times to ensure they are the same
    server_data["times"] = [time.replace(minute=0) for time in server_data["times"]]
    region_data["times"] = [time.replace(minute=0) for time in region_data["times"]]


    # run the remove_outliers function on both price lists
    if fix_outliers:
        server_prices = remove_outliers(server_prices)
        region_prices = remove_outliers(region_prices)
        
        
        
    server_std_mean = np.mean( pd.Series(server_prices).rolling(2).mean().dropna().tolist() )
    region_std_mean = np.mean( pd.Series(region_prices).rolling(2).mean().dropna().tolist() )
    
    server_std_dev = np.std( pd.Series(server_prices).rolling(2).mean().dropna().tolist() )
    region_std_dev = np.std( pd.Series(region_prices).rolling(2).mean().dropna().tolist() )
        
    std_dev = min(server_std_dev, region_std_dev)
    server_upper_limit  =  server_std_mean + 3*std_dev
    region_upper_limit  =  region_std_mean + 3*std_dev
    
    for i in range(len(server_prices)):
        if server_prices[i] > server_upper_limit:
            server_prices[i] = server_upper_limit
            
    for i in range(len(region_prices)):
        if region_prices[i] > region_upper_limit:
            region_prices[i] = region_upper_limit
        
        
        
#     server_upper_limit  =  (
#         np.mean(pd.Series(server_prices).rolling(2).mean().dropna().tolist())  +  
#         3*np.std(pd.Series(server_prices).rolling(2).mean().dropna().tolist()) 
#     )
    
#     for i in range(len(server_prices)):
#         if server_prices[i] > server_upper_limit:
#             server_prices[i] = server_upper_limit
            
            
#     region_upper_limit  =  (
#         np.mean(pd.Series(region_prices).rolling(2).mean().dropna().tolist())  +  
#         3*np.std(pd.Series(region_prices).rolling(2).mean().dropna().tolist()) 
#     )
    
#     for i in range(len(region_prices)):
#         if region_prices[i] > region_upper_limit:
#             region_prices[i] = region_upper_limit
    


    ###  MIGHT BE ABLE TO GET RID OF ALL THIS LENGTH CHECKING STUFF  ###

#     last_time_server = server_data["times"][-1]
#     last_time_region = region_data["times"][-1]

#     if last_time_server != last_time_region:
#         if last_time_server > last_time_region:         # the server_data time is later, so remove the last element of server_data
#             server_prices = server_prices[:-1]
#             server_data["times"] = server_data["times"][:-1]
#         elif last_time_server < last_time_region:       # the region_data time is later, so remove the last element of region_data
#             region_prices = region_prices[:-1]
#             region_data["times"] = region_data["times"][:-1]

#     # check that the lengths of the two lists are the same
#     if len(server_data["times"]) != len(region_data["times"]):
#         if len(server_data["times"]) > len(region_data["times"]):
#             diff_len = len(server_data["times"]) - len(region_data["times"])
#             server_data["times"] = server_data["times"][diff_len:]
#             server_prices = server_prices[diff_len:]
#         elif len(server_data["times"]) < len(region_data["times"]):
#             diff_len = len(region_data["times"]) - len(server_data["times"])
#             region_data["times"] = region_data["times"][diff_len:]
#             region_prices = region_prices[diff_len:]
            
    ####################################################################




    server_data = pd.DataFrame(
        {
            "Time": server_data["times"], ylabel: server_prices,
            "4-hour moving average":  pd.Series(server_prices).rolling(2).mean().round(2),
            "12-hour moving average": pd.Series(server_prices).rolling(6).mean().round(2),
            "24-hour moving average": pd.Series(server_prices).rolling(12).mean().round(2),
        }
    )
    region_data = pd.DataFrame(
        {
            "Time": region_data["times"], ylabel: region_prices,
            "4-hour moving average":  pd.Series(region_prices).rolling(2).mean().round(2),
            "12-hour moving average": pd.Series(region_prices).rolling(6).mean().round(2),
            "24-hour moving average": pd.Series(region_prices).rolling(12).mean().round(2),
        }
    )

    # make sure server_data and region_data have the same number of rows
    #if len(server_data) > len(region_data):
    #    server_data = server_data.iloc[-len(region_data):]
    #elif len(region_data) > len(server_data):
    #    aregion_data = region_data.iloc[-len(server_data):]

    
    if hide_original:
        min4_server  = min(server_data["4-hour moving average" ].dropna().tolist()[1:])
        min4_region  = min(region_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_server  = max(server_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_region  = max(region_data["4-hour moving average" ].dropna().tolist()[1:])
        min12_server = min(server_data["12-hour moving average"].dropna().tolist()[1:])
        min12_region = min(region_data["12-hour moving average"].dropna().tolist()[1:])
        max12_server = max(server_data["12-hour moving average"].dropna().tolist()[1:])
        max12_region = max(region_data["12-hour moving average"].dropna().tolist()[1:])
        min24_server = min(server_data["24-hour moving average"].dropna().tolist()[1:])
        min24_region = min(region_data["24-hour moving average"].dropna().tolist()[1:])
        max24_server = max(server_data["24-hour moving average"].dropna().tolist()[1:])
        max24_region = max(region_data["24-hour moving average"].dropna().tolist()[1:])
        min4  = min(min4_server,  min4_region )
        max4  = max(max4_server,  max4_region )
        min12 = min(min12_server, min12_region)
        max12 = max(max12_server, max12_region)
        min24 = min(min24_server, min24_region)
        max24 = max(max24_server, max24_region)

        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min( min(server_prices), min(region_prices) )
            maximum = max( max(server_prices), max(region_prices) )
    else:
        minimum = min( min(server_prices), min(region_prices) )
        maximum = max( max(server_prices), max(region_prices) )
    
    
    try: chart_ylims = (int(minimum/1.25), int(maximum*1.2))
    except Exception as e:
        chart_ylims = (
            int(min( min(server_prices), min(region_prices) )/1.25),
            int(max( max(server_prices), max(region_prices) )*1.20),
        )
        st.markdown(f"**Error:** {e}")
        # st.markdown(f"**min4  = ** {min(data['4-hour moving average'].dropna().tolist()[1:])}")
        # st.markdown(f"**max4  = ** {max(data['4-hour moving average'].dropna().tolist()[1:])}")
        # st.markdown(f"**min12 = ** {min(data['12-hour moving average'].dropna().tolist()[1:])}")
        # st.markdown(f"**max12 = ** {max(data['12-hour moving average'].dropna().tolist()[1:])}")
        # st.markdown(f"**min24 = ** {min(data['24-hour moving average'].dropna().tolist()[1:])}")
        # st.markdown(f"**max24 = ** {max(data['24-hour moving average'].dropna().tolist()[1:])}")
        
        
        
        
    # fix the issue with chart y-limit scaling when
    # the price of something is barely over a gold (saronite ore)
    if minimum < 1 and maximum < 2 and scale != 100:
        try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))
        except: pass
        
        
    

    # if not hide_original:
    #     ... server = #83c9ff, region = #ff6f83
    # if ma4:
    #     if hide_original:
    #         ... server = #7defa1, region = #7defa1 (#ff8700)
    #     else:
    #         ... server = #7defa1, region = #7defa1 (#ff8700)
    # if ma12:
    #     if hide_original:
    #         # if ma4:
    #               ... server = #6d3fc0, region = #6d3fc0
    #         # else:
    #               ... server = #6d3fc0, region = #6d3fc0
    #     else:
    #         ... server = #6d3fc0, region = #6d3fc0
    # if ma24:
    #     if hide_original:
    #         # if ma4 or ma12:
    #               ... server = #bd4043, region = #bd4043
    #         # else:
    #               ... server = #bd4043, region = #bd4043
    #     else:
    #         ... server = #bd4043, region = #bd4043

    # For the following colors, the region price is always the lighter-shade version of any two colors

    
    XAXIS_DATETIME_FORMAT = ( "%b %d" )
    
    
    if not hide_original:
        chart = alt.Chart(server_data).mark_line(
            # color="#83c9ff" if not hide_original else "#0e1117",
            color="#3aa9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
#             x=alt.X("Time", axis=alt.Axis(title="Date")),
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        ) + alt.Chart(region_data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",                                            #  <------ NOTE: "#ff6f83" can be changed
            strokeWidth=2,
        ).encode(
#             x=alt.X("Time", axis=alt.Axis(title="Date")),
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        )
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        chart = chart + price_line_mouseover1 + price_line_mouseover2
        chart = chart.properties(height=600)

        
    if ma4:
        if hide_original:
            chart = alt.Chart(server_data).mark_line(
                        # color="#7defa1",strokeWidth=2).encode(
                        color="#0ce550",strokeWidth=2).encode(
#                         x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            ) + alt.Chart(region_data).mark_line(
                        color="#7defa1",strokeWidth=2).encode(                     #  <------ NOTE: "#7defa1" can be changed
#                         x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            )
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server_data).mark_line(
                                # color="#7defa1").encode(
                                color="#0ce550").encode(
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average")
            ) + alt.Chart(region_data).mark_line(
                                color="#7defa1").encode(                                    #  <------ NOTE: "#7defa1" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
    
    
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(server_data).mark_line(
                                    # color="#6d3fc0",strokeWidth=2.1).encode(
                                    color="#6029c1",strokeWidth=2.1).encode(
#                                     x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(
                                    color="#9670dc",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
#                                     x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
            else:
                chart = alt.Chart(server_data).mark_line(
                            # color="#6d3fc0",strokeWidth=2.1).encode(
                            color="#6029c1",strokeWidth=2.1).encode(
#                             x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(
                            color="#9670dc",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
#                             x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server_data).mark_line(
                                # color="#6d3fc0").encode(
                                color="#6029c1").encode(
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average")
            ) + alt.Chart(region_data).mark_line(
                                color="#9670dc").encode(                                    #  <------ NOTE: "#6d3fc0" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2

    
    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(server_data).mark_line(
                                    # color="#bd4043",strokeWidth=2.2).encode(
                                    color="#ba191c",strokeWidth=2.2).encode(
#                                     x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(
                                    color="#ff5169",strokeWidth=2.2).encode(                 #  <------ NOTE: "#bd4043" can be changed
#                                     x=alt.X("Time", axis=alt.Axis(title="Date")),
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
            else:
                chart = alt.Chart(server_data).mark_line(
                            # color="#bd4043",strokeWidth=2.2).encode(
                            color="#ba191c",strokeWidth=2.2).encode(
#                             x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(
                            color="#ff5169",strokeWidth=2.2).encode(                 #  <------ NOTE: "#ff6f83" can be changed
#                             x=alt.X("Time", axis=alt.Axis(title="Date")),
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server_data).mark_line(
                # color="#bd4043").encode(
                color="#ba191c").encode(
                x=alt.X("Time"),
                y=alt.Y("24-hour moving average")
            ) + alt.Chart(region_data).mark_line(
                color="#ff5169").encode(                                    #  <------ NOTE: "#bd4043" can be changed
                x=alt.X("Time"),
                y=alt.Y("24-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=region_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2


    chart = chart.properties(height=600)
    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    
    
    
    
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        
        chart = chart.properties(title=f"{item} {ylabel.replace('(', '(in ')}")
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center'
        )
        
        chart = chart.properties(height=400)

    return chart










def plot_price_history_comparison(item: str, server1: str, faction1: str, server2: str, faction2: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    server1_data = get_server_history(item, server1, faction1, num_days)
    server2_data = get_server_history(item, server2, faction2, num_days)
    if server1_data["prices"][-1] < 10000 or server2_data["prices"][-1] < 10000:
        scale = 100
    else: scale = 10000
    server1_prices = [round(price/scale,2) for price in server1_data["prices"]]
    server2_prices = [round(price/scale,2) for price in server2_data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    # set the minute to 0 for all times to ensure they are the same
    server1_data["times"] = [time.replace(minute=0) for time in server1_data["times"]]
    server2_data["times"] = [time.replace(minute=0) for time in server2_data["times"]]

    # run the remove_outliers function on both price lists
    if fix_outliers:
        server1_prices = remove_outliers(server1_prices)
        server2_prices = remove_outliers(server2_prices)
    
    
    
    upper_limit1  =  (
        np.mean(pd.Series(server1_prices).rolling(2).mean().dropna().tolist())  +  
        3*np.std(pd.Series(server1_prices).rolling(2).mean().dropna().tolist()) 
    )
    for i in range(len(server1_prices)):
        if server1_prices[i] > upper_limit1:
            server1_prices[i] = upper_limit1
    
    
    upper_limit2  =  (
        np.mean(pd.Series(server2_prices).rolling(2).mean().dropna().tolist())  +  
        3*np.std(pd.Series(server2_prices).rolling(2).mean().dropna().tolist()) 
    )
    for i in range(len(server2_prices)):
        if server2_prices[i] > upper_limit2:
            server2_prices[i] = upper_limit2
    
    
    
    
    server1_data = pd.DataFrame(
        {
            "Time": server1_data["times"], ylabel: server1_prices,
            "4-hour moving average":  pd.Series(server1_prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(server1_prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(server1_prices).rolling(12).mean(),
        }
    )
    server2_data = pd.DataFrame(
        {
            "Time": server2_data["times"], ylabel: server2_prices,
            "4-hour moving average":  pd.Series(server2_prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(server2_prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(server2_prices).rolling(12).mean(),
        }
    )


    if hide_original:
        min4_server1  = min(server1_data["4-hour moving average" ].dropna().tolist()[1:])
        min4_server2  = min(server2_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_server1  = max(server1_data["4-hour moving average" ].dropna().tolist()[1:])
        max4_server2  = max(server2_data["4-hour moving average" ].dropna().tolist()[1:])
        min12_server1 = min(server1_data["12-hour moving average"].dropna().tolist()[1:])
        min12_server2 = min(server2_data["12-hour moving average"].dropna().tolist()[1:])
        max12_server1 = max(server1_data["12-hour moving average"].dropna().tolist()[1:])
        max12_server2 = max(server2_data["12-hour moving average"].dropna().tolist()[1:])
        min24_server1 = min(server1_data["24-hour moving average"].dropna().tolist()[1:])
        min24_server2 = min(server2_data["24-hour moving average"].dropna().tolist()[1:])
        max24_server1 = max(server1_data["24-hour moving average"].dropna().tolist()[1:])
        max24_server2 = max(server2_data["24-hour moving average"].dropna().tolist()[1:])
        
        min4  = min(min4_server1 ,  min4_server2)
        max4  = max(max4_server1 ,  max4_server2)
        min12 = min(min12_server1, min12_server2)
        max12 = max(max12_server1, max12_server2)
        min24 = min(min24_server1, min24_server2)
        max24 = max(max24_server1, max24_server2)

        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min( min(server1_prices), min(server2_prices) )
            maximum = max( max(server1_prices), max(server2_prices) )
    else:
        minimum = min( min(server1_prices), min(server2_prices) )
        maximum = max( max(server1_prices), max(server2_prices) )


    try: chart_ylims = (int(minimum/1.25), int(maximum*1.2))
    except Exception as e:
        chart_ylims = (
            int(min( min(server1_prices), min(server2_prices) )/1.25),
            int(max( max(server1_prices), max(server2_prices) )*1.20),
        )
        st.markdown(f"**Error:** {e}")
        
        
    XAXIS_DATETIME_FORMAT = ( "%b %d" )


    if not hide_original:
        chart = alt.Chart(server1_data).mark_line(
            color="#3aa9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
#             x = alt.X("Time", axis=alt.Axis(title="Date")),
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y = alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale = alt.Scale(domain=chart_ylims))
        ) + alt.Chart(server2_data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
#             x = alt.X("Time", axis=alt.Axis(title="Date")),
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y = alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale = alt.Scale(domain=chart_ylims))
        )
        # make a second price line but with zero opacity
        # to assist in tooltip visibility when mousing over
        price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label=ylabel, yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
        chart = chart + price_line_mouseover1 + price_line_mouseover2
        chart = chart.properties(height=600)

        
    if ma4:
        if hide_original:
            chart = alt.Chart(server1_data).mark_line(
                        color="#0ce550",strokeWidth=2).encode(
#                         x = alt.X("Time", axis=alt.Axis(title="Date")), 
                        x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                        y = alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
            ) + alt.Chart(server2_data).mark_line(
                        color="#7defa1",strokeWidth=2).encode(
#                         x = alt.X("Time", axis=alt.Axis(title="Date")), 
                        x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                        y = alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
            )
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server1_data).mark_line(
                                color="#0ce550").encode(
                                x = alt.X("Time"),
                                y = alt.Y("4-hour moving average")
            ) + alt.Chart(server2_data).mark_line(
                                color="#7defa1").encode(
                                x = alt.X("Time"),
                                y = alt.Y("4-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="4-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
    
    
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(server1_data).mark_line(
                                    color="#6029c1",strokeWidth=2.1).encode(
#                                     x = alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y = alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                ) + alt.Chart(server2_data).mark_line(
                                    color="#9670dc",strokeWidth=2.1).encode(
#                                     x = alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y = alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
            else:
                chart = alt.Chart(server1_data).mark_line(
                            color="#6029c1",strokeWidth=2.1).encode(
#                             x = alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y = alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                ) + alt.Chart(server2_data).mark_line(
                            color="#9670dc",strokeWidth=2.1).encode(
#                             x = alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y = alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server1_data).mark_line(
                                color="#6029c1").encode(
                                x = alt.X("Time"),
                                y = alt.Y("12-hour moving average")
            ) + alt.Chart(server2_data).mark_line(
                                color="#9670dc").encode(
                                x = alt.X("Time"),
                                y = alt.Y("12-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="12-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
    
    
    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(server1_data).mark_line(
                                    color="#ba191c",strokeWidth=2.2).encode(
#                                     x = alt.X("Time", axis=alt.Axis(title="Date")), 
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y = alt.Y("24-hour moving average", axis = alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                ) + alt.Chart(server2_data).mark_line(
                                    color="#ff5169",strokeWidth=2.2).encode(
#                                     x = alt.X("Time", axis=alt.Axis(title="Date")),
                                    x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                                    y = alt.Y("24-hour moving average", axis = alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
            else:
                chart = alt.Chart(server1_data).mark_line(
                            color="#ba191c",strokeWidth=2.2).encode(
#                             x = alt.X("Time", axis=alt.Axis(title="Date")), 
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y = alt.Y("24-hour moving average", axis = alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                ) + alt.Chart(server2_data).mark_line(
                            color="#ff5169",strokeWidth=2.2).encode(
#                             x = alt.X("Time", axis=alt.Axis(title="Date")),
                            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                            y = alt.Y("24-hour moving average", axis = alt.Axis(title=ylabel), scale = alt.Scale(domain=chart_ylims))
                )
                # make a second price line but with zero opacity
                # to assist in tooltip visibility when mousing over
                price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
                chart = chart + price_line_mouseover1 + price_line_mouseover2
        else:
            chart = chart + alt.Chart(server1_data).mark_line(
                color="#ba191c").encode(
                x = alt.X("Time"),
                y = alt.Y("24-hour moving average")
            ) + alt.Chart(server2_data).mark_line(
                color="#ff5169").encode(
                x = alt.X("Time"),
                y = alt.Y("24-hour moving average"))
            # make a second price line but with zero opacity
            # to assist in tooltip visibility when mousing over
            price_line_mouseover1 = mouseover_line(data=server1_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            price_line_mouseover2 = mouseover_line(data=server2_data, color="#0ce550", y_label="24-hour moving average", yaxis_title=ylabel, chart_ylimits=chart_ylims, opacity=0)
            chart = chart + price_line_mouseover1 + price_line_mouseover2
    
    
    chart = chart.properties(
        height=600,
    )
    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        chart = chart.properties(
            title=f"{item} {ylabel.replace('(', '(in ')}",
        )
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center',
        )
        chart = chart.properties(
            height=400,
        )

    
    return chart
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
def plot_price_and_mats_history(item: str, server: str, faction: str, num_days: int, ma4: bool, ma12: bool, ma24: bool, hide_original: bool, mobile: bool, fix_outliers = False) -> alt.Chart:
    data = get_server_history(item, server, faction, num_days)
    scale = 100 if data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    icethorn_data = get_server_history("Icethorn", server, faction, num_days)
    lichbloom_data = get_server_history("Lichbloom", server, faction, num_days)
    frostlotus_data = get_server_history("Frost Lotus", server, faction, num_days)
    enchanted_vial = 9000 # copper
    
    crafting_prices = icethorn_data["prices"] + lichbloom_data["prices"] + frostlotus_data["prices"] + 9000
    crafting_prices = [round(crafting_price/scale,2) for crafting_price in crafting_prices]
    
    # run the remove_outliers function
    if fix_outliers:
        prices = remove_outliers(prices)

    data = pd.DataFrame(
        {
            "Time": data["times"], ylabel: prices,
            "4-hour moving average":  pd.Series(prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(prices).rolling(12).mean(),
        }
    )
    
    mat_data = pd.DataFrame(
        {
            "Time": data["times"], ylabel: crafting_prices,
            "4-hour moving average":  pd.Series(crafting_prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(crafting_prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(crafting_prices).rolling(12).mean(),
        }
    )

    if hide_original:
        min4  = min(data["4-hour moving average" ].dropna().tolist()[1:])
        max4  = max(data["4-hour moving average" ].dropna().tolist()[1:])
        min12 = min(data["12-hour moving average"].dropna().tolist()[1:])
        max12 = max(data["12-hour moving average"].dropna().tolist()[1:])
        min24 = min(data["24-hour moving average"].dropna().tolist()[1:])
        max24 = max(data["24-hour moving average"].dropna().tolist()[1:])
        if ma4 and not ma12 and not ma24:
            minimum = min4
            maximum = max4
        elif ma12 and not ma4 and not ma24:
            minimum = min12
            maximum = max12
        elif ma24 and not ma4 and not ma12:
            minimum = min24
            maximum = max24
        elif ma4 and ma12 and not ma24:
            minimum = min(min4, min12)
            maximum = max(max4, max12)
        elif ma4 and ma24 and not ma12:
            minimum = min(min4, min24)
            maximum = max(max4, max24)
        elif ma12 and ma24 and not ma4:
            minimum = min(min12, min24)
            maximum = max(max12, max24)
        elif ma4 and ma12 and ma24:
            minimum = min(min4, min12, min24)
            maximum = max(max4, max12, max24)
        else:
            minimum = min(prices)
            maximum = max(prices)
    else:
        minimum = min(prices)
        maximum = max(prices)
        
    try: chart_ylims = (int(minimum/1.25), int(maximum*1.2))
    except Exception as e:
        chart_ylims = (int(min(prices)/1.25), int(max(prices)*1.2))
        st.markdown(f"**Error:** {e}")
        st.markdown(f"**min4  = ** {min(data['4-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max4  = ** {max(data['4-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**min12 = ** {min(data['12-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max12 = ** {max(data['12-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**min24 = ** {min(data['24-hour moving average'].dropna().tolist()[1:])}")
        st.markdown(f"**max24 = ** {max(data['24-hour moving average'].dropna().tolist()[1:])}")



    if not hide_original:
        chart = alt.Chart(data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        )
        chart = chart.properties(height=600)

    if ma4:
        if hide_original:
            chart = alt.Chart(data).mark_line(color="#7defa1",strokeWidth=2).encode(
                        x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
        else:
            chart = chart + alt.Chart(data).mark_line(color="#7defa1").encode(x=alt.X("Time"), y=alt.Y("4-hour moving average"))
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
            else:
                chart = alt.Chart(data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
        else:
            chart = chart + alt.Chart(data).mark_line(color="#6d3fc0").encode(x=alt.X("Time"), y=alt.Y("12-hour moving average"))
    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
            else:
                chart = alt.Chart(data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)))
        else:
            chart = chart + alt.Chart(data).mark_line(color="#bd4043").encode(x=alt.X("Time"), y=alt.Y("24-hour moving average"))
    



    chart = chart.properties(height=600)

    chart = chart.configure_axisY(
        grid=True,           gridOpacity=0.2,         tickCount=6,
        titleFont="Calibri", titleColor="#ffffff",    titlePadding=20,
        titleFontSize=24,    titleFontStyle="italic", titleFontWeight="bold",
        labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
        labelFontSize=16,    labelFontWeight="bold",
    )
    chart = chart.configure_axisX(
        grid=False,          tickCount="day",        titleOpacity=0,
        labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
        labelFontSize=20,    labelFontWeight="bold",
    )
    chart = chart.configure_view(
        strokeOpacity=0,    # remove border
    )
    
    
    if mobile:
        chart = chart.configure_axisY(
            grid=True,           gridOpacity=0.2,         tickCount=5,
            titleFont="Calibri", titleColor="#ffffff",    titlePadding=0,
            titleFontSize=1,     titleFontStyle="italic", titleFontWeight="bold",
            labelFont="Calibri", labelColor="#ffffff",    labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold",  titleOpacity=0,
        )
        chart = chart.configure_axisX(
            grid=False,          tickCount="day",        titleOpacity=0,
            labelFont="Calibri", labelColor="#ffffff",   labelPadding=10,
            labelFontSize=16,    labelFontWeight="bold", 
        )
        
        chart = chart.properties(title=f"{item} {ylabel.replace('(', '(in ')}")
        chart.configure_title(
            fontSize=20,
            font='Calibri',
            anchor='start',
            color='#ffffff',
            align='center'
        )
        
        chart = chart.properties(height=400)
    

    return chart
