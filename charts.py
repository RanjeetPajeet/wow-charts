import pandas as pd
import altair as alt
import streamlit as st
from data import get_server_history, get_region_history



def plot_price_history(item:str, server:str, faction:str, num_days:int, ma4:bool, ma12:bool, ma24:bool, hide_original:bool, mobile:bool) -> alt.Chart:
    data = get_server_history(item, server, faction, num_days)
    scale = 100 if data["prices"][-1] < 10000 else 10000
    prices = [round(price/scale,2) for price in data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"

    data = pd.DataFrame(
        {
            "Time": data["times"], ylabel: prices,
            "4-hour moving average":  pd.Series(prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(prices).rolling(12).mean(),
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





def plot_price_and_region_history(item:str, server:str, faction:str, num_days:int, ma4:bool, ma12:bool, ma24:bool, hide_original:bool, mobile:bool) -> alt.Chart:
    server_data = get_server_history(item, server, faction, num_days)
    region_data = get_region_history(item, numDays=num_days)
    scale = 100 if server_data["prices"][-1] < 10000 else 10000
    server_prices = [round(price/scale,2) for price in server_data["prices"]]
    region_prices = [round(price/scale,2) for price in region_data["prices"]]
    ylabel = "Price (silver)" if scale==100 else "Price (gold)"

    # make sure server_prices and region_prices are the same length
    if len(server_prices) > len(region_prices):
        server_prices = server_prices[:len(region_prices)]
    elif len(region_prices) > len(server_prices):
        region_prices = region_prices[:len(server_prices)]

    server_data = pd.DataFrame(
        {
            "Time": server_data["times"], ylabel: server_prices,
            "4-hour moving average":  pd.Series(server_prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(server_prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(server_prices).rolling(12).mean(),
        }
    )
    region_data = pd.DataFrame(
        {
            "Time": region_prices["times"], ylabel: region_prices,
            "4-hour moving average":  pd.Series(region_prices).rolling(2).mean(),
            "12-hour moving average": pd.Series(region_prices).rolling(6).mean(),
            "24-hour moving average": pd.Series(region_prices).rolling(12).mean(),
        }
    )

    # make sure server_data and region_data have the same number of rows
    if len(server_data) > len(region_data):
        server_data = server_data.iloc[-len(region_data):]
    elif len(region_data) > len(server_data):
        region_data = region_data.iloc[-len(server_data):]
    
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
    


    if not hide_original:
        chart = alt.Chart(server_data).mark_line(
            color="#83c9ff" if not hide_original else "#0e1117",
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        ) + alt.Chart(region_data).mark_line(
            color="#ff6f83" if not hide_original else "#0e1117",                                            #  <------ NOTE: "#ff6f83" can be changed
            strokeWidth=2,
        ).encode(
            x=alt.X("Time", axis=alt.Axis(title="Date")),
            y=alt.Y(ylabel, axis=alt.Axis(title=ylabel) , scale=alt.Scale(domain=chart_ylims))
        )
        chart = chart.properties(height=600)

    if ma4:
        if hide_original:
            chart = alt.Chart(server_data).mark_line(color="#7defa1",strokeWidth=2).encode(
                        x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            ) + alt.Chart(region_data).mark_line(color="#7defa1",strokeWidth=2).encode(                     #  <------ NOTE: "#7defa1" can be changed
                        x=alt.X("Time", axis=alt.Axis(title="Date")), 
                        y=alt.Y("4-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
            )
        else:
            chart = chart + alt.Chart(server_data).mark_line(color="#7defa1").encode(
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average")
            ) + alt.Chart(region_data).mark_line(color="#7defa1").encode(                                    #  <------ NOTE: "#7defa1" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("4-hour moving average"))
    
    if ma12:
        if hide_original:
            if ma4:
                chart = chart + alt.Chart(server_data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
            else:
                chart = alt.Chart(server_data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(color="#6d3fc0",strokeWidth=2.1).encode(                 #  <------ NOTE: "#6d3fc0" can be changed
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("12-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
        else:
            chart = chart + alt.Chart(server_data).mark_line(color="#6d3fc0").encode(
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average")
            ) + alt.Chart(region_data).mark_line(color="#6d3fc0").encode(                                    #  <------ NOTE: "#6d3fc0" can be changed
                                x=alt.X("Time"),
                                y=alt.Y("12-hour moving average"))

    if ma24:
        if hide_original:
            if ma4 or ma12:
                chart = chart + alt.Chart(server_data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
                                    x=alt.X("Time", axis=alt.Axis(title="Date")), 
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(color="#bd4043",strokeWidth=2.2).encode(                 #  <------ NOTE: "#bd4043" can be changed
                                    x=alt.X("Time", axis=alt.Axis(title="Date")),
                                    y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
            else:
                chart = alt.Chart(server_data).mark_line(color="#bd4043",strokeWidth=2.2).encode(
                            x=alt.X("Time", axis=alt.Axis(title="Date")), 
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                ) + alt.Chart(region_data).mark_line(color="#bd4043",strokeWidth=2.2).encode(                 #  <------ NOTE: "#bd4043" can be changed
                            x=alt.X("Time", axis=alt.Axis(title="Date")),
                            y=alt.Y("24-hour moving average", axis=alt.Axis(title=ylabel), scale=alt.Scale(domain=chart_ylims))
                )
        else:
            chart = chart + alt.Chart(server_data).mark_line(color="#bd4043").encode(
                x=alt.X("Time"),
                y=alt.Y("24-hour moving average")
            ) + alt.Chart(region_data).mark_line(color="#bd4043").encode(                                    #  <------ NOTE: "#bd4043" can be changed
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
