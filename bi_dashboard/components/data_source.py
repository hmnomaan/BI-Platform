"""
Data source component for BI Dashboard.
"""
from dash import html, dcc, dash_table
import pandas as pd
from typing import Dict, Any, Optional

from ..core.data_connector import DataSourceManager
from ..utils.helpers import get_logger


logger = get_logger("DataSourceComponent")


class DataSourceComponent:
    """Component for managing data sources."""
    
    def __init__(self):
        """Initialize the data source component."""
        self.data_manager = DataSourceManager()
    
    def create_data_source_selector(self, source_id: str = "data-source") -> html.Div:
        """Create a data source selector component."""
        return html.Div([
            html.H5("Select Data Source", className="mb-3"),
            dcc.Dropdown(
                id=f"{source_id}-type",
                options=[
                    {"label": "Database", "value": "database"},
                    {"label": "CSV/Excel File", "value": "file"},
                    {"label": "API", "value": "api"}
                ],
                placeholder="Select data source type",
                className="mb-3"
            ),
            html.Div(id=f"{source_id}-config")
        ], className="data-source-selector p-3")
    
    def create_file_uploader(self, upload_id: str = "file-upload") -> dcc.Upload:
        """Create a file upload component."""
        return dcc.Upload(
            id=upload_id,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        )
    
    def create_data_preview(self, data: pd.DataFrame,
                          preview_id: str = "data-preview") -> html.Div:
        """Create a data preview component."""
        if data is None or data.empty:
            return html.Div("No data to preview", className="text-muted")
        
        # Show first 100 rows
        preview_data = data.head(100)
        
        return html.Div([
            html.H6(f"Data Preview ({len(data)} rows, {len(data.columns)} columns)"),
            dash_table.DataTable(
                id=preview_id,
                data=preview_data.to_dict('records'),
                columns=[{"name": col, "id": col} for col in preview_data.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontSize': '12px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        ], className="data-preview p-3")

