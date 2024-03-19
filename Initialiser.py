"""Log events in the program for debugging purposes"""

import logging
from Utilities import JsonHandler
import datetime
import os
import time
import csv
from datetime import datetime

jasonreader = JsonHandler()
logger = logging.getLogger()
        
# Setup directories for the program. This includes a directory for the log files, a directory for the sensor data, and a directory for the videos
class SetupDirectories:
    output_directory = None
    monitoring_data_dir = None
    daily_logging_dir = None
    video_folder = None
    filename_prefix = None

    def __init__(self, camera_number=None):
        if camera_number is not None:
            jasonreader.update_json_value('cam_number', camera_number)            

        self.output_directory = self.create_output_directory()
        self.monitoring_data_dir = self.create_monitoring_data_folder()
        self.filename_prefix = self.create_filename_prefix()
        self.daily_logging_dir = self.create_daily_logging_folder()
        self.video_folder = self.create_camera_output_folder()

    #Read the output_directory to save the files in from the json file
    def create_output_directory(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        output_directory = os.path.join(pwd, '')
        jasonreader.update_json_value('output_directory', output_directory) 
        return output_directory

        

    # Create Monitoring_Data Folder in the current directory, if it does not exist
    def create_monitoring_data_folder(self):
        monitoring_data_folder = self.output_directory + 'Monitoring_Data'
        if not os.path.exists(monitoring_data_folder):
            os.makedirs(monitoring_data_folder)
        else:
            pass

        return monitoring_data_folder

    # Create a folder with the name in Camera_Number_YYYYMMDD format in the Monitoring_Data folder if it does not exist
    def create_camera_folder(self, camera_number):
        monitoring_data_folder = self.monitoring_data_dir
        camera_folder = self.generate_folder_name
        camera_folder_path = monitoring_data_folder + camera_folder
        print(camera_folder_path)
        if not os.path.exists(camera_folder_path):
            os.makedirs(camera_folder_path)
        else:
            pass

    def create_daily_logging_folder(self):
        folder_name = self.generate_folder_name()
        folder_directory = self.monitoring_data_dir + folder_name
        if not os.path.exists(folder_directory):
            os.makedirs(folder_directory)
        else:
            pass

        return folder_directory
    

    def generate_folder_name(self):
        current_date = time.strftime("%Y%m%d", time.localtime())
        camera_number  = jasonreader.read_json_parameter('cam_number')
        folder_name = '/Camera_'+str(camera_number) + '_' + str(current_date)

        return folder_name
    
    def create_camera_output_folder(self):
        video_folder_name = self.daily_logging_dir + str("/Video_recordings")
        if not os.path.exists(video_folder_name):
            os.makedirs(video_folder_name)
        else:
            pass

        return video_folder_name
    
    # Create a filename prefix in the format Camera_Number_YYYYMMDD
    
    def create_filename_prefix(self):
        current_date = time.strftime("%Y%m%d", time.localtime())
        camera_number  = jasonreader.read_json_parameter('cam_number')
        filename_prefix = '/Camera_'+str(camera_number) + '_' + str(current_date)

        return str(filename_prefix)
    

    
class DirectoryInfo(SetupDirectories):

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

    

class SensorDataLogger(DirectoryInfo):
    csv_file_path = None
    daily_logging_folder = None

    def __init__(self):
        super().__init__()
        self.monitoring_data_dir = self.get_daily_logging_folder()
        self.csv_file_path = self.initialise_csv_file()
        logger.info("CSVWriter initialised")


    # def generate_csv_filename(self):
    #     filename_prefix = self.get_filename_prefix()
    #     # current_date = time.strftime("%Y%m%d", time.localtime())
    #     # camera_number  = jasonreader.read_json_parameter('cam_number')
    #     csv_file_name = filename_prefix + '.csv'

    #     return csv_file_name

    
    # def create_csv_file(self, _csv_file_name):
    #     with open(_csv_file_name, 'w', newline='') as csvfile:
    #         fieldnames = ['Date', 'Time', 'Temperature', 'Humidity', 'Pressure', 'Light' ,'CPU Temperature', 'Free Space', 'Total Space', 
    #                       'Bearing', 'Pitch', 'Roll', 'Yaw', 'X', 'Y', 'Z',
    #                       'Battery Charge', 'Battery Temperature', 'Battery Voltage' ,'Battery Current', 'Battery IO Voltage','Battery IO Current',
    #                       'Recording', 'Streaming']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #         writer.writeheader()
    #         csvfile.close()
        
    #     return None
        
    def create_csv_file(self, _csv_file_name):
        with open(_csv_file_name, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Time' ,'CPU Temperature', 'Free Space', 'Total Space']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
        return None
        
    def initialise_csv_file(self):
        csv_file_name = self.get_filename_prefix() + '.csv'
        csv_file_path = self.monitoring_data_dir + csv_file_name

        if not os.path.exists(csv_file_path):
            self.create_csv_file(csv_file_path)
            logger.info("CSV file created at: " + csv_file_path)
        else:
            pass

        return csv_file_path


class SetupEventLogger:
    logger = logging.getLogger()

    def __init__(self, _log_directory, _filename_prefix):
        # Set the logging level
        self.logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)-14s] [%(funcName)-14s] [%(threadName)-14s] %(msg)s"))

        log_filename = _log_directory +_filename_prefix + '.log'
        
        # Create a file handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)-8s] [%(module)-14s] [%(funcName)-14s] [%(threadName)-14s] %(msg)s"))

        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # current_time = datetime.now()
        # logger.info(f"Starting processing at :  {datetime.fromtimestamp(current_time)}")
        # logger.info(f"Running main() with Config:  {config.__dict__}")
        # logger.info(f"Outputting to {log_message}")


        # # Set the format of the log messages
        # formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
        # file_handler.setFormatter(formatter)

        # # Add the file handler to the logger
        # self.logger.addHandler(file_handler)

        # self.logger.info('Logger initialized at directory ' + log_filename)

        return None
    
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
    

    
# class SetupEventLogger:
#     logger = logging.getLogger()

#     def __init__(self, _log_directory, _filename_prefix):
#         # Set the logging level
#         self.logger.setLevel(logging.DEBUG)

#         log_filename = _log_directory +_filename_prefix + '.log'
        
#         # Create a file handler
#         file_handler = logging.FileHandler(log_filename)

#         # Set the format of the log messages
#         formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s')
#         file_handler.setFormatter(formatter)

#         # Add the file handler to the logger
#         self.logger.addHandler(file_handler)

#         self.logger.info('Logger initialized at directory ' + log_filename)

#         return None
    
#     def debug(self, msg, *args, **kwargs):
#         """Log a debug message."""
#         self.logger.debug(msg, *args, **kwargs)

#     def info(self, msg, *args, **kwargs):
#         """Log an info message."""
#         self.logger.info(msg, *args, **kwargs)

#     def warning(self, msg, *args, **kwargs):
#         """Log a warning message."""
#         self.logger.warning(msg, *args, **kwargs)

#     def error(self, msg, *args, **kwargs):
#         """Log an error message."""
#         self.logger.error(msg, *args, **kwargs)
    

class LoggingThread:
    """A wrapper around `threading.Thread` with convenience methods for logging.
    
    This class extends the functionality of the `threading.Thread` class by providing
    additional convenience methods for logging. It serves as a base class for other
    threads that require logging capabilities.
    
    Attributes:
        name (str): The name of the thread.
        logger (logging.Logger): The logger object used for logging.
    """
    def __init__(self, name: str, logger: logging.Logger) -> None:
        super().__init__(name=name)

        self.logger = logger

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

    def __init__(self):
        super().__init__()
        

    def create_video_list_file(self, test=False):

        if test is True:
            video_list_filename = self.get_filename_prefix() + '_test_video_list.txt'
        else:
            video_list_filename = self.get_filename_prefix() + '_video_list.txt'
            
        video_list_file = self.get_daily_logging_folder() + video_list_filename

        if not os.path.exists(video_list_file):
            open(video_list_file, 'w').close()
        else:
            pass

        return video_list_file


    def add_video_to_list(self, _video_list_file, _video_filename):
        with open(_video_list_file, 'a') as file:
            file.write(_video_filename + '\n')
            file.close()

        return None


class SetupMonitoring(SetupDirectories):
    def __init__(self, camera_number):
        SetupDirectories.__init__(self, camera_number)
        SetupEventLogger(self.daily_logging_dir, self.filename_prefix)
        logging.info('Monitoring initialized at directory ' + self.daily_logging_dir)

        return None

# initiate_monitoring = SetupMonitoring()