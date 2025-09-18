# Warehouse Data Analysis (SQL + Python)

**What it does:**  
Analyze warehouse data from **Google BigQuery** and generate **5 key charts** to understand inventory and product demand trends.
---

## Charts Included
1. Top 20 Products by Forecasted Demand
![Top 20 Products](warehouse_dashboard_python/charts_output/top20_products.png)

2. Items at Risk of Stockout
![Items at Risk of Stockout](warehouse_dashboard_python/charts_output/risk_stockout.png)

3. Average Picking Time by Zone
![Average Picking Time by Zone](warehouse_dashboard_python/charts_output/picking_efficiency.png)

4. Order Fulfillment & KPI Overview by Category  
![Order Fulfillment & KPI Overview by Category](warehouse_dashboard_python/charts_output/order_fulfillment_kpi.png)

5. Top 20 Items by Profit Margin Estimate
![Top 20 Items by Profit Margin Estimate](warehouse_dashboard_python/charts_output/cost_analysis.png)

## How to Run
`1.` Clone repo:  
`git clone https://github.com/tuyettran15999/warehouse-dashboard-python.git
cd warehouse-dashboard-python`

`2.` Install packages:
`pip install -r requirements.txt`

`3.` Set Google Cloud credentials:
`export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"` 

`4.` Run:
`python warehouse.py` 
Charts will appear and also be saved in charts_output/.


```markdown
## What’s Inside

- `python_code/` → main code  
- `charts_output/` → generated charts  
- `raw_data/` → optional CSVs
