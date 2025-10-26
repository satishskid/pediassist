"""
Database initialization script
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pediassist.config import settings
from pediassist.database import init_database

async def main():
    """Initialize the database"""
    print("🚀 Initializing PediAssist database...")
    
    try:
        # Initialize database with sample data
        db_manager = await init_database(settings.database_url, populate_sample=True)
        
        print("✅ Database initialization completed successfully!")
        print(f"📊 Database URL: {settings.database_url}")
        print("📋 Sample data has been populated")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())