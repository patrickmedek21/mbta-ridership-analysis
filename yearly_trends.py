import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
from matplotlib import patheffects

# Load and prepare data
file_path = 'MBTA_Monthly_Ridership_By_Mode_and_Line.csv'
df = pd.read_csv(file_path)

# Parse dates and filter for 2019-2024
df['month_date'] = pd.to_datetime(df['month_of_service']).dt.tz_localize(None)
df = df[df['month_date'].dt.year.between(2019, 2024)]

# Exclude aggregate categories
excluded_categories = ['Heavy Rail', 'Light Rail', 'All Bus']
filtered_df = df[~df['route_or_line'].isin(excluded_categories)].copy()
filtered_df = filtered_df[~filtered_df["daytype"].isin(["Total"])]

# Calculate monthly totals
monthly_totals = (filtered_df.groupby([pd.Grouper(key='month_date', freq='M')])
                  ['ridership_total'].sum()
                  .rename('total_ridership')
                  .reset_index())

# Extract year and month
monthly_totals['year'] = monthly_totals['month_date'].dt.year
monthly_totals['month_name'] = monthly_totals['month_date'].dt.month_name()

# Proper month ordering
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_totals['month_name'] = pd.Categorical(monthly_totals['month_name'],
                                              categories=month_order,
                                              ordered=True)

# Enhanced color palette
marker_colors = {
    2019: '#E41A1C',  # Vibrant red
    2020: '#FF7F00',  # Orange
    2021: '#FFD700',  # Gold
    2022: '#4DAF4A',  # Green
    2023: '#377EB8',  # Blue
    2024: '#984EA3'  # Purple
}

plt.figure(figsize=(12, 7))  # Adjusted width
plt.style.use('default')
sns.set_style('whitegrid')
ax = plt.gca()

# Plot each year with optimized sizing
for year, group in monthly_totals.groupby('year'):
    ax.plot(group['month_name'],
            group['total_ridership'],
            color='black',
            marker='o',
            markersize=12,
            markerfacecolor=marker_colors[year],
            markeredgecolor='black',
            markeredgewidth=1,
            linewidth=1.5,
            linestyle='--',
            label=str(year),
            alpha=0.9)

    # Year labels
    for x, y in zip(group['month_name'], group['total_ridership']):
        ax.text(x, y, f"{str(year)[2:]}",
                ha='center',
                va='center',
                fontsize=7,
                color='white',
                fontweight='normal',
                path_effects=[
                    patheffects.withStroke(linewidth=1, foreground='black')
                ])

# Formatting
ax.set_title('MBTA Monthly Ridership by Year (2019-2024)',
             pad=20, fontsize=14)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Total Monthly Ridership', fontsize=12)
plt.xticks(rotation=45)


# Custom millions formatter
def millions_formatter(x, pos):
    return f'{x / 1_000_000:.0f}M'


ax.yaxis.set_major_formatter(mticker.FuncFormatter(millions_formatter))
plt.ylim(0, monthly_totals['total_ridership'].max() * 1.1)

# Enhanced legend
legend = ax.legend(title='Year',
                   loc='center left',
                   bbox_to_anchor=(1.05, 0.5),
                   frameon=True,
                   framealpha=1,
                   edgecolor='black',
                   fontsize=10,
                   handletextpad=0.5)

# Style legend markers
for handle in legend.legend_handles:
    handle.set_markersize(12)
    handle.set_markerfacecolor(marker_colors[int(handle.get_label())])
    handle.set_markeredgewidth(1)

# Final layout adjustment
plt.tight_layout(rect=[0, 0, 0.92, 1])  # Adjusted right margin
plt.show()