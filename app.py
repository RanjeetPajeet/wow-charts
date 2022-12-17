import streamlit as st
from charts import plot_price_history

st.set_page_config(
    layout     = "centered",
    page_icon  = ":moneybag:",
    page_title = "AH Prices",
)
st.title("Auction House Charts")


st.markdown("---")


with st.container():
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

    chart_type = st.selectbox("Chart type", ["Price","Price & Quantity","Price & Region"])
    chart_smoothing = st.select_slider("Smoothing", options=[2,4,8,12,24,48], value=2, help="Amount of smoothing for the chart, in hours.")

    st.markdown("##")

    st.markdown("### Moving averages")

    ma_col4, ma_col12, ma_col24, hide_og_col = st.columns(4)
    with ma_col4:
        ma4 = st.checkbox("4 hour", value=False)
    with ma_col12:
        ma12 = st.checkbox("12 hour", value=True)
    with ma_col24:
        ma24 = st.checkbox("24 hour", value=False)
    with hide_og_col:
        hide_original = st.checkbox("Hide raw data", value=True)



st.markdown("---")


st.markdown("##")
st.markdown("##")


chart = st.empty()



if st.button("Submit"):
    if chart_type == "Price":
        chart = st.altair_chart(plot_price_history(item, server, faction, num_days, ma4, ma12, ma24, hide_original), use_container_width=True)











# if __name__ == "__main__":
#     import streamlit as st
#     from plots import price, price_and_quantity, price_and_region
    
#     st.set_page_config(
#         page_title="AH Prices",
#         layout="centered",
#         page_icon=":moneybag:"
#     )
    
#     with open("style/style.css") as f:      # load css file
#         st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    

#     st.title("Auction House Plots")
#     # st.write("Simple tool for plotting price & quantity of items.")

#     st.write("")

#     item = st.text_input("Item name", "Saronite Ore")
#     numDays = st.number_input("Number of days", 1, 90, 7)

#     server = st.selectbox("Server", ["Skyfury", "Faerlina", "Whitemane"])
#     faction = st.selectbox("Faction", ["Alliance", "Horde"])

#     chartType = st.selectbox("Chart type", ["Price", "Price & Quantity", "Price & Region"], help="Select the type of chart you want to view.")

#     st.write("")

#     # replaceOutliers = st.checkbox("Replace outliers", False)
#     # threshold = st.number_input("Outlier threshold", 1, 5, 2)
#     # html(javascript, height=0)

#     if st.button("Plot"):
#         if chartType == "Price":
#             st.pyplot(price(item, numDays, server, faction))
#             # disable the view fullscreen button (button title="View fullscreen" class="css-e370rw e191ei0e1")
#             # st.markdown("""<style>button[title="View fullscreen"]{display: none;}</style>""", unsafe_allow_html=True)
#         elif chartType == "Price & Quantity":
#             st.pyplot(price_and_quantity(item, numDays, server, faction))
#         elif chartType == "Price & Region":
#             st.pyplot(price_and_region(item, numDays, server, faction, replaceOutliers=True, threshold=3))
