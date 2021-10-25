import unittest

from ..umlayer.model.diagram import Diagram
from ..umlayer.model.folder import Folder
from ..umlayer.model.node import Node
from ..umlayer.model.project import Project


class TestDiagram(unittest.TestCase):
    def test_diagram_id(self):
        d1 = Diagram()
        d2 = Diagram()
        self.assertNotEqual(d1.id, d2.id)

    def test_node(self):
        n1 = Node(Folder("Root"))
        n2 = Node(Diagram(), n1.element.id)
        self.assertEqual(n1.element.id, n2.parent_id)

    def test_project(self):
        p = Project()
        e1 = Folder("Root")
        p.setRoot(e1)

        e2 = Diagram("My diagram")
        p.add(e2, e1.id)
        e22 = p.get(e2.id)
        self.assertEqual(e2, e22)
