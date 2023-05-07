import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from collections import namedtuple
from colors import LineColors, GradientColors
from data import get_server_history, remove_outliers, get_server_history_OHLC
from misc import map_value, get_min_max_of_data, get_min_max_of_data2, enforce_upper_price_limit, enforce_lower_price_limit



MOUSEOVER_LINE_THICKNESS = 15.0             # the stroke width of the zero opacity line added to charts to assist in tooltip visibility when mousing over price lines
XAXIS_DATETIME_FORMAT = ( "%b %d" )         # the format of the x-axis datetime labels
TOOLTIP_DATETIME_FORMAT = ( "%b %d, %Y" )   # the format of the datetime labels in the tooltip






def enforce_price_limits(prices: list, num_std_deviations: int = 3) -> list:
    """
    Defines an upper and lower limit as `mean(prices) +/- num_std_deviations*std_dev(prices)`,
    then iterates through the given list of prices, setting any values above or below these values equal to them.
    
    Parameters
    ----------
    `prices`: The list to set an upper limit on.
    `num_std_deviations`: The number of standard deviations away from the mean to define the upper limit as.
    
    Returns
    -------
    A new list with any values too high/too low replaced with the upper/lower limit, respectively.
    """
    prices = enforce_upper_price_limit(prices, num_std_deviations)
    prices = enforce_lower_price_limit(prices, num_std_deviations)
    return prices





def get_tooltip(dataframe_price_column_label: str, price_scale: int, tooltip_price_line_title: str, is_quantity: bool = False) -> list[alt.Tooltip]:
    """
    Creates a list of tooltips for a chart.

    Parameters
    ----------
    `dataframe_price_column_label`: The name of the column in the dataframe containing the price data, e.g. `ylabel`, `"12-hour moving average"`, etc.
    `price_scale`: The scaling factor of the price data (`100` or `10000`).
    `tooltip_price_line_title`: The title to give the line of the tooltip that shows price, e.g. `"Price"`, `"Price (12h avg)"`, etc.
    `is_quantity`: Whether the tooltip is for a quantity or not.

    Returns
    -------
    A list of tooltip objects.
    """
    if is_quantity:         # Quantity formatting
        return [alt.Tooltip("Time",title="Time",format=TOOLTIP_DATETIME_FORMAT), alt.Tooltip(dataframe_price_column_label,title=tooltip_price_line_title,format=",.0f")]
    if price_scale != 100:  # Prices are in gold
        return [alt.Tooltip("Time",title="Time",format=TOOLTIP_DATETIME_FORMAT), alt.Tooltip(dataframe_price_column_label,title=tooltip_price_line_title,format=",.2f")]
    else:                   # Prices are in silver
        return [alt.Tooltip("Time",title="Time",format=TOOLTIP_DATETIME_FORMAT), alt.Tooltip(dataframe_price_column_label,title=tooltip_price_line_title,format=",.0f")]





def get_mouseover_line(data: pd.DataFrame, dataframe_price_column_label: str, yaxis_title: str, 
                       chart_ylimits: tuple, price_scale: int, tooltip_price_line_title: str) -> alt.Chart:
    """
    Generates a line equivalent to what is used for an item's price,
    except the stroke width (thickness) is much larger and it has zero opacity.
    This creates a region around the visible line where the mouse will generate a tooltip.

    Parameters
    ----------
    `data`: The dataframe containing the data to be plotted.
    `dataframe_price_column_label`: The name of the column in the dataframe containing the price data, e.g. `ylabel`, `"12-hour moving average"`, etc.
    `yaxis_title`: The title of the chart's y-axis (one of `"Price (gold)"` or `"Price (silver)"`).
    `chart_ylimits`: The minimum and maximum values of the chart's y-axis.
    `price_scale`: The scaling factor of the price data (`100` or `10000`).
    `tooltip_price_line_title`: The title to give the line of the tooltip that shows price, e.g. `"Price"`, `"Price (12h avg)"`, etc.

    Returns
    -------
    An `alt.Chart` object containing the mouseover line.
    """
    return alt.Chart(data).mark_line(
        color = "#ffffff",
        opacity = 0.001,
        strokeWidth = MOUSEOVER_LINE_THICKNESS,
    ).encode(
        x = alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
        y = alt.Y(dataframe_price_column_label, axis=alt.Axis(title=yaxis_title), scale=alt.Scale(domain=chart_ylimits)),
        tooltip=get_tooltip(dataframe_price_column_label, price_scale, tooltip_price_line_title))










class Plot:
    """
    A class containing methods for plotting data.

    Methods
    -------
    `price_history()`: Creates a line chart of the price history of an item.
    `price_history_with_quantity()`: Creates a line chart of the price history of an item, with a volume/quantity area chart below.
    """
    @staticmethod
    def price_history(historical_price_data: dict, ma4: bool, ma12: bool, ma24: bool, ma48: bool, ma72: bool, hide_original: bool, mobile: bool, fix_outliers: bool = False, regression_line: bool = False) -> alt.Chart:
        """
        Creates a line chart of the price history of an item.

        Parameters
        ----------
        `historical_price_data`: A dictionary containing the historical price data of an item, as returned from `data.get_server_history()`.
        `ma4`: Boolean indicating whether or not to plot the 4-hour moving average.
        `ma12`: Boolean indicating whether or not to plot the 12-hour moving average.
        `ma24`: Boolean indicating whether or not to plot the 24-hour moving average.
        `ma48`: Boolean indicating whether or not to plot the 48-hour moving average.
        `ma72`: Boolean indicating whether or not to plot the 72-hour moving average.
        `hide_original`: Boolean indicating whether or not to hide the original price data.
        `mobile`: Boolean indicating whether or not to render the chart for mobile.
        `fix_outliers`: An optional boolean value indicating whether or not to remove outliers from the data. Note that this is currently not working.
        `regression_line`: An optional boolean value indicating whether or not to plot a least-squares regression line.
        
        Returns
        -------
        An Altair chart object which can be rendered via `st.altair_chart( chart )`.
        """
        scale = 100 if historical_price_data["prices"][-1] < 10000 else 10000
        prices = [round(price/scale,2) for price in historical_price_data["prices"]]
        ylabel = "Price (silver)" if scale==100 else "Price (gold)"
        if fix_outliers:
            prices = remove_outliers(prices)
        prices = enforce_price_limits(prices)
        data = pd.DataFrame({
            "Time": historical_price_data["times"], ylabel: prices,
            "4-hour moving average":  pd.Series(prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(prices).rolling(36).mean().round(2),
        })
        if not ma72:
            minimum, maximum = get_min_max_of_data(data, prices, ma4, ma12, ma24, ma48, hide_original)
        else: minimum, maximum = get_min_max_of_data2(data, prices, ma4, ma12, ma24, ma48, ma72, hide_original)
        try: chart_ylims = (int(minimum/1.25), int(maximum*1.1))
        except Exception as e: chart_ylims = (int(min(prices)/1.25), int(max(prices)*1.10))
        if minimum < 1 and maximum < 2 and scale != 100:                        # Fix the issue with y-limit scaling when
            try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))    # the price of something is barely over a gold
            except: pass                                                        # Such is the case when plotting the price of Saronite Ore
        
        if regression_line:
            from scipy import stats
            if not ma4 and not ma12 and not ma24 and not ma48:
                highest_ma = False
                regression_line = False
            else:
                highest_ma = "4-hour moving average"
                MAs = {"4-hour moving average":ma4, "12-hour moving average":ma12, "24-hour moving average":ma24, "48-hour moving average":ma48}
                for ma in MAs:
                    if MAs[ma] and int(ma.split("-")[0]) > int(highest_ma.split("-")[0]):   # Base the regression line on the highest moving average
                        highest_ma = ma
            if highest_ma:
                y = np.array(data[highest_ma].dropna().tolist())                # Create a list of x values of equal length of data["Time"]
                x = np.array([i for i in range(len(data["Time"]))])[-len(y):]   # since we can't use data["Time"] directly in the regression line
                slope, intercept,_,_,_ = stats.linregress(x, y)
                data["Linear Regression Line"] = [slope*i + intercept for i in range(len(data["Time"]))]    # y = mx + b
                regression_line = alt.Chart(data).mark_line(color = "#83C9FF", strokeWidth = 2).encode(
                    x = alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                    y = alt.Y("Linear Regression Line", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                    strokeDash = alt.value([5,5]),  # make the line dashed
                    tooltip = get_tooltip("Linear Regression Line", scale, "Linear Regression")
                )
                regression_line = regression_line + get_mouseover_line(data, "Linear Regression Line", ylabel, chart_ylims, scale, "Linear Regression")

                # 3rd order polynomial regression line
                coeffs = np.polyfit(x, y, 3)
                data["3rd-Order Regression Line"] = [coeffs[0]*i**3 + coeffs[1]*i**2 + coeffs[2]*i + coeffs[3] for i in range(len(data["Time"]))]    # y = ax^3 + bx^2 + cx + d
                regression_line_3rd_order = alt.Chart(data).mark_line(color = "#83C9FF", strokeWidth = 2).encode(
                    x = alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                    y = alt.Y("3rd-Order Regression Line", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                    strokeDash = alt.value([5,5]),  # make the line dashed
                    tooltip = get_tooltip("3rd-Order Regression Line", scale, "3rd-Order Regression")
                )
                regression_line_3rd_order = regression_line_3rd_order + get_mouseover_line(data, "3rd-Order Regression Line", ylabel, chart_ylims, scale, "3rd-Order Regression")
                regression_line = regression_line + regression_line_3rd_order



        if not hide_original:
            chart = alt.Chart(data).mark_line(color = LineColors.red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, "Price"))
            chart = chart + get_mouseover_line(data, ylabel, ylabel, chart_ylims, scale, "Price")
        if ma4:
            price_line_ma4 = alt.Chart(data).mark_line(color = LineColors.green, strokeWidth = 2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, "Price (4h avg)"))
            price_line_ma4 = price_line_ma4 + get_mouseover_line(data, "4-hour moving average", ylabel, chart_ylims, scale, "Price (4h avg)")
            chart = price_line_ma4 if hide_original else chart + price_line_ma4
        if ma12:
            price_line_ma12 = alt.Chart(data).mark_line(color = LineColors.purple, strokeWidth = 2.1).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, "Price (12h avg)"))
            price_line_ma12 = price_line_ma12 + get_mouseover_line(data, "12-hour moving average", ylabel, chart_ylims, scale, "Price (12h avg)")
            if hide_original:
                if ma4: chart = chart + price_line_ma12
                else: chart = price_line_ma12
            else: chart = chart + price_line_ma12
        if ma24:
            price_line_ma24 = alt.Chart(data).mark_line(color = LineColors.blue, strokeWidth = 2.2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, "Price (24h avg)"))
            price_line_ma24 = price_line_ma24 + get_mouseover_line(data, "24-hour moving average", ylabel, chart_ylims, scale, "Price (24h avg)")
            if hide_original:
                if ma4 or ma12: chart = chart + price_line_ma24
                else: chart = price_line_ma24
            else: chart = chart + price_line_ma24
        if ma48:
            price_line_ma48 = alt.Chart(data).mark_line(color = LineColors.orange, strokeWidth = 2.3).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, "Price (48h avg)"))
            price_line_ma48 = price_line_ma48 + get_mouseover_line(data, "48-hour moving average", ylabel, chart_ylims, scale, "Price (48h avg)")
            if hide_original:
                if ma4 or ma12 or ma24: chart = chart + price_line_ma48
                else: chart = price_line_ma48
            else: chart = chart + price_line_ma48
        if ma72:
            price_line_ma72 = alt.Chart(data).mark_line(color = LineColors.pink, strokeWidth = 2.4).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, "Price (72h avg)"))
            price_line_ma72 = price_line_ma72 + get_mouseover_line(data, "72-hour moving average", ylabel, chart_ylims, scale, "Price (72h avg)")
            if hide_original:
                if ma4 or ma12 or ma24 or ma48: chart = chart + price_line_ma72
                else: chart = price_line_ma72
            else: chart = chart + price_line_ma72
        
        if regression_line:
            chart = chart + regression_line

        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0, 
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{ylabel.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
        return chart










    @staticmethod
    def price_history_comparison(server1_price_data: dict, server2_price_data: dict, server1_name: str, server2_name: str, ma4: bool, ma12: bool, ma24: bool, ma48: bool, ma72: bool, hide_original: bool, mobile: bool, fix_outliers: bool = False, regression_line: bool = False) -> alt.Chart:
        """
        Creates a line chart of the price history of an item compared between two server/factions.

        Parameters
        ----------
        `server1_price_data`: A dictionary containing the historical price data of an item, as returned from `data.get_server_history()`, for the first server.
        `server2_price_data`: A dictionary containing the historical price data of an item, as returned from `data.get_server_history()`, for the second server.
        `server1_name`: The name of the first server.
        `server2_name`: The name of the second server.
        `ma4`: Boolean indicating whether or not to plot the 4-hour moving average.
        `ma12`: Boolean indicating whether or not to plot the 12-hour moving average.
        `ma24`: Boolean indicating whether or not to plot the 24-hour moving average.
        `ma48`: Boolean indicating whether or not to plot the 48-hour moving average.
        `ma72`: Boolean indicating whether or not to plot the 72-hour moving average.
        `hide_original`: Boolean indicating whether or not to hide the original price data.
        `mobile`: Boolean indicating whether or not to render the chart for mobile.
        `fix_outliers`: An optional boolean value indicating whether or not to remove outliers from the data. Note that this is currently not working.
        `regression_line`: An optional boolean value indicating whether or not to plot a least-squares regression line.
        
        Returns
        -------
        An Altair chart object which can be rendered via `st.altair_chart( chart )`.
        """
        scale = 100 if (server1_price_data["prices"][-1] < 10000 or server2_price_data["prices"][-1] < 10000) else 10000
        server1_prices = [round(price/scale,2) for price in server1_price_data["prices"]]
        server2_prices = [round(price/scale,2) for price in server2_price_data["prices"]]
        ylabel = "Price (silver)" if scale==100 else "Price (gold)"
        if fix_outliers:
            server1_prices = remove_outliers(server1_prices)
            server2_prices = remove_outliers(server2_prices)
        server1_prices = enforce_price_limits(server1_prices)
        server2_prices = enforce_price_limits(server2_prices)
        server1_price_data["times"] = [time.replace(minute=0) for time in server1_price_data["times"]]
        server2_price_data["times"] = [time.replace(minute=0) for time in server2_price_data["times"]]
        server1_data  = pd.DataFrame({
            "Time": server1_price_data["times"], ylabel: server1_prices,
            "4-hour moving average":  pd.Series(server1_prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(server1_prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(server1_prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(server1_prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(server1_prices).rolling(36).mean().round(2),
        })
        server2_data  = pd.DataFrame({
            "Time": server2_price_data["times"], ylabel: server2_prices,
            "4-hour moving average":  pd.Series(server2_prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(server2_prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(server2_prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(server2_prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(server2_prices).rolling(36).mean().round(2),
        })
        if not ma72:
            minimum, maximum = get_min_max_of_data([server1_data,server2_data], [server1_prices,server2_prices], ma4, ma12, ma24, ma48, hide_original)
        else: minimum, maximum = get_min_max_of_data2([server1_data,server2_data], [server1_prices,server2_prices], ma4, ma12, ma24, ma48, ma72, hide_original)
        try: chart_ylims = (int(minimum/1.25), int(maximum*1.1))
        except Exception as e: chart_ylims = (int(min(min(server1_prices),min(server2_prices))/1.25), int(max(max(server1_prices),max(server2_prices))*1.10))
        if minimum < 1 and maximum < 2 and scale != 100:                        # Fix the issue with y-limit scaling when
            try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))    # the price of something is barely over a gold
            except: pass                                                        # Such is the case when plotting the price of Saronite Ore

        if not hide_original:
            chart = alt.Chart(server1_data).mark_line(color = LineColors.red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, f"{server1_name} Price")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, f"{server2_name} Price"))
            chart = chart + get_mouseover_line(server1_data, ylabel, ylabel, chart_ylims, scale, f"{server1_name} Price")
            chart = chart + get_mouseover_line(server2_data, ylabel, ylabel, chart_ylims, scale, f"{server2_name} Price")
        if ma4:
            price_line_ma4 = alt.Chart(server1_data).mark_line(color = LineColors.green, strokeWidth = 2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, f"{server1_name} Price (4h avg)")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_green, strokeWidth = 2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, f"{server2_name} Price (4h avg)"))
            price_line_ma4 = price_line_ma4 + get_mouseover_line(server1_data, "4-hour moving average", ylabel, chart_ylims, scale, f"{server1_name} Price (4h avg)")
            price_line_ma4 = price_line_ma4 + get_mouseover_line(server2_data, "4-hour moving average", ylabel, chart_ylims, scale, f"{server2_name} Price (4h avg)")
            chart = price_line_ma4 if hide_original else chart + price_line_ma4
        if ma12:
            price_line_ma12 = alt.Chart(server1_data).mark_line(color = LineColors.purple, strokeWidth = 2.1).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, f"{server1_name} Price (12h avg)")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_purple, strokeWidth = 2.1).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, f"{server2_name} Price (12h avg)"))
            price_line_ma12 = price_line_ma12 + get_mouseover_line(server1_data, "12-hour moving average", ylabel, chart_ylims, scale, f"{server1_name} Price (12h avg)")
            price_line_ma12 = price_line_ma12 + get_mouseover_line(server2_data, "12-hour moving average", ylabel, chart_ylims, scale, f"{server2_name} Price (12h avg)")
            if hide_original:
                if ma4: chart = chart + price_line_ma12
                else: chart = price_line_ma12
            else: chart = chart + price_line_ma12
        if ma24:
            price_line_ma24 = alt.Chart(server1_data).mark_line(color = LineColors.blue, strokeWidth = 2.2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, f"{server1_name} Price (24h avg)")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_blue, strokeWidth = 2.2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, f"{server2_name} Price (24h avg)"))
            price_line_ma24 = price_line_ma24 + get_mouseover_line(server1_data, "24-hour moving average", ylabel, chart_ylims, scale, f"{server1_name} Price (24h avg)")
            price_line_ma24 = price_line_ma24 + get_mouseover_line(server2_data, "24-hour moving average", ylabel, chart_ylims, scale, f"{server2_name} Price (24h avg)")
            if hide_original:
                if ma4 or ma12: chart = chart + price_line_ma24
                else: chart = price_line_ma24
            else: chart = chart + price_line_ma24
        if ma48:
            price_line_ma48 = alt.Chart(server1_data).mark_line(color = LineColors.orange, strokeWidth = 2.3).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, f"{server1_name} Price (48h avg)")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_orange, strokeWidth = 2.3).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, f"{server2_name} Price (48h avg)"))
            price_line_ma48 = price_line_ma48 + get_mouseover_line(server1_data, "48-hour moving average", ylabel, chart_ylims, scale, f"{server1_name} Price (48h avg)")
            price_line_ma48 = price_line_ma48 + get_mouseover_line(server2_data, "48-hour moving average", ylabel, chart_ylims, scale, f"{server2_name} Price (48h avg)")
            if hide_original:
                if ma4 or ma12 or ma24: chart = chart + price_line_ma48
                else: chart = price_line_ma48
            else: chart = chart + price_line_ma48
        if ma72:
            price_line_ma72 = alt.Chart(server1_data).mark_line(color = LineColors.pink, strokeWidth = 2.4).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, f"{server1_name} Price (72h avg)")
            ) + alt.Chart(server2_data).mark_line(color = LineColors.lighter_pink, strokeWidth = 2.4).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, f"{server2_name} Price (72h avg)"))
            price_line_ma72 = price_line_ma72 + get_mouseover_line(server1_data, "72-hour moving average", ylabel, chart_ylims, scale, f"{server1_name} Price (72h avg)")
            price_line_ma72 = price_line_ma72 + get_mouseover_line(server2_data, "72-hour moving average", ylabel, chart_ylims, scale, f"{server2_name} Price (72h avg)")
            if hide_original:
                if ma4 or ma12 or ma24 or ma48: chart = chart + price_line_ma72
                else: chart = price_line_ma72
            else: chart = chart + price_line_ma72
        
        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0, 
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{ylabel.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
        return chart
    









    @staticmethod
    def price_and_region_history_comparison(server_price_data: dict, region_price_data: dict, server_name: str, ma4: bool, ma12: bool, ma24: bool, ma48: bool, ma72: bool, hide_original: bool, mobile: bool, fix_outliers: bool = False, regression_line: bool = False) -> alt.Chart:
        """
        Creates a line chart of the price history of an item compared to the price history of the region (US).

        Parameters
        ----------
        `server_price_data`: A dictionary containing the historical price data of an item, as returned from `data.get_server_history()`, for the server.
        `region_price_data`: A dictionary containing the historical price data of an item, as returned from `data.get_region_history()`, for the region.
        `server_name`: The name of the server.
        `ma4`: Boolean indicating whether or not to plot the 4-hour moving average.
        `ma12`: Boolean indicating whether or not to plot the 12-hour moving average.
        `ma24`: Boolean indicating whether or not to plot the 24-hour moving average.
        `ma48`: Boolean indicating whether or not to plot the 48-hour moving average.
        `ma72`: Boolean indicating whether or not to plot the 72-hour moving average.
        `hide_original`: Boolean indicating whether or not to hide the original price data.
        `mobile`: Boolean indicating whether or not to render the chart for mobile.
        `fix_outliers`: An optional boolean value indicating whether or not to remove outliers from the data. Note that this is currently not working.
        `regression_line`: An optional boolean value indicating whether or not to plot a least-squares regression line.
        
        Returns
        -------
        An Altair chart object which can be rendered via `st.altair_chart( chart )`.
        """
        scale = 100 if (server_price_data["prices"][-1] < 10000 or region_price_data["prices"][-1] < 10000) else 10000
        server_prices = [round(price/scale,2) for price in server_price_data["prices"]]
        region_prices = [round(price/scale,2) for price in region_price_data["prices"]]
        ylabel = "Price (silver)" if scale==100 else "Price (gold)"
        if fix_outliers:
            server_prices = remove_outliers(server_prices)
            region_prices = remove_outliers(region_prices)
        server_prices = enforce_price_limits(server_prices)
        region_prices = enforce_price_limits(region_prices)
        server_std_dev = np.std( pd.Series(server_prices).rolling(2).mean().dropna().tolist() )
        region_std_dev = np.std( pd.Series(region_prices).rolling(2).mean().dropna().tolist() )
        server_std_mean = np.mean( pd.Series(server_prices).rolling(2).mean().dropna().tolist() )
        region_std_mean = np.mean( pd.Series(region_prices).rolling(2).mean().dropna().tolist() )
        std_dev = min(server_std_dev, region_std_dev)
        server_upper_limit = server_std_mean + 3*std_dev
        region_upper_limit = region_std_mean + 3*std_dev
        for i in range(len(server_prices)):
            if server_prices[i] > server_upper_limit: server_prices[i] = server_upper_limit
        for i in range(len(region_prices)):
            if region_prices[i] > region_upper_limit: region_prices[i] = region_upper_limit
        server_price_data["times"] = [time.replace(minute=0) for time in server_price_data["times"]]
        region_price_data["times"] = [time.replace(minute=0) for time in region_price_data["times"]]
        server_data  = pd.DataFrame({
            "Time": server_price_data["times"], ylabel: server_prices,
            "4-hour moving average":  pd.Series(server_prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(server_prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(server_prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(server_prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(server_prices).rolling(36).mean().round(2),
        })
        region_data  = pd.DataFrame({
            "Time": region_price_data["times"], ylabel: region_prices,
            "4-hour moving average":  pd.Series(region_prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(region_prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(region_prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(region_prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(region_prices).rolling(36).mean().round(2),
        })
        if not ma72:
            minimum, maximum = get_min_max_of_data([server_data,region_data], [server_prices,region_prices], ma4, ma12, ma24, ma48, hide_original)
        else: minimum, maximum = get_min_max_of_data2([server_data,region_data], [server_prices,region_prices], ma4, ma12, ma24, ma48, ma72, hide_original)
        try: chart_ylims = (int(minimum/1.25), int(maximum*1.1))
        except Exception as e: chart_ylims = (int(min(min(server_prices),min(region_prices))/1.25), int(max(max(server_prices),max(region_prices))*1.10))
        if minimum < 1 and maximum < 2 and scale != 100:                        # Fix the issue with y-limit scaling when
            try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))    # the price of something is barely over a gold
            except: pass                                                        # Such is the case when plotting the price of Saronite Ore

        if not hide_original:
            chart = alt.Chart(server_data).mark_line(color = LineColors.red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, f"{server_name} Price")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, "Region Price"))
            chart = chart + get_mouseover_line(server_data, ylabel, ylabel, chart_ylims, scale, f"{server_name} Price")
            chart = chart + get_mouseover_line(region_data, ylabel, ylabel, chart_ylims, scale, "Region Price")
        if ma4:
            price_line_ma4 = alt.Chart(server_data).mark_line(color = LineColors.green, strokeWidth = 2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, f"{server_name} Price (4h avg)")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_green, strokeWidth = 2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, f"Region Price (4h avg)"))
            price_line_ma4 = price_line_ma4 + get_mouseover_line(server_data, "4-hour moving average", ylabel, chart_ylims, scale, f"{server_name} Price (4h avg)")
            price_line_ma4 = price_line_ma4 + get_mouseover_line(region_data, "4-hour moving average", ylabel, chart_ylims, scale, "Region Price (4h avg)")
            chart = price_line_ma4 if hide_original else chart + price_line_ma4
        if ma12:
            price_line_ma12 = alt.Chart(server_data).mark_line(color = LineColors.purple, strokeWidth = 2.1).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, f"{server_name} Price (12h avg)")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_purple, strokeWidth = 2.1).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, "Region Price (12h avg)"))
            price_line_ma12 = price_line_ma12 + get_mouseover_line(server_data, "12-hour moving average", ylabel, chart_ylims, scale, f"{server_name} Price (12h avg)")
            price_line_ma12 = price_line_ma12 + get_mouseover_line(region_data, "12-hour moving average", ylabel, chart_ylims, scale, "Region Price (12h avg)")
            if hide_original:
                if ma4: chart = chart + price_line_ma12
                else: chart = price_line_ma12
            else: chart = chart + price_line_ma12
        if ma24:
            price_line_ma24 = alt.Chart(server_data).mark_line(color = LineColors.blue, strokeWidth = 2.2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, f"{server_name} Price (24h avg)")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_blue, strokeWidth = 2.2).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, "Region Price (24h avg)"))
            price_line_ma24 = price_line_ma24 + get_mouseover_line(server_data, "24-hour moving average", ylabel, chart_ylims, scale, f"{server_name} Price (24h avg)")
            price_line_ma24 = price_line_ma24 + get_mouseover_line(region_data, "24-hour moving average", ylabel, chart_ylims, scale, "Region Price (24h avg)")
            if hide_original:
                if ma4 or ma12: chart = chart + price_line_ma24
                else: chart = price_line_ma24
            else: chart = chart + price_line_ma24
        if ma48:
            price_line_ma48 = alt.Chart(server_data).mark_line(color = LineColors.orange, strokeWidth = 2.3).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, f"{server_name} Price (48h avg)")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_orange, strokeWidth = 2.3).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, "Region Price (48h avg)"))
            price_line_ma48 = price_line_ma48 + get_mouseover_line(server_data, "48-hour moving average", ylabel, chart_ylims, scale, f"{server_name} Price (48h avg)")
            price_line_ma48 = price_line_ma48 + get_mouseover_line(region_data, "48-hour moving average", ylabel, chart_ylims, scale, "Region Price (48h avg)")
            if hide_original:
                if ma4 or ma12 or ma24: chart = chart + price_line_ma48
                else: chart = price_line_ma48
            else: chart = chart + price_line_ma48
        if ma72:
            price_line_ma72 = alt.Chart(server_data).mark_line(color = LineColors.pink, strokeWidth = 2.4).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, f"{server_name} Price (72h avg)")
            ) + alt.Chart(region_data).mark_line(color = LineColors.lighter_pink, strokeWidth = 2.4).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, "Region Price (72h avg)"))
            price_line_ma72 = price_line_ma72 + get_mouseover_line(server_data, "72-hour moving average", ylabel, chart_ylims, scale, f"{server_name} Price (72h avg)")
            price_line_ma72 = price_line_ma72 + get_mouseover_line(region_data, "72-hour moving average", ylabel, chart_ylims, scale, "Region Price (72h avg)")
            if hide_original:
                if ma4 or ma12 or ma24 or ma48: chart = chart + price_line_ma72
                else: chart = price_line_ma72
            else: chart = chart + price_line_ma72
        
        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0, 
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{ylabel.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
        return chart
    





    @staticmethod
    def price_and_quantity_history(historical_data: dict, ma4: bool, ma12: bool, ma24: bool, ma48: bool, ma72: bool, hide_original: bool, mobile: bool, fix_outliers: bool = False, regression_line: bool = False) -> alt.Chart:
        """
        Creates a line chart of the price and quantity history of an item.

        Parameters
        ----------
        `historical_data`: A dictionary containing the historical data of an item, as returned from `data.get_server_history()`.
        `ma4`: Boolean indicating whether or not to plot the 4-hour moving average.
        `ma12`: Boolean indicating whether or not to plot the 12-hour moving average.
        `ma24`: Boolean indicating whether or not to plot the 24-hour moving average.
        `ma48`: Boolean indicating whether or not to plot the 48-hour moving average.
        `ma72`: Boolean indicating whether or not to plot the 48-hour moving average.
        `hide_original`: Boolean indicating whether or not to hide the original price data.
        `mobile`: Boolean indicating whether or not to render the chart for mobile.
        `fix_outliers`: An optional boolean value indicating whether or not to remove outliers from the data. Note that this is currently not working.
        `regression_line`: An optional boolean value indicating whether or not to plot a least-squares regression line.
        
        Returns
        -------
        An Altair chart object which can be rendered via `st.altair_chart( chart )`.
        """
        scale = 100 if historical_data["prices"][-1] < 10000 else 10000
        prices = [round(price/scale,2) for price in historical_data["prices"]]
        ylabel = "Price (silver)" if scale==100 else "Price (gold)"
        if fix_outliers:
            prices = remove_outliers(prices)
        prices = enforce_price_limits(prices)
        data = pd.DataFrame({
            "Time": historical_data["times"], ylabel: prices,
            "Quantity": historical_data["quantities"],
            "Quantity  4hMA": pd.Series(historical_data["quantities"]).rolling( 2).mean(),
            "Quantity 12hMA": pd.Series(historical_data["quantities"]).rolling( 6).mean(),
            "Quantity 24hMA": pd.Series(historical_data["quantities"]).rolling(12).mean(),
            "Quantity 48hMA": pd.Series(historical_data["quantities"]).rolling(24).mean(),
            "Quantity 72hMA": pd.Series(historical_data["quantities"]).rolling(36).mean(),
            "4-hour moving average":  pd.Series(prices).rolling( 2).mean().round(2),
            "12-hour moving average": pd.Series(prices).rolling( 6).mean().round(2),
            "24-hour moving average": pd.Series(prices).rolling(12).mean().round(2),
            "48-hour moving average": pd.Series(prices).rolling(24).mean().round(2),
            "72-hour moving average": pd.Series(prices).rolling(36).mean().round(2),
            "Raw Quantity":     pd.Series(historical_data["quantities"]).rolling( 1).mean().dropna().apply(lambda x: int(x)),
            "4h Avg Quantity":  pd.Series(historical_data["quantities"]).rolling( 2).mean().dropna().apply(lambda x: int(x)),
            "12h Avg Quantity": pd.Series(historical_data["quantities"]).rolling( 6).mean().dropna().apply(lambda x: int(x)),
            "24h Avg Quantity": pd.Series(historical_data["quantities"]).rolling(12).mean().dropna().apply(lambda x: int(x)),
            "48h Avg Quantity": pd.Series(historical_data["quantities"]).rolling(24).mean().dropna().apply(lambda x: int(x)),
            "72h Avg Quantity": pd.Series(historical_data["quantities"]).rolling(36).mean().dropna().apply(lambda x: int(x)),
        })
        if not ma72:
            minimum, maximum = get_min_max_of_data(data, prices, ma4, ma12, ma24, ma48, hide_original)
        else: minimum, maximum = get_min_max_of_data2(data, prices, ma4, ma12, ma24, ma48, ma72, hide_original)
        try: chart_ylims = (int(minimum/1.25), int(maximum*1.1))
        except Exception as e: chart_ylims = (int(min(prices)/1.25), int(max(prices)*1.10))
        if minimum < 1 and maximum < 2 and scale != 100:                        # Fix the issue with y-limit scaling when
            try: chart_ylims = (round(minimum/1.25,2), round(maximum*1.1,2))    # the price of something is barely over a gold
            except: pass                                                        # Such is the case when plotting the price of Saronite Ore

        if not hide_original:
            range_quantity = [data["Quantity"].min(), data["Quantity"].max()]
            data["Quantity"] = data["Quantity"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
            chart = alt.Chart(data).mark_line(color = LineColors.red, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y(ylabel, axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip(ylabel, scale, "Price")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.red.bottom, offset=0),     # bottom color
                           alt.GradientStop(color=GradientColors.red.top,    offset=1)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 2, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("Raw Quantity", scale, "Quantity", is_quantity=True))
            chart = chart + get_mouseover_line(data, ylabel, ylabel, chart_ylims, scale, "Price")
        if ma4:
            range_quantity = [data["Quantity  4hMA"].min(), data["Quantity  4hMA"].max()]
            data["Quantity  4hMA"] = data["Quantity  4hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
            ma4_lines = alt.Chart(data).mark_line(color = LineColors.green, strokeWidth = 2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4-hour moving average", scale, "Price (4h avg)")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.green.bottom, offset=0.0),     # bottom color
                           alt.GradientStop(color=GradientColors.green.top,    offset=0.4)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 2, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity  4hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("4h Avg Quantity", scale, "Quantity (4h avg)", is_quantity=True))
            ma4_lines = ma4_lines + get_mouseover_line(data, "4-hour moving average", ylabel, chart_ylims, scale, "Price (4h avg)")
            chart = ma4_lines if hide_original else chart + ma4_lines
        if ma12:
            range_quantity = [data["Quantity 12hMA"].min(), data["Quantity 12hMA"].max()]
            data["Quantity 12hMA"] = data["Quantity 12hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))

            ma12_lines = alt.Chart(data).mark_line(color = LineColors.purple, strokeWidth = 2.1).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12-hour moving average", scale, "Price (12h avg)")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.purple.bottom, offset=0.3),     # bottom color
                           alt.GradientStop(color=GradientColors.purple.top,    offset=0.7)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 1, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity 12hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("12h Avg Quantity", scale, "Quantity (12h avg)", is_quantity=True))
            ma12_lines = ma12_lines + get_mouseover_line(data, "12-hour moving average", ylabel, chart_ylims, scale, "Price (12h avg)")
            if hide_original:
                if ma4: chart = chart + ma12_lines
                else: chart = ma12_lines
            else: chart = chart + ma12_lines
        if ma24:
            range_quantity = [data["Quantity 24hMA"].min(), data["Quantity 24hMA"].max()]
            data["Quantity 24hMA"] = data["Quantity 24hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
            ma24_lines = alt.Chart(data).mark_line(color = LineColors.blue, strokeWidth = 2.2).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24-hour moving average", scale, "Price (24h avg)")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.blue.bottom, offset=0.0),     # bottom color
                           alt.GradientStop(color=GradientColors.blue.top,    offset=0.4)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 2.2, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity 24hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("24h Avg Quantity", scale, "Quantity (24h avg)", is_quantity=True))
            ma24_lines = ma24_lines + get_mouseover_line(data, "24-hour moving average", ylabel, chart_ylims, scale, "Price (24h avg)")
            if hide_original:
                if ma4 or ma12: chart = chart + ma24_lines
                else: chart = ma24_lines
            else: chart = chart + ma24_lines
        if ma48:
            range_quantity = [data["Quantity 48hMA"].min(), data["Quantity 48hMA"].max()]
            data["Quantity 48hMA"] = data["Quantity 48hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
            ma48_lines = alt.Chart(data).mark_line(color = LineColors.orange, strokeWidth = 2.3).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y("48-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48-hour moving average", scale, "Price (48h avg)")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.orange.bottom, offset=0.3),     # bottom color
                           alt.GradientStop(color=GradientColors.orange.top,    offset=0.7)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 1, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity 48hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("48h Avg Quantity", scale, "Quantity (48h avg)", is_quantity=True))
            ma48_lines = ma48_lines + get_mouseover_line(data, "48-hour moving average", ylabel, chart_ylims, scale, "Price (48h avg)")
            if hide_original:
                if ma4 or ma12 or ma24: chart = chart + ma48_lines
                else: chart = ma48_lines
            else: chart = chart + ma48_lines
        if ma72:
            range_quantity = [data["Quantity 72hMA"].min(), data["Quantity 72hMA"].max()]
            data["Quantity 72hMA"] = data["Quantity 72hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum]))
            ma72_lines = alt.Chart(data).mark_line(color = LineColors.pink, strokeWidth = 2.4).encode(
                x = alt.X("Time", axis=alt.Axis(title="Date" , format=XAXIS_DATETIME_FORMAT)),
                y = alt.Y("72-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72-hour moving average", scale, "Price (72h avg)")
            ) + alt.Chart(data).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color=GradientColors.pink.bottom, offset=0.3),     # bottom color
                           alt.GradientStop(color=GradientColors.pink.top,    offset=0.7)],    # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.5, strokeWidth = 1, interpolate = "monotone", clip = True).encode(
                x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("Quantity 72hMA", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims)),
                tooltip = get_tooltip("72h Avg Quantity", scale, "Quantity (72h avg)", is_quantity=True))
            ma72_lines = ma72_lines + get_mouseover_line(data, "72-hour moving average", ylabel, chart_ylims, scale, "Price (72h avg)")
            if hide_original:
                if ma4 or ma12 or ma24 or ma48: chart = chart + ma72_lines
                else: chart = ma72_lines
            else: chart = chart + ma72_lines

        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0, 
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{ylabel.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
        return chart
    




    @staticmethod
    def OHLC_chart(OHLC_data: dict, minimum: float, maximum: float, show_quantity: bool = False, mobile: bool = False) -> alt.Chart:
        """
        Creates an OHLC chart from the given data.

        Parameters
        ----------
        `OHLC_data`: The data to create the chart from.
        `minimum`: The minimum price in the data.
        `maximum`: The maximum price in the data.
        `show_quantity`: Whether or not to show the quantity area chart.
        `mobile`: Whether or not the chart is being displayed on a mobile device.

        NOTE: `OHLC_data`, `minimum`, and `maximum` come from `data.get_server_history_OHLC()`.

        Returns
        -------
        An Altair chart object.
        """
        df = pd.DataFrame({'median_price': [OHLC_data[date]["median"]["price"] for date in OHLC_data]})
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
            'percent_change_price': [OHLC_data[date]["percent_change"]["price"] for date in OHLC_data],
            'percent_change_quantity': [OHLC_data[date]["percent_change"]["quantity"] for date in OHLC_data],
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
        OHLC_df['percent_change_price'] = OHLC_df['percent_change_price'].apply(lambda x: x / 100)
        OHLC_df['percent_change_quantity'] = OHLC_df['percent_change_quantity'].apply(lambda x: x / 100)
        OHLC_df['pct_change_mean_price'] = OHLC_df['pct_change_mean_price'].apply(lambda x: x / 100)
        OHLC_df['pct_change_mean_quantity'] = OHLC_df['pct_change_mean_quantity'].apply(lambda x: x / 100)
        OHLC_df['pct_change_median_price'] = OHLC_df['pct_change_median_price'].apply(lambda x: x / 100)
        OHLC_df['pct_change_median_quantity'] = OHLC_df['pct_change_median_quantity'].apply(lambda x: x / 100)

        RED = "#AE1325"
        GREEN = "#06982D"
        XAXIS_DATETIME_FORMAT = ("%b %d")

        # Wick line mouseover helper
        mouseover = alt.Chart(OHLC_df).mark_rule().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y('low_price', axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
            y2='high_price',
            color=alt.value('#FB00FF'),
            opacity=alt.value(0.01),
            size=alt.value(6),
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])
        
        # Wick lines
        chart = alt.Chart(OHLC_df).mark_rule().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y('low_price', axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
            y2='high_price',
            color=alt.condition('datum.open_price <= datum.close_price', alt.value(GREEN), alt.value(RED)),    # green if open <= close, else red
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])
        
        # Candle bodies
        chart += alt.Chart(OHLC_df).mark_bar().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y='open_price',
            y2='close_price',
            # size=alt.value(8), stroke=alt.value('black'), strokeWidth=alt.value(0.25),
            color=alt.condition('datum.open_price <= datum.close_price', alt.value(GREEN), alt.value(RED)),
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])

        chart += mouseover
        
        if show_quantity:
            quantity_chart = alt.Chart(OHLC_df).mark_area(
                color=alt.Gradient(
                    gradient="linear",
                    stops=[alt.GradientStop(color="#83c9ff", offset=0.0),   # bottom color
                        alt.GradientStop(color="#52A9FA", offset=0.4)],  # top color
                    x1=1, x2=1, y1=1, y2=0),
                opacity = 0.2, strokeWidth = 2, interpolate = "monotone", clip = True).encode(
                x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
                y=alt.Y("quantities", axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
                tooltip=[alt.Tooltip('date', title='Date'), alt.Tooltip('mean_quantity', title='Quantity')])
            chart += quantity_chart
        
        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{YLABEL.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
        return chart



    
    
        
    @staticmethod
    def OHLC_chart2(item, server, faction, num_days, mobile: bool = False) -> alt.Chart:
        """
        Creates an OHLC chart from the given data.

        Parameters
        ----------
        `OHLC_data`: The data to create the chart from.
        `minimum`: The minimum price in the data.
        `maximum`: The maximum price in the data.
        `show_quantity`: Whether or not to show the quantity area chart.
        `mobile`: Whether or not the chart is being displayed on a mobile device.

        NOTE: `OHLC_data`, `minimum`, and `maximum` come from `data.get_server_history_OHLC()`.

        Returns
        -------
        An Altair chart object.
        """
        historical_data = get_server_history(item, server, faction, num_days)
        OHLC_data, minimum, maximum = get_server_history_OHLC(item, server, faction, num_days)
        
        df = pd.DataFrame({'median_price': [OHLC_data[date]["median"]["price"] for date in OHLC_data]})
        SCALE = 100 if df["median_price"].mean() < 10000 else 10000
        YLABEL = "Price (silver)" if SCALE==100 else "Price (gold)"
        chart_ylims = (int(minimum/1.25/SCALE), int(maximum*1.0/SCALE))
        if minimum < 1 and maximum < 2 and SCALE != 100:
            chart_ylims = (round(minimum/1.25,2), round(maximum*1.0,2))

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
            'percent_change_price': [OHLC_data[date]["percent_change"]["price"] for date in OHLC_data],
            'percent_change_quantity': [OHLC_data[date]["percent_change"]["quantity"] for date in OHLC_data],
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
        OHLC_df['percent_change_price'] = OHLC_df['percent_change_price'].apply(lambda x: x / 100)
        OHLC_df['percent_change_quantity'] = OHLC_df['percent_change_quantity'].apply(lambda x: x / 100)
        OHLC_df['pct_change_mean_price'] = OHLC_df['pct_change_mean_price'].apply(lambda x: x / 100)
        OHLC_df['pct_change_mean_quantity'] = OHLC_df['pct_change_mean_quantity'].apply(lambda x: x / 100)
        OHLC_df['pct_change_median_price'] = OHLC_df['pct_change_median_price'].apply(lambda x: x / 100)
        OHLC_df['pct_change_median_quantity'] = OHLC_df['pct_change_median_quantity'].apply(lambda x: x / 100)

        RED = "#AE1325"
        GREEN = "#06982D"
        XAXIS_DATETIME_FORMAT = ("%b %d")

        # Wick line mouseover helper
        mouseover = alt.Chart(OHLC_df).mark_rule().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y('low_price', axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
            y2='high_price',
            color=alt.value('#FB00FF'),
            opacity=alt.value(0.01),
            size=alt.value(6),
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])
        
        # Wick lines
        chart = alt.Chart(OHLC_df).mark_rule().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y('low_price', axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
            y2='high_price',
            color=alt.condition('datum.open_price <= datum.close_price', alt.value(GREEN), alt.value(RED)),    # green if open <= close, else red
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])
        
        # Candle bodies
        chart += alt.Chart(OHLC_df).mark_bar().encode(
            x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y='open_price',
            y2='close_price',
            # size=alt.value(8), stroke=alt.value('black'), strokeWidth=alt.value(0.25),
            color=alt.condition('datum.open_price <= datum.close_price', alt.value(GREEN), alt.value(RED)),
            tooltip=[alt.Tooltip('date'  , title='Date'),
                alt.Tooltip('open_price' , title='Open' , format='.2f'),
                alt.Tooltip('close_price', title='Close', format='.2f'),
                alt.Tooltip('high_price' , title='High' , format='.2f'),
                alt.Tooltip('low_price'  , title='Low'  , format='.2f'),
                alt.Tooltip('percent_change_price'  , title='% Change'  , format='.2%')])

        chart += mouseover
        
#         if show_quantity:
#             quantity_chart = alt.Chart(OHLC_df).mark_area(
#                 color=alt.Gradient(
#                     gradient="linear",
#                     stops=[alt.GradientStop(color="#83c9ff", offset=0.0),   # bottom color
#                         alt.GradientStop(color="#52A9FA", offset=0.4)],  # top color
#                     x1=1, x2=1, y1=1, y2=0),
#                 opacity = 0.2, strokeWidth = 2, interpolate = "monotone", clip = True).encode(
#                 x=alt.X("date", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
#                 y=alt.Y("quantities", axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
#                 tooltip=[alt.Tooltip('date', title='Date'), alt.Tooltip('mean_quantity', title='Quantity')])
#             chart += quantity_chart
            
        scale = 100 if historical_data["prices"][-1] < 10000 else 10000
        prices = [round(price/scale,2) for price in historical_data["prices"]]
        ylabel = "Price (silver)" if scale==100 else "Price (gold)"
        prices = enforce_price_limits(prices)
        data = pd.DataFrame({
            "Time": historical_data["times"], ylabel: prices,
            "Quantity": historical_data["quantities"],
            "Quantity 24hMA": pd.Series(historical_data["quantities"]).rolling(12).mean(),
            "24-hour moving average": pd.Series(prices).rolling(12).mean().round(2),
            "24h Avg Quantity": pd.Series(historical_data["quantities"]).rolling(12).mean().dropna().apply(lambda x: int(x)),
        })
        range_quantity = [OHLC_df["mean_quantity"].min(), OHLC_df["mean_quantity"].max()]
        quantities = [ map_value(x, range_quantity, [chart_ylims[0],minimum/SCALE]) for x in OHLC_df["mean_quantity"] ]

        data["Quantity 24hMA"] = data["Quantity 24hMA"].apply(lambda x: map_value(x, range_quantity, [chart_ylims[0],minimum/SCALE]))
        chart += alt.Chart(data).mark_area(
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color=GradientColors.green.bottom, offset=0.0),     # bottom color
                       alt.GradientStop(color=GradientColors.green.top,    offset=0.4)],    # top color
                x1=1, x2=1, y1=1, y2=0),
            opacity = 0.5, strokeWidth = 2.2, interpolate = "monotone", clip = True).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date", format=XAXIS_DATETIME_FORMAT)),
            y=alt.Y("Quantity 24hMA", axis=alt.Axis(title=YLABEL), scale=alt.Scale(domain=chart_ylims)),
            tooltip = get_tooltip("24h Avg Quantity", scale, "Quantity (24h avg)", is_quantity=True))
        
        chart = chart.properties(height=600)
        chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=6,
            titleFont="Calibri", titleColor="#FFFFFF", titlePadding=20, titleFontSize=24, titleFontStyle="italic", 
            titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
        chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
            labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=20, labelFontWeight="bold")
        chart = chart.configure_view(strokeOpacity=0)
        if mobile:
            chart = chart.configure_axisY(grid=True, gridOpacity=0.2, tickCount=5,
                titleFont="Calibri", titleColor="#FFFFFF", titlePadding=0, titleFontSize=1, titleFontStyle="italic", 
                titleFontWeight="bold", labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold", titleOpacity=0)
            chart = chart.configure_axisX(grid=False, tickCount="day", titleOpacity=0,
                labelFont="Calibri", labelColor="#FFFFFF", labelPadding=10, labelFontSize=16, labelFontWeight="bold")
            chart = chart.properties(title=f"{YLABEL.replace('(', '(in ')}")
            chart.configure_title(fontSize=20, font='Calibri', anchor='start', color='#FFFFFF', align='center')
            chart = chart.properties(height=400)
        
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
    
    values = enforce_upper_price_limit(values)
    values = enforce_lower_price_limit(values,2)
    
    saronite_ore_data = get_server_history("Saronite Ore", server, faction, num_days)
    scale = 100 if saronite_ore_data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in saronite_ore_data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"
    
    if fix_outliers:
        prices = remove_outliers(prices)
    
    prices = enforce_upper_price_limit(prices)
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
