import pandas as pd
import numpy as np

# Load the two CSVs
breach_df = pd.read_csv(r'C:\olist_data\breach_master.csv')
carrier_df = pd.read_csv(r'C:\olist_data\carrier_summary.csv')

# Quick sanity check
print("=== BREACH MASTER ===")
print(f"Total rows: {len(breach_df)}")
print(f"Columns: {list(breach_df.columns)}")
print()
print("=== CARRIER SUMMARY ===")
print(f"Total rows: {len(carrier_df)}")
print(f"Columns: {list(carrier_df.columns)}")



# ── MULTI-SKU ANALYSIS ──────────────────────────────────────────
# Tag each order as single or multi-SKU
breach_df['sku_segment'] = breach_df['sku_count'].apply(
    lambda x: 'single' if x == 1 else 'multi'
)

# Late rate by segment
sku_analysis = breach_df.groupby('sku_segment').agg(
    total_orders=('order_id', 'nunique'),
    total_breaches=('is_breach', 'sum')
).reset_index()

sku_analysis['late_rate'] = (
    sku_analysis['total_breaches'] / sku_analysis['total_orders'] * 100
).round(2)

print("=== MULTI-SKU ANALYSIS ===")
print(sku_analysis)
print()

# Calculate the multiplier
single_rate = sku_analysis.loc[sku_analysis['sku_segment'] == 'single', 'late_rate'].values[0]
multi_rate = sku_analysis.loc[sku_analysis['sku_segment'] == 'multi', 'late_rate'].values[0]
multiplier = round(multi_rate / single_rate, 2)

print(f"Single-SKU late rate : {single_rate}%")
print(f"Multi-SKU late rate  : {multi_rate}%")
print(f"Multiplier           : {multiplier}x")




# ── DRSI SCORING ────────────────────────────────────────────────
# Component 1: Delay frequency (35%)
drsi = carrier_df.copy()
drsi['delay_freq_norm'] = (
    drsi['breach_rate_pct'] / drsi['breach_rate_pct'].max() * 100
)

# Component 2: Average days late - proxy for review drop (25%)
drsi['avg_days_late'] = drsi['avg_days_late'].fillna(0)
drsi['review_drop_norm'] = (
    drsi['avg_days_late'] / drsi['avg_days_late'].max() * 100
)

# Component 3: Revenue at risk (25%)
drsi['revenue_at_risk'] = drsi['total_breaches'] * drsi['avg_order_value']
drsi['revenue_norm'] = (
    drsi['revenue_at_risk'] / drsi['revenue_at_risk'].max() * 100
)

# Component 4: Carrier variance (15%)
drsi['carrier_variance'] = drsi['breach_rate_pct'] - drsi.groupby('seller_state')['breach_rate_pct'].transform('mean')
drsi['variance_norm'] = (
    drsi['carrier_variance'].clip(lower=0) / drsi['carrier_variance'].max() * 100
)

# Final DRSI score
drsi['drsi_score'] = (
    drsi['delay_freq_norm'] * 0.35 +
    drsi['review_drop_norm'] * 0.25 +
    drsi['revenue_norm'] * 0.25 +
    drsi['variance_norm'] * 0.15
).round(2)

# Filter to carriers with minimum 50 orders for statistical reliability
drsi_filtered = drsi[drsi['total_orders'] >= 50].copy()

top_risk = drsi_filtered[['seller_id', 'seller_state', 'total_orders',
                  'breach_rate_pct', 'revenue_at_risk',
                  'drsi_score']].sort_values('drsi_score', ascending=False).head(20)

print("=== TOP 20 HIGH RISK CARRIERS BY DRSI (min 50 orders) ===")
print(top_risk.to_string(index=False))
print()
print(f"Total carriers scored: {len(drsi_filtered)}")
print(f"DRSI score range: {drsi_filtered['drsi_score'].min()} - {drsi_filtered['drsi_score'].max()}")





# ── SAVINGS MODEL ───────────────────────────────────────────────
# Top quartile carriers = benchmark (lowest 25% breach rate)
top_quartile_threshold = drsi_filtered['breach_rate_pct'].quantile(0.25)
top_quartile_rate = drsi_filtered[
    drsi_filtered['breach_rate_pct'] <= top_quartile_threshold
]['breach_rate_pct'].mean()

# High risk carriers = top 25% by DRSI score
high_risk_threshold = drsi_filtered['drsi_score'].quantile(0.75)
high_risk_carriers = drsi_filtered[
    drsi_filtered['drsi_score'] >= high_risk_threshold
].copy()

# Savings calculation per carrier
high_risk_carriers['current_breaches'] = high_risk_carriers['total_breaches']
high_risk_carriers['projected_breaches'] = (
    high_risk_carriers['total_orders'] * top_quartile_rate / 100
).round(0)
high_risk_carriers['breaches_avoided'] = (
    high_risk_carriers['current_breaches'] - high_risk_carriers['projected_breaches']
).clip(lower=0)
high_risk_carriers['savings'] = (
    high_risk_carriers['breaches_avoided'] * high_risk_carriers['avg_order_value']
).round(2)

total_savings = high_risk_carriers['savings'].sum()

print("=== SAVINGS MODEL ===")
print(f"Top quartile benchmark breach rate : {top_quartile_rate:.2f}%")
print(f"High risk carriers identified      : {len(high_risk_carriers)}")
print(f"Total projected annual savings     : ${total_savings:,.0f}")





# ── EXPORT FOR TABLEAU ──────────────────────────────────────────
# 1. Full DRSI scored carriers
drsi_filtered.to_csv(r'C:\olist_data\drsi_scored_routes.csv', index=False)

# 2. Savings model results
high_risk_carriers.to_csv(r'C:\olist_data\savings_model.csv', index=False)

# 3. SKU segment analysis
sku_analysis.to_csv(r'C:\olist_data\segment_analysis.csv', index=False)

# 4. Full breach data (already have this but re-export clean)
breach_df.to_csv(r'C:\olist_data\breach_master_clean.csv', index=False)

print("=== EXPORTS COMPLETE ===")
print("Files saved to C:\\olist_data\\")
print(" - drsi_scored_routes.csv")
print(" - savings_model.csv")
print(" - segment_analysis.csv")
print(" - breach_master_clean.csv")