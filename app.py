import streamlit as st
from charts import plot_price_history, plot_price_and_region_history

st.set_page_config(
    layout     = "centered",
    page_icon  = ":moneybag:",
    page_title = "AH Prices",
)
st.title("Auction House Charts")


st.markdown("---")



with st.container():
    st.markdown("### Parameters")
    st.markdown("###")
    item_col, days_col = st.columns(2)
    with item_col:
        item = st.text_input("Item name", "Titanium Ore")
    with days_col:
        num_days = st.number_input("Number of days", 1, 90, 30)

    server_col, faction_col = st.columns(2)
    with server_col:
        server = st.selectbox("Server", ["Skyfury","Faerlina","Whitemane"])
    with faction_col:
        faction = st.selectbox("Faction", ["Alliance","Horde"])
    
    st.markdown("##")

    chart_type = st.selectbox("Chart type", ["Price","Price & Quantity","Price & Region Price"])

    if chart_type == "Price":
        #st.markdown("##")
        compare_with = st.selectbox("Compare with", [None,"A","B","C"])

    # chart_smoothing = st.select_slider("Smoothing", options=[2,4,8,12,24,48], value=2, help="Amount of smoothing for the chart, in hours.")

    st.markdown("#")

    st.markdown("### Moving averages")
    st.markdown("###")

    ma_col4, ma_col12, ma_col24, hide_og_col = st.columns(4)
    with ma_col4:
        ma4 = st.checkbox("4 hour", value=False, key="ma4_checkbox")
    with ma_col12:
        ma12 = st.checkbox("12 hour", value=True, key="ma12_checkbox")
    with ma_col24:
        ma24 = st.checkbox("24 hour", value=False, key="ma24_checkbox")
    with hide_og_col:
        hide_original = st.checkbox("Hide raw data", value=True, key="hide_original_checkbox")


    
    st.markdown("##")
    
    mobile = st.checkbox("Mobile", value=False)

    


st.markdown("---")


st.markdown("##")
st.markdown("##")


chart = st.empty()



if st.button("Submit"):
    if chart_type == "Price":
        if mobile:
            st.markdown("#")
            st.markdown("#")
            st.markdown("""<style>button[title="View fullscreen"]{display: none;}</style>""", unsafe_allow_html=True)
        chart = st.altair_chart(plot_price_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)

    elif chart_type == "Price & Region Price":
        if mobile:
            st.markdown("#")
            st.markdown("#")
            st.markdown("""<style>button[title="View fullscreen"]{display: none;}</style>""", unsafe_allow_html=True)
        chart = st.altair_chart(plot_price_and_region_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)


