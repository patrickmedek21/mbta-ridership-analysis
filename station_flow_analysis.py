import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# Load the data
df = pd.read_csv("Fall_2024_MBTA_Rail_Ridership_by_Hour%2C_Route_Line%2C_and_Stop.csv")

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = [20, 12]  # Increased height to prevent label cutoff
plt.rcParams['font.size'] = 12


# Function to format numbers in thousands with K
def thousands_formatter(x, pos):
    return f'{x:.0f}K'


# Color mapping for route lines
color_mapping = {
    'Red Line': 'red',
    'Orange Line': 'orange',
    'Green Line': 'green',
    'Blue Line': 'blue',
    'Silver Line': 'silver',
    'Commuter Rail': 'purple',
    'Bus': 'goldenrod',
    'Other': 'gray'
}


def plot_top_stations_daily_ridership():
    # Create figure with adjusted size and constrained layout
    fig, ax = plt.subplots(figsize=(20, 13))  # Slightly taller figure
    fig.set_constrained_layout(True)  # Helps prevent label cutoff

    # Calculate average daily ridership by summing average_flow across all occurrences
    daily_ridership = df.groupby(['stop_name', 'route_name'])['average_flow'].sum().reset_index()

    # [Rest of your data processing code remains exactly the same...]
    # Calculate total ridership for each station (sum across all lines)
    station_totals = daily_ridership.groupby('stop_name')['average_flow'].sum()

    # Get number of lines per station
    lines_per_station = daily_ridership.groupby('stop_name')['route_name'].nunique()

    # Get top 10 stations by total ridership in descending order
    top_stations = station_totals.nlargest(10).index
    top_stations_ordered = station_totals.loc[top_stations].sort_values(ascending=False).index

    # Filter to only include top stations and maintain order
    top_data = daily_ridership[daily_ridership['stop_name'].isin(top_stations_ordered)]
    top_data['stop_name'] = pd.Categorical(top_data['stop_name'], categories=top_stations_ordered, ordered=True)
    top_data = top_data.sort_values('stop_name')

    # Pivot to create stacked bar data
    pivot_df = top_data.pivot(index='stop_name', columns='route_name', values='average_flow')
    pivot_df = pivot_df.fillna(0)

    # Sort routes by color mapping order for consistent stacking
    routes = [r for r in color_mapping.keys() if r in pivot_df.columns]
    pivot_df = pivot_df[routes]

    # Create stacked bars
    pivot_df.div(1000).plot(kind='bar', stacked=True,
                            color=[color_mapping[r] for r in pivot_df.columns],
                            width=0.8, ax=ax)

    # Create simplified labels with just station name
    labels = [f"{station}" for station in pivot_df.index]

    # Add exact numbers for each segment (inside the bars)
    for i, station in enumerate(pivot_df.index):
        bottom = 0
        for route in pivot_df.columns:
            value = pivot_df.loc[station, route]
            if value > 0:
                height = value / 1000
                # White text for colored segments
                text_color = 'white' if route != 'Silver Line' else 'black'  # Special case for silver
                ax.text(i, bottom + height / 2, f'{value:,.0f}',
                        ha='center', va='center', color=text_color, fontsize=10, fontweight='bold')
                bottom += height

    # Add total numbers on top of bars only for stations with multiple lines (positioned closer)
    for i, station in enumerate(pivot_df.index):
        if lines_per_station[station] > 1:  # Only show total for multi-line stations
            total = pivot_df.loc[station].sum()
            ax.text(i, total / 1000 - 0.05 * total / 1000, f'{total:,.0f}',
                    ha='center', va='top', color='black', fontsize=11, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=1))

    # Create custom legend with "Service Line" title positioned inside plot
    legend_elements = [Patch(facecolor=color, label=route.replace(' Line', ''))
                       for route, color in color_mapping.items()
                       if route in pivot_df.columns]
    ax.legend(handles=legend_elements, title='Service Line',
              loc='upper right', framealpha=1)

    # Formatting with extra padding for y-axis label
    plt.title('Top 10 MBTA Stations by Average Daily Flow (Fall 2024)', pad=20, fontsize=16)
    plt.xlabel('Station', labelpad=15, fontsize=14)
    plt.ylabel('Average Daily Flow', labelpad=20, fontsize=14)  # Increased labelpad
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right', fontsize=12)
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
    plt.grid(True, axis='y', alpha=0.3)

    # Explicitly adjust subplot parameters to ensure ylabel isn't cut off
    plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.15)

    plt.savefig('top_stations_daily_ridership_final.png', dpi=300, bbox_inches='tight')
    plt.show()


# Run the plotting function
plot_top_stations_daily_ridership()