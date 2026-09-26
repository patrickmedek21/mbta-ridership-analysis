import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.lines as mlines

# Load the dataset with the correct file name
file_path = 'Fall_2024_MBTA_Rail_Ridership_by_Hour%2C_Route_Line%2C_and_Stop.csv'  # Corrected file path
df = pd.read_csv(file_path)

# Filter for Fall 2024 and the Northeastern stop
df_northeastern = df[
    (df['season'] == 'Fall 2024') &
    (df['stop_name'] == 'Northeastern University')
].copy()

# Calculate net onboard (average_ons - average_offs)
df_northeastern['net_onboard'] = df_northeastern['average_ons'] - df_northeastern['average_offs']

# Extract hour of service from the 'hour_of_service' column
df_northeastern['hour'] = pd.to_datetime(df_northeastern['hour_of_service'], format='%H:%M:%S').dt.hour

# Select features for clustering: hour and net onboard
features = df_northeastern[['hour', 'net_onboard']]

# Standardize the features
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# KMeans clustering (k=3)
kmeans = KMeans(n_clusters=3, random_state=42)
df_northeastern['cluster'] = kmeans.fit_predict(scaled_features)

# Set up the plot with 3 subplots (1 row, 3 columns)
fig, axes = plt.subplots(1, 3, figsize=(24, 8), sharey=True)  # Increased figure size

# Day types and colors for clustering
day_types = ['Weekday', 'Saturday', 'Sunday']
colors = ['r', 'g', 'b']
shapes = {'EB': 'o', 'WB': 's'}  # Circle for EB, Square for WB

# Define custom legends
cluster_labels = [f'Cluster {i}' for i in range(3)]
direction_labels = ['Eastbound (EB)', 'Westbound (WB)']

# Plot each day type in a separate subplot
for i, day_type in enumerate(day_types):
    ax = axes[i]
    day_data = df_northeastern[df_northeastern['day_type_name'] == day_type]

    # Plot each cluster with a different color and shape for direction
    for cluster, color in zip(range(3), colors):
        for direction, shape in shapes.items():
            direction_data = day_data[day_data['cluster'] == cluster]
            direction_data = direction_data[direction_data['dir_id'] == direction]

            # Plot data with the correct shape and color
            ax.scatter(direction_data['hour'], direction_data['net_onboard'],
                       s=50, alpha=0.7, color=color, marker=shape)

    # Title and labels
    ax.set_title(f"{day_type}s")
    ax.set_xlabel("Hour of Service")
    if i == 0:  # Only show the y-axis label on the leftmost subplot
        ax.set_ylabel("Net Onboardings")
    ax.grid(True)

    # Set x-ticks to 0, 6, 12, 18, 24
    ax.set_xticks([0, 6, 12, 18, 24])

# Adjust layout to avoid overlap and leave space for the y-axis label and legend
plt.tight_layout(rect=[0.05, 0, 0.85, 0.9])  # Adjusted to leave space for the title and legends

# Add the big title above all subplots
fig.suptitle("Clustering of Net Onboardings by Hour and Direction at Northeastern University (Fall 2024)",
             fontsize=16, fontweight='bold')

# Create the legend for each cluster and direction combination with full names
cluster_direction_handles = []

for cluster, color in zip(range(3), colors):
    for direction, shape in shapes.items():
        label = f'Cluster {cluster} {direction.replace("EB", "Eastbound").replace("WB", "Westbound")}'
        cluster_direction_handles.append(mlines.Line2D([], [], color=color, marker=shape, markersize=10, label=label))

# Create a legend and place it to the right of the plots
fig.legend(handles=cluster_direction_handles, loc='center right', title="Clusters and Directions", fontsize=10)

# Display the plot
plt.show()