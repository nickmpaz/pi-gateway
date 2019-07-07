from pynet import Pynet
import os, code, time, unittest

CONN = 'http://localhost/'

class PynetTest(unittest.TestCase):

    def setUp(self):
        self.p = Pynet()
        self.p.set_connection(CONN)

    def tearDown(self):
        self.p.purge()

    def test_connection(self):
        self.p.test_connection()

    def test_create_device(self):
        self.p.create_device(1,10)
        self.p.create_device(2,10)
        self.p.create_device(3,10)

    def test_list_devices(self):
        self.p.create_device(1,10)
        self.p.create_device(2,10)
        self.p.create_device(3,10)
        devices_answer = [1,2,3]
        devices = self.p.list_devices()
        self.assertListEqual(devices, devices_answer)

    def test_device_status(self):
        self.p.create_device(1,10)
        self.p.send_data(1,ch0=0,ch1=1,ch2=2,ch3=3)
        status_answer = [0.0, 1.0, 2.0, 3.0]
        status = self.p.device_status(1)
        status.pop(0)
        self.assertListEqual(status, status_answer)
        self.p.send_data(1,ch0=0,ch2=2)
        status_answer = [0.0, None, 2.0, None]
        status = self.p.device_status(1)
        status.pop(0)
        self.assertListEqual(status, status_answer)
        
    def test_send_data(self):
        self.p.create_device(1,10)
        self.p.send_data(1,ch0=0,ch1=1,ch2=2,ch3=3)
        self.p.send_data(1,ch0=0)

    def test_get_data(self):
        self.p.create_device(1,10)
        self.p.send_data(1,ch0=0,ch2=2)
        data = self.p.get_data(1)
        data[0].pop(1)
        self.assertListEqual(data, [[1,0.0,None,2.0,None]])        

    def test_get_config(self):
        self.p.create_device(1,10)
        config_answer = [1,10]
        config = self.p.get_config(1)
        self.assertListEqual(config, config_answer)

    def test_set_config(self):
        self.p.create_device(1,10)
        config_answer = [1,10]
        config = self.p.get_config(1)
        self.assertListEqual(config, config_answer)
        self.p.set_config(1,5)
        config_answer = [1,5]
        config = self.p.get_config(1)
        self.assertListEqual(config, config_answer)

    def test_device_status(self):
        self.p.create_device(1,10)

        self.p.send_data(1,ch0=0,ch2=2)
        data = self.p.get_status(1)
        data.pop(0)
        self.assertListEqual(data, [0.0,None,2.0,None])
        self.p.send_data(1,ch0=0,ch1=1,ch2=2,ch3=3)
        data = self.p.get_status(1)
        data.pop(0)
        self.assertListEqual(data, [0.0,1.0,2.0,3.0])

    def test_purge_device(self):
        self.p.create_device(1,10)
        self.p.create_device(2,10)
        self.p.create_device(3,10)
        self.assertListEqual(self.p.list_devices(), [1,2,3])
        self.p.purge(2)
        self.assertListEqual(self.p.list_devices(), [1,3])
        self.p.create_device(2,10)
        self.p.purge()
        self.assertListEqual(self.p.list_devices(), [])


if __name__ == "__main__":
    unittest.main()
