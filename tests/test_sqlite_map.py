"""
Contains the test DB data and the unittest for the example map format.
Dependency: apt install sqlite3 libsqlite3-mod-spatialite"""

import unittest

from openlr import Coordinates

from openlr_dereferencer.example_sqlite_map import (
    ExampleMapReader, Line, ExampleMapError, Node
)

from .example_mapformat import setup_testdb,setup_testdb_in_memory, remove_db_file

class SQLiteMapTest(unittest.TestCase):
    "A few unit tests for the example sqlite mapformat"

    def setUp(self):
        self.reader = ExampleMapReader(":memory:")
        self.reader.connection = setup_testdb_in_memory()

    def test_line_invalid_id_type(self):
        "Check if an invalid line id raises an error"
        with self.assertRaises(ExampleMapError):
            Line(self.reader, "Hello")

    def test_line_nonexistent_id(self):
        "Check if a nonexistent line ID leads to an exception"
        with self.assertRaises(TypeError):
            _ = Line(self.reader, 21).length
        with self.assertRaises(ExampleMapError):
            self.reader.get_line(21)

    def test_line_length(self):
        "Check the length of the line with ID 1"
        line = self.reader.get_line(1)
        self.assertAlmostEqual(line.length, 271, delta=1)

    def test_linepoints(self):
        "Test the point count of every line"
        pointcounts = {line.line_id: line.num_points() for line in self.reader.get_lines()}
        self.assertEqual(pointcounts.pop(18), 5)
        self.assertEqual(pointcounts.pop(19), 3)
        self.assertEqual(pointcounts.pop(20), 5)
        for pointcount in pointcounts.values():
            self.assertEqual(pointcount, 2)

    def test_nearest(self):
        "Test find_nodes_close_to with a manually chosen location"
        nodes = []
        nodes = [node.node_id for node \
            in self.reader.find_nodes_close_to(Coordinates(13.411, 52.525), 100)]
        self.assertSequenceEqual(nodes, [0, 14])

    def test_line_coords(self):
        "Test known line coordinates()"
        path = self.reader.get_line(1).coordinates()
        self.assertSequenceEqual(
            list(path), [Coordinates(13.41, 52.525), Coordinates(13.414, 52.525)]
        )

    def test_line_distance(self):
        "Test if a point on a line has zero distance from it"
        line = self.reader.get_line(1)
        point = Coordinates(13.41, 52.525)
        self.assertEqual(line.distance_to(point), 0.0)

    def test_line_enumeration(self):
        "Test if a sorted list of line IDs is as expected"
        lines = []
        lines = [line.line_id for line in self.reader.get_lines()]
        self.assertSequenceEqual(sorted(lines), range(1, 21))

    def test_get_line(self):
        "Get a test line"
        _line = self.reader.get_line(17)

    def test_node_invalid_id_type(self):
        "Check if an invalid node id raises an error"
        with self.assertRaises(ExampleMapError):
            Node(self.reader, "Hello")

    def test_node_nonexistent_id(self):
        "Check if a nonexistent node ID leads to an exception"
        with self.assertRaises(TypeError):
            _ = Node(self.reader, 15).coordinates

    def test_node_enumeration(self):
        "Test if a sorted list of point IDs is as expected"
        nodes = []
        nodes = [node.node_id for node in self.reader.get_nodes()]
        self.assertEqual(len(nodes), 15)
        self.assertSequenceEqual(range(15), sorted(nodes))

    def test_get_near_nodes(self):
        "Test if connected nodes are near to a connecting line"
        line = self.reader.get_line(17)
        # Get all node ids within 1 meter tolerance
        nodes = [node.node_id for node in line.near_nodes(1)]
        self.assertIn(line.start_node.node_id, nodes)
        self.assertIn(line.end_node.node_id, nodes)

    def test_incoming_lines(self):
        "Test if the right lines lead to a certain node"
        lines = [line.line_id for line in self.reader.get_node(4).incoming_lines()]
        self.assertSequenceEqual(lines, [4, 5])

    def test_connected_lines(self):
        "Test if the right lines connect to a certain node"
        lines = [line.line_id for line in self.reader.get_node(4).connected_lines()]
        self.assertSequenceEqual(lines, [4, 5, 6, 8])

    def test_nodecount(self):
        "Test node count"
        self.assertEqual(self.reader.get_nodecount(), 15)

    def test_linecount(self):
        "Test line count"
        self.assertEqual(self.reader.get_linecount(), 20)

    def tearDown(self):
        self.reader.connection.close()
