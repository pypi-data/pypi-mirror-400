"""
JSON Storage - Simple file-based persistence
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime
from decimal import Decimal


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for banking types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "value"):  # Enum
            return obj.value
        return super().default(obj)


class JSONStorage:
    """
    Simple JSON file storage for banking data
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".nanopy-bank"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, collection: str) -> Path:
        """Get file path for a collection"""
        return self.data_dir / f"{collection}.json"

    def load(self, collection: str) -> List[Dict]:
        """Load all items from a collection"""
        file_path = self._get_file_path(collection)
        if not file_path.exists():
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, collection: str, data: List[Dict]):
        """Save all items to a collection"""
        file_path = self._get_file_path(collection)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, cls=JSONEncoder, default=str)

    def get(self, collection: str, key: str, key_field: str = "id") -> Optional[Dict]:
        """Get a single item by key"""
        items = self.load(collection)
        for item in items:
            if item.get(key_field) == key:
                return item
        return None

    def put(self, collection: str, item: Dict, key_field: str = "id"):
        """Add or update an item"""
        items = self.load(collection)
        key = item.get(key_field)

        # Update existing or append
        updated = False
        for i, existing in enumerate(items):
            if existing.get(key_field) == key:
                items[i] = item
                updated = True
                break

        if not updated:
            items.append(item)

        self.save(collection, items)

    def delete(self, collection: str, key: str, key_field: str = "id") -> bool:
        """Delete an item"""
        items = self.load(collection)
        original_len = len(items)
        items = [item for item in items if item.get(key_field) != key]

        if len(items) < original_len:
            self.save(collection, items)
            return True
        return False

    def clear(self, collection: str):
        """Clear all items from a collection"""
        self.save(collection, [])

    def count(self, collection: str) -> int:
        """Count items in a collection"""
        return len(self.load(collection))

    def query(self, collection: str, filters: Dict[str, Any]) -> List[Dict]:
        """Query items with filters"""
        items = self.load(collection)
        results = []

        for item in items:
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)

        return results


# Singleton
_storage_instance: Optional[JSONStorage] = None


def get_json_storage(data_dir: Optional[str] = None) -> JSONStorage:
    """Get or create JSON storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = JSONStorage(data_dir)
    return _storage_instance
