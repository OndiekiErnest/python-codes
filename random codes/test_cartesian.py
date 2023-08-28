
import unittest
from cartesian import Movements

class TestMove(unittest.TestCase):

    def setUp(self):
        self.m = Movements()

    def tearDown(self):
        pass

    def test_move_up(self):
        self.assertEqual(self.m.move_up(5), [0, 5])
        self.assertEqual(self.m.move_up(-5), [0, 0])
        self.assertEqual(self.m.distance, 0.0)

    def test_move_down(self):
        self.assertEqual(self.m.move_down(5), [0, -5])
        self.assertEqual(self.m.move_down(-5), [0, 0])

    def test_move_right(self):
        self.assertEqual(self.m.move_right(5), [5, 0])
        self.assertEqual(self.m.move_right(-5), [0, 0])

    def test_move_left(self):
        self.assertEqual(self.m.move_left(5), [-5, 0])
        self.assertEqual(self.m.distance, 5.0)
        self.assertEqual(self.m.move_left(-5), [0, 0])
        

if __name__ == "__main__":
    unittest.main()
