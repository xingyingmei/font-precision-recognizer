"""
Database initialization and management
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    """Font database manager"""
    
    def __init__(self, db_path: str = './data/font_database.json'):
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if not os.path.exists(self.db_path):
            initial_db = {
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'fonts': []
            }
            self.save(initial_db)
            logger.info(f"Database initialized at {self.db_path}")
    
    def load(self) -> Dict[str, Any]:
        """Load database from file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading database: {str(e)}")
            return {'fonts': []}
    
    def save(self, data: Dict[str, Any]) -> bool:
        """Save database to file"""
        try:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Database saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving database: {str(e)}")
            return False
    
    def add_fonts(self, fonts: List[Dict[str, Any]]) -> bool:
        """Add fonts to database"""
        try:
            db = self.load()
            existing_names = {f['name'].lower() for f in db.get('fonts', [])}
            
            new_fonts = [f for f in fonts if f['name'].lower() not in existing_names]
            db['fonts'].extend(new_fonts)
            
            return self.save(db)
        except Exception as e:
            logger.error(f"Error adding fonts: {str(e)}")
            return False
    
    def get_all_fonts(self) -> List[Dict[str, Any]]:
        """Get all fonts from database"""
        db = self.load()
        return db.get('fonts', [])
    
    def search_font(self, query: str) -> List[Dict[str, Any]]:
        """Search for fonts by name"""
        db = self.load()
        query_lower = query.lower()
        return [f for f in db.get('fonts', []) if query_lower in f.get('name', '').lower()]
    
    def clear(self) -> bool:
        """Clear all fonts from database"""
        try:
            initial_db = {
                'version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'fonts': []
            }
            return self.save(initial_db)
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return False


# Initialize default database instance
db = Database()


if __name__ == '__main__':
    # Test database initialization
    print("Testing database initialization...")
    db = Database()
    fonts = db.get_all_fonts()
    print(f"Database contains {len(fonts)} fonts")
    print("✓ Database is ready")
