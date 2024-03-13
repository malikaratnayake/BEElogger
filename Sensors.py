from PiicoDev_BME280 import PiicoDev_BME280
from PiicoDev_QMC6310 import PiicoDev_QMC6310
# from PiicoDev_LIS3DH import PiicoDev_LIS3DH
# from PiicoDev_RFID import PiicoDev_RFID
import logging
import os
import time
from Utilities import JsonReader
from datetime import datetime
from Initialiser import SensorDataLogger
import socket
import fcntl
import struct
from Displays import LEDs

jsonreader = JsonReader()
logger = logging.getLogger()
sensor_data_logger = SensorDataLogger()
# accelerometer = PiicoDev_LIS3DH()
compass = PiicoDev_QMC6310()
environment_sensor = PiicoDev_BME280()
led_display = LEDs()
# rfid_reader= PiicoDev_RFID(asw=[1,0])

round_off_digits = 3


class EnvironmentSensor:
    
    def __init__(self):
        return None

    def read_env_sensor(self):
        try:
            tempC, presPa, humRH = environment_sensor.values()
        except:
            tempC, presPa, humRH = 0,0,0
            
        tempC, presPa, humRH = environment_sensor.values()
        pres_hPa = presPa / 100

        return round(tempC,round_off_digits), round(pres_hPa,round_off_digits), round(humRH,round_off_digits)
    
    def read_altitude(self):
        try:
            altitude = environment_sensor.altitude()
            return altitude
        except:
            return None
    
    def read_temperature(self):
        _tempC, _, _ = self.read_env_sensor()
        return _tempC
    
    def read_pressure(self):
        _, _pres_hPa, _ = self.read_env_sensor()
        return _pres_hPa
    
    def read_humidity(self):
        _, _, _humRH = self.read_env_sensor()
        return _humRH

    


class Accelerometer:
    base_x, base_y, base_z = 0,0,0
    mov_threshold = 0.4
    previous_data = [0,0,0]
    calibrating = False
    start_time =0
    calibration_time = 3
    shaking = False
    initial_calibration = False
    motion_status = True

    def __init__(self): 
        self.calibration_time = jsonreader.read_json_parameter('calibration_time')
        self.mov_threshold = jsonreader.read_json_parameter('movement_threshold')
        # self.set_motion_status(True)
    
    def read_acceleration(self):
        try:
            x, y, z = accelerometer.acceleration
            x = round(x,round_off_digits) # round data for a nicer-looking print()
            y = round(y,round_off_digits)
            z = round(z,round_off_digits)
        except:
            x, y, z = self.previous_data[0], self.previous_data[1], self.previous_data[2]

        return x, y, z
    
    def read_tilt(self):
        try:
            x_tilt, y_tilt, z_tilt = accelerometer.angle

            return round(x_tilt,round_off_digits), round(y_tilt,round_off_digits), round(z_tilt,round_off_digits)

        except:
            return 0,0,0
    
    
    def detect_shake(self, _movement_data):
        x_acc, y_acc, z_acc = abs(_movement_data[0]),abs(_movement_data[1]),abs(_movement_data[2])
        dx = round(abs(x_acc - self.base_x),2)
        dy = round(abs(y_acc - self.base_y),2)
        dz = round(abs(z_acc- self.base_z),2)

        max_movement = max(dx,dy,dz)
        if max_movement > self.mov_threshold:
            return True
        else:            
            return False
        
    def start_calibration(self):
        _calibrating = True
        start_time = time.monotonic() 

        return _calibrating, start_time
        
    def calibrate_accelerometer(self, _movement_data, _previous_data, _start_time):
        [x_acc, y_acc, z_acc] = _movement_data
        [px_acc, py_acc, pz_acc] = _previous_data
        
        dx = round(abs(x_acc - px_acc),2)
        dy = round(abs(y_acc - py_acc),2)
        dz = round(abs(z_acc - pz_acc),2)

        time_elapsed = time.monotonic() - _start_time
        max_movement_allowed = 6*self.mov_threshold
        max_movement = max(dx,dy,dz)
        # print(f"Time Elapsed: {time_elapsed}, Max Movement: {max_movement}", self.calibration_time)

        if max_movement <= max_movement_allowed:
            if time_elapsed >= self.calibration_time:
                self.base_x, self.base_y, self.base_z = x_acc, y_acc, z_acc
                self.initial_calibration = True
                logger.info("Accelerometer calibration complete")
                led_display.movement_indication_led(False)
                return False
            else:
                return True
        else:
            return False
        
    def manage_motion(self, _all_movement_data):
        x_acc = abs(_all_movement_data["x_acc"])
        y_acc = abs(_all_movement_data["y_acc"])
        z_acc = abs(_all_movement_data["z_acc"])
        
        _movement_data = [x_acc, y_acc, z_acc]
        self.shaking = self.detect_shake(_movement_data)
        if self.shaking  == True:
            led_display.movement_indication_led(True)
            if self.calibrating is False:
                self.calibrating, self.start_time = self.start_calibration()
                # logger.warning("Shaking detected. Calibrating accelerometer")
                self.previous_data = _movement_data
            else:
                self.calibrating = self.calibrate_accelerometer(_movement_data, self.previous_data, self.start_time)
                self.previous_data = _movement_data
        else:
            led_display.movement_indication_led(False)
            self.calibrating = False
            self.previous_data = _movement_data

        return None
    
    def get_init_calibration_status(self):
        return self.initial_calibration
    
    def reset_sensors(self):
        # self.motion_status = True
        self.initial_calibration = False
        self.base_x, self.base_y, self.base_z = 0,0,0
        self.calibrating = False
        self.shaking = False
        logger.info("Sensor reset")
        return None
    
    def get_motion_status(self):
        return self.motion_status
    
    def set_motion_status(self, _status):
        self.motion_status = _status
        led_display.motor_motion_status_led(_status)
        logger.info(f"Motion status set to: {_status}")
        return None


class Compass:

    def __init__(self):
        # self.compass.setDeclination(12.3) # Found with: https://www.magnetic-declination.com/Australia/Newcastle/122944.html

        return None
    
    def read_compass(self):
        heading = compass.readHeading()   # get the heading from the sensor
        if compass.dataValid():           # Rejects invalid data
            heading = round(heading)      # round to the nearest degree
            # print(heading)
        else:
            heading = None

        time.sleep(0.1)
        
        return heading
    
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

class RFIDReader:
    raw_station_tag = None

    def __init__(self):
        self.raw_station_tag = None
        self.last_detected_time = self.update_last_tag_detected_time()
        self.min_travel_time = jsonreader.read_json_parameter('min_travel_time')

        return None
    
    def update_last_tag_detected_time(self):
        self.last_detected_time = time.monotonic()
        return self.last_detected_time

    # def read_rfid_tag(self):
    #     # try:
    #     station_tag = rfid_reader.readText()
    #     self.raw_station_tag = station_tag
        # except:
        #     pass

    # def process_rfid_tag(self):
        # If the new rfid tag is different from the raw one, process it.

            # If station is None, then no tag was detected. Return None
        #     if station_tag.startswith('TAG_'):
        #         # Get the station number from the tag. Format TAG_XX where XXis the station number
        #         station_tag = station_tag.replace('TAG_','')
        #         station_tag = "1"
        #         return station_tag
        #     else:
        #         return None            
        # except:
        #     return None

    # def _readTextFromNtag(self):
    #     total_string = ''
    #     try:
    #         for page_adr in range (_NTAG_PAGE_ADR_MIN,_NTAG_PAGE_ADR_MAX+1):
    #             page_data = rfid_reader._read(page_adr)[:4]
    #             page_text = "".join(chr(x) for x in page_data)
    #             total_string = total_string + page_text
    #             page_adr = page_adr + _NTAG_NO_BYTES_PER_PAGE
    #     except:
    #         pass
    #     return total_string


    # def read_tag(self):
    #     tag_info = rfid_reader.readTagID()
    #     if tag_info['type'] == 'ntag':
    #         tag_id = self._readTextFromNtag()
    #         return tag_id
        
    def read_tag(self):
        tag_info = rfid_reader.readTagID()
        if tag_info['type'] == 'ntag':
            tag_id = rfid_reader._readTextFromNtag()
            time.sleep(0.001)
            return tag_id
        
    def read_RFID_ID(self):
        # if rfid_reader.tagPresent():    # if an RFID tag is present
        id = rfid_reader.readID()   # get the id
#         id = rfid.readID(detail=True) # gets more details eg. tag type

        print(id)

    def detect_station(self, motion_status):
        tag_detected = False
        _TAG_CMD_REQIDL = 0x26
        (stat, _) = rfid_reader._request(_TAG_CMD_REQIDL)
        if stat == 1:
            tag_detected = self.verify_detected_tag(motion_status)
            
        return tag_detected


    def verify_detected_tag(self, motion_status):
        time_elapsed = time.monotonic() - self.last_detected_time
        # print(f"Time Elapsed: {time_elapsed}")
        if (motion_status is True) and (time_elapsed > self.min_travel_time):
            logger.info(f"Tag detected and verified")
            self.update_last_tag_detected_time()
            return True
        else:
            return False



    def read_station(self):
        # station_tag = rfid_reader.readText(timeout=0.0001)
        station_tag = self.read_tag()
        print(station_tag)
        # self.read_RFID_ID()

        try:
            if station_tag.startswith('TAG_'):
                # Get the station number from the tag. Format TAG_XX where XXis the station number
                station_tag = station_tag.replace('TAG_','')
                # station_tag = "04"
                # print(station_tag)
                return station_tag
            else:
                return None
            
        except:
            return None
        
    

    
class Sensors(EnvironmentSensor, Accelerometer, Compass,PiSensor, RFIDReader):
    next_record_time = 0
    record_interval = None
    latest_readings = None
    sensors_initialised = False
    current_station = 0
    motion_status = True
    estimated_station = current_station
    motor_direction = 'forward'
    moved = True
    docked = False
    

    def __init__(self):
        # super().__init__()
        EnvironmentSensor.__init__(self)
        Accelerometer.__init__(self)
        Compass.__init__(self)
        PiSensor.__init__(self)
        RFIDReader.__init__(self)
        self.record_interval = jsonreader.read_json_parameter('data_log_interval')
        self.latest_readings, self.sensors_initialised = self.initiate_sensors()
        self.stopping_stations = jsonreader.read_json_parameter('stopping_stations')

        return None
    
    def set_motor_direction(self, _direction):
        self.motor_direction = _direction
        logger.info(f"Motor direction set to: {_direction}")
        self.update_last_tag_detected_time()
        self.moved = True
        return None

    
    def get_motor_direction(self):
        return self.motor_direction
    
    def get_environment_sensor_data(self):
        _tempC, _pres_hPa, _humRH = self.read_env_sensor()

        _environment_sensor_data = {
                                    'temperature': _tempC,
                                    'pressure': _pres_hPa,
                                    'humidity': _humRH,
                                }
        if self.sensors_initialised is True:
            self.latest_readings.update(_environment_sensor_data)

        return _environment_sensor_data

    def set_docking_status(self, _status):
        self.docked = _status
        return None
    
    def get_docking_status(self):
        return self.docked
    
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
    

    def get_movement_sensor_data(self):
        x_acc, y_acc, z_acc = self.read_acceleration()
        x_tilt, y_tilt, z_tilt = self.read_tilt()

        _movement_sensor_data = {
                                'x_acc': x_acc,
                                'y_acc': y_acc,
                                'z_acc': z_acc,
                                'x_tilt': x_tilt,
                                'y_tilt': y_tilt,
                                'z_tilt': z_tilt}

        if self.sensors_initialised is True:
            self.latest_readings.update(_movement_sensor_data)
        
        return _movement_sensor_data
    
    def get_compass_data(self):
        heading = self.read_compass()

        _compass_data = {'compass': heading}

        if self.sensors_initialised is True:
            self.latest_readings.update(_compass_data)

        return _compass_data

    def get_positional_data(self):
        heading = self.read_compass()

        _positional_data = {'compass': heading}

        if self.sensors_initialised is True:
            self.latest_readings.update({'compass': heading})

        return _positional_data
    
    def get_station_info(self):
        station = self.latest_readings.get('station')
        return station

    
    
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
        
    def update_current_station(self):
        _current_station = None
        _station_number = self.read_station()
        _last_recorded_station = self.latest_readings.get('station')
        if _station_number is not None and _station_number.isdigit():
            _station_number = int(_station_number)
            logger.debug(f"Station number detected: {_station_number}")

        else:
            motor_direction = self.get_motor_direction()
            _station_number = self.get_estimated_station(motor_direction,_last_recorded_station)
            logger.debug(f"Station number estimated: {_station_number}")

        if _station_number != _last_recorded_station:
            _current_station = _station_number
            self.latest_readings.update({'station': _current_station})
            logger.info(f"Station updated to: {_current_station}")
        else:
            pass

        return _current_station

    
    def get_estimated_station(self, _direction, _last_station):
        if _direction == 'forward':
            _estimated_station = _last_station + 1
        else:
            _estimated_station = _last_station - 1

        return _estimated_station
    
    def process_current_station(self, current_station):
        try:
            if current_station in self.stopping_stations:
                return False
            else:
                return True
        except:
            return True

     

    def initiate_sensors(self):

        _env_sensor_data = self.get_environment_sensor_data()
        _rpi_sensor_data = self.get_rpi_sensor_data()
        _compass_data = self.get_compass_data()

        # Combine the dictionary data
        _sensor_data = {**_env_sensor_data, **_rpi_sensor_data, **_compass_data}

        return _sensor_data, True
    
    def read_sensors(self):

        _env_sensor_data = self.get_environment_sensor_data()
        _rpi_sensor_data = self.get_rpi_sensor_data()
        _positional_data = self.get_positional_data()

        # Combine the dictionary data
        _sensor_data = {**_env_sensor_data, **_rpi_sensor_data, **_positional_data}

        return _sensor_data
    
    def reset_recording_times(self):
        self.next_record_time = 0
        return None
    

        






