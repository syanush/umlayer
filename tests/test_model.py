import unittest
import json
import jsonpickle

from marshmallow import Schema, fields
from pprint import pprint

from umlayer import model, storage


class TestFolder(unittest.TestCase):
    def test_serialize_folder(self):
        folder = model.Folder()
        folder.name = 'Folder 1'
        FolderSchema = Schema.from_dict({'name': fields.Str()})
        schema = FolderSchema()
        dto = schema.dump(folder)
        # print(json.dumps(dto))
        # print(jsonpickle.encode(dto))
        # print(jsonpickle.encode(folder))


class TestDiagram(unittest.TestCase):
    def test_diagram_id(self):
        d1 = model.Diagram()
        d2 = model.Diagram()
        self.assertNotEqual(d1.id, d2.id)

    def test_parent_id(self):
        n1 = model.Folder("Root")
        n2 = model.Diagram(parent_id=n1.id)
        self.assertEqual(n1.id, n2.parent_id)

    def test_project(self):
        p = model.Project()
        e1 = model.Folder("Root")
        p.setRoot(e1)

        e2 = model.Diagram("My diagram")
        p.add(e2, e1.id)
        e22 = p.get(e2.id)
        self.assertEqual(e2, e22)

    def test_repository(self):
        store = storage.ProjectStorageImpl()
