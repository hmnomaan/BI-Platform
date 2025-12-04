# bi_dashboard/core/data_connector.py
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from pathlib import Path
from typing import Dict, Any, Union, Optional
import logging
import yaml
import os

class DataSourceManager:
    def __init__(self, config_path: Optional[Path] = None):
        self.connections = {}
        self._cache = {}
        self.config_path = config_path or Path(__file__).parent.parent.parent / "configs" / "datasource_config.yaml"
        self.datasource_config: Dict[str, Any] = {}
        self._load_datasource_config()
    
    def _load_datasource_config(self):
        """Load datasource configuration from YAML file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.datasource_config = yaml.safe_load(f) or {}
                    logging.info(f"Loaded datasource config from {self.config_path}")
            except Exception as e:
                logging.warning(f"Failed to load datasource config: {e}")
                self.datasource_config = {}
        else:
            logging.warning(f"Datasource config file not found at {self.config_path}")
    
    def get_datasource_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific data source."""
        return self.datasource_config.get("data_sources", {}).get(source_name)
    
    def get_field_mappings(self, source_name: str) -> Dict[str, Any]:
        """Get field mappings for a data source."""
        ds_config = self.get_datasource_config(source_name)
        if ds_config:
            return ds_config.get("field_mappings", {})
        return {}
    
    def list_available_sources(self) -> list:
        """List all available data source names from config."""
        return list(self.datasource_config.get("data_sources", {}).keys())
    
    def load_from_datasource_config(self, source_name: str) -> pd.DataFrame:
        """Load a data source directly from datasource_config.yaml by name."""
        return self.load_from_config(self.datasource_config, source_name)
        
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

    def load_from_config(self, config: Dict[str, Any], source_name: str) -> pd.DataFrame:
        """Load a data source specified in a configuration dictionary.

        Config structure example:
        data_sources:
          sales_csv:
            type: file
            file_type: csv
            path: data/sales_data.csv

          db_primary:
            type: database
            name: primary
            query: SELECT * FROM sales LIMIT 10000

          api_feed:
            type: api
            url: https://api.example.com/data
            params:
              limit: 1000

        The method returns a pandas DataFrame and caches by source_name.
        """
        ds = (config or {}).get("data_sources", {}).get(source_name)
        if ds is None:
            raise KeyError(f"Data source '{source_name}' not found in config")

        # Simple in-memory cache check
        cache_key = f"ds::{source_name}"
        if ds.get("cache", False):
            entry = self._cache.get(cache_key)
            if entry:
                return entry

        dtype = ds.get("type")
        if dtype == "file":
            path = Path(ds.get("path"))
            file_type = ds.get("file_type", "csv")
            df = self.read_file(path, file_type)
        elif dtype == "database":
            # ensure connection exists
            db_name = ds.get("name") or ds.get("connection")
            db_cfg = ds.get("connection_config")
            if db_cfg:
                # connect if not already
                self.connect_database(db_cfg)
                engine = self.connections.get(db_cfg.get("name"))
            else:
                engine = self.connections.get(db_name)

            if engine is None:
                raise RuntimeError(f"Database connection for '{db_name}' not available")

            query = ds.get("query") or ds.get("table")
            if not query:
                raise ValueError("No query or table specified for database source")
            # If table is provided, convert to SELECT *
            if ds.get("table"):
                query = f"SELECT * FROM {ds.get('table')}"

            df = pd.read_sql(query, engine)
        elif dtype == "api":
            api_cfg = {
                "url": ds.get("url"),
                "headers": ds.get("headers", {}),
                "params": ds.get("params", {})
            }
            df = self.fetch_api_data(api_cfg)
        else:
            raise ValueError(f"Unsupported data source type: {dtype}")

        # post-load optimizations
        if ds.get("optimize", False):
            # simple downcast for numeric columns
            for col in df.select_dtypes(include=["int64"]).columns:
                df[col] = pd.to_numeric(df[col], downcast="integer")
            for col in df.select_dtypes(include=["float64"]).columns:
                df[col] = pd.to_numeric(df[col], downcast="float")

        if ds.get("cache", False):
            self._cache[cache_key] = df

        return df
    
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