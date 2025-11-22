"""
Performance utilities for BI Dashboard.
"""
import time
from functools import wraps
from typing import Callable, Any
import pandas as pd

from .helpers import get_logger


logger = get_logger("Performance")


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger.info(f"{func.__name__} took {elapsed_time:.2f} seconds")
        return result
    return wrapper


def cache_dataframe(func: Callable) -> Callable:
    """Decorator to cache DataFrame results."""
    cache = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        cache_key = str(args) + str(sorted(kwargs.items()))
        
        if cache_key in cache:
            logger.info(f"Cache hit for {func.__name__}")
            return cache[cache_key].copy()
        
        result = func(*args, **kwargs)
        
        if isinstance(result, pd.DataFrame):
            cache[cache_key] = result.copy()
            logger.info(f"Cached result for {func.__name__}")
        
        return result
    
    return wrapper


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize DataFrame memory usage by downcasting numeric types.
    
    Args:
        df: DataFrame to optimize
    
    Returns:
        Optimized DataFrame
    """
    start_memory = df.memory_usage(deep=True).sum() / 1024**2
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            
            if str(col_type)[:3] == 'int':
                if c_min > pd.iinfo(pd.Int8Dtype()).min and c_max < pd.iinfo(pd.Int8Dtype()).max:
                    df[col] = df[col].astype('Int8')
                elif c_min > pd.iinfo(pd.Int16Dtype()).min and c_max < pd.iinfo(pd.Int16Dtype()).max:
                    df[col] = df[col].astype('Int16')
                elif c_min > pd.iinfo(pd.Int32Dtype()).min and c_max < pd.iinfo(pd.Int32Dtype()).max:
                    df[col] = df[col].astype('Int32')
            elif str(col_type)[:5] == 'float':
                if c_min > pd.finfo(pd.Float32Dtype()).min and c_max < pd.finfo(pd.Float32Dtype()).max:
                    df[col] = df[col].astype('Float32')
    
    end_memory = df.memory_usage(deep=True).sum() / 1024**2
    logger.info(f"Memory usage reduced from {start_memory:.2f} MB to {end_memory:.2f} MB")
    
    return df

