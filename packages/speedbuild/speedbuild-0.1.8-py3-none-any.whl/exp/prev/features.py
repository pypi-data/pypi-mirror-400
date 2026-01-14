import json
from main import get_connection, init_db
from typing import Any, Dict, List, Optional

# add speedbuild project id to features
# we need project db schema

def create_feature(
    *,
    name: str,
    code: str,
    feature_filename: str,
    doc: Optional[str] = None,
    code_import: List[str] = None,
    dependencies: List[str] = None,
    root_feature: bool = False,
    framework: str = "",
    vector_db_id: Optional[str] = None,
    project_id : str
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO feature (
                doc, code, name, code_import, dependencies,
                root_feature, feature_filename, framework,
                vector_db_id,project_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
            """,
            (
                doc,
                code,
                name,
                json.dumps(code_import or []),
                json.dumps(dependencies or []),
                int(root_feature),
                feature_filename,
                framework,
                vector_db_id,
                project_id
            )
        )
        return cur.lastrowid
    
def feature_exist(name: str, filename: str, code: str) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT 1
            FROM feature
            WHERE name = ?
              AND feature_filename = ?
              AND code = ?
            LIMIT 1
            """,
            (name, filename, code)
        )
        return cur.fetchone() is not None
    

def get_feature_by_name(name: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT 1 FROM feature WHERE name = ? LIMIT 1",
            (name,)
        )
        row = cur.fetchone()

        if not row:
            return None
        
        return {"name":name,"id":row['id']}

        return {
            **dict(row),
            "code_import": json.loads(row["code_import"]),
            "dependencies": json.loads(row["dependencies"]),
            "root_feature": bool(row["root_feature"]),
        }

def get_feature(feature_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT * FROM feature WHERE id = ?",
            (feature_id,)
        )
        row = cur.fetchone()

        if not row:
            return None

        return {
            **dict(row),
            "code_import": json.loads(row["code_import"]),
            "dependencies": json.loads(row["dependencies"]),
            "root_feature": bool(row["root_feature"]),
        }


def update_feature(
    feature_id: int,
    **updates
) -> None:
    if not updates:
        return

    allowed = {
        "doc", "code", "name", "code_import", "dependencies",
        "root_feature", "feature_filename", "framework",
        "vector_db_id"
    }

    fields = []
    values = []

    for key, value in updates.items():
        if key not in allowed:
            continue

        if key in {"code_import", "dependencies"}:
            value = json.dumps(value)
        elif key == "root_feature":
            value = int(value)

        fields.append(f"{key} = ?")
        values.append(value)

    if not fields:
        return

    values.append(feature_id)

    with get_connection() as conn:
        conn.execute(
            f"UPDATE feature SET {', '.join(fields)} WHERE id = ?",
            values
        )

def delete_feature(feature_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM feature WHERE id = ?",
            (feature_id,)
        )


if __name__ == "__main__":
    init_db()
    data = get_feature(2)
    print(data)