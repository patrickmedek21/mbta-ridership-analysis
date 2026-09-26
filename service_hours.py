import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Load the dataset with the correct file name
file_path = 'Fall_2024_MBTA_Rail_Ridership_by_Hour%2C_Route_Line%2C_and_Stop.csv'  # Corrected file path
df = pd.read_csv(file_path)

# Filter for Fall 2024
df_fall_2024 = df[df['season'] == 'Fall 2024'].copy()

# Calculate net onboard (average_ons - average_offs)
df_fall_2024['net_onboard'] = df_fall_2024['average_ons'] - df_fall_2024['average_offs']

# Extract hour of service from the 'hour_of_service' column
df_fall_2024['hour'] = pd.to_datetime(df_fall_2024['hour_of_service'], format='%H:%M:%S').dt.hour

# Day types (Weekday, Saturday, Sunday)
day_types = ['Weekday', 'Saturday', 'Sunday']

# Set up the plot with 3 subplots (1 row, 3 columns)
fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)  # Increased figure size

# Colors for the lines
colors = ['blue', 'orange', 'green']

# Plot each day type in a separate subplot
for i, day_type in enumerate(day_types):
    ax = axes[i]
    day_data = df_fall_2024[df_fall_2024['day_type_name'] == day_type]

    # Group by hour and aggregate the ons, offs, and net onboard
    hourly_data = day_data.groupby('hour')[['average_ons', 'average_offs', 'net_onboard']].sum()

    # Plot each of ons, offs, and net onboard only on the first subplot to avoid duplicating legend entries
    if i == 0:  # Only add labels on the first plot
        ax.plot(hourly_data.index, hourly_data['average_ons'], label='Onboardings', color='blue', linestyle='-', marker='o')
        ax.plot(hourly_data.index, hourly_data['average_offs'], label='Offboardings', color='orange', linestyle='-', marker='s')
        ax.plot(hourly_data.index, hourly_data['net_onboard'], label='Net Onboarding', color='green', linestyle='-', marker='^')
    else:  # No labels for subsequent subplots
        ax.plot(hourly_data.index, hourly_data['average_ons'], color='blue', linestyle='-', marker='o')
        ax.plot(hourly_data.index, hourly_data['average_offs'], color='orange', linestyle='-', marker='s')
        ax.plot(hourly_data.index, hourly_data['net_onboard'], color='green', linestyle='-', marker='^')

    # Title and labels
    ax.set_title(f"{day_type}s")
    ax.set_xlabel("Hour of Service")
    if i == 0:  # Only show the y-axis label on the leftmost subplot
        ax.set_ylabel("Boarding Amounts")
    ax.grid(True)

    # Set x-ticks to 0, 6, 12, 18, 24
    ax.set_xticks([0, 6, 12, 18, 24])

    # Apply custom formatting for y-axis ticks (10K, 100K, etc.)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x/1000)}K' if x >= 1000 else str(int(x))))

# Adjust layout to avoid overlap
plt.tight_layout(rect=[0.05, 0, 0.85, 0.9])  # Adjust layout to leave space for the title and legends

# Add the big title above all subplots
fig.suptitle("MBTA Onboardings, Offboardings, and Net Onboarding by Hour and Day Type (Fall 2024)\nLight and Heavy Rails Only",
             fontsize=16, fontweight='bold')

# Create the legend only once (using handles from the first subplot)
fig.legend(loc='center right', title="Legend", fontsize=10)

# Display the plot
plt.show()