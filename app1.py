import streamlit as st
import json
import requests
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.express as px
import pymysql

# Function to establish database connection
def get_database_connection():
    host = "phonepe-pulse.cr6e2igouppo.ap-south-1.rds.amazonaws.com"
    user = "admin"
    password = "admin123"
    return pymysql.connect(host=host, user=user, password=password, database="Phonepe_pulse")

# Function to execute SQL query
def execute_query(conn, query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

# Function to fetch data from database and create DataFrame
def fetch_data_to_dataframe(conn, query, columns):
    data = execute_query(conn, query)
    return pd.DataFrame(data, columns=columns)

# Function to fetch GeoJSON data
@st.cache
def fetch_geojson_data():
    url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(url)
    return response.json()

# Function to create choropleth map
def create_choropleth_map(df, geojson_data, title, color_column, location_column='State'):
    fig = px.choropleth(df, geojson=geojson_data, locations=location_column, color=color_column,
                        color_continuous_scale='thermal', title=title)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
    return fig
def fetch_transaction_data(cursor,state, year, quarter_tr):
    cursor.execute(f"SELECT Transacion_type, Transacion_amount FROM aggregated_transaction WHERE State = '{state}' AND Year = '{year}' AND Quater = '{quarter_tr}';")
    return cursor.fetchall()


# Define a function to fetch user data based on state and year
def fetch_user_data(cursor,state, year):
    cursor.execute(f"SELECT Quater, SUM(Registered_user) FROM user_by_map WHERE State = '{state}' AND Year = '{year}' GROUP BY Quater;")
    return cursor.fetchall()

# Main function
def main():
    conn = get_database_connection()
    cur = conn.cursor()

    # Streamlit layout
    st.set_page_config(layout="wide")
    selected = option_menu(None,
                           options=["Analysis", "Insights", ],
                           icons=["bar-chart", "at"],
                           default_index=0,
                           orientation="horizontal",
                           styles={"container": {"width": "100%"},
                                   "icon": {"color": "white", "font-size": "24px"},
                                   "nav-link": {"font-size": "24px", "text-align": "center", "margin": "-2px"},
                                   "nav-link-selected": {"background-color": "#6F36AD"}})

    if selected == "Analysis":
        st.title(':red[ANALYSIS]')
        st.header('Analysis for Indian States from 2018 to 2023')
        select = st.radio("Select Option", ["India", "States", "Top categories"], index=0)

        if select == "India":
            tab1, tab2 = st.tabs(["TRANSACTION", "USER"])

            with tab1:
                trans_year = st.selectbox('**Select Transaction Year**',
                                          ('2018', '2019', '2020', '2021', '2022', '2023'),
                                          key='trans_year')
                trans_qtr = st.selectbox("**Select the Quarter**", ('1', '2', '3', '4'), key='trans_qtr')
                trans_type = st.selectbox("**Select the Transactions type**",
                                          ('Financial Services', 'Merchant payments', 'Recharge & bill payments',
                                           'Peer-to-peer payments', 'Others'), key="trans_type")
                # Query
                cur.execute(
                    f'SELECT State,Transacion_amount FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
                result_one = cur.fetchall()
                df_transactions = pd.DataFrame(result_one, columns=['State', 'Transaction_amount'])
                df_transactions1 = df_transactions.set_index(pd.Index(range(1, len(df_transactions) + 1)))
                cur.execute(
                    f'SELECT State, Transacion_amount,Transacion_count FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
                result_two = cur.fetchall()
                df_two = pd.DataFrame(np.array(result_two),
                                      columns=["State", "Transaction_amount", "Transaction_count"])
                df_for_rp_index_result2 = df_two.set_index(pd.Index(range(1, len(df_two) + 1)))
                # st.dataframe(df_for_rp_index_result2)

                cur.execute(
                    f'SELECT Sum(Transacion_amount),AVG(Transacion_amount) FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
                result_3 = cur.fetchall()
                df_three = pd.DataFrame(np.array(result_3),
                                        columns=["Sum of Transaction_amount", "Avg_Transaction_amt"])
                df_for_rp_index_result3 = df_three.set_index(pd.Index(range(1, len(df_three) + 1)))
                # st.dataframe(df_for_rp_index_result3)

                cur.execute(
                    f'SELECT Sum(Transacion_count),AVG(Transacion_count) FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
                result_4 = cur.fetchall()
                df_four = pd.DataFrame(np.array(result_4),
                                       columns=["Sum of Transaction_count", "Avg_Transaction_count"])
                df_for_rp_index_result4 = df_four.set_index(pd.Index(range(1, len(df_three) + 1)))
                df_transactions.drop(columns=['State'], inplace=True)

                url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
                geojson_response = requests.get(url)
                geojson_data = geojson_response.json()

                # Extract state names and sort them in alphabetical order
                state_names = sorted(feature['properties']['ST_NM'] for feature in geojson_data['features'])

                # Create a DataFrame from GeoJSON data
                df_geojson = pd.DataFrame({'State': state_names})
                df_transactions.rename(columns={'State': 'State'}, inplace=True)

                # Merge transaction data with GeoJSON data
                df_merged = df_geojson.merge(df_transactions1, on='State', how='left').fillna(0)

                # Create choropleth map
                fig_tra = px.choropleth(
                    df_merged,
                    geojson=geojson_data,
                    featureidkey='properties.ST_NM',
                    locations='State',  # Make sure this matches the column name in df_merged
                    color='Transaction_amount',
                    color_continuous_scale='thermal',
                    title='Transaction Analysis'
                )
                fig_tra.update_geos(fitbounds="locations", visible=False)
                fig_tra.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)

                # Display choropleth map
                st.plotly_chart(fig_tra, use_container_width=True)
                                # ---------   /   All India Transaction Analysis Bar chart  /  ----- #
                df_transactions1['State'] = df_transactions1['State'].astype(str)
                df_transactions1['Transaction_amount'] = df_transactions1['Transaction_amount'].astype(float)

                fig = px.bar(df_transactions1, x='State', y='Transaction_amount',
                             color='Transaction_amount', color_continuous_scale='thermal',
                             title='Transaction Analysis Chart', height=700)

                fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')

                # Set x-axis tick labels to state names
                fig.update_xaxes(tickvals=df_transactions1['State'], ticktext=df_transactions1['State'])

                # Display the plot
                st.plotly_chart(fig, use_container_width=True)

                st.header(':violet[Total calculation]')

                # Create columns layout
                cols = st.columns(1)
                col4 = cols[0]
                with col4:
                    st.subheader(':violet[Transaction Analysis]')
                    st.dataframe(df_two)
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    user_year = st.selectbox('**Select Transaction Year**',
                                             ('2018', '2019', '2020', '2021', '2022', '2023'),
                                             key='user_year')
                with col2:
                    user_qtr = st.selectbox("**Select the Quarter**", ('1', '2', '3', '4'), key='user_qtr')

                cur.execute(
                    f"SELECT State, SUM(Registered_user) FROM user_by_map WHERE Year = '{user_year}' AND Quater = '{user_qtr}' GROUP BY State;")
                result5 = cur.fetchall()
                result_five = pd.DataFrame(np.array(result5), columns=['State', 'Registered_user'])
                res_five_index = result_five.set_index(pd.Index(range(1, len(result_five) + 1)))
                cur.execute(
                    f"SELECT SUM(Registered_user), AVG(Registered_user) FROM user_by_map WHERE Year = '{user_year}' AND Quater = '{user_qtr}';")
                result6 = cur.fetchall()
                result_six = pd.DataFrame(np.array(result6), columns=['Total', 'Average'])
                result_six_index = result_six.set_index(['Average'])

                result_five.drop(columns=['State'], inplace=True)
                # Clone the gio data
                url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
                response = requests.get(url)
                data2 = json.loads(response.content)
                # Extract state names and sort them in alphabetical order
                state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
                state_names_use.sort()
                # Create a DataFrame with the state names column
                df_state_names_use = pd.DataFrame({'State': state_names_use})
                # Combine the Gio State name with df_in_tr_tab_qry_rslt
                df_state_names_use['Registered_user'] = result_five
                # convert dataframe to csv file
                df_state_names_use.to_csv('State_user.csv', index=False)
                # Read csv
                df_use = pd.read_csv('State_user.csv')
                # Geo plot
                fig_use = px.choropleth(
                    df_use,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM', locations='State', color='Registered_user',
                    color_continuous_scale='thermal', title='User Analysis')
                fig_use.update_geos(fitbounds="locations", visible=False)
                fig_use.update_layout(title_font=dict(size=33), title_font_color='#AD71EF', height=800)
                st.plotly_chart(fig_use, use_container_width=True)

                res_five_index['State'] = res_five_index['State'].astype(str)
                res_five_index['Registered_user'] = res_five_index['Registered_user'].astype(int)
                df_res_five = px.bar(res_five_index, x='State', y='Registered_user', color='Registered_user',
                                     color_continuous_scale='thermal', title='User Analysis Chart',
                                     height=700, )
                df_res_five.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                st.plotly_chart(df_res_five, use_container_width=True)

                # -----   /   All India Total User calculation Table   /   ----- #
                st.header(':violet[Total calculation]')

                col3, col4 = st.columns(2)
                with col3:
                    st.subheader(':violet[User Analysis]')
                    st.dataframe(res_five_index)
                with col4:
                    st.subheader(':violet[User Count]')
                    st.dataframe(result_six_index)
        if select == "States":
            tab1, tab2 = st.tabs(["TRANSACTION", "USER"])
            with tab1:
                st.header("Transaction Analysis")
                state_tr = st.selectbox('Select State', (
                    'Andaman & Nicobar',
                    'Andhra Pradesh',
                    'Arunachal Pradesh',
                    'Assam',
                    'Bihar',
                    'Chandigarh',
                    'Chhattisgarh',
                    'Dadra And Nagar Haveli And Daman And Diu',
                    'Delhi',
                    'Goa',
                    'Gujarat',
                    'Haryana',
                    'Himachal Pradesh',
                    'Jammu & Kashmir',
                    'Jharkhand',
                    'Karnataka',
                    'Kerala',
                    'Ladakh',
                    'Lakshadweep',
                    'Madhya Pradesh',
                    'Maharashtra',
                    'Manipur',
                    'Meghalaya',
                    'Mizoram',
                    'Nagaland',
                    'Odisha',
                    'Puducherry',
                    'Punjab',
                    'Rajasthan',
                    'Sikkim',
                    'Tamil Nadu',
                    'Telangana',
                    'Tripura',
                    'Uttar Pradesh',
                    'Uttarakhand',
                    'West Bengal'
                ), key='state_selectbox')

                year_tr = st.selectbox('Select Year', ('2018', '2019', '2020', '2021', '2022','2023'))
                quarter_tr = st.selectbox('Select Quarter', ('1', '2', '3', '4'))

                cursor = conn.cursor()

                # Call the fetch_transaction_data function with the cursor object
                transaction_data = fetch_transaction_data(cursor, state_tr, year_tr, quarter_tr)

                # Close the cursor after fetching the data
                cursor.close()
                df_transaction = pd.DataFrame(transaction_data, columns=['Transaction_type', 'Transaction_amount'])

                st.write("Transaction Data:")
                st.write(df_transaction)
                df_transaction['pull'] = [0, 0.2, 0.2, 0.2,0.2]
                # Adjust the pull values as needed

                # Create the pie chart without using the pull parameter
                fig_tr = px.pie(df_transaction, values="Transaction_amount", names="Transaction_type")

                # Update the layout to include the pull values
                fig_tr.update_traces(pull=df_transaction['pull'])

                st.plotly_chart(fig_tr)
            with tab2:
                st.header("User Analysis")
                state_us = st.selectbox('Select State', (
                    'Andaman & Nicobar',
                    'Andhra Pradesh',
                    'Arunachal Pradesh',
                    'Assam',
                    'Bihar',
                    'Chandigarh',
                    'Chhattisgarh',
                    'Dadra And Nagar Haveli And Daman And Diu',
                    'Delhi',
                    'Goa',
                    'Gujarat',
                    'Haryana',
                    'Himachal Pradesh',
                    'Jammu & Kashmir',
                    'Jharkhand',
                    'Karnataka',
                    'Kerala',
                    'Ladakh',
                    'Lakshadweep',
                    'Madhya Pradesh',
                    'Maharashtra',
                    'Manipur',
                    'Meghalaya',
                    'Mizoram',
                    'Nagaland',
                    'Odisha',
                    'Puducherry',
                    'Punjab',
                    'Rajasthan',
                    'Sikkim',
                    'Tamil Nadu',
                    'Telangana',
                    'Tripura',
                    'Uttar Pradesh',
                    'Uttarakhand',
                    'West Bengal'
                ))

                year_us = st.selectbox('Select Year', ('2018', '2019', '2020', '2021', '2022','2023'), key='year_selectbox')
                cursor = conn.cursor()

                user_data = fetch_user_data(cursor,state_us, year_us)
                cursor.close()
                df_user = pd.DataFrame(user_data, columns=['Quarter', 'User_Count'])

                st.write("User Data:")
                st.write(df_user)

                    # Visualize user data
                fig_us = px.bar(df_user, x='Quarter', y='User_Count', color='User_Count',
                                    color_continuous_scale='thermal',
                                    title='User Analysis Chart')
                st.plotly_chart(fig_us)

        if select == "Top categories":
            tab5, tab6 = st.tabs(["TRANSACTION", "USER"])
            with tab5:
                top_tr_yr = st.selectbox('**Select Year**', ('2018', '2019', '2020', '2021', '2022','2023'),
                                             key='top_tr_yr')

                    # SQL QUERY

                    # Top Transaction Analysis bar chart query
                cur.execute(
                    f'SELECT State, SUM(Transacion_amount) FROM aggregated_transaction WHERE Year="{top_tr_yr}" GROUP BY State ORDER BY Transacion_amount DESC LIMIT 10')
                result_top = cur.fetchall()
                df_top = pd.DataFrame(np.array(result_top),
                                      columns=["State", "Top Transaction amount"])
                df_top_index = df_top.set_index(pd.Index(range(1, len(df_top) + 1)))
                    # Top Transaction Analysis table query
                cur.execute(
                        f"SELECT State, SUM(Transacion_amount) as Transaction_amount, SUM(Transacion_count) as Transaction_count FROM aggregated_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
                result_tr= cur.fetchall()
                df_rslt = pd.DataFrame(np.array(result_tr),
                                                               columns=['State', 'Top Transaction amount',
                                                                        'Total Transaction count'])
                df_rslt_index = df_rslt.set_index(pd.Index(range(1, len(df_rslt) + 1)))



                df_top_index['State'] = df_top_index['State'].astype(str)
                df_top_index['Top Transaction amount'] = df_top_index[
                    'Top Transaction amount'].astype(float)
                df_fig1 = px.bar(df_top_index, x='State', y='Top Transaction amount',
                                                     color='Top Transaction amount', color_continuous_scale='thermal',
                                                     title='Top Transaction Analysis Chart', height=600, )
                df_fig1.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                st.plotly_chart(df_fig1, use_container_width=True)

                # All India Total Transaction calculation Table
                st.header(':violet[Total calculation]')
                st.subheader('Top Transaction Analysis')
                st.dataframe(df_top_index)
            with tab6:
                top_us_yr=st.selectbox('**Select Year**',('2018','2019','2020','2021','2022','2023'),key='top_us_yr')

                cur.execute(
                    f"SELECT State,SUM(Registered_user) AS Top_User FROM user_by_map WHERE Year = '{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10")
                result6 = cur.fetchall()
                result_six = pd.DataFrame(np.array(result6), columns=['State', 'Top_user'])
                df_six_index = result_six.set_index(
                    pd.Index(range(1, len(result_six) + 1)))
                st.markdown("From 2018 to 2023 the user base in <span style='color:blue'>Maharashtra</span>, <span style='color:blue'>Uttar Pradesh</span> is increased by 7 times.", unsafe_allow_html=True)

                df_six_index['State'] = df_six_index['State'].astype(str)
                df_six_index['Top_user'] = df_six_index['Top_user'].astype(float)
                df_top_usser_fig = px.bar(df_six_index, x='State', y='Top_user',
                                                     color='Top_user', color_continuous_scale='thermal',
                                                     title='Top User Analysis Chart', height=600, )
                df_top_usser_fig.update_layout(title_font=dict(size=33), title_font_color='#AD71EF')
                st.plotly_chart(df_top_usser_fig, use_container_width=True)
                st.subheader(
                    "From 2018 to 2023 the user base in Maharashtra, Uttar Pradesh is increased by 7 times ")

                # All India Total Transaction calculation Table
                st.header(':violet[Total calculation]')
                st.subheader('violet[Total User Analysis]')
                st.dataframe(df_six_index)

            # Analysis code goes here...

    if selected == "Insights":
        st.title(':violet[BASIC INSIGHTS]')
        st.subheader("The basic insights are derived from the Analysis of the Phonepe Pulse data. It provides a clear idea about the analysed data.")
        options = ["--select--",
                   "Top 10 states based on amount of transaction",
                   "Least 10 states based on amount of transaction",
                   "Top 10 States and Districts based on Registered Users",
                   "Least 10 States and Districts based on Registered Users",
                   "Top 10 Districts based on the Transaction Amount",
                   "Least 10 Districts based on the Transaction Amount",
                   "Top 10 Districts based on the Transaction count",
                   "Least 10 Districts based on the Transaction count",
                   "Top Transaction types based on the Transaction Amount",
                   "Top 10 Mobile Brands based on the User count of transaction"]
        select = st.selectbox(":violet[Select the option]", options)

        if select == "Top 10 states based on amount of transaction":
            cur.execute(
                "SELECT DISTINCT State, SUM(Transacion_amount) AS Total_Transaction_Amount FROM aggregated_transaction GROUP BY State ORDER BY Total_Transaction_Amount DESC LIMIT 10")
            data = cur.fetchall()
            columns = ['States', 'Transaction_amount']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                st.title("Top 10 states based on amount of transaction")
                # st.bar_chart(data=df, x="Transaction_amount", y="States")
                st.bar_chart(data=df, x="States", y="Transaction_amount", color="Transaction_amount", width=0, height=0,
                             use_container_width=True)

        # 2
        elif select == "Least 10 states based on amount of transaction":
            cur.execute(
                "SELECT DISTINCT State, SUM(Transacion_amount) as Total FROM aggregated_transaction GROUP BY State ORDER BY Total ASC LIMIT 10")
            data = cur.fetchall()
            columns = ['States', 'Transaction_amount']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                st.title("Least 10 states based on amount of transaction")
                st.bar_chart(data=df, x="States", y="Transaction_amount", color="Transaction_amount")

        # 3
        elif select == "Top 10 States and Districts based on Registered Users":
            cur.execute(
                "SELECT DISTINCT State,District_name, SUM(Registered_User) AS Users FROM user_by_map GROUP BY State ORDER BY Users DESC LIMIT 10;")
            data = cur.fetchall()
            columns = ['State', 'District_name', 'Registered_User']
            df = pd.DataFrame(data, columns=columns)
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.bar(df, x='State', y='Registered_User', color='District_name')
                fig.update_layout(title="Top 10 States and Districts based on Registered Users")
                st.plotly_chart(fig)

        # 4
        elif select == "Least 10 States and Districts based on Registered Users":
            cur.execute(
                "SELECT DISTINCT State,District_name, SUM(Registered_User) AS Users FROM user_by_map GROUP BY State ORDER BY Users ASC LIMIT 10")
            data = cur.fetchall()
            columns = ['State', 'District_name', 'Registered_User']
            df = pd.DataFrame(data, columns=columns)

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.bar(df, x='State', y='Registered_User', color='District_name')
                fig.update_layout(title="Least 10 States and Districts based on Registered Users")
                st.plotly_chart(fig)

        # 5
        elif select == "Top 10 Districts based on the Transaction Amount":
            cur.execute(
                "SELECT DISTINCT State ,District_name,SUM(Amount) AS Total FROM trans_by_map GROUP BY State ,District_name ORDER BY Total DESC LIMIT 10;")
            data = cur.fetchall()
            columns = ['States', 'District_name', 'Transaction_Amount']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.bar(df, x="States", y="Transaction_Amount", color="District_name")
                fig.update_layout(title="Top 10 Districts based on Transaction Amount")
                st.plotly_chart(fig)

        # 6
        elif select == "Least 10 Districts based on the Transaction Amount":
            cur.execute(
                "SELECT DISTINCT State ,District_name,SUM(Amount) AS Total FROM trans_by_map GROUP BY State ,District_name ORDER BY Total ASC LIMIT 10")
            data = cur.fetchall()
            columns = ['States', 'District_name', 'Transaction_amount']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                st.title("Least 10 Districts based on Transaction Amount")
                st.bar_chart(data=df, x="District_name", y="Transaction_amount", color="States")

        # 7
        elif select == "Top 10 Districts based on the Transaction count":
            cur.execute(
                "SELECT DISTINCT State,District_name as District,SUM(Count) AS Transaction_Count FROM trans_by_map GROUP BY State ,District ORDER BY Transaction_Count DESC LIMIT 10")
            data = cur.fetchall()
            columns = ['States', 'District', 'Transaction_Count']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.bar(df, x="District", y="Transaction_Count", color="States")
                fig.update_layout(title="Top 10 Districts based on Transaction Count")
                st.plotly_chart(fig)
        # 8
        elif select == "Least 10 Districts based on the Transaction count":
            cur.execute(
                "SELECT DISTINCT State,District_name as District,SUM(Count) AS Transaction_Count FROM trans_by_map GROUP BY State ,District ORDER BY Transaction_Count ASC LIMIT 10")
            data = cur.fetchall()
            columns = ['States', 'District', 'Transaction_Count']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.bar(df, x="States", y="Transaction_Count", color="District")
                fig.update_layout(title="Least 10 Districts based on the Transaction count")
                st.plotly_chart(fig)
        elif select == "Top Transaction types based on the Transaction Amount":
            cur.execute(
                "SELECT DISTINCT Transacion_type,SUM(Transacion_amount) AS Amount FROM aggregated_transaction GROUP BY Transacion_type ORDER BY Amount DESC")
            data = cur.fetchall()
            columns = ['Transaction_type', 'Amount']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.pie(df, values="Amount", names="Transaction_type")
                fig.update_layout(title="Top Transaction types based on the Transaction Amount")
                st.plotly_chart(fig)
        elif select == "Top 10 Mobile Brands based on the User count of transaction":
            cur.execute(
                "SELECT DISTINCT Brand,SUM(Device_count) AS Count FROM aggregated_user GROUP BY Brand ORDER BY Count DESC LIMIT 10")
            data = cur.fetchall()
            columns = ['Brand', 'Count']
            df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

            col1, col2 = st.columns(2)
            with col1:
                st.write(df)
            with col2:
                fig = px.pie(df, values="Count", names="Brand")
                fig.update_layout(title="Top 10 Mobile Brands based on the User count of transaction")
                st.plotly_chart(fig)
            cur.close()
            conn.close()

# Entry point of the application
if __name__ == "__main__":
    main()
