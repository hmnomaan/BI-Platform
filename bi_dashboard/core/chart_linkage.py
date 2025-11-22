"""
Chart linkage and drill-down functionality.
Enables interactive filtering between charts.
"""
import pandas as pd
from typing import Dict, Any, Optional, Callable, List
from dash import Input, Output, State, callback_context

from ..utils.helpers import get_logger


logger = get_logger("ChartLinkage")


class ChartLinkageManager:
    """Manages chart linkage and drill-down interactions."""
    
    def __init__(self):
        """Initialize the linkage manager."""
        self.linkages: Dict[str, List[str]] = {}  # source_chart_id -> [target_chart_ids]
        self.drill_down_configs: Dict[str, Dict[str, Any]] = {}
    
    def link_charts(self, source_chart_id: str, target_chart_ids: List[str]):
        """
        Link charts so clicking on source filters targets.
        
        Args:
            source_chart_id: ID of the source chart
            target_chart_ids: List of target chart IDs to filter
        """
        self.linkages[source_chart_id] = target_chart_ids
        logger.info(f"Linked chart {source_chart_id} to {len(target_chart_ids)} targets")
    
    def create_linkage_callback(self, source_id: str, target_ids: List[str],
                                filter_func: Callable[[Dict[str, Any], pd.DataFrame], pd.DataFrame]) -> Callable:
        """
        Create a callback for chart linkage.
        
        Args:
            source_id: Source chart ID
            target_ids: Target chart IDs
            filter_func: Function that takes click data and full data, returns filtered DataFrame
        
        Returns:
            Callback function
        """
        def callback(click_data, *data_stores):
            if not click_data or not click_data.get('points'):
                # No selection, return original data
                return [data for data in data_stores]
            
            try:
                # Get clicked point data
                point = click_data['points'][0]
                
                # Get full data from stores
                filtered_data = []
                for data_store in data_stores:
                    if data_store:
                        df = pd.DataFrame(data_store)
                        # Apply filter based on clicked point
                        filtered_df = filter_func(point, df)
                        filtered_data.append(filtered_df.to_dict('records'))
                    else:
                        filtered_data.append([])
                
                logger.info(f"Linked charts filtered based on click: {point}")
                return filtered_data
            except Exception as e:
                logger.error(f"Linkage callback error: {e}")
                return [data for data in data_stores]
        
        return callback
    
    def setup_drill_down(self, chart_id: str, drill_config: Dict[str, Any]):
        """
        Setup drill-down configuration for a chart.
        
        Args:
            chart_id: Chart ID
            drill_config: Configuration with drill-down rules
                {
                    "levels": ["country", "region", "city"],
                    "current_level": 0,
                    "data_mapping": {...}
                }
        """
        self.drill_down_configs[chart_id] = drill_config
        logger.info(f"Drill-down configured for chart {chart_id}")
    
    def create_drill_down_callback(self, chart_id: str,
                                  drill_func: Callable[[Dict[str, Any], pd.DataFrame, int], pd.DataFrame]) -> Callable:
        """
        Create a callback for drill-down functionality.
        
        Args:
            chart_id: Chart ID
            drill_func: Function that takes click data, current data, and level, returns drilled data
        
        Returns:
            Callback function
        """
        def callback(click_data, current_data, current_level):
            if not click_data or not click_data.get('points'):
                return current_data, current_level
            
            try:
                point = click_data['points'][0]
                df = pd.DataFrame(current_data) if current_data else pd.DataFrame()
                
                # Get drill config
                config = self.drill_down_configs.get(chart_id, {})
                levels = config.get("levels", [])
                
                if current_level < len(levels) - 1:
                    # Drill down to next level
                    next_level = current_level + 1
                    drilled_df = drill_func(point, df, next_level)
                    
                    logger.info(f"Drilled down from level {current_level} to {next_level}")
                    return drilled_df.to_dict('records'), next_level
                else:
                    # Already at deepest level
                    logger.info("Already at deepest drill-down level")
                    return current_data, current_level
            except Exception as e:
                logger.error(f"Drill-down callback error: {e}")
                return current_data, current_level
        
        return callback
    
    def create_time_range_filter(self, data_store_id: str, 
                                 date_column: str) -> Callable:
        """
        Create a time range filter callback.
        
        Args:
            data_store_id: ID of the data store
            date_column: Name of the date column
        
        Returns:
            Callback function
        """
        def callback(start_date, end_date, full_data):
            if not start_date or not end_date or not full_data:
                return full_data
            
            try:
                df = pd.DataFrame(full_data)
                df[date_column] = pd.to_datetime(df[date_column])
                
                filtered_df = df[
                    (df[date_column] >= pd.to_datetime(start_date)) &
                    (df[date_column] <= pd.to_datetime(end_date))
                ]
                
                logger.info(f"Filtered data by date range: {start_date} to {end_date}")
                return filtered_df.to_dict('records')
            except Exception as e:
                logger.error(f"Time range filter error: {e}")
                return full_data
        
        return callback
    
    def create_aggregation_calculator(self, aggregation_type: str = "sum") -> Callable:
        """
        Create a function to calculate aggregations (sum, average, proportion).
        
        Args:
            aggregation_type: Type of aggregation (sum, mean, count, proportion)
        
        Returns:
            Aggregation function
        """
        def calculate(data: pd.DataFrame, value_column: str, 
                    group_by: Optional[str] = None) -> Dict[str, Any]:
            try:
                if group_by:
                    grouped = data.groupby(group_by)[value_column]
                else:
                    # Overall aggregation
                    if aggregation_type == "sum":
                        result = data[value_column].sum()
                    elif aggregation_type == "mean":
                        result = data[value_column].mean()
                    elif aggregation_type == "count":
                        result = len(data)
                    else:
                        result = data[value_column].sum()
                    
                    return {
                        "type": aggregation_type,
                        "value": float(result),
                        "formatted": f"{result:,.2f}"
                    }
                
                # Grouped aggregation
                if aggregation_type == "sum":
                    result = grouped.sum().to_dict()
                elif aggregation_type == "mean":
                    result = grouped.mean().to_dict()
                elif aggregation_type == "count":
                    result = grouped.count().to_dict()
                else:
                    result = grouped.sum().to_dict()
                
                return {
                    "type": aggregation_type,
                    "values": result,
                    "formatted": {k: f"{v:,.2f}" for k, v in result.items()}
                }
            except Exception as e:
                logger.error(f"Aggregation calculation error: {e}")
                return {"error": str(e)}
        
        return calculate

