import unittest

from umlayer.model.diagram import Diagram
from umlayer.model.folder import Folder
from umlayer.model.project import Project
from umlayer.storage.project_storage_impl import ElementStorageImpl


class TestDiagram(unittest.TestCase):
    def test_diagram_id(self):
        d1 = Diagram()
        d2 = Diagram()
        self.assertNotEqual(d1.id, d2.id)

    def test_parent_id(self):
        n1 = Folder("Root")
        n2 = Diagram(parent_id=n1.id)
        self.assertEqual(n1.id, n2.parent_id)

    def test_project(self):
        p = Project()
        e1 = Folder("Root")
        p.setRoot(e1)

        e2 = Diagram("My diagram")
        p.add(e2, e1.id)
        e22 = p.get(e2.id)
        self.assertEqual(e2, e22)

    def test_repository(self):
        storage = ElementStorageImpl()
