import os
import logging
import json
import subprocess
from typing import Dict, Any

# Config
# We now use docker exec, so DSN is internal to the container ref
INTERNAL_DB_DSN = "postgresql://aurenix:aurenix_password@localhost:5432/aurenix_db"

class ResearchDatabase:
    @staticmethod
    async def save_item(item: Dict[str, Any]):
        """
        Saves a filtered research item to the database using docker exec for stability.
        """
        logging.info(f"Saving research item: {item.get('title')}")
        
        # Prepare SQL params
        title = item.get('title', '').replace("'", "''")
        link = item.get('link', '').replace("'", "''")
        summary = item.get('summary', '').replace("'", "''")
        source = item.get('source', '')
        score = item.get('score', 0)
        metadata = json.dumps(item.get('metadata', {}))
        
        sql = f"""
        INSERT INTO research_items (title, link, summary, source, score, metadata)
        VALUES ('{title}', '{link}', '{summary}', '{source}', {score}, '{metadata}')
        """
        
        # Clean up newlines for CLI
        sql = sql.replace('\n', ' ').strip()
        
        try:
            # We use subprocess.run to execute psql inside the container
            # psql -c "SQL"
            command = [
                "docker", "exec", "-i", "aurenix-postgres", 
                "psql", "-U", "aurenix", "-d", "aurenix_db", 
                "-c", sql
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("Item saved successfully via Docker Exec.")
            else:
                logging.error(f"Docker Exec Failed: {result.stderr}")
                
        except Exception as e:
            logging.error(f"Failed to save item: {e}")
