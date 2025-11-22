"""
Main Dash application for BI Dashboard.
"""
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
from .core.data_connector import DataSourceManager
from .core.viz_engine import ChartBuilder
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

# Sample data for demo
def create_sample_data():
    """Create sample data for demonstration."""
    import numpy as np
    dates = pd.date_range("2023-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "date": dates,
        "sales": np.random.randint(1000, 5000, 100) + np.sin(np.arange(100) * 0.1) * 500,
        "region": np.random.choice(["North", "South", "East", "West"], 100),
        "product": np.random.choice(["Product A", "Product B", "Product C"], 100),
        "revenue": np.random.randint(5000, 20000, 100)
    })

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
    
    # Data Source Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Data Sources"),
                dbc.CardBody([
                    data_source_component.create_data_source_selector(),
                    data_source_component.create_file_uploader(),
                    html.Div(id="data-preview-container")
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
                                {"label": "Line Chart", "value": "line"},
                                {"label": "Bar Chart", "value": "bar"},
                                {"label": "Pie Chart", "value": "pie"},
                                {"label": "Table", "value": "table"}
                            ],
                            value="line",
                            className="mb-3"
                        ),
                        dbc.Label("X-Axis Column"),
                        dcc.Dropdown(id="x-axis-selector", className="mb-3"),
                        dbc.Label("Y-Axis Column"),
                        dcc.Dropdown(id="y-axis-selector", className="mb-3"),
                        dbc.Button("Create Chart", id="create-chart-btn", color="primary", className="mb-3")
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),
    
    # Charts Display Section
    dbc.Row([
        dbc.Col([
            html.Div(id="charts-container")
        ], width=12)
    ]),
    
    # Store for current data
    dcc.Store(id="current-data-store", data=sample_data.to_dict('records')),
    
    # Store for charts
    dcc.Store(id="charts-store", data=[])
], fluid=True)


@app.callback(
    Output("x-axis-selector", "options"),
    Output("y-axis-selector", "options"),
    Input("current-data-store", "data")
)
def update_column_selectors(data):
    """Update column selector options based on current data."""
    if not data:
        return [], []
    
    df = pd.DataFrame(data)
    options = [{"label": col, "value": col} for col in df.columns]
    return options, options


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


@app.callback(
    Output("charts-container", "children"),
    Output("charts-store", "data"),
    Input("create-chart-btn", "n_clicks"),
    State("chart-type-selector", "value"),
    State("x-axis-selector", "value"),
    State("y-axis-selector", "value"),
    State("current-data-store", "data"),
    State("charts-store", "data")
)
def create_chart(n_clicks, chart_type, x_axis, y_axis, data, existing_charts):
    """Create a new chart and add it to the dashboard."""
    if n_clicks is None or not data:
        return html.Div("Create a chart to get started"), existing_charts or []
    
    df = pd.DataFrame(data)
    
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
            chart_components.append(
                dbc.Card([
                    dbc.CardHeader(f"Chart {i+1}: {chart_info['type'].title()}"),
                    dbc.CardBody([chart_fig])
                ], className="mb-3")
            )
        
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
    
    try:
        run_server(host="127.0.0.1", port=8050, debug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
