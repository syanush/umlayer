"""Project storage implementation"""

import jsonpickle

from sqlalchemy import create_engine, text

from umlayer.model.element import Element
from umlayer.model.project_storage import ProjectStorage


class ProjectStorageImpl(ProjectStorage):
    def save(self, elements: list[Element], filename: str = None):
        engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE elements (id text PRIMARY KEY, json_data text)"))

            for element in elements:
                json_data = jsonpickle.encode(element)
                sql = f"INSERT INTO elements (id, json_data) VALUES ('{str(element.id)}', '{json_data}')"
                conn.execute(text(sql))

    def load(self, filename: str = None) -> list[Element]:
        engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)

        with engine.begin() as conn:
            sql = f"SELECT * FROM elements"
            result = conn.execute(text(sql))
            # restore elements here
            # jsonpickle.decode(frozen)
            elements = None
            return elements
