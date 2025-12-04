"""Chart factory for BI Dashboard.

Small, configurable factory to create Plotly figures from a chart configuration dict.
This is intentionally lightweight and supports common chart types: line, bar, pie, table.
"""
from typing import Dict, Any
import plotly.express as px
import pandas as pd


def build_chart(chart_config: Dict[str, Any], df: pd.DataFrame):
    """Build a Plotly figure based on `chart_config` and a pandas DataFrame.

    chart_config example:
    {
        "type": "line",
        "x": "date",
        "y": "sales",
        "color": "region",
        "title": "Sales over time"
    }
    """
    chart_type = chart_config.get("type", "line").lower()
    x = chart_config.get("x")
    y = chart_config.get("y")
    color = chart_config.get("color")
    title = chart_config.get("title")

    if chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color, title=title)
    elif chart_type == "bar":
        fig = px.bar(df, x=x, y=y, color=color, title=title)
    elif chart_type == "pie":
        names = chart_config.get("names") or x
        values = chart_config.get("values") or y
        fig = px.pie(df, names=names, values=values, title=title)
    elif chart_type == "table":
        # For a table, return a plotly figure with table trace
        from plotly.graph_objs import Figure, Table
        header_vals = chart_config.get("columns") or list(df.columns)
        cells = [df[col].tolist() for col in header_vals]
        fig = Figure(data=[Table(header=dict(values=header_vals), cells=dict(values=cells))])
    else:
        # default to line
        fig = px.line(df, x=x, y=y, color=color, title=title)

    # Apply simple style overrides and responsive defaults
    layout_overrides = chart_config.get("layout", {})
    # sensible defaults for responsiveness and spacing
    defaults = {
        "template": chart_config.get("template", "plotly_white"),
        "autosize": True,
        "margin": {"t": 40, "l": 10, "r": 10, "b": 10},
    }
    # merge defaults with layout_overrides (overrides take precedence)
    merged = {**defaults, **layout_overrides}
    fig.update_layout(**merged)

    # make sure axes have responsive ticks when time series
    try:
        if "x" in chart_config and chart_config.get("type") in ("line", "bar"):
            fig.update_xaxes(automargin=True)
            fig.update_yaxes(automargin=True)
    except Exception:
        pass

    return fig


__all__ = ["build_chart"]
