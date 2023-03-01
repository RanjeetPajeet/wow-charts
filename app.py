import streamlit as st
from api import api_online, api_offline
from misc import hide_element, titleize
from data import get_server_history_OHLC
from charts import plot_price_history, plot_price_and_quantity_history, plot_price_and_region_history, plot_price_history_comparison, create_OHLC_chart

st.set_page_config(
    layout     = "centered",
    page_icon  = ":moneybag:",
    page_title = "AH Prices",
)


st.title("Auction House Data")
st.markdown("---")




with st.container():
    st.markdown("### Parameters")
    st.markdown("### ")
    
    item_col, days_col = st.columns(2)
    with item_col:  item = st.text_input("Item name", "Saronite Ore")
    with days_col:  num_days = st.number_input("Number of days", 1, 730, 120)
        
    server_col, faction_col = st.columns(2)
    with server_col:  server = st.selectbox("Server", ["Skyfury","Pagle","Atiesh","Faerlina","Whitemane"])
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
                elif server_compare == "Skyfury" or server_compare == "Atiesh":
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

st.markdown("## ")
candlestick = st.checkbox("Candlestick", value=False)

st.markdown("## ")
submit = st.button("Submit")

st.markdown("## ")
chart = st.empty()



if submit:
    try:
        if candlestick:
            with st.spinner("Loading..."):
                ohlc_data, data_min, data_max = get_server_history_OHLC(item, server, faction, num_days)
                st.markdown("# ")
                st.markdown("# ")
                st.markdown(f"### [{titleize(item)}] {chart_type} -- Last {num_days} Days")
                st.markdown("## ")
                chart = st.altair_chart(create_OHLC_chart(ohlc_data, data_min, data_max, mobile=mobile))
        else:
            st.markdown("# ")
            st.markdown("# ")
            st.markdown(f"### [{titleize(item)}] {chart_type} -- Last {num_days} Days")
            st.markdown("## ")
            
            chart = st.empty()
            if chart_type == "Price":
                if server_compare is not None and faction_compare is not None:
                    chart = st.altair_chart(plot_price_history_comparison(item, server, faction, server_compare, faction_compare, num_days, ma4, ma12, ma24, ma48, hide_original, mobile), use_container_width=True)
                else: chart = st.altair_chart(plot_price_history(item, server, faction, num_days, ma4, ma12, ma24, ma48, hide_original, mobile), use_container_width=True)
            elif chart_type == "Price & Quantity":
                chart = st.altair_chart(plot_price_and_quantity_history(item, server, faction, num_days, ma4, ma12, ma24, ma48, hide_original, mobile), use_container_width=True)
            elif chart_type == "Price & Region Price":
                chart = st.altair_chart(plot_price_and_region_history(item, server, faction, num_days, ma4, ma12, ma24, ma48, hide_original, mobile), use_container_width=True)
        
        if mobile:
            hide_element("button", "title", "View fullscreen")
    
    except Exception as e:
        st.error("NexusHub API is currently offline.", icon="🚨") if api_offline() else st.markdown(f"### Error: {e}")

