"""
Example usage of the BI Dashboard.
"""
import pandas as pd
from pathlib import Path
from bi_dashboard.core.data_connector import DataSourceManager
from bi_dashboard.components.dashboard import Dashboard
from bi_dashboard.components.chart_builder import ChartBuilderComponent

# Initialize components
data_manager = DataSourceManager()
dashboard = Dashboard()
chart_builder = ChartBuilderComponent()

# Example 1: Load data from CSV
try:
    csv_path = Path("data/sample_data.csv")
    if csv_path.exists():
        df = data_manager.read_csv_excel(csv_path)
        print(f"Loaded {len(df)} rows from CSV")
        
        # Infer schema
        schema = data_manager.infer_schema(df)
        print(f"Schema: {schema['column_count']} columns, {schema['row_count']} rows")
except Exception as e:
    print(f"CSV loading failed: {e}")

# Example 2: Connect to database
try:
    db_config = {
        "type": "postgresql",
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "user": "postgres",
        "password": "password",
        "query": "SELECT * FROM sales LIMIT 100"
    }
    df = data_manager.connect_database(db_config)
    print(f"Loaded {len(df)} rows from database")
except Exception as e:
    print(f"Database connection failed: {e}")

# Example 3: Fetch data from API
try:
    api_config = {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {"Authorization": "Bearer token"}
    }
    df = data_manager.fetch_api_data(api_config)
    print(f"Fetched {len(df)} rows from API")
except Exception as e:
    print(f"API fetch failed: {e}")

# Example 4: Create sample data and build dashboard
sample_data = pd.DataFrame({
    "date": pd.date_range("2023-01-01", periods=30, freq="D"),
    "sales": [1000 + i * 50 + (i % 7) * 100 for i in range(30)],
    "region": ["North", "South", "East", "West"] * 7 + ["North", "South"]
})

# Add charts to dashboard
dashboard.add_chart(
    chart_type="line",
    data=sample_data,
    config={
        "x_axis": "date",
        "y_axis": "sales",
        "title": "Sales Over Time"
    }
)

dashboard.add_chart(
    chart_type="bar",
    data=sample_data.groupby("region")["sales"].sum().reset_index(),
    config={
        "dimensions": "region",
        "measures": "sales",
        "title": "Sales by Region"
    }
)

print("Dashboard created with 2 charts")

