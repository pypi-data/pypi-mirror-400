import sqlite3
import json
import logging
import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List

logger = logging.getLogger(__name__)

class BlackboardMemory:
    """
    A SQLite-backed shared memory (Blackboard) for agents.
    Allows persistent key-value storage with scoping.
    """

    def __init__(self, db_path: str = ".adk/blackboard.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blackboard (
                    scope TEXT,
                    namespace TEXT,
                    key TEXT,
                    value TEXT,
                    updated_at DATETIME,
                    PRIMARY KEY (scope, namespace, key)
                )
            """)
            conn.commit()

    def set(self, key: str, value: Any, scope: str = "global", namespace: str = "shared"):
        """Sets a value in the blackboard."""
        val_str = json.dumps(value)
        now = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO blackboard (scope, namespace, key, value, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (scope, namespace, key, val_str, now))
            conn.commit()

    def get(self, key: str, scope: str = "global", namespace: str = "shared") -> Any:
        """Gets a value from the blackboard."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT value FROM blackboard WHERE scope = ? AND namespace = ? AND key = ?
            """, (scope, namespace, key)).fetchone()
            if row:
                return json.loads(row[0])
            return None

    def delete(self, key: str, scope: str = "global", namespace: str = "shared"):
        """Deletes a key from the blackboard."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM blackboard WHERE scope = ? AND namespace = ? AND key = ?
            """, (scope, namespace, key))
            conn.commit()

    def list_keys(self, scope: Optional[str] = None, namespace: Optional[str] = None) -> List[Dict[str, str]]:
        """Lists keys in the blackboard, optionally filtered by scope/namespace."""
        query = "SELECT scope, namespace, key, updated_at FROM blackboard"
        params = []
        if scope and namespace:
            query += " WHERE scope = ? AND namespace = ?"
            params = [scope, namespace]
        elif scope:
            query += " WHERE scope = ?"
            params = [scope]
        elif namespace:
            query += " WHERE namespace = ?"
            params = [namespace]

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                {"scope": r[0], "namespace": r[1], "key": r[2], "updated_at": r[3]}
                for r in rows
            ]

    def get_all(self, scope: str = "global", namespace: str = "shared") -> Dict[str, Any]:
        """Gets all key-value pairs for a specific scope and namespace."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT key, value FROM blackboard WHERE scope = ? AND namespace = ?
            """, (scope, namespace)).fetchall()
            return {r[0]: json.loads(r[1]) for r in rows}

if __name__ == "__main__":
    # Quick test
    bb = BlackboardMemory("test_blackboard.db")
    bb.set("status", "scanning", scope="sprint-025")
    print(f"Status: {bb.get('status', scope='sprint-025')}")
    print(f"All keys: {bb.list_keys()}")
    bb.delete("status", scope="sprint-025")
    import os
    if os.path.exists("test_blackboard.db"):
        os.remove("test_blackboard.db")
