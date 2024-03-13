
import logging
import os
from Utilities import JsonReader
from datetime import datetime
from Initialiser import SensorDataLogger
import socket
import fcntl
import struct

jsonreader = JsonReader()
logger = logging.getLogger()
sensor_data_logger = SensorDataLogger()

round_off_digits = 3


    
class PiSensor:
    def __init__(self):
        return None

    def read_cpu_temp(self):
        res = os.popen("vcgencmd measure_temp").readline()
        t = float(res.replace("temp=","").replace("'C\n",""))
        return(t)
    
    def read_free_space(self):
        statvfs = os.statvfs('/')
        free_space = round((statvfs.f_bavail * statvfs.f_frsize)/(1024*1024*1024),3)
        
        return free_space
    
    def read_total_space(self):
        statvfs = os.statvfs('/')
        total_space = round((statvfs.f_blocks * statvfs.f_frsize)/(1024*1024*1024),3)

        return total_space
    
        # Get the IP address of the Raspberry Pi
    def get_ip_address(self,interface):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                sock.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(interface[:15], 'utf-8'))
            )[20:24])
            return ip_address
        except Exception as e:
            print(f"Error getting IP address for {interface}: {str(e)}")
            return None




    
class Sensors(PiSensor):
    next_record_time = 0
    record_interval = None
    latest_readings = None
    sensors_initialised = False

    
    def __init__(self):
        PiSensor.__init__(self)

        self.record_interval = jsonreader.read_json_parameter('data_log_interval')
        self.latest_readings, self.sensors_initialised = self.initiate_sensors()
    

        return None

    
    
    def time_to_record(self, _current_time):
        self.moved = False
        if (_current_time >= self.next_record_time):
            self.next_record_time = _current_time + self.record_interval
            return True
        else:
            return False
        
    def assess_record_time(self, _current_time, _camera_warmup_status, _calibration_status):

        if (_camera_warmup_status is True or self.time_to_record(_current_time) is True) and _calibration_status is True:
            return True
        else:
            return False
        


    def get_rpi_sensor_data(self):
        _cpu_temp = self.read_cpu_temp()
        _free_space = self.read_free_space()
        _total_space = self.read_total_space() 

        _system_data = {"cpu_temp": _cpu_temp, 
                            "free_space": _free_space, 
                            "total_space": _total_space}
        
        if self.sensors_initialised is True:
            self.latest_readings.update(_system_data)

        return _system_data

    def initiate_sensors(self):

        _rpi_sensor_data = self.get_rpi_sensor_data()

        # Combine the dictionary data
        _sensor_data = {**_rpi_sensor_data}

        return _sensor_data, True
    
    def read_sensors(self):

        _rpi_sensor_data = self.get_rpi_sensor_data()

        # Combine the dictionary data
        _sensor_data = {**_rpi_sensor_data}

        return _sensor_data

    

        






