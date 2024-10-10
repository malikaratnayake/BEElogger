import logging
import os
import socket
import fcntl
import struct
import board
import busio
import adafruit_hts221
import adafruit_tsl2591

# Initialize I2C bus and sensors
i2c = busio.I2C(board.SCL, board.SDA)
hts_sensor = adafruit_hts221.HTS221(i2c)
light_sensor = adafruit_tsl2591.TSL2591(i2c)
light_sensor.gain = adafruit_tsl2591.GAIN_LOW
light_sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_200MS

# Initialize the logger
logger = logging.getLogger()

class EnvironmentSensor:
    """
    Class to handle environment sensor readings.
    """
    
    def __init__(self):
        """
        Initialize the EnvironmentSensor.
        """
        return None
    
    def read_temperature(self):
        """
        Read the temperature from the HTS221 sensor.
        """
        temperature = round(hts_sensor.temperature, 2)
        return temperature
    
    def read_humidity(self):
        """
        Read the humidity from the HTS221 sensor.
        """
        humidity = round(hts_sensor.relative_humidity, 2)
        return humidity
    
    def read_light(self):
        """
        Read the light level from the TSL2591 sensor.
        """
        light = round(light_sensor.lux, 2)
        return light
    
    def read_env_sensor(self):
        """
        Read all environment sensor data (temperature, humidity, light).
        """
        _tempC = self.read_temperature()
        _humidity = self.read_humidity()
        _light = self.read_light()
        
        return _tempC, _humidity, _light

class PiSensor:
    """
    Class to handle Raspberry Pi sensor readings.
    """
    
    def __init__(self):
        """
        Initialize the PiSensor.
        """
        return None

    def read_cpu_temp(self):
        """
        Read the CPU temperature of the Raspberry Pi.
        """
        res = os.popen("vcgencmd measure_temp").readline()
        t = float(res.replace("temp=", "").replace("'C\n", ""))
        return t
    
    def read_free_space(self):
        """
        Read the available disk space on the Raspberry Pi.
        """
        statvfs = os.statvfs('/')
        free_space = round((statvfs.f_bavail * statvfs.f_frsize) / (1024 * 1024 * 1024), 3)
        return free_space
    
    def read_total_space(self):
        """
        Read the total disk space on the Raspberry Pi.
        """
        statvfs = os.statvfs('/')
        total_space = round((statvfs.f_blocks * statvfs.f_frsize) / (1024 * 1024 * 1024), 3)
        return total_space
    
    def get_ip_address(self, interface):
        """
        Get the IP address of the Raspberry Pi for the given network interface.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip_address = socket.inet_ntoa(fcntl.ioctl(
                sock.fileno(),
                0x8915,  # SIOCGIFADDR
                struct.pack('256s', bytes(interface[:15], 'utf-8'))
            )[20:24])
            return ip_address
        except Exception as e:
            logger.warning(f"Error getting IP address for {interface}: {str(e)}")
            return None

class Sensors(PiSensor, EnvironmentSensor):
    """
    Class to handle both Raspberry Pi and environment sensor readings.
    """
    next_record_time = 0
    latest_readings = None
    sensors_initialised = False

    def __init__(self, data_log_interval: int) -> None:
        """
        Initialize the Sensors class with the given data log interval.
        """
        self.data_log_interval = data_log_interval

        # Initialize parent classes
        PiSensor.__init__(self)
        EnvironmentSensor.__init__(self)

        # Initialize sensors and get initial readings
        self.latest_readings, self.sensors_initialised = self.initiate_sensors()
    
        return None

    def time_to_record(self, _current_time):
        """
        Check if it's time to record sensor data based on the current time.
        """
        self.moved = False
        if _current_time >= self.next_record_time:
            self.next_record_time = _current_time + self.data_log_interval
            return True
        else:
            return False
        
    def assess_record_time(self, _current_time, _camera_warmup_status, _calibration_status):
        """
        Assess if it's time to record sensor data based on various conditions.
        """
        if (_camera_warmup_status is True or self.time_to_record(_current_time) is True) and _calibration_status is True:
            return True
        else:
            return False

    def get_rpi_sensor_data(self):
        """
        Get sensor data from the Raspberry Pi.
        """
        _cpu_temp = self.read_cpu_temp()
        _free_space = self.read_free_space()
        _total_space = self.read_total_space() 

        _system_data = {"cpu_temp": _cpu_temp, 
                        "free_space": _free_space, 
                        "total_space": _total_space}
        
        if self.sensors_initialised is True:
            self.latest_readings.update(_system_data)

        return _system_data
    
    def get_environment_sensor_data(self):
        """
        Get sensor data from the environment sensors.
        """
        _tempC, _humidity, _light = self.read_env_sensor()

        _environment_sensor_data = {
            'temperature': _tempC,
            'humidity': _humidity,
            'light': _light,
        }
        if self.sensors_initialised is True:
            self.latest_readings.update(_environment_sensor_data)

        return _environment_sensor_data

    def initiate_sensors(self):
        """
        Initialize sensors and get initial readings.
        """
        _rpi_sensor_data = self.get_rpi_sensor_data()
        _environment_sensor_data = self.get_environment_sensor_data()

        # Combine the dictionary data
        _sensor_data = {**_rpi_sensor_data, **_environment_sensor_data}

        return _sensor_data, True
    
    def read_sensors(self):
        """
        Read sensor data from both Raspberry Pi and environment sensors.
        """
        _rpi_sensor_data = self.get_rpi_sensor_data()
        _environment_sensor_data = self.get_environment_sensor_data()

        # Combine the dictionary data
        _sensor_data = {**_rpi_sensor_data, **_environment_sensor_data}

        return _sensor_data