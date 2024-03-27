import streamlit as st
import json
import requests
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import plotly.express as px
import matplotlib.pyplot as plt
import PIL
from PIL import Image
import psycopg2
import pymysql

# Connect to PostgreSQL database
host = "phonepe-pulse.cr6e2igouppo.ap-south-1.rds.amazonaws.com"
user = "admin"
password = "admin123"

# Establish connection to your AWS RDS MySQL database
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database="Phonepe_pulse"
)

# Create a cursor object
cur = conn.cursor()

# Create engine for SQLAlchemy
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/Phonepe_pulse')

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

    # Option menu
    select = st.radio("Select Option", ["India", "States", "Top categories"], index=0)

    if select == "India":
        tab1, tab2 = st.columns(2)

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
            df_transactions.set_index('State', inplace=True)  # Set 'State' column as index

            # st.dataframe(df_transactions)

            cur.execute(
                f'SELECT State, Transacion_amount,Transacion_count FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
            result_two = cur.fetchall()
            df_two = pd.DataFrame(np.array(result_two), columns=["State", "Transaction_amount", "Transaction_count"])
            df_for_rp_index_result2 = df_two.set_index(pd.Index(range(1, len(df_two) + 1)))
            # st.dataframe(df_for_rp_index_result2)

            cur.execute(
                f'SELECT Sum(Transacion_amount),AVG(Transacion_amount) FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
            result_3 = cur.fetchall()
            df_three = pd.DataFrame(np.array(result_3), columns=["Sum of Transaction_amount", "Avg_Transaction_amt"])
            df_for_rp_index_result3 = df_three.set_index(pd.Index(range(1, len(df_three) + 1)))
            # st.dataframe(df_for_rp_index_result3)

            cur.execute(
                f'SELECT Sum(Transacion_count),AVG(Transacion_count) FROM aggregated_transaction WHERE Year="{trans_year}" AND Quater ="{trans_qtr}" AND Transacion_type="{trans_type}";')
            result_4 = cur.fetchall()
            df_four = pd.DataFrame(np.array(result_4),
                                   columns=["Sum of Transaction_count", "Avg_Transaction_count"])
            df_for_rp_index_result4 = df_four.set_index(pd.Index(range(1, len(df_three) + 1)))
            # st.dataframe(df_for_rp_index_result4)

            # df_in_tr_tab_qry_rslt1.drop(columns=['State'], inplace=True)

            url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
            response = requests.get(url)
            data = json.loads(response.content)

            # Create DataFrame from GeoJSON data
            df_geojson = pd.DataFrame([{"State": feature['properties']['ST_NM']} for feature in data['features']])
            df_geojson.set_index('State', inplace=True)  # Set 'State' column as index

            # Merge transaction data with GeoJSON data
            df_merged = df_geojson.join(df_transactions)

            # Plot choropleth map
            fig = px.choropleth(df_merged,
                                geojson=data,
                                featureidkey='properties.ST_NM',
                                locations=df_merged.index,
                                color='Transaction_amount',
                                color_continuous_scale='thermal',
                                title='Transaction Analysis')
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(title_font=dict(size=37), title_font_color='#AD71EF', height=800)
            st.plotly_chart(fig, use_container_width=True)


# Here we continue from the last point of the code provided

#INSIGHTS TAB
if selected == "Insights":
    st.title(':violet[BASIC INSIGHTS]')
    st.subheader("The basic insights are derived from the Analysis of the Phonepe Pulse data. It provides a clear idea about the analysed data.")
    options = ["--select--",
               "Top 10 states based on year and amount of transaction",
               "Least 10 states based on year and amount of transaction",
               "Top 10 States and Districts based on Registered Users",
               "Least 10 States and Districts based on Registered Users",
               "Top 10 Districts based on the Transaction Amount",
               "Least 10 Districts based on the Transaction Amount",
               "Top 10 Districts based on the Transaction count",
               "Least 10 Districts based on the Transaction count",
               "Top Transaction types based on the Transaction Amount",
               "Top 10 Mobile Brands based on the User count of transaction"]
    select = st.selectbox(":violet[Select the option]", options)

    #1
    if select == "Top 10 states based on year and amount of transaction":
        cur.execute("SELECT DISTINCT State,Year, SUM(Transacion_amount) AS Total_Transaction_Amount FROM aggregated_transaction GROUP BY State,Year ORDER BY Total_Transaction_Amount DESC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'Year', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 states based on amount of transaction")
            # st.bar_chart(data=df, x="Transaction_amount", y="States")
            st.bar_chart(data=df, x="States", y="Transaction_amount", color="#ff0000", width=0, height=0, use_container_width=True)

    #2
    elif select == "Least 10 states based on year and amount of transaction":
        cur.execute("SELECT DISTINCT State, SUM(Transacion_amount) as Total FROM aggregated_transaction GROUP BY State ORDER BY Total ASC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 states based on amount of transaction")
            st.bar_chart(data=df, x="States", y="Transaction_amount",color="#ff0000")

    #3
    elif select == "Top 10 States and Districts based on Registered Users":
        cur.execute(
            "SELECT DISTINCT State, SUM(Registered_User) AS Users FROM user_by_pincode GROUP BY State ORDER BY Users DESC LIMIT 10")
        data = cur.fetchall()
        columns = ['State', 'Registered_User']
        df = pd.DataFrame(data, columns=columns)
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            fig = px.pie(df, values='Registered_User', names='State',
                         title='Top 10 States and Districts based on Registered Users')

            # Display the pie chart
            st.plotly_chart(fig)


    #4
    elif select == "Least 10 States and Districts based on Registered Users":
        cur.execute(
            "SELECT DISTINCT State, Pincode, SUM(Registered_User) AS Users FROM user_by_pincode GROUP BY State ORDER BY Users ASC LIMIT 10")
        data = cur.fetchall()
        columns = ['State', 'District_Pincode', 'Registered_User']
        df = pd.DataFrame(data, columns=columns)

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            fig = px.bar(df, x='State', y='Registered_User', color='State')
            fig.update_layout(title="Least 10 States and Districts based on Registered Users")
            st.plotly_chart(fig)

    #5
    elif select == "Top 10 Districts based on the Transaction Amount":
        cur.execute("SELECT DISTINCT State ,Pincode,SUM(Amount) AS Total FROM trans_by_pincode GROUP BY State ,Pincode ORDER BY Total DESC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'District', 'Transaction_Amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))
        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            fig=px.bar(df,x="States",y="Transaction_Amount",color="States")
            fig.update_layout(title="Top 10 Districts based on Transaction Amount")
            st.plotly_chart(fig)

    #6
    elif select == "Least 10 Districts based on the Transaction Amount":
        cur.execute("SELECT DISTINCT State,District,SUM(Transaction_amount) AS Total FROM map_transaction GROUP BY State, District ORDER BY Total ASC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'District', 'Transaction_amount']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Least 10 Districts based on Transaction Amount")
            st.bar_chart(data=df, x="District", y="Transaction_amount")

    #7
    elif select == "Top 10 Districts based on the Transaction count":
        cur.execute("SELECT DISTINCT State,District,SUM(Transaction_Count) AS Counts FROM map_transaction GROUP BY State ,District ORDER BY Counts DESC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on Transaction Count")
            st.bar_chart(data=df, x="Transaction_Count", y="District")

    #8
    elif select == "Least 10 Districts based on the Transaction count":
        cur.execute("SELECT DISTINCT State ,District,SUM(Transaction_Count) AS Counts FROM map_transaction GROUP BY State ,District ORDER BY Counts ASC LIMIT 10")
        data = cur.fetchall()
        columns = ['States', 'District', 'Transaction_Count']
        df = pd.DataFrame(data, columns=columns, index=range(1, len(data) + 1))

        col1, col2 = st.columns(2)
        with col1:
            st.write(df)
        with col2:
            st.title("Top 10 Districts based on the Transaction Count")
            st.bar_chart(data=df, x="Transaction_Count", y="District")

    #9
    # elif select == "Top Transaction types based on the Transaction Amount":
    #     cursor.execute("SELECT DISTINCT Transaction_type, SUM(Transaction_amount) AS Amount FROM aggregated_transaction GROUP BY Transaction_type ORDER BY Amount DESC






