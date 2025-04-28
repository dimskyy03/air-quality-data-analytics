import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set_style("whitegrid")

st.title("Air Quality Dashboard")

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv("cleaned_air_quality_data.csv")
    return data

df = load_data()
# convert column year, month, day, hour to datetime without hour in one column
df['Date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']].astype(str), format='%Y-%m-%d-%H')

#place date column as first column
df = df[['Date'] + [col for col in df.columns if col != 'Date']]


st.sidebar.header("Display Data:")
selected_display = st.sidebar.selectbox("Select data to display", ("Daily", "Monthly", "Yearly"), key="data_display")


# function sidebar for select pollutants
def selected_pollutants(df):
    st.sidebar.header("Select Pollutants")
    pollutants = df.columns[6:12]  # Assuming the first column is 'Date'
    selected_pollutants = st.sidebar.multiselect("Select pollutants to visualize", pollutants, default=pollutants)
    return selected_pollutants

# function plot the selected pollutants
def plot_pollutants_trend(df, selected_pollutants):
    fig, ax = plt.subplots(figsize=(12, 6))
    for pollutant in selected_pollutants:
        sns.lineplot(data=df, x='Date', y=pollutant, ax=ax, label=pollutant, markers=True, dashes=True)
    ax.set_title("Air Quality Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Concentration")
    st.pyplot(fig)

def plot_pollutants_monthly(df, selected_pollutants):
    fig, ax = plt.subplots(figsize=(12, 6))
    for pollutant in selected_pollutants:
        sns.lineplot(data=df, x='Month', y=pollutant, ax=ax, label=pollutant, markers=True, dashes=True)
    ax.set_title("Air Quality Monthly Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Concentration")
    st.pyplot(fig)

def plot_pollutants_yearly(df, selected_pollutants):
    fig, ax = plt.subplots(figsize=(12, 6))
    for pollutant in selected_pollutants:
        # use barplot to show the yearly trend
        sns.barplot(data=df, x='Year', y=pollutant, ax=ax, label=pollutant)
    ax.set_title("Air Quality Yearly Trend")
    ax.set_xlabel("Year")
    ax.set_ylabel("Concentration")
    st.pyplot(fig)


# check if the user select "Daily", "Monthly" or "Yearly"
if selected_display == "Daily":
    try:
        start_date = df['Date'].min()
        end_date = df['Date'].max()
        selected_date_range = st.sidebar.date_input("Select date range", [start_date, end_date], min_value=start_date, max_value=end_date)
        # filter the dataframe based on the selected date range
        df = df[(df['Date'] >= pd.to_datetime(selected_date_range[0])) & (df['Date'] <= pd.to_datetime(selected_date_range[1]))]
    except IndexError:
        st.error("Please select a date range with at least two dates.")

    # plot the daily data
    st.subheader(f"Air Quality Data from {selected_date_range[0]} to {selected_date_range[1]}")
    plot_pollutants_trend(df, selected_pollutants(df))

if selected_display == "Monthly":
    # select the month range to display
    start_month = st.sidebar.selectbox("Select start month", df['Date'].dt.to_period('M').unique(), format_func=lambda x: x.strftime("%Y-%m"), index=0)
    end_month = st.sidebar.selectbox("Select end month", df['Date'].dt.to_period('M').unique(), format_func=lambda x: x.strftime("%Y-%m"), index=len(df['Date'].dt.to_period('M').unique())-1)
    
    # group the data by month and calculate the mean for each month
    df['Month'] = df['Date'].dt.to_period('M')
    df_monthly = df.drop(columns=["wd", "station"]).groupby('Month').mean().reset_index()
    
    # filter the dataframe based on the selected month range
    df_monthly = df_monthly[(df_monthly['Month'] >= start_month) & (df_monthly['Month'] <= end_month)]
    df_monthly['Month'] = df_monthly['Month'].dt.to_timestamp()


    # plot the monthly data
    st.subheader(f"Air Quality Data from {start_month} to {end_month}")
    plot_pollutants_monthly(df_monthly, selected_pollutants(df))

if selected_display == "Yearly":
    # select the year range to display
    start_year = st.sidebar.selectbox("Select start year", df['Date'].dt.year.unique(), index=0)
    end_year = st.sidebar.selectbox("Select end year", df['Date'].dt.year.unique(), index=len(df['Date'].dt.year.unique())-1)
    
    # group the data by year and calculate the mean for each year
    df['Year'] = df['Date'].dt.year
    df_yearly = df.drop(columns=["wd", "station"]).groupby('Year').mean().reset_index()
    
    # filter the dataframe based on the selected year range
    df_yearly = df_yearly[(df_yearly['Year'] >= start_year) & (df_yearly['Year'] <= end_year)]

    # plot the yearly data
    st.subheader(f"Air Quality Data from {start_year} to {end_year}")
    plot_pollutants_yearly(df_yearly, selected_pollutants(df))


########################################################################

# Displaying the mean values of pollutants based on hourly data
hourly_pollutants = df.groupby('hour')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].mean().reset_index()

# Define pollutant quality thresholds

quality_thresholds = {
    'PM2.5': {'Good': 30, 'Satisfactory': 60, 'Moderately Polluted': 90, 'Unhealthy': 120, 'Very Unhealthy': 250},
    'PM10': {'Good': 50, 'Satisfactory': 100, 'Moderately Polluted': 250, 'Unhealthy': 350, 'Very Unhealthy': 430},
    'SO2': {'Good': 40, 'Satisfactory': 80, 'Moderately Polluted': 380, 'Unhealthy': 800, 'Very Unhealthy': 1600},
    'NO2': {'Good': 40, 'Satisfactory': 80, 'Moderately Polluted': 180, 'Unhealthy': 280, 'Very Unhealthy': 400},
    'CO': {'Good': 1000, 'Satisfactory': 2000, 'Moderately Polluted': 10000, 'Unhealthy': 17000, 'Very Unhealthy': 34000},
    'O3': {'Good': 50, 'Satisfactory': 100, 'Moderately Polluted': 168, 'Unhealthy': 208, 'Very Unhealthy': 748}
}


def get_pollutant_quality(value, pollutant):
    thresholds = quality_thresholds.get(pollutant)
    if thresholds:
        if value <= thresholds['Good']:
            return 'Good'
        elif value <= thresholds['Satisfactory']:
            return 'Satisfactory'
        elif value <= thresholds['Moderately Polluted']:
            return 'Moderately Polluted'
        elif value <= thresholds['Unhealthy']:
            return 'Unhealthy'
        elif value <= thresholds['Very Unhealthy']:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    else:
        return 'Unknown'


for index, row in hourly_pollutants.iterrows():
    for pollutant in ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']:
        quality = get_pollutant_quality(row[pollutant], pollutant)

data = {'hour': []}
for pollutant in ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']:
    data[pollutant] = []

for index, row in hourly_pollutants.iterrows():
    data['hour'].append(index)  # Add the hour to the 'hour' column
    for pollutant in ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']:
        quality = get_pollutant_quality(row[pollutant], pollutant)
        data[pollutant].append(quality)  # Add the air quality to the corresponding pollutant column


pollutant_quality_df = pd.DataFrame(data)

def airpolution_display(df):
    with st.container():
        col1, col2 = st.columns([1,1])
        with col1:
            st.metric("PM2.5: ", value = df['PM2.5'], delta_color="normal")
        with col2:
            st.metric("PM10: ", value = df['PM10'], delta_color="normal")
        col3, col4 = st.columns([1,1])
        with col3:
            st.metric("SO2: ", value = df['SO2'], delta_color="normal")
        with col4:
            st.metric("NO2: ", value = df['NO2'], delta_color="normal")
        col5, col6 = st.columns([1,1])
        with col5:
            st.metric("CO: ", value = df['CO'], delta_color="normal")
        with col6:
            st.metric("O3: ", value = df['O3'], delta_color="normal")

#side bar for choose the hour to display the air quality data
selected_hour = st.sidebar.selectbox("Select hour to display air quality data", df['hour'].unique(), index=0)
st.subheader(f"Average Air Quality at {hourly_pollutants['hour'].iloc[selected_hour]}:00") 
airpolution_display(pollutant_quality_df.iloc[selected_hour])

#########################################################################

# Display the correlation matrix of the pollutants in streamlit
correlation_matrix_all = df[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'RAIN']].corr()
polutant_correlation = correlation_matrix_all.iloc[:6, 6:]
st.subheader("Correlation Matrix of Pollutants")
fig, ax = plt.subplots()  # for Figure dan Axes
sns.heatmap(polutant_correlation, annot=True, cmap='coolwarm', fmt=".2f", cbar=True, square=True, ax=ax)
st.pyplot(fig)  # display figure, not axes

###########################################################################

# lineplot for hourly wind speed

wind_speed = df.groupby('hour')['WSPM'].mean()
st.subheader("Hourly Wind Speed")
st.line_chart(wind_speed, x_label="Hour", y_label="Wind Speed (m/s)")

# choose the hour to display the wind speed
selected_hour = st.sidebar.selectbox("Select hour to display wind speed", df['hour'].unique(), index=0)

selected_wind_speed = str(round(df[df['hour'] == selected_hour]['WSPM'].mean(),3)) + " m/s"
st.metric(f"Wind Speed at {selected_hour}:00: ", value=selected_wind_speed, delta_color="normal")
