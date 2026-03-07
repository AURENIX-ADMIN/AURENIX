import sys
import os
import asyncio

# Add the project root and core directory to PYTHONPATH
project_root = r"c:\Users\Usuario\Desktop\AURENIX\AURENIX AGENCY\proyecto\MIGRACION-COMPLETA"
sys.path.append(project_root)

# Import the test
# We need to use absolute import as aurenix_core
from aurenix_core.tests.test_postgres_storage import test_postgres_lifecycle

if __name__ == "__main__":
    print("🚀 Starting Postgres Integration Test...")
    try:
        asyncio.run(test_postgres_lifecycle())
        print("✅ Postgres Integration Test PASSED")
    except Exception as e:
        print(f"❌ Postgres Integration Test FAILED: {e}")
        sys.exit(1)
