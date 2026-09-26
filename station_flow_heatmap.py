import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import numpy as np

# Load the data
df = pd.read_csv("Fall_2024_MBTA_Rail_Ridership_by_Hour%2C_Route_Line%2C_and_Stop.csv")

# Convert hour_of_service to datetime and extract hour
df['hour'] = pd.to_datetime(df['hour_of_service']).dt.hour

# Function to format numbers in thousands with K (no decimals)
def thousands_formatter(x, pos):
    return f'{int(x)}K' if x >= 1 else f'{x:.0f}K'

# Ridership Heatmap by Hour and Stop
def plot_heatmap_hour_stop():
    # Create a much larger figure
    fig, ax = plt.subplots(figsize=(30, 20))  # Bigger canvas

    # Get top 15 stops
    top_stops = df.groupby('stop_name')['average_flow'].sum().nlargest(15).index
    heatmap_data = df[df['stop_name'].isin(top_stops)].pivot_table(
        index='stop_name', columns='hour', values='average_flow', aggfunc='sum') / 1000

    # Create annotation matrix with K suffix and 1 decimal point
    annot_matrix = np.where(pd.isna(heatmap_data),
                            '',
                            heatmap_data.applymap(lambda x: f'{x:.1f}K'))

    # Plot heatmap
    sns.heatmap(heatmap_data, cmap='YlOrRd',
                annot=annot_matrix, fmt='',
                annot_kws={"size": 8},
                linewidths=0.5,
                cbar_kws={
                    'label': 'Average Ridership',
                    'format': FuncFormatter(thousands_formatter)
                },
                ax=ax)

    # Titles and labels
    ax.set_title('Ridership Flow Heatmap by Hour and Station (Top 15 Stations)', fontsize=20, pad=30)
    ax.set_xlabel('Hour of Day', fontsize=16)
    ax.set_ylabel('Station', fontsize=16)

    # Colorbar formatting
    cbar = ax.collections[0].colorbar
    cbar.ax.set_ylabel('Average Ridership Flow', fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    # Rotate y-ticks
    plt.yticks(rotation=0)

    # Adjust spacing around the plot
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.15, right=0.95)

    # Final layout and save
    plt.savefig('heatmap_hour_stop_optimized_big.png', dpi=300, bbox_inches='tight')
    plt.show()

plot_heatmap_hour_stop()
