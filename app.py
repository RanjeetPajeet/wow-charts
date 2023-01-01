import streamlit as st
from api import api_offline
from charts import plot_price_history, plot_price_and_quantity_history, plot_price_and_region_history, plot_price_history_comparison


st.set_page_config(
    layout     = "centered",
    page_icon  = ":moneybag:",
    page_title = "AH Prices",
)

st.title("Auction House Data")
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
        if server == "Skyfury":
            faction = st.selectbox("Faction", ["Alliance","Horde"])
        else:
            faction = st.selectbox("Faction", ["Horde","Alliance"])
    
    st.markdown("##")

    chart_type = st.selectbox("Chart type", ["Price","Price & Quantity","Price & Region Price"])

    if chart_type == "Price":
        server_col_compare, faction_col_compare = st.columns(2)
        with server_col_compare:
            server_compare = st.selectbox("Compare with", [None,"Skyfury","Faerlina","Whitemane"], key="server_compare")
        with faction_col_compare:
            if server_compare is not None:
                if server_compare == server:
                    faction_compare = st.selectbox(" ", [f for f in ["Alliance","Horde"] if f != faction], key="faction_compare", disabled=True)
                elif server_compare == "Skyfury":
                    faction_compare = st.selectbox(" ", ["Alliance","Horde"], key="faction_compare")
                else:
                    faction_compare = st.selectbox(" ", ["Horde","Alliance"], key="faction_compare")
            else:
                faction_compare = st.selectbox(" ", [None,"Alliance","Horde"], key="faction_compare", disabled=True)

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



st.markdown("---")
st.markdown("#")


mobile = st.checkbox("Mobile", value=False)
st.markdown("##")
submit = st.button("Submit")


chart = st.empty()



# Hides the Submit button if on mobile
# st.markdown("""<style>@media (pointer:none),(pointer:coarse) {button[kind="secondary"]{display: none;}}</style>""", unsafe_allow_html=True)


def run_custom_css(css: str):
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)


# Hides the "Made with Streamlit" footer element

run_custom_css("""
footer[class="css-1lsmgbg egzxvld0"] {
    display: none;
}
""")

# st.markdown("""<style>

# footer[class="css-1lsmgbg egzxvld0"] {
#     display: none;
# }

# </style>""", unsafe_allow_html=True)



if submit:
    if mobile:
        st.markdown("#")
        st.markdown("#")
        st.markdown("""<style>button[title="View fullscreen"]{display: none;}</style>""", unsafe_allow_html=True)
    
    if chart_type == "Price":
        if server_compare is not None and faction_compare is not None:
            chart = st.altair_chart(plot_price_history_comparison(item, server, faction, server_compare, faction_compare, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)
        else:
            chart = st.altair_chart(plot_price_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)


    elif chart_type == "Price & Quantity":
        chart = st.altair_chart(plot_price_and_quantity_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)


    elif chart_type == "Price & Region Price":
        chart = st.altair_chart(plot_price_and_region_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original, mobile), use_container_width=True)

