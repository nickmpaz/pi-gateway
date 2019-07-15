import requests
import os, subprocess

class Pynet:

    TIMEOUT = 3

    def set_connection(self, hostname):
        self.hostname = str(hostname)

    def test_connection(self):
        r = requests.get(self.hostname, timeout=self.TIMEOUT)
        r.raise_for_status()
        return True if r.text == "[Pynet] - Connection Successful" else False

    def clear_database(self):
        r = requests.post(self.hostname + "/devices", timeout=self.TIMEOUT)
        r.raise_for_status()

    def list_devices(self):
        r = requests.get(self.hostname + "/devices", timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()['response']

    def create_device(self, device_id, frequency=60, config=""): 
        device_id = str(device_id)
        frequency = str(frequency)
        config = str(config)
        payload = {'frequency':frequency, 'config':config}
        r = requests.post(self.hostname + "/devices/" + device_id, params=payload, timeout=self.TIMEOUT)
        r.raise_for_status()

    def get_frequency(self, device_id): 
        device_id = str(device_id)
        r = requests.get(self.hostname + "/devices/" + device_id, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()['response'][1]

    def get_config(self, device_id): 
        device_id = str(device_id)
        r = requests.get(self.hostname + "/devices/" + device_id, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()['response'][2]
    
    def get_data(self, device_id): 
        device_id = str(device_id)
        r = requests.get(self.hostname + "/devices/" + device_id + "/data", timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()['response']
        
    def get_status(self, device_id): 
        device_id = str(device_id)
        r = requests.get(self.hostname + "/devices/" + device_id, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()['response'][3:]

    def set_frequency(self, device_id, frequency): 
        device_id = str(device_id)
        frequency = str(frequency)
        payload = {'frequency':frequency}
        r = requests.post(self.hostname + "/devices/" + device_id, params=payload, timeout=self.TIMEOUT)
        r.raise_for_status()

    def set_config(self, device_id, config):
        device_id = str(device_id)
        config = str(config)
        payload = {'config':config}
        r = requests.post(self.hostname + "/devices/" + device_id, params=payload, timeout=self.TIMEOUT)
        r.raise_for_status()

    def set_data(self, device_id, ch0=None, ch1=None, ch2=None, ch3=None): 
        device_id = str(device_id)
        payload = {'ch0':ch0,'ch1':ch1,'ch2':ch2,'ch3':ch3}
        r = requests.post(self.hostname + "/devices/" + device_id + "/data", params=payload, timeout=self.TIMEOUT)
        r.raise_for_status()