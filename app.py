import streamlit as st
from charts import Plot
from api import api_offline
from scipy.signal import savgol_filter
from streamlit_searchbox import st_searchbox
from streamlit_javascript import st_javascript as js
from misc import hide_element, titleize, hide_markdown_links
from data import get_server_history, get_server_history_OHLC, get_region_history

USE_SEARCHBOX = False
SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER = 4
SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT = 1    # Percent of total data points

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

# st.markdown(body=\
#     """
#     <script type="text/javascript">var wowhead_searchbox_format = "160x200"</script>
#     <script type="text/javascript" src="http://wow.zamimg.com/widgets/searchbox.js"></script>
#     """, unsafe_allow_html=True
# )

# st.markdown(body=\
#     """
#     <script>const whTooltips = {colorLinks: true, iconizeLinks: true, renameLinks: true};</script>
#     <script src="https://wow.zamimg.com/js/tooltips.js"></script>
#     """, unsafe_allow_html=True
# )

# st.write("https://www.wowhead.com/item=31015")

if "auto" not in st.session_state:
    st.session_state["auto"] = True
if "ma4" not in st.session_state:
    st.session_state["ma4"]  = False
if "ma12" not in st.session_state:
    st.session_state["ma12"] = False
if "ma24" not in st.session_state:
    st.session_state["ma24"] = False
if "ma48" not in st.session_state:
    st.session_state["ma48"] = False
if "ma72" not in st.session_state:
    st.session_state["ma72"] = False
    

if USE_SEARCHBOX:
    if "items" not in st.session_state:
        with open("items.txt", 'r') as f:
            items = f.read()
            items = items.split(',')
            items = [item.strip() for item in items]
        st.session_state['items'] = items
    if "searched_item" not in st.session_state:
        st.session_state['searched_item'] = None


def search_items(search_term: str) -> list[tuple[str,str]]:
    """
    Searches for `search_term` in the list of all items that could appear on the AH.
    """
    if len(search_term) < 3: return []
    items = st.session_state['items']
    # Get most broad similarity based off of `search_term`
    similar = [string for string in st.session_state['items'] if search_term.lower() in string.lower()]
    # Further filter by similarity, only showing strings from `items` that share at least 3 consecutive characters with `search_term`
    similar = [string for string in similar if len([char for char in search_term.lower() if char in string.lower()]) >= 3]
    # Sort by degree of similarity
    similar = sorted(similar, key=lambda x: len([char for char in search_term.lower() if char in x.lower()]), reverse=True)
    # Sort again by placing any string that contains all of `search_term` in a single word at the top
    #   For example, if `search_term` is "ore", then "Titanium Ore" should appear in results before "Claymore"
    similar = sorted(similar, key=lambda x: len([word for word in x.lower().split() if search_term.lower() in word and len(word) == len(search_term)]), reverse=True)
    # Sort one more time, placing any string that starts with `search_term` at the top
    #   For example, if `search_term` is "titan", then "Titanium Ore" should come before "Plans: Titansteel Spellblade"
    similar = sorted(similar, key=lambda x: x.lower().startswith(search_term.lower()), reverse=True)
    return [(string, string) for string in similar]
    
    

def update_sessionstate(checkbox, name):    # update other checkboxes when the Auto checkbox is pressed
    if checkbox:
        st.session_state[name] = True
    else:
        st.session_state[name] = False

        
def hide_footer():
    st.markdown(body=\
        """ <style>
        footer {visibility:hidden}
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



# st.title("Auction House Data")
st.title("WoW Classic Auction House Data")
st.markdown("---")


if api_offline():
    st.error('Nexushub API is currently offline.', icon="🚨")


with st.container():
    st.markdown("### Parameters")
    st.markdown("### ")
    
    item_col, days_col = st.columns(2)
    if USE_SEARCHBOX:
        with item_col:
            item = st.session_state['searched_item'] = st_searchbox(
                search_function=search_items,
                placeholder="Search...",
                label="Item name",
                default=None,
                clear_on_submit=False,
                clearable=True,
                key="search_items",
            )
    else:
        with item_col:  item = st.text_input("Item name", "Abyss Crystal").strip()
    with days_col:  num_days = st.number_input("Number of days", 1, 730, 120)
        
    server_col, faction_col = st.columns(2)
    with server_col:  server = st.selectbox("Server", ["Whitemane","Pagle","Faerlina","Skyfury","Atiesh"])
    with faction_col: faction = st.selectbox("Faction", ["Alliance","Horde"]) if server in ["Skyfury","Pagle","Atiesh"] else st.selectbox("Faction", ["Horde","Alliance"])

    st.markdown("## ")

    # chart_type = st.selectbox("Chart type", ["Price & Quantity","Price","Price & Region Price"])
    # chart_type = st.selectbox("Chart type", ["Price", "Price & Quantity", "Price & Region Price"], index=1)
    chart_type_col, chart_style_col = st.columns(2)
    with chart_type_col:
        chart_type = st.selectbox("Chart type", ["Price", "Price & Quantity", "Price & Region Price"], index=1)
    with chart_style_col:
        if chart_type in ["Price", "Price & Quantity"]:
            chart_style = st.selectbox("Chart style", ["Line", "Candle"], index=0)
        else:
            chart_style = st.selectbox("Chart style", ["Line"], index=0, disabled=True)
    server_compare = None   # Need to initialize as `None` to avoid exception when determining if the `candlestick` checkbox should be drawn


    if chart_type == "Price" and chart_style != "Candle":
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
    
    auto_col, ma4_col, ma12_col, ma24_col, ma48_col, ma72_col, hideOG_col = st.columns(7)
    with auto_col:   auto = st.checkbox("Auto",    value=True,  key="auto_checkbox", help="Selects an appropriate moving average depending on the number of days specified")
    with ma4_col:    ma4  = st.checkbox("4 hour ",  value=False, key="ma4_checkbox" )
    with ma12_col:   ma12 = st.checkbox("12 hour ", value=False, key="ma12_checkbox")
    with ma24_col:   ma24 = st.checkbox("24 hour ", value=False, key="ma24_checkbox")
    with ma48_col:   ma48 = st.checkbox("48 hour ", value=False, key="ma48_checkbox")
    with ma72_col:   ma72 = st.checkbox("72 hour ", value=False, key="ma72_checkbox")
    with hideOG_col: hide_original = st.checkbox("Hide raw", value=True, key="hide_original_checkbox", help="Hides the original, non-averaged data in displayed charts")




st.markdown("---")



st.markdown("# ")
filter = st.checkbox("Filter", value=True, help="Uses the Savitzky-Golay filter to de-noise data")
st.markdown("## ")
mobile = st.checkbox("Mobile", value=False, help="Optimizes charts for viewing on smaller screens")

# if chart_type in ["Price","Price & Quantity"] and server_compare is None:
#     st.markdown("##")
#     candlestick = st.checkbox("Candlestick", value=False, key="candlestick_checkbox", help="Generates a candlestick chart instead of a line chart - ignores all moving averages")
# else: candlestick = False

candlestick = chart_style=="Candle"

st.markdown("## ")
# submit = st.button("Submit")
submit_col, _ = st.columns([0.133, 0.867])
with submit_col:
    submit = st.button(label=":green[Submit]", use_container_width=True)

st.markdown("## ")
chart = st.empty()


hide_markdown_links()


if submit:

    if "db" in item.lower():
        pass
    #     #import json
    #     import zipfile
    #     import firebase_admin
    #     from io import BytesIO
    #     from wcltooltips import *
    #     from firebase_admin import credentials, db
    #     if not firebase_admin._apps:
    #         cred = credentials.Certificate("!FirebaseRealtimeDatabaseCredentials.json")
    #         app = firebase_admin.initialize_app(cred, {"databaseURL": "https://wcltooltips-default-rtdb.firebaseio.com/"})
    #     DB_REF = db.reference("/")

    #     hide_footer()

    #     with st.spinner("Loading..."):
            
    #         pagle_dict = DB_REF.child("pagle_json").get()
    #         # pagle_guilds_dict = DB_REF.child("pagle_guilds_json").get()
    #         faerlina_dict = DB_REF.child("faerlina_json").get()
    #         # faerlina_guilds_dict = DB_REF.child("faerlina_guilds_json").get()
    #         whitemane_dict = DB_REF.child("whitemane_json").get()
    #         # whitemane_guilds_dict = DB_REF.child("whitemane_guilds_json").get()
    
    #         hide_footer()
            
    #         def get_lua_strings(parses_dict, server_):
    #             lua_strings = []
    #             for player_name, player_data in parses_dict.items():
    #                 lua_strings.append(
    #                     get_lua_string_for_player(player_data["parses"], player_name, server_.lower(), player_data["class"])
    #                 )
    #             return lua_strings
            
    #         zip_dl, pagle_dl, faerlina_dl, whitemane_dl = st.columns(4)
    
    #         hide_footer()
            
    #         pagle_strings = get_lua_strings(pagle_dict, "Pagle")
    #         faerlina_strings = get_lua_strings(faerlina_dict, "Faerlina")
    #         whitemane_strings = get_lua_strings(whitemane_dict, "Whitemane")
    
    #         hide_footer()
            
    #         with zip_dl:
    #             pagle_str = ""
    #             pagle_str += "\nWCL.DB." + "Pagle.Guilds = " + "{}" + "\n\n\n"
    #             for string in pagle_strings: pagle_str += string
    #             pagle_str += "\n\n\n"
    #             faerlina_str = ""
    #             faerlina_str += "\nWCL.DB." + "Faerlina.Guilds = " + "{}" + "\n\n\n"
    #             for string in faerlina_strings: faerlina_str += string
    #             faerlina_str += "\n\n\n"
    #             whitemane_str = ""
    #             whitemane_str += "\nWCL.DB." + "Whitemane.Guilds = " + "{}" + "\n\n\n"
    #             for string in whitemane_strings: whitemane_str += string
    #             whitemane_str += "\n\n\n"
    #             zip_io = BytesIO()
    #             with zipfile.ZipFile(zip_io, 'w') as lua_zip:
    #                 lua_zip.writestr('Pagle.lua', pagle_str)
    #                 lua_zip.writestr('Faerlina.lua', faerlina_str)
    #                 lua_zip.writestr('Whitemane.lua', whitemane_str)
    #             zip_io.seek(0)
    #             st.download_button(
    #                 data = zip_io.getvalue(),
    #                 label = "AllServers.zip",
    #                 file_name = "lua_files.zip",
    #                 mime = 'application/zip',
    #                 use_container_width = True
    #             )
    #         with pagle_dl:
    #             f = ""
    #             f += "\nWCL.DB." + "Pagle.Guilds = " + "{}" + "\n\n\n"
    #             for string in pagle_strings: f += string
    #             f += "\n\n\n"
    #             st.download_button(
    #                 data = f,
    #                 label = "Pagle.lua",
    #                 file_name = "Pagle.lua",
    #                 use_container_width = True
    #             )
    #         with faerlina_dl:
    #             f = ""
    #             f += "\nWCL.DB." + "Faerlina.Guilds = " + "{}" + "\n\n\n"
    #             for string in faerlina_strings: f += string
    #             f += "\n\n\n"
    #             st.download_button(
    #                 data = f,
    #                 label = "Faerlina.lua",
    #                 file_name = "Faerlina.lua",
    #                 use_container_width = True
    #             )
    #         with whitemane_dl:
    #             f = ""
    #             f += "\nWCL.DB." + "Whitemane.Guilds = " + "{}" + "\n\n\n"
    #             for string in whitemane_strings: f += string
    #             f += "\n\n\n"
    #             st.download_button(
    #                 data = f,
    #                 label = "Whitemane.lua",
    #                 file_name = "Whitemane.lua",
    #                 use_container_width = True
    #             )
    #         hide_footer()
    #         #st.markdown("### ")
    #         #_, last_updated_col, _ = st.columns([0.2,0.6,0.2])
    #         last_updated_str = DB_REF.child("last_updated").get()
    #         st.info(f"_Last updated_ : {last_updated_str}")
    #         #hide_markdown_links()
    #         #with last_updated_col:
    #         #    last_updated_str = DB_REF.child("last_updated").get()
    #         #    st.info(f"Last updated: {last_updated_str}")
    #         #    hide_markdown_links()
        

    else:
        if USE_SEARCHBOX:
            if item is None:
                st.info("Searching for Titanium Ore - item was not specified correctly.")
                item = "Titanium Ore"
            #else:
                #st.session_state['search_items'] = {"result": None, "search": "", "options": []}
        if auto:
            if num_days <= 5:
                hide_original = False
                for i in [4,12,24,48,72]:
                    exec(f"ma{i} = False")
            elif num_days <= 30:
                ma4 = True
                hide_original = True
                for i in [12,24,48,72]:
                    exec(f"ma{i} = False")
            elif num_days <= 60:
                ma12 = True
                hide_original = True
                for i in [4,24,48,72]:
                    exec(f"ma{i} = False")
            elif num_days <= 120:
                ma24 = True
                hide_original = True
                for i in [4,12,48,72]:
                    exec(f"ma{i} = False")
            elif num_days <= 240:
                ma48 = True
                hide_original = True
                for i in [4,12,24,72]:
                    exec(f"ma{i} = False")
            else:
                ma72 = True
                hide_original = True
                for i in [4,12,24,48]:
                    exec(f"ma{i} = False")
        try:
            if candlestick:
                with st.spinner("Loading..."):
                    hide_footer()
                    ohlc_data, data_min, data_max = get_server_history_OHLC(item, server, faction, num_days)
                    title(item, chart_type, num_days)
                    chart = st.altair_chart(Plot.OHLC_chart2(item, server, faction, num_days, mobile=mobile), use_container_width=True)
                    #chart = st.altair_chart(Plot.OHLC_chart(ohlc_data, data_min, data_max, mobile=mobile), use_container_width=True)
            elif chart_type == "Price":
                if server_compare is None and faction_compare is None:
                    with st.spinner("Loading..."):
                        hide_footer()
                        price_data = get_server_history(item, server, faction, num_days)
                        title(item, chart_type, num_days)
                        if filter:
                            filter_window_length = int(len(price_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                            if filter_window_length == 0: filter_window_length = 1
                            price_data["prices"] = savgol_filter(price_data["prices"], filter_window_length, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                        chart = st.altair_chart(Plot.price_history(price_data, ma4, ma12, ma24, ma48, ma72, hide_original, mobile, regression_line=False), use_container_width=True)
                else:
                    with st.spinner("Loading..."):
                        hide_footer()
                        server1_data = get_server_history(item, server, faction, num_days)
                        server2_data = get_server_history(item, server_compare, faction_compare, num_days)
                        title(item, chart_type, num_days)
                        if filter:
                            filter_window_length1 = int(len(server1_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                            if filter_window_length1 == 0: filter_window_length1 = 1
                            filter_window_length2 = int(len(server2_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                            if filter_window_length2 == 0: filter_window_length2 = 1
                            server1_data["prices"] = savgol_filter(server1_data["prices"], filter_window_length1, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                            server2_data["prices"] = savgol_filter(server2_data["prices"], filter_window_length2, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                        chart = st.altair_chart(Plot.price_history_comparison(server1_data, server2_data, server, server_compare, ma4, ma12, ma24, ma48, ma72, hide_original, mobile, regression_line=False), use_container_width=True)
            elif chart_type == "Price & Region Price":
                with st.spinner("Loading..."):
                    hide_footer()
                    region_data = get_region_history(item, numDays=num_days)
                    server_data = get_server_history(item, server, faction, num_days)
                    title(item, chart_type, num_days)
                    if filter:
                        filter_window_length1 = int(len(server_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                        if filter_window_length1 == 0: filter_window_length1 = 1
                        filter_window_length2 = int(len(region_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                        if filter_window_length2 == 0: filter_window_length2 = 1
                        server_data["prices"] = savgol_filter(server_data["prices"], filter_window_length1, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                        region_data["prices"] = savgol_filter(region_data["prices"], filter_window_length2, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                    chart = st.altair_chart(Plot.price_and_region_history_comparison(server_data, region_data, server, ma4, ma12, ma24, ma48, ma72, hide_original, mobile, regression_line=False), use_container_width=True)
            elif chart_type == "Price & Quantity":
                with st.spinner("Loading..."):
                    hide_footer()
                    server_data = get_server_history(item, server, faction, num_days)
                    title(item, chart_type, num_days)
                    if filter:
                        filter_window_length1 = int(len(server_data["prices"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                        if filter_window_length1 == 0: filter_window_length1 = 1
                        filter_window_length2 = int(len(server_data["quantities"])*(SAVITZKY_GOLAY_FILTER_WINDOW_LENGTH_PCT/100))
                        if filter_window_length2 == 0: filter_window_length2 = 1
                        server_data["prices"] = savgol_filter(server_data["prices"], filter_window_length1, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                        server_data["quantities"] = savgol_filter(server_data["quantities"], filter_window_length2, SAVITZKY_GOLAY_FILTER_POLYNOMIAL_ORDER)
                    chart = st.altair_chart(Plot.price_and_quantity_history(server_data, ma4, ma12, ma24, ma48, ma72, hide_original, mobile, regression_line=False), use_container_width=True)
            if mobile:
                hide_element("button", "title", "View fullscreen")
            hide_markdown_links()
        
        except Exception as e:
            if api_offline():
                st.error("NexusHub API is currently offline.", icon="🚨")
            else: st.markdown(f"### Error: {e}")

            
hide_footer()   
hide_markdown_links()
