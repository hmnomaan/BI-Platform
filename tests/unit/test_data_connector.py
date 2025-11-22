# tests/unit/test_data_connector.py
import pytest
import pandas as pd
from bi_dashboard.core.data_connector import DataSourceManager

def test_file_reading():
    manager = DataSourceManager()
    
    # Create test CSV
    test_data = pd.DataFrame({
        'name': ['Alice', 'Bob'],
        'age': [25, 30],
        'salary': [50000.0, 60000.0]
    })
    test_data.to_csv('test.csv', index=False)
    
    df = manager.read_file('test.csv', 'csv')
    assert len(df) == 2
    assert 'name' in df.columns

def test_schema_inference():
    manager = DataSourceManager()
    
    test_data = pd.DataFrame({
        'text_col': ['a', 'b'],
        'number_col': [1, 2],
        'date_col': pd.to_datetime(['2023-01-01', '2023-01-02'])
    })
    
    schema = manager.infer_schema(test_data)
    assert schema['text_col'] == 'text'
    assert schema['number_col'] == 'number'