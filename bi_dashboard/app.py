"""
Main Dash application for BI Dashboard.
"""
# Fix for Python 3.12+ compatibility: pkgutil.find_loader was removed
import sys
import pkgutil
if sys.version_info >= (3, 12) and not hasattr(pkgutil, 'find_loader'):
    def _find_loader_compat(name):
        """Compatibility shim for pkgutil.find_loader removed in Python 3.12+"""
        try:
            # Use importlib.util.find_spec instead
            import importlib.util
            spec = importlib.util.find_spec(name)
            return spec.loader if spec and spec.loader else None
        except (ImportError, AttributeError, ValueError):
            return None
    pkgutil.find_loader = _find_loader_compat

import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from pathlib import Path
import pandas as pd
import base64
import io

from .components.dashboard import Dashboard
from .components.chart_builder import ChartBuilderComponent
from .components.data_source import DataSourceComponent
from .components.enhanced_data_source import EnhancedDataSourceComponent
from .components.drag_drop_field_selector import DragDropFieldSelector
from .utils.auto_chart_generator import AutoChartGenerator
from .core.data_connector import DataSourceManager
from .core.viz_engine import ChartBuilder
from .config_loader import BIDashboardConfigLoader
import plotly.io as pio
from .utils.helpers import get_logger


logger = get_logger("BIApp")


# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "BI Platform Dashboard"

# Initialize components
dashboard = Dashboard()
data_manager = DataSourceManager()
chart_builder = ChartBuilderComponent()
data_source_component = DataSourceComponent()
enhanced_data_source = EnhancedDataSourceComponent()
drag_drop_selector = DragDropFieldSelector()
auto_chart_gen = AutoChartGenerator(data_manager)

# Load configuration
# set a clean default template and responsive behavior for Plotly figures
pio.templates.default = "plotly_white"
config_loader = BIDashboardConfigLoader()


# Sample data for demo
def create_sample_data():
    """Create sample data for demonstration."""
    import numpy as np
    # If config provides a csv path, attempt to load it
    csv_path = config_loader.get("datasource.sample_csv")
    if csv_path:
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception:
            pass

    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "date": dates,
        "sales": np.random.randint(1000, 5000, 100) + np.sin(np.arange(100) * 0.1) * 500,
        "region": np.random.choice(["North", "South", "East", "West"], 100),
        "product": np.random.choice(["Product A", "Product B", "Product C"], 100),
        "revenue": np.random.randint(5000, 20000, 100)
    })

# Create initial sample data (may be overridden by config)
sample_data = create_sample_data()

# Main layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("BI Platform Dashboard", className="text-center mb-4"),
            html.P("Connect to data sources and create interactive visualizations", 
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    # Enhanced Data Source Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📊 Data Sources", className="mb-0"),
                    html.Small("Upload files, connect to databases, or fetch from APIs", className="text-muted")
                ]),
                dbc.CardBody([
                    enhanced_data_source.create_data_source_tabs(),
                    html.Div(id="enhanced-data-preview-container", className="mt-4")
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    # Chart Builder Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Chart Builder"),
                dbc.CardBody([
                    html.Div([
                        dbc.Label("Chart Type"),
                        dcc.Dropdown(
                            id="chart-type-selector",
                            options=[
                                {"label": "📈 Line Chart", "value": "line"},
                                {"label": "📊 Bar Chart", "value": "bar"},
                                {"label": "🥧 Pie Chart", "value": "pie"},
                                {"label": "📍 Scatter Plot", "value": "scatter"},
                                {"label": "📉 Area Chart", "value": "area"},
                                {"label": "📊 Histogram", "value": "histogram"},
                                {"label": "📦 Box Plot", "value": "box"},
                                {"label": "🔥 Heatmap", "value": "heatmap"},
                                {"label": "📋 Table", "value": "table"}
                            ],
                            value="line",
                            className="mb-3"
                        ),
                        # Initialize with sample data fields on first load
                        drag_drop_selector.create_field_selector(
                            available_fields=list(sample_data.columns),
                            x_axis_field=None,
                            y_axis_field=None,
                            field_types=data_manager.infer_schema(sample_data),
                            component_id_prefix="field-selector"
                        ),
                        dcc.Checklist(
                            id="downsample-toggle",
                            options=[{"label": "Auto-downsample large data for performance", "value": "on"}],
                            value=["on"],
                            inputStyle={"margin-right": "6px"},
                            className="mb-2"
                        ),
                        dbc.Button("Create Chart", id="create-chart-btn", color="primary", className="mb-3")
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    # Charts Display Section
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="charts-loading",
                type="circle",
                children=html.Div(id="charts-container"),
            )
        ], width=12)
    ]),
    
    # Store for current data
    dcc.Store(id="current-data-store", data=sample_data.to_dict('records')),
    
    # Store for charts
    dcc.Store(id="charts-store", data=[]),
    
    # Stores for drag-and-drop field selection (updated via JavaScript)
    dcc.Store(id="field-selector-x-axis-store", data=None),
    dcc.Store(id="field-selector-y-axis-store", data=None),
    
    # Store for auto-generated charts
    dcc.Store(id="auto-charts-config-store", data=[]),
    
    # Hidden divs to store current field selections (updated by JS, read by callbacks)
    html.Div(id="field-selector-x-axis-value", style={"display": "none"}, **{"data-field": None}),
    html.Div(id="field-selector-y-axis-value", style={"display": "none"}, **{"data-field": None}),
    
    # Trigger for automatic chart generation
    dcc.Store(id="auto-generate-charts-trigger", data=0),
    
    # Download helper for full dataset
    dcc.Download(id="download-full-data")
], fluid=True)


# Update field selector when new data is loaded (to show new available fields)
@app.callback(
    Output("drag-drop-field-selector-container", "children"),
    Input("current-data-store", "data"),
    prevent_initial_call=True
)
def update_field_selector_on_data_change(data):
    """Update available fields when new data is loaded."""
    if not data:
        return dash.no_update
    
    df = pd.DataFrame(data)
    
    # Get field types from data manager
    schema = data_manager.infer_schema(df)
    
    # Auto-select best fields
    x_field, y_field = auto_chart_gen.get_auto_selected_fields(df)
    
    # Create drag-and-drop field selector with auto-selected fields
    selector = drag_drop_selector.create_field_selector(
        available_fields=list(df.columns),
        x_axis_field=x_field,
        y_axis_field=y_field,
        field_types=schema,
        component_id_prefix="field-selector"
    )
    
    return selector


@app.callback(
    Output("data-preview-container", "children"),
    Input("current-data-store", "data")
)
def update_data_preview(data):
    """Update data preview when data changes."""
    if not data:
        return html.Div("No data loaded")
    
    df = pd.DataFrame(data)
    return data_source_component.create_data_preview(df)


# Callbacks for click-to-assign field buttons
@app.callback(
    Output("field-selector-x-axis-store", "data", allow_duplicate=True),
    Input({"type": "field-to-x", "field": dash.dependencies.ALL}, "n_clicks"),
    State({"type": "field-to-x", "field": dash.dependencies.ALL}, "id"),
    prevent_initial_call=True
)
def assign_field_to_x_axis(n_clicks_list, button_ids):
    """Assign field to X-axis when X button is clicked."""
    ctx = callback_context
    if not ctx.triggered or not any(n_clicks_list):
        return dash.no_update
    
    # Get the clicked button
    trigger_id = ctx.triggered[0]["prop_id"]
    import json
    import re
    match = re.search(r'"field":\s*"([^"]+)"', trigger_id)
    if match:
        field_name = match.group(1)
        return field_name
    
    return dash.no_update


@app.callback(
    Output("field-selector-y-axis-store", "data", allow_duplicate=True),
    Input({"type": "field-to-y", "field": dash.dependencies.ALL}, "n_clicks"),
    State({"type": "field-to-y", "field": dash.dependencies.ALL}, "id"),
    prevent_initial_call=True
)
def assign_field_to_y_axis(n_clicks_list, button_ids):
    """Assign field to Y-axis when Y button is clicked."""
    ctx = callback_context
    if not ctx.triggered or not any(n_clicks_list):
        return dash.no_update
    
    # Get the clicked button
    trigger_id = ctx.triggered[0]["prop_id"]
    import json
    import re
    match = re.search(r'"field":\s*"([^"]+)"', trigger_id)
    if match:
        field_name = match.group(1)
        return field_name
    
    return dash.no_update


@app.callback(
    [Output({"type": "x-axis-field-display", "index": "display"}, "children"),
     Output({"type": "x-axis-field-display", "index": "display"}, "className"),
     Output({"type": "y-axis-field-display", "index": "display"}, "children"),
     Output({"type": "y-axis-field-display", "index": "display"}, "className")],
    [Input("field-selector-x-axis-store", "data"),
     Input("field-selector-y-axis-store", "data")]
)
def update_field_displays(x_field, y_field):
    """Update the visual display of selected fields."""
    x_display = x_field if x_field else "Drag field here"
    x_class = "dropped-field" if x_field else "drop-zone-placeholder"
    y_display = y_field if y_field else "Drag field here"
    y_class = "dropped-field" if y_field else "drop-zone-placeholder"
    return x_display, x_class, y_display, y_class


@app.callback(
    Output("field-selector-x-axis-store", "data"),
    Output("field-selector-y-axis-store", "data"),
    Input("create-chart-btn", "n_clicks"),
    State({"type": "x-axis-field-display", "index": "display"}, "children"),
    State({"type": "y-axis-field-display", "index": "display"}, "children"),
    prevent_initial_call=True
)
def sync_field_stores(n_clicks, x_display, y_display):
    """Sync stores with display values when creating chart."""
    # Extract field names from display (could be string or component)
    x_field = x_display if isinstance(x_display, str) and x_display != "Drag field here" else None
    y_field = y_display if isinstance(y_display, str) and y_display != "Drag field here" else None
    return x_field, y_field


@app.callback(
    Output("charts-container", "children"),
    Output("charts-store", "data"),
    Input("create-chart-btn", "n_clicks"),
    State("chart-type-selector", "value"),
    State("field-selector-x-axis-store", "data"),
    State("field-selector-y-axis-store", "data"),
    State("downsample-toggle", "value"),
    State("current-data-store", "data"),
    State("charts-store", "data")
)
def create_chart(n_clicks, chart_type, x_axis, y_axis, downsample_toggle, data, existing_charts):
    """Create a new chart and add it to the dashboard."""
    if n_clicks is None or not data:
        return html.Div("Create a chart to get started"), existing_charts or []
    
    df = pd.DataFrame(data)

    # Determine whether downsampling is enabled via the toggle (default on)
    downsample_enabled = bool(downsample_toggle and "on" in downsample_toggle)

    # Performance: downsample large datasets based on configured max points
    max_points = config_loader.get("dashboard.max_data_points", 10000)
    downsample_notice = None
    original_len = len(df)
    if downsample_enabled and original_len > max_points:
        try:
            df = df.sample(n=max_points, random_state=42).reset_index(drop=True)
            downsample_notice = html.Div([
                html.Span(f"Data downsampled to {max_points} rows for performance (original {original_len} rows).", className="me-3 text-warning"),
                dbc.Button("Download full dataset", id="download-full-btn", size="sm")
            ], className="mb-2")
        except Exception:
            df = df.head(max_points)
            downsample_notice = html.Div([
                html.Span(f"Data truncated to {max_points} rows for performance (original {original_len} rows).", className="me-3 text-warning"),
                dbc.Button("Download full dataset", id="download-full-btn", size="sm")
            ], className="mb-2")
    
    # Prepare config based on chart type
    if chart_type == "line":
        if not x_axis or not y_axis:
            return html.Div("Please select both X and Y axes"), existing_charts or []
        config = {
            "x_axis": x_axis,
            "y_axis": y_axis,
            "title": f"{y_axis} over {x_axis}"
        }
    elif chart_type == "bar":
        if not x_axis or not y_axis:
            return html.Div("Please select both X and Y axes"), existing_charts or []
        config = {
            "x_axis": x_axis,
            "y_axis": y_axis,
            "title": f"{y_axis} by {x_axis}"
        }
    elif chart_type == "pie":
        if not x_axis or not y_axis:
            return html.Div("Please select Names and Values columns"), existing_charts or []
        config = {
            "names": x_axis,
            "values": y_axis,
            "title": f"{y_axis} Distribution"
        }
    elif chart_type == "table":
        config = {"title": "Data Table"}
    else:
        return html.Div("Invalid chart type"), existing_charts or []
    
    # Create chart
    try:
        chart = chart_builder.build_chart(chart_type, df, config)
        chart_id = f"chart-{len(existing_charts)}"
        
        # Add to existing charts
        new_charts = existing_charts.copy() if existing_charts else []
        new_charts.append({
            "id": chart_id,
            "type": chart_type,
            "config": config
        })
        
        # Build all charts
        chart_components = []
        for i, chart_info in enumerate(new_charts):
            chart_fig = chart_builder.build_chart(
                chart_info["type"],
                df,
                chart_info["config"]
            )

            # chart_builder may return a dcc.Graph component or a plotly Figure.
            # Normalize to a Figure object for consistent wrapping.
            try:
                # If it's a Dash Graph component, it will have a 'figure' attribute
                fig_obj = chart_fig.figure if hasattr(chart_fig, "figure") else chart_fig
            except Exception:
                fig_obj = chart_fig

            # ensure responsive layout and consistent sizing
            graph = dcc.Graph(
                id={"type": "dashboard-graph", "index": i},
                figure=fig_obj,
                config={"responsive": True, "displayModeBar": False},
                style={"width": "100%", "height": "420px"}
            )

            chart_components.append(
                dbc.Card([
                    dbc.CardHeader(f"Chart {i+1}: {chart_info['type'].title()}"),
                    dbc.CardBody([graph], className="p-2")
                ], className="mb-3 chart-item")
            )
        
        # Prepend downsample warning if applicable
        if downsample_notice is not None:
            chart_components.insert(0, downsample_notice)

        return html.Div(chart_components), new_charts
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        return html.Div(f"Error creating chart: {str(e)}"), existing_charts or []


@app.callback(
    Output("current-data-store", "data"),
    Input("file-upload", "contents"),
    State("file-upload", "filename")
)
def handle_file_upload(contents, filename):
    """Handle file upload and parse data."""
    if contents is None:
        return dash.no_update
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return dash.no_update
        
        logger.info(f"File uploaded: {filename}, {len(df)} rows")
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        return dash.no_update


@app.callback(
    Output("download-full-data", "data"),
    Input("download-full-btn", "n_clicks"),
    State("current-data-store", "data"),
    prevent_initial_call=True
)
def download_full_dataset(n_clicks, data):
    """Provide the full dataset as CSV when download button is clicked."""
    if not n_clicks:
        return dash.no_update
    try:
        df = pd.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "full_dataset.csv", index=False)
    except Exception as e:
        logger.error(f"Failed to prepare dataset for download: {e}")
        return dash.no_update


# Enhanced Data Source Callbacks

@app.callback(
    [Output("current-data-store", "data", allow_duplicate=True),
     Output("file-upload-status", "children"),
     Output("auto-analytics-container", "children")],
    Input("enhanced-file-upload", "contents"),
    State("enhanced-file-upload", "filename"),
    prevent_initial_call=True
)
def handle_enhanced_file_upload(contents, filename):
    """Handle enhanced file upload with automatic analytics."""
    if contents is None:
        return dash.no_update, "", html.Div()
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return dash.no_update, dbc.Alert("Unsupported file type. Please upload CSV or Excel files.", color="warning"), html.Div()
        
        logger.info(f"File uploaded: {filename}, {len(df)} rows")
        
        # Create status message
        status = dbc.Alert(
            f"✓ Successfully loaded {filename} - {len(df):,} rows, {len(df.columns)} columns",
            color="success"
        )
        
        # Create automatic analytics
        analytics = enhanced_data_source.create_auto_analytics_section(df)
        
        return df.to_dict('records'), status, analytics
    except Exception as e:
        logger.error(f"Error parsing file: {e}")
        error_msg = dbc.Alert(f"Error loading file: {str(e)}", color="danger")
        return dash.no_update, error_msg, html.Div()


@app.callback(
    [Output("current-data-store", "data", allow_duplicate=True),
     Output("database-connection-status", "children"),
     Output("database-auto-analytics", "children")],
    Input("connect-database-btn", "n_clicks"),
    [State("db-type-selector", "value"),
     State("db-connection-name", "value"),
     State("db-host", "value"),
     State("db-port", "value"),
     State("db-database", "value"),
     State("db-schema", "value"),
     State("db-user", "value"),
     State("db-password", "value"),
     State("db-query", "value")],
    prevent_initial_call=True
)
def handle_database_connection(n_clicks, db_type, conn_name, host, port, database, schema, user, password, query):
    """Handle database connection and data loading."""
    if not n_clicks or not all([db_type, host, port, database, user, password, query]):
        return dash.no_update, dbc.Alert("Please fill in all required fields.", color="warning"), html.Div()
    
    try:
        db_config = {
            "type": db_type,
            "name": conn_name or "default",
            "host": host,
            "port": int(port),
            "database": database,
            "user": user,
            "password": password
        }
        
        # Connect to database
        if data_manager.connect_database(db_config):
            # Build query
            if not query.strip().upper().startswith("SELECT"):
                # Assume it's a table name
                table_name = query.strip()
                if schema:
                    query = f'SELECT * FROM "{schema}"."{table_name}" LIMIT 1000'
                else:
                    query = f'SELECT * FROM "{table_name}" LIMIT 1000'
            
            # Load data
            engine = data_manager.connections.get(db_config["name"])
            df = pd.read_sql(query, engine)
            
            status = dbc.Alert(f"✓ Connected successfully! Loaded {len(df):,} rows", color="success")
            analytics = enhanced_data_source.create_auto_analytics_section(df)
            
            return df.to_dict('records'), status, analytics
        else:
            return dash.no_update, dbc.Alert("Failed to connect to database.", color="danger"), html.Div()
            
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return dash.no_update, dbc.Alert(f"Error: {str(e)}", color="danger"), html.Div()


@app.callback(
    [Output("current-data-store", "data", allow_duplicate=True),
     Output("api-connection-status", "children"),
     Output("api-auto-analytics", "children")],
    Input("fetch-api-btn", "n_clicks"),
    [State("api-url", "value"),
     State("api-method", "value"),
     State("api-format", "value"),
     State("api-headers", "value"),
     State("api-params", "value")],
    prevent_initial_call=True
)
def handle_api_fetch(n_clicks, url, method, format_type, headers_str, params_str):
    """Handle API data fetching."""
    if not n_clicks or not url:
        return dash.no_update, dbc.Alert("Please provide API URL.", color="warning"), html.Div()
    
    try:
        import json
        
        headers = {}
        if headers_str:
            try:
                headers = json.loads(headers_str)
            except:
                pass
        
        params = {}
        if params_str:
            try:
                params = json.loads(params_str)
            except:
                pass
        
        api_config = {
            "url": url,
            "method": method or "GET",
            "headers": headers,
            "params": params
        }
        
        df = data_manager.fetch_api_data(api_config)
        
        status = dbc.Alert(f"✓ Successfully fetched {len(df):,} rows from API", color="success")
        analytics = enhanced_data_source.create_auto_analytics_section(df)
        
        return df.to_dict('records'), status, analytics
        
    except Exception as e:
        logger.error(f"API fetch error: {e}")
        return dash.no_update, dbc.Alert(f"Error: {str(e)}", color="danger"), html.Div()


@app.callback(
    [Output("current-data-store", "data", allow_duplicate=True),
     Output("config-source-status", "children"),
     Output("config-auto-analytics", "children")],
    Input("load-config-source-btn", "n_clicks"),
    State("config-source-selector", "value"),
    prevent_initial_call=True
)
def handle_config_source_load(n_clicks, source_name):
    """Handle loading data from config file."""
    if not n_clicks or not source_name:
        return dash.no_update, html.Div(), html.Div()
    
    try:
        df = data_manager.load_from_datasource_config(source_name)
        
        status = dbc.Alert(f"✓ Successfully loaded '{source_name}' - {len(df):,} rows", color="success")
        analytics = enhanced_data_source.create_auto_analytics_section(df)
        
        return df.to_dict('records'), status, analytics
        
    except Exception as e:
        logger.error(f"Config source load error: {e}")
        return dash.no_update, dbc.Alert(f"Error: {str(e)}", color="danger"), html.Div()


@app.callback(
    Output("enhanced-data-preview-container", "children"),
    Input("current-data-store", "data")
)
def update_enhanced_data_preview(data):
    """Update enhanced data preview when data changes."""
    if not data:
        return html.Div("No data loaded. Please upload a file or connect to a data source.", className="text-muted text-center p-5")
    
    df = pd.DataFrame(data)
    return enhanced_data_source.create_data_preview(df)


@app.callback(
    [Output("charts-container", "children", allow_duplicate=True),
     Output("charts-store", "data", allow_duplicate=True),
     Output("auto-charts-config-store", "data")],
    Input("current-data-store", "data"),
    State("charts-store", "data"),
    prevent_initial_call=True
)
def auto_generate_charts_on_load(data, existing_charts):
    """Automatically generate charts when new data is loaded."""
    if not data:
        return dash.no_update, dash.no_update, dash.no_update
    
    try:
        df = pd.DataFrame(data)
        
        # Only auto-generate if no charts exist yet
        if existing_charts and len(existing_charts) > 0:
            return dash.no_update, dash.no_update, dash.no_update
        
        # Generate automatic chart configurations
        chart_configs = auto_chart_gen.generate_chart_configs(df, max_charts=2)
        
        if not chart_configs:
            return dash.no_update, dash.no_update, []
        
        # Create charts automatically
        chart_components = []
        new_charts = []
        
        for i, config in enumerate(chart_configs):
            try:
                chart_type = config["type"]
                fig = chart_builder.build_chart(chart_type, df, config)
                
                chart_id = f"auto-chart-{i}"
                graph = dcc.Graph(
                    id={"type": "dashboard-graph", "index": i},
                    figure=fig if hasattr(fig, 'figure') else fig,
                    config={"responsive": True, "displayModeBar": True},
                    style={"width": "100%", "height": "450px"}
                )
                
                chart_component = dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H6(f"📊 {config.get('title', 'Auto-Generated Chart')}", className="mb-0"),
                            html.Small("Automatically generated", className="text-muted")
                        ])
                    ]),
                    dbc.CardBody([graph], className="p-3")
                ], className="mb-4 chart-item")
                
                chart_components.append(chart_component)
                new_charts.append({
                    "id": chart_id,
                    "type": chart_type,
                    "config": config
                })
                
            except Exception as e:
                logger.warning(f"Failed to auto-generate chart {i}: {e}")
                continue
        
        if chart_components:
            return html.Div([
                dbc.Alert(
                    f"🎉 {len(chart_components)} chart(s) automatically generated from your data!",
                    color="success",
                    className="mb-3"
                )
            ] + chart_components), new_charts, chart_configs
        
        return dash.no_update, dash.no_update, []
        
    except Exception as e:
        logger.error(f"Error in auto-generate charts: {e}")
        return dash.no_update, dash.no_update, []


# Auto-generate charts from suggestions
@app.callback(
    [Output("charts-container", "children", allow_duplicate=True),
     Output("charts-store", "data", allow_duplicate=True)],
    Input({"type": "auto-chart-btn", "index": dash.dependencies.ALL}, "n_clicks"),
    State("current-data-store", "data"),
    State("auto-analytics-container", "children"),
    prevent_initial_call=True
)
def create_auto_chart(n_clicks_list, data, analytics_container):
    """Create chart automatically from suggestion."""
    if not any(n_clicks_list) or not data:
        return dash.no_update, dash.no_update
    
    # Get the clicked button index
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]["prop_id"]
    # Parse the button index from the prop_id
    import json
    import re
    match = re.search(r'\{.*?"index":\s*(\d+).*?\}', trigger_id)
    if match:
        button_index = int(match.group(1))
    else:
        return dash.no_update, dash.no_update
    
    # Extract suggestion from analytics (this is a simplified version)
    # In a real implementation, you'd store suggestions in a store
    df = pd.DataFrame(data)
    schema = data_manager.infer_schema(df)
    
    numeric_cols = [col for col, dtype in schema.items() if dtype == 'number']
    date_cols = [col for col, dtype in schema.items() if dtype == 'date']
    categorical_cols = [col for col, dtype in schema.items() if dtype == 'text']
    
    # Generate chart based on index
    chart_config = None
    if button_index == 0 and date_cols and numeric_cols:
        chart_config = {
            "type": "line",
            "x_axis": date_cols[0],
            "y_axis": numeric_cols[0],
            "title": f"{numeric_cols[0]} Over Time"
        }
    elif button_index == 1 and categorical_cols and numeric_cols:
        chart_config = {
            "type": "bar",
            "x_axis": categorical_cols[0],
            "y_axis": numeric_cols[0],
            "title": f"{numeric_cols[0]} by {categorical_cols[0]}"
        }
    elif button_index == 2 and categorical_cols and numeric_cols:
        chart_config = {
            "type": "pie",
            "names": categorical_cols[0],
            "values": numeric_cols[0],
            "title": f"Distribution of {numeric_cols[0]}"
        }
    
    if chart_config:
        try:
            fig = chart_builder.build_chart(chart_config["type"], df, chart_config)
            chart_id = "auto-chart-0"
            
            graph = dcc.Graph(
                id={"type": "dashboard-graph", "index": 0},
                figure=fig if hasattr(fig, 'figure') else fig,
                config={"responsive": True, "displayModeBar": False},
                style={"width": "100%", "height": "420px"}
            )
            
            chart_component = dbc.Card([
                dbc.CardHeader(f"Auto-Generated: {chart_config.get('title', 'Chart')}"),
                dbc.CardBody([graph], className="p-2")
            ], className="mb-3 chart-item")
            
            return html.Div([chart_component]), [{"id": chart_id, "type": chart_config["type"], "config": chart_config}]
        except Exception as e:
            logger.error(f"Error creating auto chart: {e}")
            return dash.no_update, dash.no_update
    
    return dash.no_update, dash.no_update


def run_server(host: str = "127.0.0.1", port: int = 8050, debug: bool = False):
    """
    Run the Dash server.
    
    Args:
        host: Server host
        port: Server port
        debug: Enable debug mode
    """
    logger.info(f"Starting BI Dashboard server on {host}:{port}")
    app.run_server(host=host, port=port, debug=debug)


def main():
    """Main entry point for the dashboard application."""
    import sys
    print("=" * 60)
    print("BI Platform Dashboard")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Allow CLI/env override for host/port
    host = None
    port = None
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", default=None)
        parser.add_argument("--port", type=int, default=None)
        parser.add_argument("--debug", action="store_true")
        args = parser.parse_args()
        host = args.host
        port = args.port
        debug = args.debug
    except Exception:
        host = None
        port = None
        debug = True

    host = host or config_loader.get("server.host", "127.0.0.1")
    port = port or config_loader.get("server.port", 8050)

    try:
        run_server(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
