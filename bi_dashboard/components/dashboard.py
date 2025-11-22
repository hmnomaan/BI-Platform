"""
Main dashboard component for BI Dashboard.
"""
from dash import html, dcc
import pandas as pd
from typing import Dict, Any, List, Optional

from ..core.viz_engine import ChartBuilder
from ..components.chart_builder import ChartBuilderComponent
from ..components.data_source import DataSourceComponent
from ..utils.helpers import get_logger


logger = get_logger("Dashboard")


class Dashboard:
    """Main dashboard class that assembles all components."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.chart_builder = ChartBuilderComponent()
        self.data_source = DataSourceComponent()
        self.charts: List[Dict[str, Any]] = []
    
    def add_chart(self, chart_type: str, data: pd.DataFrame, config: Dict[str, Any]):
        """Add a chart to the dashboard."""
        chart_config = {
            "id": f"chart-{len(self.charts)}",
            "type": chart_type,
            **config
        }
        self.charts.append({
            "config": chart_config,
            "data": data
        })
        logger.info(f"Chart added: {chart_type}")
    
    def build_layout(self, title: str = "BI Dashboard") -> html.Div:
        """
        Build the complete dashboard layout.
        
        Args:
            title: Dashboard title
        
        Returns:
            Complete dashboard layout
        """
        # Build all charts
        chart_components = []
        for i, chart_info in enumerate(self.charts):
            chart = self.chart_builder.build_chart(
                chart_info["config"]["type"],
                chart_info["data"],
                chart_info["config"]
            )
            chart_components.append(
                html.Div(chart, className="chart-item mb-4", id=f"chart-container-{i}")
            )
        
        # Main layout
        layout = html.Div([
            # Header
            html.Div([
                html.H1(title, className="display-4"),
                html.P("Interactive Business Intelligence Dashboard", className="lead")
            ], className="dashboard-header mb-4"),
            
            # Data source section
            html.Div([
                html.H3("Data Sources", className="mb-3"),
                self.data_source.create_data_source_selector()
            ], className="data-source-section mb-4"),
            
            # Charts section
            html.Div([
                html.H3("Charts", className="mb-3"),
                html.Div(chart_components, className="charts-container")
            ], className="charts-section"),
            
            # Store for data
            dcc.Store(id="dashboard-data-store")
        ], className="dashboard-container")
        
        return layout
    
    def create_grid_layout(self, charts_per_row: int = 2) -> html.Div:
        """
        Create a grid layout for charts.
        
        Args:
            charts_per_row: Number of charts per row
        
        Returns:
            Grid layout
        """
        chart_components = []
        for i, chart_info in enumerate(self.charts):
            chart = self.chart_builder.build_chart(
                chart_info["config"]["type"],
                chart_info["data"],
                chart_info["config"]
            )
            chart_components.append(
                html.Div(chart, className=f"col-md-{12 // charts_per_row} mb-4")
            )
        
        return html.Div([
            html.Div(chart_components, className="row")
        ], className="dashboard-grid")

