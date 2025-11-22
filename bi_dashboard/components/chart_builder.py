"""
Chart builder component for BI Dashboard.
"""
from dash import html, dcc
import pandas as pd
from typing import Dict, Any, Optional, List

from ..core.viz_engine import ChartBuilder
from ..utils.helpers import get_logger


logger = get_logger("ChartBuilder")


class ChartBuilderComponent:
    """Component for building and managing charts."""
    
    def __init__(self):
        """Initialize the chart builder component."""
        self.chart_builder = ChartBuilder()
    
    def build_chart(self, chart_type: str, data: pd.DataFrame,
                   config: Dict[str, Any]) -> dcc.Graph:
        """
        Build a chart based on type and configuration.
        
        Args:
            chart_type: Type of chart (line, bar, pie, table)
            data: DataFrame with data
            config: Chart configuration dictionary
        
        Returns:
            Dash Graph component
        """
        chart_type = chart_type.lower()
        
        # Prepare config for the new API
        chart_config = config.copy()
        
        # Map old config keys to new ones
        if chart_type == "line":
            if "x_axis" not in chart_config and "x_axis" in config:
                chart_config["x_axis"] = config["x_axis"]
            if "y_axis" not in chart_config and "y_axis" in config:
                chart_config["y_axis"] = config["y_axis"]
        elif chart_type == "bar":
            if "x_axis" not in chart_config:
                chart_config["x_axis"] = config.get("dimensions") or config.get("x_axis")
            if "y_axis" not in chart_config:
                chart_config["y_axis"] = config.get("measures") or config.get("y_axis")
        elif chart_type == "pie":
            if "names" not in chart_config:
                chart_config["names"] = config.get("names")
            if "values" not in chart_config:
                chart_config["values"] = config.get("values")
        
        # Create the chart figure
        fig = self.chart_builder.create_chart(data, chart_type, chart_config)
        
        # Wrap in Dash Graph component
        return dcc.Graph(figure=fig)
    
    def build_chart_with_controls(self, chart_type: str, data: pd.DataFrame,
                                 config: Dict[str, Any]) -> html.Div:
        """
        Build a chart with control panel.
        
        Args:
            chart_type: Type of chart
            data: DataFrame with data
            config: Chart configuration
        
        Returns:
            Div containing chart and controls
        """
        chart = self.build_chart(chart_type, data, config)
        
        controls = html.Div([
            html.H6("Chart Controls", className="mb-2"),
            dcc.Dropdown(
                id=f"chart-filter-{config.get('id', 'default')}",
                options=[{"label": col, "value": col} for col in data.columns],
                placeholder="Select filter column",
                className="mb-2"
            ),
            dcc.RangeSlider(
                id=f"chart-range-{config.get('id', 'default')}",
                min=0,
                max=len(data) - 1,
                value=[0, len(data) - 1],
                marks={i: str(i) for i in range(0, len(data), max(1, len(data) // 5))}
            )
        ], className="chart-controls p-3")
        
        return html.Div([
            html.Div(chart, className="chart-container"),
            controls
        ], className="chart-with-controls")

