# bi_dashboard/core/data_connector.py
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from pathlib import Path
from typing import Dict, Any, Union
import logging

class DataSourceManager:
    def __init__(self):
        self.connections = {}
        
    def connect_database(self, db_config: Dict[str, Any]) -> bool:
        """Connect to PostgreSQL/MySQL database"""
        try:
            if db_config['type'] == 'postgresql':
                engine = create_engine(
                    f"postgresql://{db_config['user']}:{db_config['password']}@"
                    f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
                )
            elif db_config['type'] == 'mysql':
                engine = create_engine(
                    f"mysql+pymysql://{db_config['user']}:{db_config['password']}@"
                    f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
                )
                
            # Test connection
            with engine.connect() as conn:
                pass
                
            self.connections[db_config['name']] = engine
            return True
            
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def read_file(self, file_path: Path, file_type: str) -> pd.DataFrame:
        """Read CSV or Excel files"""
        try:
            if file_type == 'csv':
                return pd.read_csv(file_path)
            elif file_type == 'excel':
                return pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logging.error(f"File reading failed: {e}")
            raise
    
    def fetch_api_data(self, api_config: Dict[str, Any]) -> pd.DataFrame:
        """Fetch data from REST API"""
        import requests
        
        try:
            response = requests.get(
                api_config['url'],
                headers=api_config.get('headers', {}),
                params=api_config.get('params', {})
            )
            response.raise_for_status()
            
            data = response.json()
            return pd.DataFrame(data)
            
        except Exception as e:
            logging.error(f"API data fetch failed: {e}")
            raise
    
    def infer_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """Auto-detect field types"""
        schema = {}
        
        for column in df.columns:
            dtype = str(df[column].dtype)
            
            if 'int' in dtype or 'float' in dtype:
                schema[column] = 'number'
            elif 'datetime' in dtype:
                schema[column] = 'date'
            else:
                # Sample data to check if it's actually numeric
                sample = df[column].dropna().head(10)
                if sample.astype(str).str.isnumeric().all():
                    schema[column] = 'number'
                else:
                    schema[column] = 'text'
                    
        return schema