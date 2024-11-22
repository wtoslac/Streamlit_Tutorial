import streamlit as st
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Set up basic information
siteName = "Turlock CA USA"
SampleRate = "1h"
st.header("Turlock AOD")

# Input for StartDate and EndDate
StartDate = st.date_input("Start Date", datetime.date(2023, 7, 1))
EndDate = st.date_input("End Date", datetime.date(2023, 7, 7))

# Convert StartDate and EndDate to datetime objects for further processing
StartDateTime = datetime.datetime.combine(StartDate, datetime.time(0, 0))
EndDateTime = datetime.datetime.combine(EndDate, datetime.time(23, 59))

# Allow the user to set y-axis limits for AOD
st.sidebar.header("Adjust Y-axis Limits")
AOD_min = st.sidebar.slider("Y-Axis Min", min_value=0.0, max_value=1.0, value=0.0, step=0.01)
AOD_max = st.sidebar.slider("Y-Axis Max", min_value=0.0, max_value=1.0, value=0.3, step=0.01)

# URL for the first dataset
file_url_1 = "https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/20230101_20241231_Turlock_CA_USA_part1.lev15"

# Function to load data from the given URL
def load_data(file_url):
    try:
        # Read the data from the provided GitHub raw URL
        df = pd.read_csv(file_url, skiprows=6, parse_dates={'datetime': [0, 1]})
        datetime_utc = pd.to_datetime(df["datetime"], format='%d:%m:%Y %H:%M:%S')
        datetime_pac = pd.to_datetime(datetime_utc).dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
        df.set_index(datetime_pac, inplace=True)
        
        return df
    except Exception as e:
        st.error(f"Failed to process the file from {file_url}: {e}")
        return None

# Load data from the first file
df_1 = None
if file_url_1:
    df_1 = load_data(file_url_1)

# Ensure data is loaded and columns are correct
if df_1 is not None:
    if 'AOD_440nm' not in df_1.columns or 'AOD_500nm' not in df_1.columns or 'AOD_675nm' not in df_1.columns:
        st.error(f"Missing expected columns in the dataset. Available columns: {df_1.columns}")
    
    # Plot data from the first repository if columns are correct
    if 'AOD_440nm' in df_1.columns and 'AOD_500nm' in df_1.columns and 'AOD_675nm' in df_1.columns:
        
        # Plot AOD_440nm, AOD_500nm, and AOD_675nm as initial plot
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.k')
        plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.k')

        # Format the plot
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.ylim(AOD_min, AOD_max)
        plt.legend()
        plt.title("AOD Turlock")  # Added title for AOD graph
        st.pyplot(plt.gcf())
        
        # Ask user to match wavelengths to positions
        st.text("\nMatch the wavelengths to the positions on the graph:")
        positions = ["Top", "Middle", "Bottom"]

        # Create user input dropdowns for selecting wavelengths
        user_matches = {}
        for pos in positions:
            user_matches[pos] = st.selectbox(f"What Wavelength will be located on the {pos} position on the graph?", 
                                             options=["Select an option", "400 nm", "500 nm", "675 nm"], 
                                             key=pos)

        # Once the user submits, show the second graph (same as the first)
        if st.button("Submit"):
            # Plot the second graph (exact same as the first one)
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_440nm"].resample(SampleRate).mean(), '.b', label="440 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_500nm"].resample(SampleRate).mean(), '.g', label="500 nm")
            plt.plot(df_1.loc[StartDateTime.strftime('%Y-%m-%d %H:%M:%S'):EndDateTime.strftime('%Y-%m-%d %H:%M:%S'), "AOD_675nm"].resample(SampleRate).mean(), '.r', label="675 nm")

            # Format the second plot
            plt.gcf().autofmt_xdate()
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz='US/Pacific'))
            plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=12, tz='US/Pacific'))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.ylim(AOD_min, AOD_max)
            plt.legend()
            plt.title("AOD Turlock")  # Added title for AOD graph
            st.pyplot(plt.gcf())

# URL for the wind data file
windfile = 'https://raw.githubusercontent.com/Rsaltos7/AERONET_Streamlit/refs/heads/main/Modesto_Wind_2023%20(2).csv'
windSampleRate = '3h'

# Read the wind data
Wdf = pd.read_csv(windfile, parse_dates={'datetime': [1]}, low_memory=False)
datetime_utc = pd.to_datetime(Wdf["datetime"], format='%d-%m-%Y %H:%M:%S')
datetime_pac = datetime_utc.dt.tz_localize('UTC').dt.tz_convert('US/Pacific')
Wdf.set_index(datetime_pac, inplace=True)

# Streamlit widgets for dynamic date range selection
st.title("Wind Vectors (Magnitude and Direction)")  # Fixing title assignment to a string
start_date = st.date_input("Select Start Date", pd.to_datetime('2023-07-01'))
end_date = st.date_input("Select End Date", pd.to_datetime('2023-07-07'))

# Convert selected dates to strings and filter the data
StartDate = start_date.strftime('%Y-%m-%d 00:00:00')
EndDate = end_date.strftime('%Y-%m-%d 23:59:59')

# Filter by the user-selected date range
Wdf_filtered = Wdf.loc[StartDate:EndDate]

# Extract wind data (direction and speed) and filter valid observations
WNDdf = Wdf_filtered['WND'].str.split(pat=',', expand=True)
WNDdf = WNDdf.loc[WNDdf[4] == '5']  # Only valid observations

# Initialize lists for Cartesian components
Xdata, Ydata = [], []

# Calculate Cartesian components of wind vectors
for _, row in WNDdf.iterrows():
    magnitude = np.float64(row[3])  # Wind speed
    direction = np.float64(row[0])  # Wind direction
    Xdata.append(magnitude * np.sin(direction * (np.pi / 180)))
    Ydata.append(magnitude * np.cos(direction * (np.pi / 180)))

# Add Cartesian components to the DataFrame
WNDdf[5], WNDdf[6] = Xdata, Ydata

# Create a plot for wind vectors
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title("Wind Vector")  # Added title for Wind Vector graph
ax.set_xlabel("Time")
ax.set_ylim(AOD_min, AOD_max)
ax.set_ylabel("Magnitude m/s")
ax2 = ax.twinx()
ax.yaxis.set_label_position('right')  # Position the label on the right axis

# Plot the data for wind vector components (X and Y wind components)
ax2.plot(WNDdf.index, WNDdf[6], 'g-', label='U-Wind Component')  # Corrected from WnDdf to WNDdf
ax.plot(WNDdf.index, WNDdf[5], 'r-', label="Wind Vector Y")  # Corrected from WnDdf to WNDdf

# Adding legends
ax2.legend(loc='best')
ax.legend(loc='best')

# Display the plot
st.pyplot(fig)
