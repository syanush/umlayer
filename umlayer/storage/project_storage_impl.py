"""Project storage implementation"""

import os
import jsonpickle
import sqlalchemy.engine.cursor

from sqlalchemy import create_engine, text

from .. import model


class ProjectStorageImpl(model.ProjectStorage):
    def save(self, elements: list[model.Element], filepath: str = None):
        if os.path.exists(filepath):
            os.remove(filepath)

        dirname = os.path.dirname(filepath)
        os.makedirs(dirname, exist_ok=True)

        engine = create_engine("sqlite+pysqlite:///" + filepath, echo=True, future=True)

        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE elements (id text PRIMARY KEY, json_data text)"))

            for element in elements:
                json_data = jsonpickle.encode(element)

                sql = f"INSERT INTO elements (id, json_data) VALUES ('{str(element.id)}', '{json_data}')"
                conn.execute(text(sql))

    def load(self, filepath: str = None) -> list[model.Element]:
        engine = create_engine("sqlite+pysqlite:///" + filepath, echo=True, future=True)

        with engine.begin() as conn:
            sql = f"SELECT * FROM elements"
            result: sqlalchemy.engine.cursor.CursorResult = conn.execute(text(sql))
            # for id, frozen in result:
            #     element = jsonpickle.decode(frozen)
            #     print(id, element)
            elements = [jsonpickle.decode(frozen) for _, frozen in result]
            return elements
