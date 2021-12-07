"""Project storage implementation"""

import os
import jsonpickle
import sqlalchemy.engine.cursor

from sqlalchemy import create_engine, text

from umlayer import model, usecases


class ProjectStorageImpl(usecases.ProjectStorage):
    def save(self, project_items: list[model.BaseItem], filepath: str = None):
        if os.path.exists(filepath):
            os.remove(filepath)

        dirname = os.path.dirname(filepath)
        os.makedirs(dirname, exist_ok=True)

        engine = create_engine("sqlite+pysqlite:///" + filepath, echo=True, future=True)

        with engine.begin() as conn:
            conn.execute(
                text("CREATE TABLE elements (id text PRIMARY KEY, json_data text)")
            )

            for project_item in project_items:
                json_data = jsonpickle.encode(project_item)

                sql = f"INSERT INTO elements (id, json_data) VALUES ('{str(project_item.id)}', '{json_data}')"
                conn.execute(text(sql))

    def load(self, filepath: str = None) -> list[model.BaseItem]:
        engine = create_engine("sqlite+pysqlite:///" + filepath, echo=True, future=True)

        with engine.begin() as conn:
            sql = "SELECT * FROM elements"
            result: sqlalchemy.engine.cursor.CursorResult = conn.execute(text(sql))
            project_items = [jsonpickle.decode(json_data) for _, json_data in result]
            return project_items
