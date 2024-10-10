import logging
import os
import time
import csv
from typing import Any

# Initialize the logger
logger = logging.getLogger()

class SetupDirectories:
    """
    Setup directories for the program. This includes a directory for the log files,
    a directory for the sensor data, and a directory for the videos.
    """
    output_directory = None
    monitoring_data_dir = None
    daily_logging_dir = None
    video_folder = None
    filename_prefix = None
    current_date = time.strftime("%Y%m%d", time.localtime())

    def __init__(self):
        """
        Initialize the directories.
        """
        self.output_directory = self.get_output_directory()
        self.monitoring_data_dir = self.create_monitoring_data_folder()
        self.filename_prefix = self.create_name_prefix()
        self.daily_logging_dir, self.video_folder = self.create_daily_logging_folder()

    def get_output_directory(self):
        """
        Read the output_directory to save the files in from the json file.
        """
        pwd = os.path.dirname(os.path.abspath(__file__))
        output_directory = '/'.join(pwd.split('/')[:-1]) + '/'
        return output_directory

    def create_monitoring_data_folder(self):
        """
        Create Monitoring_Data Folder in the current directory, if it does not exist.
        """
        monitoring_data_folder = self.output_directory + 'Monitoring_Data'
        if not os.path.exists(monitoring_data_folder):
            os.makedirs(monitoring_data_folder)
        return monitoring_data_folder

    def create_daily_logging_folder(self):
        """
        Create a daily logging folder based on the current date.
        """
        folder_directory = self.monitoring_data_dir + self.create_name_prefix()
        if not os.path.exists(folder_directory):
            os.makedirs(folder_directory)
        video_directory = self.create_video_data_folder(folder_directory)
        return folder_directory, video_directory
    
    def create_name_prefix(self):
        """
        Create a name prefix based on the current date.
        """
        current_date = time.strftime("%Y%m%d", time.localtime())
        name_prefix = f'/{current_date}'
        return name_prefix

    def create_video_data_folder(self, _folder_directory):
        """
        Create a folder for video recordings.
        """
        video_folder_name = _folder_directory + str("/Video_recordings")
        if not os.path.exists(video_folder_name):
            os.makedirs(video_folder_name)
        return video_folder_name

class DirectoryInfo(SetupDirectories):
    """
    Class to provide directory information.
    """
    def __init__(self):
        super().__init__()

    def get_video_folder(self):
        return self.video_folder
    
    def get_monitoring_data_folder(self):
        return self.monitoring_data_dir
    
    def get_daily_logging_folder(self):
        return self.daily_logging_dir
    
    def get_filename_prefix(self):
        return self.filename_prefix
    
    def get_current_date(self):
        return self.current_date

class SensorDataLogger(DirectoryInfo):
    """
    Class to handle logging sensor data to CSV files.
    """
    csv_file_path = None
    daily_logging_folder = None

    def __init__(self):
        super().__init__()
        self.monitoring_data_dir = self.get_daily_logging_folder()
        self.csv_file_path = self.initialise_csv_file()
        logger.info("CSVWriter initialised")
        
    def create_csv_file(self, _csv_file_name):
        """
        Create a new CSV file with the specified filename and write the header row.
        """
        with open(_csv_file_name, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Time' ,'CPU Temperature', 'Free Space', 'Total Space', 'Temperature', 'Humidity', 'Light']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        return None
        
    def initialise_csv_file(self):
        """
        Initialize the CSV file for logging data. Create a new file if it doesn't exist.
        """
        csv_file_name = self.get_filename_prefix() + '.csv'
        csv_file_path = self.monitoring_data_dir + csv_file_name

        if not os.path.exists(csv_file_path):
            self.create_csv_file(csv_file_path)
            logger.info("CSV file created at: " + csv_file_path)
        return csv_file_path

class SetupEventLogger:
    """
    Class to setup event logging.
    """
    logger = logging.getLogger()

    def __init__(self, _log_directory, _filename_prefix):
        """
        Initialize the event logger with the given log directory and filename prefix.
        """
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)-14s] [%(funcName)-14s] [%(threadName)-14s] %(msg)s"))

        log_filename = _log_directory + _filename_prefix + '.log'
        
        # Create a file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)-14s] [%(funcName)-14s] [%(threadName)-14s] %(msg)s"))

        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

class SetupVideoFileList(DirectoryInfo):
    """
    Class to setup and manage the video file list.
    """
    def __init__(self):
        super().__init__()

    def create_video_list_file(self, test=False):
        """
        Create a video list file. If test is True, create a test video list file.
        """
        if test is True:
            video_list_filename = self.get_filename_prefix() + '_test_video_list.txt'
        else:
            video_list_filename = self.get_filename_prefix() + '_video_list.txt'
            
        video_list_file = self.get_daily_logging_folder() + video_list_filename

        if not os.path.exists(video_list_file):
            open(video_list_file, 'w').close()
        return video_list_file

    def add_video_to_list(self, _video_list_file, _video_filename):
        """
        Add a video filename to the video list file.
        """
        with open(_video_list_file, 'a') as file:
            file.write(_video_filename + '\n')
        return None

class SetupMonitoring(SetupDirectories):
    """
    Class to setup the monitoring system.
    """
    def __init__(self):
        SetupDirectories.__init__(self)
        SetupEventLogger(self.daily_logging_dir, self.filename_prefix)
        logging.info('Monitoring initialized at directory ' + self.daily_logging_dir)
        logging.info('Video data recording initialized at directory ' + self.video_folder)

class HealthManager:
    """
    Class to manage the health of the unit.
    """
    def __init__(self,
                 max_operating_temp: int,
                 min_storage: int,
                 unit_turnoff_time: str,
                 unit_turnon_time: str,
                 diagnostic_interval: int,
                 pisensor,
                 directory_info) -> None:
        """
        Initialize the HealthManager with the given parameters.
        """
        self.max_operating_temp = max_operating_temp
        self.min_storage = min_storage
        self.unit_turnoff_time = unit_turnoff_time
        self.unit_turnon_time = unit_turnon_time
        self.diagnostic_interval = diagnostic_interval
        self.pisensor = pisensor
        self.directory_info = directory_info
        
        logger.info("UnitManager initialised with parameters:")
        logger.info("Max operating temperature: " + str(self.max_operating_temp))
        logger.info("Minimum storage: " + str(self.min_storage))
        logger.info("Unit turnoff time: " + str(self.unit_turnoff_time))
        logger.info("Unit turnon time: " + str(self.unit_turnon_time))
        logger.info("Diagnostic interval: " + str(self.diagnostic_interval))

        self.last_recording_status = False
        self.unit_is_operational = True
        self.next_diagonistic_run = None
        self.in_recording_period = False
        self.latest_diagnosis = None

    def set_unit_operational_status(self, _status):
        """
        Set the operational status of the unit.
        """
        self.unit_is_operational = _status

    def get_unit_operational_status(self):
        """
        Get the operational status of the unit.
        """
        return self.unit_is_operational 

    def get_unit_status(self):
        """
        Get the current status of the unit including free space and CPU temperature.
        """
        current_time = time.time()
        free_space = self.pisensor.read_free_space()
        cpu_temp = self.pisensor.read_cpu_temp()

        self.latest_diagnosis = {"recorded_time": current_time, 
                                 "free_space": free_space,
                                 "cpu_temp": cpu_temp}

        return self.latest_diagnosis
    
    def assess_recording_capability(self):
        """
        Assess if the unit is capable of recording based on its status.
        """
        _unit_status = self.get_unit_status()
        logger.info("Unit status: " + str(_unit_status))

        if _unit_status["cpu_temp"] > self.max_operating_temp:
            logger.warning("Battery temperature is high: " + str(_unit_status["cpu_temp"]))
            return False
        elif self.assess_shutdown_requirement() is True:
            return False
        else:
            logger.info("Unit is operational")
            return True
        
    def assess_shutdown_requirement(self):
        """
        Assess if the unit needs to be shut down based on its status.
        """
        _unit_status = self.latest_diagnosis
        if _unit_status["free_space"] < self.min_storage:
            logger.warning("Free space is low: " + str(_unit_status["free_space"]))
            return True
        else:
            return False

    def assess_restart_requirement(self):
        """
        Assess if the unit needs to be restarted based on the current date.
        """
        recorded_date = self.directory_info.get_current_date()
        date_now = time.strftime("%Y%m%d", time.localtime())

        if recorded_date != date_now:
            logger.info("Restarting unit as current date has changed")
            return True
        else:
            return False

    def schedule_unit_turnoff(self):
        """
        Schedule the unit to turn off.
        """
        # turn_off_duration = self.calculate_unit_off_duration(self.unit_turnon_time)
        # logger.info("Scheduling unit turnoff for: " + str(turn_off_duration) + " seconds")
        # pijuice.power.SetPowerOff(30)
        time.sleep(2)
        os.system("sudo shutdown now")

    def run_diagnostics(self, camera, stop_signal):
        """
        Run diagnostics to assess the health of the unit.
        """
        diagnostic_run = False 
        recording_capability = True
        if self.latest_diagnosis is None:
            recording_capability = self.assess_recording_capability()
            restart_requirement = self.assess_restart_requirement()
            diagnostic_run = True
            self.next_diagonistic_run = time.time() + self.diagnostic_interval
        else:
            if time.time() > self.next_diagonistic_run:
                recording_capability = self.assess_recording_capability()
                restart_requirement = self.assess_restart_requirement()
                diagnostic_run = True
                self.next_diagonistic_run = time.time() + self.diagnostic_interval

        if diagnostic_run is True:
            if restart_requirement is True:
                self.schedule_restart()
            if recording_capability is False:
                shutdown_requirement = self.assess_shutdown_requirement()
            else:
                shutdown_requirement = False

            if shutdown_requirement is True:
                stop_signal.set()
            elif shutdown_requirement is False and recording_capability is False:
                self.last_recording_status = camera.get_recording_status()
                self.set_unit_operational_status(False)
                camera.set_recording_status(False)
                logger.warning("Recording stopped due to heating issues")
            else:
                self.set_unit_operational_status(True)
                if self.last_recording_status is True and camera.get_recording_status() is False:
                    camera.set_recording_status(True)
                    logger.info("Recording restarted after heating issues")
        else:
            pass

    def schedule_restart(self):
        """
        Schedule the unit to restart.
        """
        logger.info("Scheduling unit restart")
        os.system("sudo reboot")