import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
from statsmodels.tsa.seasonal import STL
from sklearn.linear_model import LinearRegression
import numpy as np

# Load and clean data
file_path = 'MBTA_Monthly_Ridership_By_Mode_and_Line.csv'
df = pd.read_csv(file_path)
df['month'] = pd.to_datetime(df['month_of_service']).dt.to_period('M').dt.to_timestamp()
df = df[df['month'].dt.year >= 2019]

# Exclude aggregate categories
excluded = ['Heavy Rail', 'Light Rail', 'All Bus']
filtered_df = df[~df['route_or_line'].isin(excluded)].copy()
filtered_df = filtered_df[~filtered_df["daytype"].isin(["Total"])]

# Aggregate total monthly ridership
monthly_totals = (
    filtered_df.groupby('month')['ridership_total']
    .sum()
    .rename('total_ridership')
    .reset_index()
)

# Focus on 2022–2024 for modeling
train_df = monthly_totals[(monthly_totals['month'].dt.year >= 2022) & (monthly_totals['month'].dt.year <= 2024)].copy()
train_df = train_df.set_index('month')

# STL decomposition
stl = STL(train_df['total_ridership'], period=12, robust=True)
res = stl.fit()
trend = res.trend
seasonal = res.seasonal

# Linear regression on trend
X = np.arange(len(trend)).reshape(-1, 1)
y = trend.values
model = LinearRegression().fit(X, y)

# Forecast trend 12 months ahead
future_X = np.arange(len(trend), len(trend) + 12).reshape(-1, 1)
predicted_trend = model.predict(future_X)

# Average seasonal component for each calendar month over 2022–2024
seasonal_df = seasonal.copy()
seasonal_df.index = train_df.index
seasonal_df = seasonal_df.to_frame(name='seasonal')
seasonal_df['month_num'] = seasonal_df.index.month
monthly_avg_seasonality = seasonal_df.groupby('month_num')['seasonal'].mean()

# Generate predictions for each month of 2025 using average seasonality
future_months = pd.date_range(start='2025-01-01', periods=12, freq='MS')
future_seasonality = [monthly_avg_seasonality[month] for month in future_months.month]
predicted_ridership = predicted_trend + future_seasonality

# Combine prediction dataframe
future_df = pd.DataFrame({
    'month': future_months,
    'total_ridership': predicted_ridership
})

# Combine all actuals (2022–2024) with predictions
actual_df = monthly_totals[(monthly_totals['month'].dt.year >= 2022) & (monthly_totals['month'].dt.year <= 2024)]
full_df = pd.concat([actual_df, future_df], ignore_index=True)

# Format x-axis in quarters
xticks = pd.date_range(start='2022-01-01', end='2025-12-01', freq='QS')
xtick_labels = [f"Q{((d.month - 1)//3 + 1)} '{str(d.year)[-2:]}" for d in xticks]

# Plotting
plt.figure(figsize=(14, 6))
sns.set(style='whitegrid')

# Plot actuals (2022–2024)
plt.plot(
    actual_df['month'],
    actual_df['total_ridership'],
    color='purple',
    marker='o',
    label='Actual (2022–2024)'
)

# Plot 2025 predictions
plt.plot(
    future_df['month'],
    future_df['total_ridership'],
    color='black',
    linestyle='--',
    marker='o',
    label='Predicted (2025)'
)

for i, (x, y) in enumerate(zip(future_df['month'], future_df['total_ridership'])):
    offset = 300_000 if i % 2 == 0 else -300_000  # alternate up and down
    va = 'bottom' if i % 2 == 0 else 'top'

    plt.text(
        x,
        y + offset,
        f'{y / 1_000_000:.1f}M',
        fontsize=8,
        fontweight='bold',
        color='black',
        ha='center',
        va=va,
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.2', alpha=0.8)
    )

# Connect Dec 2024 to Jan 2025
last_actual = actual_df[actual_df['month'] == '2024-12-01']['total_ridership'].values[0]
first_pred = future_df[future_df['month'] == '2025-01-01']['total_ridership'].values[0]
plt.plot(
    [pd.Timestamp('2024-12-01'), pd.Timestamp('2025-01-01')],
    [last_actual, first_pred],
    color='purple',
    linestyle='dashed'
)

# Add vertical line at 2025
plt.axvline(pd.Timestamp('2025-01-01'), color='gray', linestyle='--')

# Set ticks and labels
plt.xticks(ticks=xticks, labels=xtick_labels, rotation=45)
plt.xlabel('Month')
plt.ylabel('Total Monthly Ridership')
plt.title('MBTA Total Monthly Ridership (2022-2024, with 2025 Forecast)')
plt.legend()

# Format y-axis
def format_y(x, pos):
    return f'{x/1_000_000:.0f}M' if x >= 1_000_000 else f'{int(x):,}'
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(format_y))

plt.tight_layout()
plt.show()
