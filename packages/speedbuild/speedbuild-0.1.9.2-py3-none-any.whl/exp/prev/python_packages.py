import json
import sqlite3
from typing import Any, Dict, Optional
from main import get_connection, init_db


def create_python_package(
    name: str,
    paths: str
) -> int:
    try:
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO python_package (name, paths)
                VALUES (?, ?)
                """,
                (name, json.dumps(paths))
            )
            return cur.lastrowid
        
    except sqlite3.IntegrityError as error:
        print(f"Error : {error}")
        return None
    

def get_python_package(name: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM python_package WHERE name = ?",
            (name,)
        )
        row = cur.fetchone()

        if not row:
            return None

        return {
            **dict(row),
            "paths": json.loads(row["paths"])
        }
    

def delete_python_package(name: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM python_package WHERE name = ?",
            (name,)
        )


if __name__ == "__main__":
    init_db()
    # data = create_python_package("sympy==1.14.0",{"pkg": ["mpmath", "sympy", "__pycache__", "pip"], "version": "1.14.0"})
    data = get_python_package("sympy==1.14.0")