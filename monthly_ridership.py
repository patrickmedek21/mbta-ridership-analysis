import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

file_path = 'MBTA_Monthly_Ridership_By_Mode_and_Line.csv'
df = pd.read_csv(file_path)
df['month'] = pd.to_datetime(df['month_of_service']).dt.tz_localize(None).dt.to_period('M').dt.to_timestamp()
df = df[df['month'].dt.year >= 2019]

filtered_df = df[~df["route_or_line"].isin(["Heavy Rail", "Light Rail", "All Bus"])]
filtered_df = filtered_df[~filtered_df["daytype"].isin(["Total"])]
filtered_df = filtered_df.copy()
filtered_df['route_or_line_grouped'] = filtered_df['route_or_line'].apply(
    lambda x: x if x in ['Bus', 'Commuter Rail', 'Red Line', 'Orange Line', 'Green Line', 'Blue Line', 'Silver Line'] else 'Other')

monthly_trends = filtered_df.groupby(['month', 'route_or_line_grouped'])['ridership_total'].sum().reset_index()

color_mapping = {
    'Bus': 'goldenrod',
    'Red Line': 'red',
    'Orange Line': 'orange',
    'Green Line': 'green',
    'Commuter Rail': 'purple',
    'Blue Line': 'blue',
    'Silver Line': 'silver',
    'Other': 'black'
}

plt.figure(figsize=(16, 8))
sns.set(style='whitegrid')
ax = sns.lineplot(
    data=monthly_trends,
    x='month',
    y='ridership_total',
    hue='route_or_line_grouped',
    palette=color_mapping,
    marker='o',
    hue_order=['Bus', 'Red Line', 'Orange Line', 'Green Line', 'Commuter Rail', 'Blue Line', 'Silver Line', 'Other']
)

xticks = pd.date_range(start='2019-01-01', end=monthly_trends['month'].max(), freq='QS')
xtick_labels = [f"Q{((d.month - 1)//3 + 1)} '{str(d.year)[-2:]}" for d in xticks]
ax.set_xticks(xticks)
ax.set_xticklabels(xtick_labels)

ax.axvline(pd.Timestamp('2025-01-01'), color='black', linestyle='--', linewidth=1)

for year in range(2019, 2025):
    ax.axvline(pd.Timestamp(f"{year}-01-01"), color='black', linestyle='--', linewidth=1)

ax.set_title('MBTA Monthly Ridership by Transit Line')
ax.set_xlabel('Month')
ax.set_ylabel('Total Monthly Ridership')

def format_y_ticks(x, pos):
    if x < 1_000_000:
        return f'{int(x):,}'
    else:
        return f'{x/1_000_000:.1f}M'

ax.yaxis.set_major_formatter(mticker.FuncFormatter(format_y_ticks))

plt.xticks(rotation=45)
plt.legend(title='Transit Line', loc='center left', bbox_to_anchor=(1, 0.5))
plt.tight_layout()
plt.show()