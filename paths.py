import os
import shutil
import sqlite3
import sys


APP_DIR = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", APP_DIR)
    return os.path.join(base_path, relative_path)


def app_path(*parts):
    return os.path.join(APP_DIR, *parts)


def _has_required_developer_tables(db_path):
    if not os.path.exists(db_path):
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
    except sqlite3.DatabaseError:
        return False

    return {"user_pw", "tournament_fin"}.issubset(tables)


def ensure_app_data():
    os.makedirs(app_path("user_db"), exist_ok=True)

    developer_db = app_path("developer.db")
    bundled_developer_db = resource_path("developer.db")
    if (
        not _has_required_developer_tables(developer_db)
        and os.path.exists(bundled_developer_db)
        and os.path.abspath(bundled_developer_db) != os.path.abspath(developer_db)
    ):
        shutil.copy2(bundled_developer_db, developer_db)

    return developer_db
