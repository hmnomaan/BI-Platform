"""
Enhanced data source component with improved UI and automatic analytics.
"""
from dash import html, dcc, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from typing import Dict, Any, Optional, List
import base64
import io
from pathlib import Path

from ..core.data_connector import DataSourceManager
from ..utils.helpers import get_logger
from ..utils.auto_chart_generator import AutoChartGenerator
from ..utils.auto_chart_generator import AutoChartGenerator


logger = get_logger("EnhancedDataSourceComponent")


class EnhancedDataSourceComponent:
    """Enhanced component for managing data sources with better UI."""
    
    def __init__(self):
        """Initialize the enhanced data source component."""
        self.data_manager = DataSourceManager()
        self.auto_chart_gen = AutoChartGenerator(self.data_manager)
        self.auto_chart_gen = AutoChartGenerator(self.data_manager)
    
    def create_data_source_tabs(self) -> html.Div:
        """Create a tabbed interface for different data source types."""
        return dbc.Tabs([
            dbc.Tab(
                label="📁 File Upload",
                tab_id="tab-file",
                children=self._create_file_upload_tab(),
                className="mt-3"
            ),
            dbc.Tab(
                label="🗄️ Database",
                tab_id="tab-database",
                children=self._create_database_tab(),
                className="mt-3"
            ),
            dbc.Tab(
                label="🌐 API",
                tab_id="tab-api",
                children=self._create_api_tab(),
                className="mt-3"
            ),
            dbc.Tab(
                label="⚙️ Config File",
                tab_id="tab-config",
                children=self._create_config_tab(),
                className="mt-3"
            )
        ], id="data-source-tabs", active_tab="tab-file")
    
    def _create_file_upload_tab(self) -> html.Div:
        """Create file upload tab content."""
        return html.Div([
            html.H6("Upload CSV or Excel File", className="mb-3"),
            dcc.Upload(
                id="enhanced-file-upload",
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-3x mb-3", style={"color": "#667eea"}),
                    html.Br(),
                    'Drag and Drop file here or ',
                    html.A('Select Files', className="text-primary fw-bold")
                ], className="text-center p-5"),
                style={
                    'width': '100%',
                    'minHeight': '150px',
                    'lineHeight': '150px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'borderColor': '#667eea',
                    'textAlign': 'center',
                    'margin': '10px 0',
                    'backgroundColor': '#f8f9fa',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
            html.Div(id="file-upload-status", className="mt-3"),
            html.Div(id="auto-analytics-container", className="mt-4")
        ])
    
    def _create_database_tab(self) -> html.Div:
        """Create database connection tab content."""
        return html.Div([
            html.H6("Connect to Database", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Database Type", className="fw-bold"),
                    dcc.Dropdown(
                        id="db-type-selector",
                        options=[
                            {"label": "PostgreSQL", "value": "postgresql"},
                            {"label": "MySQL", "value": "mysql"}
                        ],
                        placeholder="Select database type",
                        className="mb-3"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Connection Name", className="fw-bold"),
                    dbc.Input(
                        id="db-connection-name",
                        placeholder="e.g., primary_db",
                        className="mb-3"
                    )
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Host", className="fw-bold"),
                    dbc.Input(id="db-host", placeholder="localhost", className="mb-3")
                ], width=6),
                dbc.Col([
                    dbc.Label("Port", className="fw-bold"),
                    dbc.Input(id="db-port", placeholder="5432", type="number", className="mb-3")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Database Name", className="fw-bold"),
                    dbc.Input(id="db-database", placeholder="mydb", className="mb-3")
                ], width=6),
                dbc.Col([
                    dbc.Label("Schema (optional)", className="fw-bold"),
                    dbc.Input(id="db-schema", placeholder="public", className="mb-3")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Username", className="fw-bold"),
                    dbc.Input(id="db-user", placeholder="postgres", className="mb-3")
                ], width=6),
                dbc.Col([
                    dbc.Label("Password", className="fw-bold"),
                    dbc.Input(id="db-password", type="password", placeholder="••••••••", className="mb-3")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("SQL Query or Table Name", className="fw-bold"),
                    dbc.Textarea(
                        id="db-query",
                        placeholder="SELECT * FROM table_name LIMIT 1000\nOR just: table_name",
                        rows=3,
                        className="mb-3"
                    )
                ], width=12)
            ]),
            dbc.Button(
                "Connect & Load Data",
                id="connect-database-btn",
                color="primary",
                className="w-100 mb-3"
            ),
            html.Div(id="database-connection-status", className="mt-3"),
            html.Div(id="database-auto-analytics", className="mt-4")
        ])
    
    def _create_api_tab(self) -> html.Div:
        """Create API connection tab content."""
        return html.Div([
            html.H6("Connect to REST API", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("API URL", className="fw-bold"),
                    dbc.Input(
                        id="api-url",
                        placeholder="https://api.example.com/data",
                        className="mb-3"
                    )
                ], width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("HTTP Method", className="fw-bold"),
                    dcc.Dropdown(
                        id="api-method",
                        options=[
                            {"label": "GET", "value": "GET"},
                            {"label": "POST", "value": "POST"}
                        ],
                        value="GET",
                        className="mb-3"
                    )
                ], width=6),
                dbc.Col([
                    dbc.Label("Response Format", className="fw-bold"),
                    dcc.Dropdown(
                        id="api-format",
                        options=[
                            {"label": "JSON", "value": "json"},
                            {"label": "CSV", "value": "csv"}
                        ],
                        value="json",
                        className="mb-3"
                    )
                ], width=6)
            ]),
            dbc.Accordion([
                dbc.AccordionItem([
                    dbc.Label("Headers (JSON format)", className="fw-bold"),
                    dbc.Textarea(
                        id="api-headers",
                        placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}',
                        rows=3,
                        className="mb-3"
                    )
                ], title="Request Headers"),
                dbc.AccordionItem([
                    dbc.Label("Parameters (JSON format)", className="fw-bold"),
                    dbc.Textarea(
                        id="api-params",
                        placeholder='{"limit": 1000, "offset": 0}',
                        rows=3,
                        className="mb-3"
                    )
                ], title="Query Parameters")
            ], start_collapsed=True, className="mb-3"),
            dbc.Button(
                "Fetch Data",
                id="fetch-api-btn",
                color="primary",
                className="w-100 mb-3"
            ),
            html.Div(id="api-connection-status", className="mt-3"),
            html.Div(id="api-auto-analytics", className="mt-4")
        ])
    
    def _create_config_tab(self) -> html.Div:
        """Create config file selector tab content."""
        available_sources = self.data_manager.list_available_sources()
        
        return html.Div([
            html.H6("Select from Configuration File", className="mb-3"),
            html.P(
                "Choose a data source that has been configured in datasource_config.yaml",
                className="text-muted mb-3"
            ),
            dbc.Label("Available Data Sources", className="fw-bold"),
            dcc.Dropdown(
                id="config-source-selector",
                options=[{"label": source, "value": source} for source in available_sources],
                placeholder="Select a configured data source" if available_sources else "No sources configured",
                disabled=len(available_sources) == 0,
                className="mb-3"
            ),
            dbc.Button(
                "Load from Config",
                id="load-config-source-btn",
                color="primary",
                className="w-100 mb-3",
                disabled=len(available_sources) == 0
            ),
            html.Div(id="config-source-status", className="mt-3"),
            html.Div(id="config-auto-analytics", className="mt-4")
        ])
    
    def create_auto_analytics_section(self, data: pd.DataFrame) -> html.Div:
        """Create automatic analytics section after data is loaded."""
        if data is None or data.empty:
            return html.Div()
        
        # Use auto chart generator for better suggestions
        suggestions = self.auto_chart_gen.generate_chart_configs(data, max_charts=3)
        
        # Get field structure for reference
        structure = self.auto_chart_gen.analyze_data_structure(data)
        numeric_cols = structure['numeric']
        date_cols = structure['date']
        categorical_cols = structure['categorical']
        
        # Time series chart if we have date and numeric columns
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            suggestions.append({
                "type": "line",
                "title": f"{numeric_col} Over Time",
                "x_axis": date_col,
                "y_axis": numeric_col,
                "description": "Time series showing trend over time"
            })
        
        # Bar chart for categorical vs numeric
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            suggestions.append({
                "type": "bar",
                "title": f"{num_col} by {cat_col}",
                "x_axis": cat_col,
                "y_axis": num_col,
                "description": "Comparison across categories"
            })
        
        # Pie chart for categorical distribution
        if categorical_cols:
            cat_col = categorical_cols[0]
            if numeric_cols:
                num_col = numeric_cols[0]
                suggestions.append({
                    "type": "pie",
                    "title": f"Distribution of {num_col}",
                    "names": cat_col,
                    "values": num_col,
                    "description": "Proportional distribution"
                })
        
        if not suggestions:
            return html.Div([
                dbc.Alert(
                    "Data loaded successfully! Use the Chart Builder to create visualizations.",
                    color="success",
                    className="mb-3"
                )
            ])
        
        # Create suggestion cards
        suggestion_cards = []
        for i, suggestion in enumerate(suggestions[:3]):  # Show max 3 suggestions
            card = dbc.Card([
                dbc.CardBody([
                    html.H6(suggestion["title"], className="card-title"),
                    html.P(suggestion.get("description", ""), className="text-muted small"),
                    dbc.Button(
                        "Create This Chart",
                        id={"type": "auto-chart-btn", "index": i},
                        color="primary",
                        size="sm",
                        className="mt-2"
                    )
                ])
            ], className="mb-2")
            suggestion_cards.append(card)
        
        return html.Div([
            dbc.Alert(
                f"✓ Data loaded successfully! {len(data)} rows, {len(data.columns)} columns",
                color="success",
                className="mb-3"
            ),
            html.H6("📊 Suggested Analytics", className="mb-3"),
            html.Div(suggestion_cards),
            html.Hr(),
            html.P(
                "You can also create custom charts using the Chart Builder below.",
                className="text-muted small"
            )
        ])
    
    def create_data_preview(self, data: pd.DataFrame, preview_id: str = "enhanced-data-preview") -> html.Div:
        """Create enhanced data preview with statistics."""
        if data is None or data.empty:
            return html.Div("No data to preview", className="text-muted")
        
        total_rows = len(data)
        total_cols = len(data.columns)
        preview_limit = 100
        preview_data = data.head(preview_limit)
        
        # Create statistics summary
        schema = self.data_manager.infer_schema(data)
        numeric_cols = [col for col, dtype in schema.items() if dtype == 'number']
        
        stats_cards = []
        if numeric_cols:
            for col in numeric_cols[:4]:  # Show stats for first 4 numeric columns
                col_data = data[col].dropna()
                if len(col_data) > 0:
                    stats_cards.append(
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(col, className="card-title small"),
                                html.P([
                                    html.Strong("Mean: "), f"{col_data.mean():.2f}",
                                    html.Br(),
                                    html.Strong("Min: "), f"{col_data.min():.2f}",
                                    html.Br(),
                                    html.Strong("Max: "), f"{col_data.max():.2f}"
                                ], className="small mb-0")
                            ])
                        ], className="mb-2")
                    )
        
        return html.Div([
            html.H6(f"Data Preview ({total_rows:,} rows, {total_cols} columns)", className="mb-3"),
            
            # Statistics cards
            html.Div([
                dbc.Row([
                    dbc.Col(card, width=3) for card in stats_cards
                ], className="mb-3")
            ]) if stats_cards else html.Div(),
            
            # Data table
            dash_table.DataTable(
                id=preview_id,
                data=preview_data.to_dict('records'),
                columns=[{"name": col, "id": col} for col in preview_data.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontSize': '12px',
                    'whiteSpace': 'normal',
                    'height': 'auto'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                filter_action="native",
                sort_action="native",
                page_action="native" if total_rows > 100 else None
            ),
            
            html.Div([
                html.Small(
                    f"Showing first {min(preview_limit, total_rows)} of {total_rows:,} rows",
                    className="text-muted"
                )
            ], className="mt-2 text-end")
        ], className="p-3")

