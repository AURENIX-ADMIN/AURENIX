import logging
import os
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from temporalio import activity

# Universal Database Connector
# Supports any database flavor supported by SQLAlchemy (Postgres, MySQL, SQLite, etc.)

@activity.defn
async def execute_query(connection_uri: str, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Executes a SELECT query on a third-party database.
    """
    activity.logger.info(f"Executing SQL query on: {connection_uri.split('@')[-1]}") # Log host only for security
    
    try:
        engine = create_engine(connection_uri)
        with engine.connect() as connection:
            result = connection.execute(text(query), params or {})
            # Convert rows to dictionaries for JSON serialization
            return [dict(row._mapping) for row in result]
    except Exception as e:
        activity.logger.error(f"Database Error: {e}")
        return [{"error": str(e)}]

@activity.defn
async def get_table_schema(connection_uri: str, table_name: str) -> Dict[str, Any]:
    """
    Retrieves the schema of a specific table for AI context.
    """
    activity.logger.info(f"Fetching schema for table: {table_name}")
    
    try:
        engine = create_engine(connection_uri)
        # Simplified schema retrieval using dialect-specific or generic SQL
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = :table"
        with engine.connect() as connection:
            result = connection.execute(text(query), {"table": table_name})
            columns = [dict(row._mapping) for row in result]
            return {"table": table_name, "columns": columns}
    except Exception as e:
        activity.logger.error(f"Schema Error: {e}")
        return {"error": str(e)}
