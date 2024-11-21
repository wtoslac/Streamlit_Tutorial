import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
StartDate = st.date_input("StartDate", datetime.date(2024, 10, 1))
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDate = st.date_input("EndDate", datetime.date(2024, 10, 7))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# Input GitHub URLs for both repositories
st.header("Load Data from Two GitHub Repositories")
file_url_1 = st.text_input(
    "Enter the raw URL of the .lev15 file from the first GitHub repository:",
    "https://raw.githubusercontent.com/your_username/your_repository/main/20230101_20241231_Turlock_CA_USA_part1.lev15"
)
file_url_2 = st.text_input(
    "Enter the raw URL of the .lev15 file from the second GitHub repository:",
    "https://raw.githubusercontent.com/your_username/your_repository/main/20230101_20241231_Turlock_CA_USA_part2.lev15"
)

# Function to load data from the given URL
def load_data(file_url):
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        
        # Print column names to help with debugging
        st.write(f"Columns in the dataset: {df.columns}")
        
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Failed to process the file from {file_url}: {e}")
        return None

# Load data from both files
df_1 = None
df_2 = None
if file_url_1:
    df_1 = load_data(file_url_1)
if file_url_2:
    df_2 = load_data(file_url_2)

# Ensure data is loaded and columns are correct
if df_1 is not None and df_2 is not None:
    if 'AOD_500nm' not in df_1.columns or 'AOD_870nm' not in df_1.columns:
        st.error(f"Missing expected columns in the first dataset. Available columns: {df_1.columns}")
    if 'AOD_500nm' not in df_2.columns or 'AOD_870nm' not in df_2.columns:
        st.error(f"Missing expected columns in the second dataset. Available columns: {df_2.columns}")
    
    # Plot data from both repositories if columns are correct
    if 'AOD_500nm' in df_1.columns and 'AOD_870nm' in df_1.columns and \
       'AOD_500nm' in df_2.columns and 'AOD_870nm' in df_2.columns:
        
        # Plot AOD_500nm and AOD_870nm for both datasets
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm (Repo 1)")
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.b', label="870 nm (Repo 1)")

        plt.plot(df_2.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm (Repo 2)")
        plt.plot(df_2.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_870nm"].resample(SampleRate).mean(), '.b', label="870 nm (Repo 2)")

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        st.pyplot(plt.gcf())

