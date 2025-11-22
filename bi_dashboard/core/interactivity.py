"""
Interactivity handlers for BI Dashboard.
"""
from typing import Dict, Any, Callable, Optional, List
from dash import Input, Output, State, callback_context
import pandas as pd

from ..utils.helpers import get_logger


class InteractivityManager:
    """Manages interactive features and callbacks for the dashboard."""
    
    def __init__(self):
        """Initialize the interactivity manager."""
        self.logger = get_logger("InteractivityManager")
        self._callbacks: Dict[str, Callable] = {}
    
    def register_callback(self, callback_id: str, callback_func: Callable):
        """Register a callback function."""
        self._callbacks[callback_id] = callback_func
        self.logger.info(f"Callback registered: {callback_id}")
    
    def create_filter_callback(self, filter_component_id: str,
                              target_component_id: str,
                              filter_func: Callable[[Any], pd.DataFrame]) -> Callable:
        """
        Create a callback that filters data based on a filter component.
        
        Args:
            filter_component_id: ID of the filter component
            target_component_id: ID of the component to update
            filter_func: Function that takes filter value and returns filtered DataFrame
        
        Returns:
            Callback function
        """
        def callback(filter_value):
            try:
                filtered_data = filter_func(filter_value)
                return filtered_data.to_dict('records')
            except Exception as e:
                self.logger.error(f"Filter callback error: {e}")
                return []
        
        return callback
    
    def create_drill_down_callback(self, source_component_id: str,
                                   target_component_id: str,
                                   drill_func: Callable[[Dict], pd.DataFrame]) -> Callable:
        """
        Create a callback for drill-down functionality.
        
        Args:
            source_component_id: ID of the source component (e.g., chart)
            target_component_id: ID of the target component to show details
            drill_func: Function that takes click data and returns detailed DataFrame
        
        Returns:
            Callback function
        """
        def callback(click_data):
            if click_data:
                try:
                    detail_data = drill_func(click_data)
                    return detail_data.to_dict('records')
                except Exception as e:
                    self.logger.error(f"Drill-down callback error: {e}")
                    return []
            return []
        
        return callback
    
    def create_cross_filter_callback(self, source_ids: List[str],
                                     target_ids: List[str],
                                     filter_func: Callable) -> Callable:
        """
        Create a callback for cross-filtering between multiple components.
        
        Args:
            source_ids: List of source component IDs
            target_ids: List of target component IDs to update
            filter_func: Function that takes all source values and returns filtered data
        
        Returns:
            Callback function
        """
        def callback(*args):
            try:
                filtered_data = filter_func(*args)
                # Return data for each target
                return [filtered_data.to_dict('records')] * len(target_ids)
            except Exception as e:
                self.logger.error(f"Cross-filter callback error: {e}")
                return [[]] * len(target_ids)
        
        return callback
