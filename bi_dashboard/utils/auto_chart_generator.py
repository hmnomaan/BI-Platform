"""
Automatic chart generation utility.
Intelligently generates charts based on data structure.
"""
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple


class AutoChartGenerator:
    """Automatically generates appropriate charts based on data structure."""
    
    def __init__(self, data_manager):
        """Initialize the auto chart generator."""
        self.data_manager = data_manager
    
    def analyze_data_structure(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Analyze data structure and return column categories."""
        schema = self.data_manager.infer_schema(df)
        
        numeric_cols = [col for col, dtype in schema.items() if dtype == 'number']
        date_cols = [col for col, dtype in schema.items() if dtype == 'date']
        categorical_cols = [col for col, dtype in schema.items() if dtype == 'text']
        
        return {
            'numeric': numeric_cols,
            'date': date_cols,
            'categorical': categorical_cols,
            'all': list(df.columns)
        }
    
    def generate_chart_configs(self, df: pd.DataFrame, max_charts: int = 3) -> List[Dict[str, Any]]:
        """Generate automatic chart configurations based on data structure."""
        structure = self.analyze_data_structure(df)
        charts = []
        
        numeric_cols = structure['numeric']
        date_cols = structure['date']
        categorical_cols = structure['categorical']
        
        # 1. Time Series Chart (Date + Numeric)
        if date_cols and numeric_cols and len(charts) < max_charts:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            charts.append({
                "type": "line",
                "title": f"{numeric_col} Over Time",
                "x_axis": date_col,
                "y_axis": numeric_col,
                "description": "Time series trend"
            })
        
        # 2. Bar Chart (Categorical + Numeric)
        if categorical_cols and numeric_cols and len(charts) < max_charts:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Check if categorical has reasonable number of unique values
            unique_count = df[cat_col].nunique()
            if unique_count <= 20:  # Only if reasonable number of categories
                charts.append({
                    "type": "bar",
                    "title": f"{num_col} by {cat_col}",
                    "x_axis": cat_col,
                    "y_axis": num_col,
                    "description": "Category comparison"
                })
        
        # 3. Scatter Plot (Numeric + Numeric)
        if len(numeric_cols) >= 2 and len(charts) < max_charts:
            charts.append({
                "type": "scatter",
                "title": f"{numeric_cols[1]} vs {numeric_cols[0]}",
                "x_axis": numeric_cols[0],
                "y_axis": numeric_cols[1],
                "description": "Correlation analysis"
            })
        
        # 4. Histogram (Numeric distribution)
        if numeric_cols and len(charts) < max_charts:
            num_col = numeric_cols[0]
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {num_col}",
                "x_axis": num_col,
                "description": "Value distribution"
            })
        
        # 5. Pie Chart (Categorical distribution with numeric)
        if categorical_cols and numeric_cols and len(charts) < max_charts:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            unique_count = df[cat_col].nunique()
            if 2 <= unique_count <= 10:  # Good for pie charts
                charts.append({
                    "type": "pie",
                    "title": f"Distribution of {num_col}",
                    "names": cat_col,
                    "values": num_col,
                    "description": "Proportional distribution"
                })
        
        # 6. Box Plot (Categorical + Numeric)
        if categorical_cols and numeric_cols and len(charts) < max_charts:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            unique_count = df[cat_col].nunique()
            if unique_count <= 10:
                charts.append({
                    "type": "box",
                    "title": f"{num_col} Distribution by {cat_col}",
                    "x_axis": cat_col,
                    "y_axis": num_col,
                    "description": "Distribution comparison"
                })
        
        # Limit to max_charts
        return charts[:max_charts]
    
    def get_auto_selected_fields(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """Automatically select best x-axis and y-axis fields."""
        structure = self.analyze_data_structure(df)
        
        numeric_cols = structure['numeric']
        date_cols = structure['date']
        categorical_cols = structure['categorical']
        
        # Priority: Date column for x-axis, numeric for y-axis
        if date_cols and numeric_cols:
            return date_cols[0], numeric_cols[0]
        
        # Fallback: Categorical for x-axis, numeric for y-axis
        if categorical_cols and numeric_cols:
            return categorical_cols[0], numeric_cols[0]
        
        # Fallback: Two numeric columns
        if len(numeric_cols) >= 2:
            return numeric_cols[0], numeric_cols[1]
        
        # Last resort: First two columns
        if len(df.columns) >= 2:
            return df.columns[0], df.columns[1]
        
        return None, None

