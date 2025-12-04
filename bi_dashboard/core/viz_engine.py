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
            'table': self._create_table,
            'scatter': self._create_scatter_chart,
            'area': self._create_area_chart,
            'histogram': self._create_histogram,
            'box': self._create_box_plot,
            'heatmap': self._create_heatmap
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
    
    def _create_scatter_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create scatter plot for correlations"""
        fig = px.scatter(
            data,
            x=config['x_axis'],
            y=config['y_axis'],
            title=config.get('title', 'Scatter Plot'),
            color=config.get('color'),
            size=config.get('size'),
            hover_data=config.get('hover_data')
        )
        return fig
    
    def _create_area_chart(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create area chart for cumulative trends"""
        fig = px.area(
            data,
            x=config['x_axis'],
            y=config['y_axis'],
            title=config.get('title', 'Area Chart'),
            color=config.get('color'),
            groupnorm=config.get('groupnorm')
        )
        return fig
    
    def _create_histogram(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create histogram for distribution"""
        fig = px.histogram(
            data,
            x=config.get('x_axis', config.get('y_axis')),
            y=config.get('y_axis'),
            title=config.get('title', 'Histogram'),
            color=config.get('color'),
            nbins=config.get('nbins', 30),
            marginal=config.get('marginal')
        )
        return fig
    
    def _create_box_plot(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create box plot for distribution comparison"""
        fig = px.box(
            data,
            x=config.get('x_axis'),
            y=config.get('y_axis'),
            title=config.get('title', 'Box Plot'),
            color=config.get('color')
        )
        return fig
    
    def _create_heatmap(self, data: pd.DataFrame, config: Dict[str, Any]) -> go.Figure:
        """Create heatmap for correlation or matrix visualization"""
        # If numeric columns specified, create correlation heatmap
        if config.get('correlation', False):
            numeric_cols = data.select_dtypes(include=['number']).columns
            corr_data = data[numeric_cols].corr()
            fig = px.imshow(
                corr_data,
                title=config.get('title', 'Correlation Heatmap'),
                color_continuous_scale=config.get('color_scale', 'RdBu'),
                aspect='auto'
            )
        else:
            # Create pivot table heatmap
            pivot_data = data.pivot_table(
                values=config.get('values', config.get('y_axis')),
                index=config.get('index'),
                columns=config.get('columns', config.get('x_axis')),
                aggfunc=config.get('aggfunc', 'mean')
            )
            fig = px.imshow(
                pivot_data,
                title=config.get('title', 'Heatmap'),
                color_continuous_scale=config.get('color_scale', 'Viridis'),
                aspect='auto'
            )
        return fig