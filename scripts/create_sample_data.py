"""
Create sample data files for testing the BI Dashboard.
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Create sample sales data
print("Creating sample sales data...")
dates = pd.date_range("2023-01-01", periods=365, freq="D")
sales_data = pd.DataFrame({
    "date": dates,
    "sales": np.random.randint(1000, 5000, 365) + np.sin(np.arange(365) * 0.02) * 1000,
    "region": np.random.choice(["North", "South", "East", "West"], 365),
    "product": np.random.choice(["Product A", "Product B", "Product C", "Product D"], 365),
    "revenue": np.random.randint(5000, 20000, 365),
    "quantity": np.random.randint(10, 100, 365),
    "customer_id": np.random.randint(1, 50, 365)
})

sales_data.to_csv(data_dir / "sales_data.csv", index=False)
print(f"Created {data_dir / 'sales_data.csv'} with {len(sales_data)} rows")

# Create sample employee data
print("Creating sample employee data...")
employee_data = pd.DataFrame({
    "employee_id": range(1, 51),
    "name": [f"Employee {i}" for i in range(1, 51)],
    "department": np.random.choice(["Sales", "Marketing", "Engineering", "HR", "Finance"], 50),
    "salary": np.random.randint(50000, 150000, 50),
    "years_experience": np.random.randint(0, 20, 50),
    "performance_score": np.random.uniform(3.0, 5.0, 50).round(2)
})

employee_data.to_csv(data_dir / "employee_data.csv", index=False)
print(f"Created {data_dir / 'employee_data.csv'} with {len(employee_data)} rows")

# Create sample time series data
print("Creating sample time series data...")
time_series = pd.DataFrame({
    "timestamp": pd.date_range("2023-01-01", periods=1000, freq="h"),
    "temperature": 20 + np.sin(np.arange(1000) * 0.1) * 10 + np.random.normal(0, 2, 1000),
    "humidity": 50 + np.random.normal(0, 10, 1000),
    "pressure": 1013 + np.random.normal(0, 5, 1000),
    "location": np.random.choice(["Location A", "Location B", "Location C"], 1000)
})

time_series.to_csv(data_dir / "time_series_data.csv", index=False)
print(f"Created {data_dir / 'time_series_data.csv'} with {len(time_series)} rows")

print("\nSample data files created successfully!")
print(f"Data directory: {data_dir.absolute()}")

