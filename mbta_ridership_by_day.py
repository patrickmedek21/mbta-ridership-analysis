import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
import math

file_path = 'MBTA_Monthly_Ridership_By_Mode_and_Line.csv'
df = pd.read_csv(file_path)

# Parse the date
df['month'] = pd.to_datetime(df['month_of_service']).dt.tz_localize(None)

# Keep only defined transit lines
defined_lines = ['Bus', 'Commuter Rail', 'Red Line', 'Orange Line', 'Green Line', 'Blue Line', 'Silver Line']
excluded_categories = ['Heavy Rail', 'Light Rail', 'All Bus', 'Key Bus Routes']
df = df[~df['route_or_line'].isin(excluded_categories)]
df['route_group'] = df['route_or_line'].apply(lambda x: x if x in defined_lines else 'Other')

# Calculate total ridership for each entry
df['total_ridership'] = df['ridership_average'] * df['daycount']

# Filter only the needed daytypes
daytypes = ['Weekday', 'Saturday', 'Sunday']
df = df[df['daytype'].isin(daytypes)]

# Function to compute weighted average by year
def get_weighted_avg(df, year):
    df_year = df[df['month'].dt.year == year].copy()
    grouped = (
        df_year.groupby(['route_group', 'daytype'])
        .agg({'total_ridership': 'sum', 'daycount': 'sum'})
        .reset_index()
    )
    grouped['ridership_average'] = grouped['total_ridership'] / grouped['daycount']
    grouped['year'] = year
    return grouped[['route_group', 'daytype', 'ridership_average', 'year']]

# Get 2024 and 2019 data
df_2024 = get_weighted_avg(df, 2024)
df_2019 = get_weighted_avg(df, 2019)

# Combine both
df_combined_2024 = pd.concat([df_2024[df_2024['year'] == 2024]])
df_combined_2019 = pd.concat([df_2019[df_2019['year'] == 2019]])

# Pivot for multi-index bar plot for 2024
pivot_df_2024 = df_combined_2024.pivot_table(
    index=['route_group', 'year'],
    columns='daytype',
    values='ridership_average'
).fillna(0)

# Pivot for multi-index bar plot for 2019
pivot_df_2019 = df_combined_2019.pivot_table(
    index=['route_group', 'year'],
    columns='daytype',
    values='ridership_average'
).fillna(0)

# Ensure column order
pivot_df_2024 = pivot_df_2024[['Weekday', 'Saturday', 'Sunday']]
pivot_df_2019 = pivot_df_2019[['Weekday', 'Saturday', 'Sunday']]

# Find maximum ridership across both years and set y-axis limit
max_ridership = max(pivot_df_2024.max().max(), pivot_df_2019.max().max())
y_upper_limit = math.ceil(max_ridership / 50000) * 50000  # Round up to nearest 50K

# Create subplots
fig, axes = plt.subplots(2, 1, figsize=(16, 14), gridspec_kw={'height_ratios': [1, 1]})

# Function to add annotations
def add_annotations(ax, pivot_df):
    bar_width = 0.8
    group_width = bar_width / 3

    for i, transit_line in enumerate(pivot_df.index):
        left_edge = i - bar_width / 2

        weekday_x = left_edge + group_width * 0.5 + 0.10
        weekday_height = pivot_df.loc[transit_line, 'Weekday']

        sat_x = left_edge + group_width * 1.5 + 0.02
        sat_height = pivot_df.loc[transit_line, 'Saturday']
        sat_perc = (sat_height / weekday_height) * 100

        sun_x = left_edge + group_width * 2.5 - 0.07
        sun_height = pivot_df.loc[transit_line, 'Sunday']
        sun_perc = (sun_height / weekday_height) * 100

        ax.text(weekday_x, weekday_height, f'{weekday_height:,.0f}',
                ha='center', va='bottom', fontsize=9, color='black')

        ax.text(sat_x, sat_height, f'{sat_perc:.1f}%',
                ha='center', va='bottom', fontsize=9, color='black', rotation=45)

        ax.text(sun_x, sun_height, f'{sun_perc:.1f}%',
                ha='center', va='bottom', fontsize=9, color='black', rotation=45)

# Plot for 2024
colors = {
    'Weekday': '#D62728',
    'Saturday': '#1f77b4',
    'Sunday': '#2ca02c'
}

pivot_df_2024.plot(
    kind='bar',
    ax=axes[0],
    color=[colors['Weekday'], colors['Saturday'], colors['Sunday']]
)

axes[0].set_title('MBTA Average Daily Ridership by Transit Line and Day Type (2024)', pad=20)
axes[0].set_ylabel('Average Daily Ridership')
axes[0].set_xlabel('Transit Line', labelpad=10)
axes[0].set_xticklabels(pivot_df_2024.index.get_level_values('route_group'), rotation=0)
axes[0].legend(title='Day Type')
axes[0].set_ylim(0, y_upper_limit)  # Set consistent y-axis limit

# Format y-axis as thousands
def thousands_formatter(x, pos):
    return f'{x/1000:.0f}K'
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))

# Add annotations to 2024 plot
add_annotations(axes[0], pivot_df_2024)

# Plot for 2019
pivot_df_2019.plot(
    kind='bar',
    ax=axes[1],
    color=[colors['Weekday'], colors['Saturday'], colors['Sunday']]
)

axes[1].set_title('MBTA Average Daily Ridership by Transit Line and Day Type (2019)', pad=20)
axes[1].set_ylabel('Average Daily Ridership')
axes[1].set_xlabel('Transit Line', labelpad=10)
axes[1].set_xticklabels(pivot_df_2019.index.get_level_values('route_group'), rotation=0)
axes[1].legend(title='Day Type')
axes[1].set_ylim(0, y_upper_limit)  # Set consistent y-axis limit

# Format y-axis as thousands
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))

# Add annotations to 2019 plot
add_annotations(axes[1], pivot_df_2019)

# Adjust layout
plt.tight_layout(pad=3.0)
plt.subplots_adjust(hspace=0.4)
plt.subplots_adjust(bottom=0.1)
plt.show()