import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import datetime as dt
sns.set(style='dark')


# membuat helper function
def create_byseason_df(df):
    rental_by_season  = day_df.groupby('season')['cnt'].sum().reset_index()
    # Mapping untuk musim
    season_mapping = {
        1: 'Spring',
        2: 'Summer',
        3: 'Fall',
        4: 'Winter'
    }
    rental_by_season['season'] = rental_by_season['season'].map(season_mapping)

    return rental_by_season

def create_byyear_df(df):
    rental_by_year  = day_df.groupby('yr')['cnt'].sum().reset_index()
    # Mapping untuk year
    year_mapping = {
        0: '2011',
        1: '2012',
    }
    rental_by_year['yr'] = rental_by_year['yr'].map(year_mapping)

    return rental_by_year

def create_byweathersit_df(df):
    # Menghitung jumlah sepeda yang disewakan untuk setiap kondisi cuaca
    rental_by_weather = day_df.groupby('weathersit')['cnt'].sum().reset_index()

    # Mapping untuk kondisi cuaca
    weather_mapping = {
        1: 'Clear',
        2: 'Mist',
        3: 'Light Snow/Rain',
        4: 'Heavy Snow/Rain'
    }

    rental_by_weather['weathersit'] = rental_by_weather['weathersit'].map(weather_mapping)

    return rental_by_weather


def create_rfm_df(df):
   # Menghitung nilai Recency, Frequency, dan Monetary
    snapshot_date = max(day_df['dteday']) + dt.timedelta(days=1)  # Tanggal snapshot setelah transaksi terakhir
    rfm_df = day_df.groupby('registered').agg({
        'dteday': lambda x: (snapshot_date - x.max()).days,  # Recency: berapa hari sejak pembelian terakhir
        'instant': 'nunique',  # Frequency: jumlah pembelian yang unik
        'cnt': 'sum'  # Monetary: total belanja
    }).reset_index()

    # Mengganti nama kolom
    rfm_df.columns = ['registered', 'recency', 'frequency', 'monetary']

    return rfm_df

day_df = pd.read_csv("main_data.csv")

datetime_columns = ["dteday",]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

# Membuat Komponen Filter
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()
 
with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

# memanggil helper function
byseason_df = create_byseason_df(main_df)
byyear_df = create_byyear_df(main_df)
byweathersit_df = create_byweathersit_df(main_df)
rfm_df = create_rfm_df(main_df)

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing Dashboard :sparkles:')

# Chart berdasarkan season
st.subheader("Total Rental Based on Season")
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(
    y='cnt', 
    x='season', 
    data=byseason_df.sort_values(by='cnt', ascending=False)
)
plt.title('Number of Rental by Season')
plt.xlabel('Season')
plt.ylabel('Rental Count')
plt.tick_params(axis='x', labelsize=12)
st.pyplot(fig)


# Chart berdasarkan tahun
st.subheader("Total Rental Trend Based on Year")
fig, ax = plt.subplots(figsize=(16, 8))
plt.plot(
    byyear_df['yr'], 
    byyear_df['cnt'], 
    marker='o', 
    linewidth=2, 
    color="#72BCD4"
)
plt.title('Number of Rental by Year')
plt.xlabel('Year')
plt.ylabel('Rental Count')
plt.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

# berdasarkan weather
st.subheader("Total Rental Based on Weather")

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(
    y='cnt', 
    x='weathersit',
    data=byweathersit_df.sort_values(by='cnt', ascending=False),
)
plt.title('Number of Rental by Weather Condition')
plt.xlabel('Weather Condition')
plt.ylabel('Rental Count')
st.pyplot(fig)


# Scatter plot untuk temperatur (temp) terhadap jumlah rental (cnt) 
st.subheader("Temperature vs Rental Count")
fig, ax = plt.subplots(figsize=(16, 8))
sns.scatterplot(x='temp', y='cnt', data=day_df)
plt.title('Temperature vs Rental Count')
st.pyplot(fig)

# Scatter plot untuk temperatur perasaan (atemp) terhadap jumlah rental (cnt)    
st.subheader("Feels-like Temperature vs Rental Count")
fig, ax = plt.subplots(figsize=(16, 8))  
sns.scatterplot(x='atemp', y='cnt', data=day_df)
plt.title('Feels-like Temperature vs Rental Count')
st.pyplot(fig)


# Scatter plot untuk kelembaban (hum) terhadap jumlah rental (cnt)
st.subheader("Humidity vs Rental Count")
fig, ax = plt.subplots(figsize=(16, 8))   
sns.scatterplot(x='hum', y='cnt', data=day_df)
plt.title('Humidity vs Rental Count')
st.pyplot(fig)

# Scatter plot untuk kecepatan angin (windspeed) terhadap jumlah rental (cnt)
st.subheader("Windspeed vs Rental Count")
fig, ax = plt.subplots(figsize=(16, 8))      
sns.scatterplot(x='windspeed', y='cnt', data=day_df)
plt.title('Windspeed vs Rental Count')
plt.tight_layout()
st.pyplot(fig)


# rfm analysis
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(16, 8))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="registered", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('registered')
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
 
sns.barplot(y="frequency", x="registered", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('registered')
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
 
sns.barplot(y="monetary", x="registered", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel('registered')
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
 
plt.suptitle("Best Customer Based on RFM Parameters (registered)", fontsize=20)
st.pyplot(fig)

