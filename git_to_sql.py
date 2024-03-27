import os
import json
import pandas as pd
# import psycopg2
import pymysql
from sqlalchemy import create_engine

# Define the path where your data files are stored
path= 'C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/aggregated/transaction/country/india/state/'

# List all files in the specified directory
Agg_state_list = os.listdir(path)

# Initialize an empty dictionary to store data
clm={'State': [], 'Year': [],'Quater': [],'Transacion_type': [], 'Transacion_count': [], 'Transacion_amount': []}

# Iterate through each file in the directory
for i in Agg_state_list:
    p_i=path+i+"/"
    Agg_yr=os.listdir(p_i)
    for j in Agg_yr:
        p_j=p_i+j+"/"
        Agg_yr_list=os.listdir(p_j)
        for k in Agg_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['transactionData']:
                Name=z['name']
                count=z['paymentInstruments'][0]['count']
                amount=z['paymentInstruments'][0]['amount']
                clm['Transacion_type'].append(Name)
                clm['Transacion_count'].append(count)
                clm['Transacion_amount'].append(amount)
                clm['State'].append(i)
                clm['Year'].append(j)
                clm['Quater'].append(int(k.strip('.json')))

# Create a DataFrame from the collected data
Agg_Trans=pd.DataFrame(clm)
Agg_Trans["State"] = Agg_Trans["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_Trans["State"] = Agg_Trans["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_Trans["State"] = Agg_Trans["State"].str.replace("-", " ")
Agg_Trans["State"] = Agg_Trans["State"].str.title()
print(Agg_Trans)


path2 = "C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/aggregated/user/country/india/state/"
Agg_user_list = os.listdir(path2)

clm={'State':[], 'Year':[],'Quater':[], 'Brand':[], 'Device_count':[] ,'Percentage':[]}

for i in Agg_user_list:
    p_i=path2+i+"/"
    Agg_yr=os.listdir(p_i)
    for j in Agg_yr:
        p_j=p_i+j+"/"
        Agg_yr_list=os.listdir(p_j)
        for k in Agg_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            try:
                for z in D['data']['usersByDevice']:
                    Name = z['brand']
                    count = z['count']
                    percentage = z["percentage"]
                    clm['Brand'].append(Name)
                    clm['Device_count'].append(count)
                    clm['Percentage'].append(percentage)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))
            except:
                pass

# Successfully created a DataFrame
Agg_device_list = pd.DataFrame(clm)
Agg_device_list["State"]=Agg_device_list["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_device_list["State"]=Agg_device_list["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_device_list["State"]=Agg_device_list["State"].str.replace("-"," ")
Agg_device_list["State"]=Agg_device_list["State"].str.title()

# print(Agg_device_list)

path3="C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/map/transaction/hover/country/india/state/"
Agg_map_data=os.listdir(path3)

clm={'State':[], 'Year':[],'Quater':[], 'District_name':[], 'Count':[] ,'Amount':[]}

for i in Agg_map_data:
    p_i=path3+i+"/"
    Agg_yr=os.listdir(p_i)
    for j in Agg_yr:
        p_j=p_i+j+"/"
        Agg_yr_list=os.listdir(p_j)
        for k in Agg_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            try:
                for z in D['data']['hoverDataList']:
                    Name = z['name']
                    count = z['metric'][0]["count"]
                    amount = z['metric'][0]["amount"]
                    clm['District_name'].append(Name)
                    clm['Count'].append(count)
                    clm['Amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    # clm['Quater'].append(int(k.strip('.json')))
                    clm['Quater'].append(int(k.strip('.json')))
            except:
                pass
Agg_district = pd.DataFrame(clm)
Agg_district["State"]=Agg_district["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_district["State"]=Agg_district["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_district["State"]=Agg_district["State"].str.replace("-"," ")
Agg_district["State"]=Agg_district["State"].str.title()
Agg_district["District_name"]=Agg_district["District_name"].str.title()


path4="C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/map/user/hover/country/india/state/"
Agg_registered_user=os.listdir(path4)

clm={'State':[], 'Year':[],'Quater':[], 'District_name':[], 'Registered_user':[] ,'App_open':[]}

for i in Agg_registered_user:
    p_i=path4+i+"/"
    Agg_yr=os.listdir(p_i)
    for j in Agg_yr:
        p_j=p_i+j+"/"
        Agg_yr_list=os.listdir(p_j)
        for k in Agg_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            try:
                for z in D['data']['hoverData'].items():
                    Name = z[0]
                    Registereduser = z[1]["registeredUsers"]
                    Appopen = z[1]["appOpens"]
                    clm['District_name'].append(Name)
                    clm['Registered_user'].append(Registereduser)
                    clm['App_open'].append(Appopen)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))
            except:
                pass


Agg_users = pd.DataFrame(clm)
Agg_users["State"]=Agg_users["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_users["State"]=Agg_users["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_users["State"]=Agg_users["State"].str.replace("-"," ")
Agg_users["State"]=Agg_users["State"].str.title()
Agg_users["District_name"]=Agg_users["District_name"].str.title()


path5="C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/top/transaction/country/india/state/"
Agg_pincode_list=os.listdir(path5)

clm={'State':[], 'Year':[],'Quater':[], 'Pincode':[], 'Count':[] ,'Amount':[]}

for i in Agg_pincode_list:
    p_i=path5+i+"/"
    Agg_yr=os.listdir(p_i)
    for j in Agg_yr:
        p_j=p_i+j+"/"
        Agg_yr_list=os.listdir(p_j)
        for k in Agg_yr_list:
            p_k=p_j+k
            # print("Processing file:", p_k)
            Data=open(p_k,'r')
            D=json.load(Data)
            try:
                for z in D['data']['pincodes']:
                # print("Processing pincode data:", z)
                    Pincode = z["entityName"]
                    Count = z["metric"]["count"]
                    Amount = z["metric"]["amount"]
                    clm['Pincode'].append(Pincode)
                    clm['Count'].append(Count)
                    clm['Amount'].append(Amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))
            except:
                pass
Agg_pincode = pd.DataFrame(clm)
# print(Agg_pincode["Quater"].unique())
# print("Shape of Agg_pincode data frame:", Agg_pincode.shape)

Agg_pincode["State"]=Agg_pincode["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_pincode["State"]=Agg_pincode["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_pincode["State"]=Agg_pincode["State"].str.replace("-"," ")
Agg_pincode["State"]=Agg_pincode["State"].str.title()

path6="C:/Users/souls/OneDrive/Desktop/Phonepe_pulse/pulse/data/top/user/country/india/state/"
Agg_userby_pincode_list=os.listdir(path6)

clm={'State':[], 'Year':[],'Quater':[], 'Pincode':[], 'Registered_User':[]}

for i in Agg_userby_pincode_list:
  p_i=path6+i+"/"
  Agg_yr=os.listdir(p_i)
  for j in Agg_yr:
    p_j=p_i+j+"/"
    Agg_yr_list=os.listdir(p_j)
    for k in Agg_yr_list:
        p_k=p_j+k
        Data=open(p_k,'r')
        D=json.load(Data)
        try:
          for z in D['data']['pincodes']:
            Pincode = z["name"]
            Count = z["registeredUsers"]
            clm['Pincode'].append(Pincode)
            clm['Registered_User'].append(Count)
            clm['State'].append(i)
            clm['Year'].append(j)
            clm['Quater'].append(int(k.strip('.json')))
        except:
          pass
Agg_user_pincode = pd.DataFrame(clm)
Agg_user_pincode["State"]=Agg_user_pincode["State"].str.replace('andaman-&-nicobar-islands','andaman & nicobar')
Agg_user_pincode["State"]=Agg_user_pincode["State"].str.replace('dadra-&-nagar-haveli-&-daman-&-diu','dadra and nagar haveli and daman and diu')
Agg_user_pincode["State"]=Agg_user_pincode["State"].str.replace("-"," ")
Agg_user_pincode["State"]=Agg_user_pincode["State"].str.title()


# Establish connection to your PostgreSQL database
host = "phonepe-pulse.cr6e2igouppo.ap-south-1.rds.amazonaws.com"
user = "admin"
password = "admin123"

# Establish connection to your AWS RDS MySQL database
conn = pymysql.connect(
    host=host,
    user=user,
    password=password
)

# Create a cursor object
cur = conn.cursor()

# Create engine for SQLAlchemy
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/Phonepe_pulse')

# Import Pandas DataFrames

# Push Pandas DataFrames into PostgreSQL
Agg_Trans.to_sql('aggregated_transaction', engine, if_exists='replace', index=False)
Agg_device_list.to_sql('aggregated_user', engine, if_exists='replace', index=False)
Agg_district.to_sql('trans_by_map', engine, if_exists='replace', index=False)
Agg_users.to_sql('user_by_map', engine, if_exists='replace', index=False)
Agg_pincode.to_sql('trans_by_pincode', engine, if_exists='replace', index=False)
Agg_user_pincode.to_sql('user_by_pincode', engine, if_exists='replace', index=False)

# Push Pandas DataFrames into PostgreSQL
# Commit the transaction and close the connection
conn.commit()
cur.close()
conn.close()
