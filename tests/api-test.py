from pynet import Pynet
import os, code, time, unittest

CONN = 'http://localhost'

class PynetTest(unittest.TestCase):

    def setUp(self):
        self.p = Pynet()
        self.p.set_connection(CONN)

    def tearDown(self): 
        self.p.clear_database()

    def test_connection(self):
        self.p.test_connection()

    def test_create_device(self):
        self.p.create_device(1)
        self.p.create_device(2)
        self.p.create_device(3)

    def test_list_devices(self):
        self.assertListEqual(
            self.p.list_devices(), 
            []
        )
        self.p.create_device(1)
        self.p.create_device(2)
        self.p.create_device(3)
        self.assertListEqual(
            self.p.list_devices(), 
            [1,2,3]
        )

    def test_clear_database(self):
        self.p.create_device(1)
        self.p.create_device(2)
        self.p.create_device(3)
        self.p.clear_database()
        self.assertListEqual(
            self.p.list_devices(), 
            []
        )

    def test_get_frequency(self):
        self.p.create_device(1)
        self.assertEqual(self.p.get_frequency(1), 60)

    def test_get_config(self):
        self.p.create_device(1)
        self.assertEqual(self.p.get_config(1), "")

    def test_set_frequency(self):
        self.p.create_device(1)
        self.p.set_frequency(1, 10)
        self.assertEqual(self.p.get_frequency(1), 10)
        self.p.set_frequency(1, 30)
        self.assertEqual(self.p.get_frequency(1), 30)

    def test_set_config(self):
        self.p.create_device(1)
        self.p.set_config(1, "test-123")
        self.assertEqual(self.p.get_config(1), "test-123")
        self.p.set_config(1, "test-456")
        self.assertEqual(self.p.get_config(1), "test-456")

    def test_set_data(self):
        self.p.create_device(1)
        self.p.set_data(1,0,1,2,3)

    def test_get_data(self):
        self.p.create_device(1)
        self.p.set_data(1,0,1,2,3)
        data1 = self.p.get_data(1)
        for datum in data1: datum.pop(1)
        self.assertListEqual(
            data1, 
            [[1, 0.0, 1.0, 2.0, 3.0]]
        )
        self.p.set_data(1,4.1,5.2,6.3,7.4)
        data2 = self.p.get_data(1)
        for datum in data2: datum.pop(1)
        self.assertListEqual(
            data2, 
            [[1, 0.0, 1.0, 2.0, 3.0],[1, 4.1, 5.2, 6.3, 7.4]]
        )

    def test_get_status(self):
        self.p.create_device(1)
        self.p.set_data(1,0,1,2,3)
        status = self.p.get_status(1)
        status.pop(0)
        self.assertListEqual(
            status, 
            [0.0, 1.0, 2.0, 3.0]
        )
        self.p.set_data(1,4.1,5.2,6.3,7.4)
        status = self.p.get_status(1)
        status.pop(0)
        self.assertListEqual(
            status, 
            [4.1, 5.2, 6.3, 7.4]
        )

    def test_integration(self):
        self.p.create_device(1)
        self.p.create_device(1)
        self.p.create_device(1, 10, "test")
        self.assertListEqual(
            self.p.list_devices(), 
            [1]
        )
        self.assertEqual(self.p.get_frequency(1), 10)
        self.assertEqual(self.p.get_config(1), "test")
        self.p.set_data(1,0,1,2,3)
        self.p.create_device(1, 100, "different")
        status = self.p.get_status(1)
        status.pop(0)
        self.assertListEqual(
            status, 
            [0.0, 1.0, 2.0, 3.0]
        )
        self.assertEqual(self.p.get_frequency(1), 100)
        self.assertEqual(self.p.get_config(1), "different")
if __name__ == "__main__":
    unittest.main()
