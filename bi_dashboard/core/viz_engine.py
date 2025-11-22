# bi_dashboard/core/viz_engine.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List

class ChartBuilder:
    def __init__(self):
        self.chart_templates = {
            'line': self._create_line_chart,
            'bar': self._create_bar_chart,
            'pie': self._create_pie_chart,
            'table': self._create_table
        }
    
    def create_chart(self, data: pd.DataFrame, chart_type: str, config: Dict[str, Any]) -> go.Figure:
        """Create chart based on type and configuration"""
        if chart_type not in self.chart_templates:
            raise ValueError(f"Unsupported chart type: {chart_type}")
            
        return self.chart_templates[chart_type](data, config)
    
    def _create_line_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create line chart for trends"""
        fig = px.line(
            data,
            x=config['x_axis'],
            y=config['y_axis'],
            title=config.get('title', 'Line Chart'),
            color=config.get('color'),
            markers=config.get('markers', True)
        )
        
        if 'x_axis_title' in config:
            fig.update_xaxes(title=config['x_axis_title'])
        if 'y_axis_title' in config:
            fig.update_yaxes(title=config['y_axis_title'])
            
        return fig
    
    def _create_bar_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create bar chart for comparisons"""
        fig = px.bar(
            data,
            x=config['x_axis'],
            y=config['y_axis'],
            title=config.get('title', 'Bar Chart'),
            color=config.get('color'),
            barmode=config.get('barmode', 'group')
        )
        
        return fig
    
    def _create_pie_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create pie chart for proportions"""
        fig = px.pie(
            data,
            names=config['names'],
            values=config['values'],
            title=config.get('title', 'Pie Chart')
        )
        
        return fig
    
    def _create_table(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create data table"""
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(data.columns),
                fill_color='paleturquoise',
                align='left'
            ),
            cells=dict(
                values=[data[col] for col in data.columns],
                fill_color='lavender',
                align='left'
            )
        )])
        
        return fig