import streamlit as st
from charts import Plot
from api import api_offline
from misc import hide_element, titleize
from data import get_server_history, get_server_history_OHLC, get_region_history

st.set_page_config(
    layout     = "centered",
    page_icon  = ":moneybag:",
    page_title = "AH Prices",
)
st.markdown(body=\
    """ <style>
    section.main > div {max-width:65rem}
    </style> """, unsafe_allow_html=True
)



def title(item: str, chart_type: str, num_days: int) -> None:
    """
    Writes the title of the chart to the page.
    """
    st.markdown("#  ")
    st.markdown("#  ")
    st.markdown(f"### [{titleize(item)}] {chart_type} -- Last {num_days} Days")
    st.markdown("##  ")



st.title("Auction House Data")
st.markdown("---")


if api_offline():
    st.error('Nexushub API is currently offline.', icon="🚨")


with st.container():
    st.markdown("### Parameters")
    st.markdown("### ")
    
    item_col, days_col = st.columns(2)
    with item_col:  item = st.text_input("Item name", "Saronite Ore")
    with days_col:  num_days = st.number_input("Number of days", 1, 730, 180)
        
    server_col, faction_col = st.columns(2)
    with server_col:  server = st.selectbox("Server", ["Pagle","Skyfury","Atiesh","Faerlina","Whitemane"])
    with faction_col: faction = st.selectbox("Faction", ["Alliance","Horde"]) if server in ["Skyfury","Pagle","Atiesh"] else st.selectbox("Faction", ["Horde","Alliance"])

    st.markdown("## ")

    chart_type = st.selectbox("Chart type", ["Price & Quantity","Price","Price & Region Price"])
    server_compare = None   # Need to initialize as `None` to avoid exception when determining if the `candlestick` checkbox should be drawn


    if chart_type == "Price":
        server_col_compare, faction_col_compare = st.columns(2)
        with server_col_compare:
            server_compare = st.selectbox("Compare with", [None,"Pagle","Atiesh","Skyfury","Faerlina","Whitemane"], key="server_compare")
        with faction_col_compare:
            if server_compare is not None:
                if server_compare == server:
                    faction_compare = st.selectbox(" ", [f for f in ["Alliance","Horde"] if f != faction], key="faction_compare", disabled=True)
                elif server_compare in ["Skyfury","Pagle","Atiesh"]:
                    faction_compare = st.selectbox(" ", ["Alliance","Horde"], key="faction_compare")
                else:
                    faction_compare = st.selectbox(" ", ["Horde","Alliance"], key="faction_compare")
            else:
                faction_compare = st.selectbox(" ", [None,"Alliance","Horde"], key="faction_compare", disabled=True)
                

    st.markdown("# ")
    st.markdown("### Moving averages")
    st.markdown("### ")
    

    ma4_col, ma12_col, ma24_col, ma48_col, hideOG_col = st.columns(5)
    with ma4_col:    ma4  = st.checkbox("4 hour",  value=False, key="ma4_checkbox")
    with ma12_col:   ma12 = st.checkbox("12 hour", value=True,  key="ma12_checkbox")
    with ma24_col:   ma24 = st.checkbox("24 hour", value=False, key="ma24_checkbox")
    with ma48_col:   ma48 = st.checkbox("48 hour", value=False, key="ma48_checkbox")
    with hideOG_col: hide_original = st.checkbox("Hide raw", value=True, key="hide_original_checkbox")



st.markdown("---")



st.markdown("# ")
mobile = st.checkbox("Mobile", value=False)

if chart_type in ["Price","Price & Quantity"] and server_compare is None:
    st.markdown("##")
    candlestick = st.checkbox("Candlestick", value=False)
else: candlestick = False

st.markdown("## ")
submit = st.button("Submit")

st.markdown("## ")
chart = st.empty()



if submit:
    try:
        if candlestick:
            with st.spinner("Loading..."):
                ohlc_data, data_min, data_max = get_server_history_OHLC(item, server, faction, num_days)
                title(item, chart_type, num_days)
                chart = st.altair_chart(Plot.OHLC_chart2(item, server, faction, num_days, mobile=mobile), use_container_width=True)
                #chart = st.altair_chart(Plot.OHLC_chart(ohlc_data, data_min, data_max, mobile=mobile), use_container_width=True)
        elif chart_type == "Price":
            if server_compare is None and faction_compare is None:
                with st.spinner("Loading..."):
                    price_data = get_server_history(item, server, faction, num_days)
                    title(item, chart_type, num_days)
                    chart = st.altair_chart(Plot.price_history(price_data, ma4, ma12, ma24, ma48, hide_original, mobile, regression_line=False), use_container_width=True)
            else:
                with st.spinner("Loading..."):
                    server1_data = get_server_history(item, server, faction, num_days)
                    server2_data = get_server_history(item, server_compare, faction_compare, num_days)
                    title(item, chart_type, num_days)
                    chart = st.altair_chart(Plot.price_history_comparison(server1_data, server2_data, server, server_compare, ma4, ma12, ma24, ma48, hide_original, mobile, regression_line=False), use_container_width=True)
        elif chart_type == "Price & Region Price":
            with st.spinner("Loading..."):
                region_data = get_region_history(item, numDays=num_days)
                server_data = get_server_history(item, server, faction, num_days)
                title(item, chart_type, num_days)
                chart = st.altair_chart(Plot.price_and_region_history_comparison(server_data, region_data, server, ma4, ma12, ma24, ma48, hide_original, mobile, regression_line=False), use_container_width=True)
        elif chart_type == "Price & Quantity":
            with st.spinner("Loading..."):
                server_data = get_server_history(item, server, faction, num_days)
                title(item, chart_type, num_days)
                chart = st.altair_chart(Plot.price_and_quantity_history(server_data, ma4, ma12, ma24, ma48, hide_original, mobile, regression_line=False), use_container_width=True)
        if mobile:
            hide_element("button", "title", "View fullscreen")
    
    except Exception as e:
        if api_offline():
            st.error("NexusHub API is currently offline.", icon="🚨")
        else: st.markdown(f"### Error: {e}")

