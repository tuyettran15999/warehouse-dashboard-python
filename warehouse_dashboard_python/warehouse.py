# ================================
# 1. IMPORT LIBARY
# ================================
from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ================================
# 2. CREATE BIGQUERY CLIENT
# ================================
client = bigquery.Client(project="warehouse-analysis")

# ================================
# 3. SQL + LOAD DATA
# ================================
queries = {
    "top20_demand": """
        SELECT item_id, category, forecasted_demand_next_7d, stock_level,
               stockout_count_last_month, item_popularity_score,
               CASE WHEN stock_level*1.1 <forecasted_demand_next_7d THEN "risk_stockout" --buffer stock 10%
               ELSE "enough"
               END AS stock_status
        FROM `warehouse-analysis.logistics_warehouse.logistics_warehouse`
        ORDER BY forecasted_demand_next_7d DESC
        LIMIT 20
    """,
    "risk_stockout_by_reorder_point": """
        SELECT item_id, category, stock_level, reorder_point,
               stockout_count_last_month,
               ROUND(stock_level / reorder_point, 2) AS stock_health_ratio,
               CASE WHEN ROUND(stock_level / reorder_point, 2) <=1 THEN 'risk' ELSE 'no_risk' END AS stockout_risk
        FROM `warehouse-analysis.logistics_warehouse.logistics_warehouse`
        ORDER BY stock_health_ratio ASC
        LIMIT 20
    """,
    "picking_efficiency": """
        SELECT zone, AVG(picking_time_seconds) AS avg_picking_time,
               AVG(layout_efficiency_score) AS avg_layout_efficiency
        FROM `warehouse-analysis.logistics_warehouse.logistics_warehouse`
        GROUP BY zone
        ORDER BY avg_picking_time ASC
    """,
    "order_kpi": """
        SELECT category,
               AVG(order_fulfillment_rate) AS avg_fulfillment_rate,
               SUM(total_orders_last_month) AS total_orders,
               AVG(KPI_score) AS avg_KPI_score,
               AVG(turnover_ratio) AS avg_turnover
        FROM `warehouse-analysis.logistics_warehouse.logistics_warehouse`
        GROUP BY category
        ORDER BY avg_KPI_score DESC
    """,
    "cost_analysis": """
        SELECT item_id, category, unit_price, handling_cost_per_unit,
               holding_cost_per_unit_day,
               ROUND(unit_price - handling_cost_per_unit - holding_cost_per_unit_day,2) AS profit_margin_estimate
        FROM `warehouse-analysis.logistics_warehouse.logistics_warehouse`
        ORDER BY profit_margin_estimate DESC
        LIMIT 20
    """
}

dfs = {}
for key, query in queries.items():
    dfs[key] = client.query(query).to_dataframe()

# ================================
# 4. CREATE OUTPUT FOLDER
# ================================
output_folder = "charts_output"
os.makedirs(output_folder, exist_ok=True)

# ================================
# 5. DRAW AND SAVE CHART
# ================================

sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12,6)

# ---- Top 20 Products ----
df_top20 = dfs["top20_demand"]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Bar chart
bars = ax1.bar(df_top20['item_id'], df_top20['forecasted_demand_next_7d'],
               color=df_top20['stock_status'].map({"risk_stockout": "red", "enough": "green"}))

ax1.set_xticklabels(df_top20['item_id'], rotation=45, ha='right')
ax1.set_title("Top 20 Products by Forecasted Demand (Next 7 Days)")
ax1.set_ylabel("Forecasted Demand")

# Add numbers
for bar in bars:
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
             f'{int(bar.get_height())}', ha='center', va='bottom')

# Table below
ax2.axis('off')
table = ax2.table(cellText=df_top20[['item_id', 'forecasted_demand_next_7d', 'stock_level', 'stock_status']].values,
                  colLabels=['Item ID', 'Forecasted Demand', 'Stock Level', 'Status'],
                  loc='center',
                  cellLoc='center',
                  colLoc='center')

plt.tight_layout()
plt.savefig(f"{output_folder}/top20_products.png", dpi=300, bbox_inches="tight")
plt.show()

# ---- Risk of Stockout ----
df_risk = dfs["risk_stockout_by_reorder_point"]
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(range(len(df_risk)), df_risk['stockout_count_last_month'],
       color=df_risk['stockout_risk'].map({"risk": "red", "no_risk": "green"}))
ax.set_xticks(range(len(df_risk)))
ax.set_xticklabels(df_risk['item_id'], rotation=45, ha='right')
ax.set_title("Stockout Risk (Last Month)")
ax.set_ylabel("Stockout Count")

plt.tight_layout()
plt.savefig(f"{output_folder}/risk_stockout.png", dpi=300, bbox_inches="tight")
plt.close()

# ---- Picking Efficiency ----
df_pick = dfs["picking_efficiency"]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
ax1.bar(range(len(df_pick)), df_pick['avg_picking_time'], color="skyblue")
ax1.set_xticks(range(len(df_pick)))
ax1.set_xticklabels(df_pick['zone'], rotation=45, ha='right')
ax1.set_title("Average Picking Time by Zone")
ax1.set_xlabel("Zone")
ax1.set_ylabel("Avg Picking Time (seconds)")

ax2.axis('off')
ax2.table(cellText=df_pick[['zone', 'avg_picking_time', 'avg_layout_efficiency']].values,
          colLabels=['Zone', 'Avg Picking Time', 'Layout Efficiency'],
          loc='center', cellLoc='center', colLoc='center')

plt.tight_layout()
plt.savefig(f"{output_folder}/picking_efficiency.png", dpi=300, bbox_inches="tight")
plt.close()

# ---- Order Fulfillment & KPI ----
df_order = dfs["order_kpi"]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
ax1.bar(range(len(df_order)), df_order['avg_KPI_score'], color="lightgreen")
ax1.set_xticks(range(len(df_order)))
ax1.set_xticklabels(df_order['category'], rotation=45, ha='right')
ax1.set_title("Order Fulfillment & KPI Overview by Category")
ax1.set_xlabel("Category")
ax1.set_ylabel("Average KPI Score")

ax2.axis('off')
ax2.table(cellText=df_order[['category','avg_fulfillment_rate','total_orders','avg_turnover']].values,
          colLabels=['Category','Fulfillment Rate','Total Orders','Turnover'],
          loc='center', cellLoc='center', colLoc='center')

plt.tight_layout()
plt.savefig(f"{output_folder}/order_fulfillment_kpi.png", dpi=300, bbox_inches="tight")
plt.close()

# ---- Cost Analysis ----
df_cost = dfs["cost_analysis"]
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(range(len(df_cost)), df_cost['profit_margin_estimate'], color="orange")
ax.set_xticks(range(len(df_cost)))
ax.set_xticklabels(df_cost['item_id'], rotation=45, ha='right')
ax.set_title("Top 20 Items by Profit Margin Estimate")
ax.set_ylabel("Profit Margin Estimate")

plt.tight_layout()
plt.savefig(f"{output_folder}/cost_analysis.png", dpi=300, bbox_inches="tight")
plt.close()

print("All 5 charts saved in folder:", output_folder)

