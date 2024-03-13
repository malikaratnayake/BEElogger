"""This python script is used to log recorded data and information to text files and 
to display important information on the sensor hat display."""
# Path: pi-cam-dev/codebase/Writers.py

# Import dependencies
import time
import os
from datetime import datetime
from typing import Any
import json
from Utilities import JsonReader
import csv
from pathlib import Path
import logging
from Initialiser import DirectoryInfo



jsonreader = JsonReader()
logger = logging.getLogger()
directory_info = DirectoryInfo()


    
class CSVWriter():
    
    csv_file_path = None
    daily_logging_folder = None
    record_interval = None

    def __init__(self):
        self.monitoring_data_dir = directory_info.get_daily_logging_folder()
        self.record_interval = jsonreader.read_json_parameter('data_log_interval')
        self.csv_file_path = self.initialise_csv_file()
        logger.info("CSVWriter initialised")


    def generate_csv_filename(self):
        current_date = time.strftime("%Y%m%d", time.localtime())
        camera_number  = jsonreader.read_json_parameter('cam_number')
        file_name = '/Camera_'+str(camera_number) + '_' + str(current_date) + '.csv'

        return file_name

    
    def create_csv_file(self, _csv_file_name):
        with open(_csv_file_name, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Time','CPU Temperature', 'Free Space', 'Total Space']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
        return None
        
    def initialise_csv_file(self):
        csv_file_name = directory_info.get_filename_prefix() + '.csv'
        csv_file_path = self.monitoring_data_dir + csv_file_name

        if not os.path.exists(csv_file_path):
            self.create_csv_file(csv_file_path)
            logger.info("CSV file created at: " + csv_file_path)
        else:
            pass

        return csv_file_path

    def log_sensor_data(self, time_now, sensor_data):
        #Get the current date from the time_now variable
        date_now_str = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d')

        #Get the current time from the time_now variable
        time_now_str = datetime.fromtimestamp(time_now).strftime('%H:%M:%S')
        # self.log_event("Logging data to file...")


        with open (self.csv_file_path, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([date_now_str, 
                             time_now_str,
                              sensor_data['cpu_temp'],
                              sensor_data['free_space'],
                              sensor_data['total_space']])
            csvfile.close()
            logger.info("Data logged to file: " + self.csv_file_path)


        return None
    
# Class to inherit from the DisplayWriter and CSVWriter classes       
class Writers(CSVWriter):
    def __init__(self):
        CSVWriter.__init__(self)

    


            