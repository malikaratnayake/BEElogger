import time
import os
from datetime import datetime
from typing import Any
import csv
import logging

# Initialize the logger
logger = logging.getLogger()

class Writers:
    """
    Class to handle writing sensor data to CSV files.
    """
    
    def __init__(self, directory_info) -> None:
        """
        Initialize the Writers class with the given directory information.
        """
        self.directory_info = directory_info  
        self.monitoring_data_dir = self.directory_info.get_daily_logging_folder()
        self.csv_file_path = self.initialise_csv_file()
        logger.info("CSVWriter initialised")

    def generate_csv_filename(self):
        """
        Generate a CSV filename based on the current date.
        """
        current_date = time.strftime("%Y%m%d", time.localtime())
        file_name = f'/{current_date}.csv'
        return file_name

    def create_csv_file(self, _csv_file_name):
        """
        Create a new CSV file with the specified filename and write the header row.
        """
        with open(_csv_file_name, 'w', newline='') as csvfile:
            fieldnames = ['Date', 'Time', 'CPU Temperature', 'Free Space', 'Total Space', 'Temperature', 'Humidity', 'Light']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        return None
        
    def initialise_csv_file(self):
        """
        Initialize the CSV file for logging data. Create a new file if it doesn't exist.
        """
        csv_file_name = self.directory_info.get_filename_prefix() + '.csv'
        csv_file_path = self.monitoring_data_dir + csv_file_name

        if not os.path.exists(csv_file_path):
            self.create_csv_file(csv_file_path)
            logger.info("CSV file created at: " + csv_file_path)
        else:
            pass

        return csv_file_path

    def log_sensor_data(self, time_now, sensor_data):
        """
        Log the sensor data to the CSV file with the current date and time.
        """
        # Get the current date from the time_now variable
        date_now_str = datetime.fromtimestamp(time_now).strftime('%Y-%m-%d')

        # Get the current time from the time_now variable
        time_now_str = datetime.fromtimestamp(time_now).strftime('%H:%M:%S')

        # Open the CSV file in append mode and write the sensor data
        with open(self.csv_file_path, "a") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([date_now_str, 
                             time_now_str,
                             sensor_data['cpu_temp'],
                             sensor_data['free_space'],
                             sensor_data['total_space'],
                             sensor_data['temperature'],
                             sensor_data['humidity'],
                             sensor_data['light']])
            csvfile.close()
            logger.info("Data logged to file: " + self.csv_file_path)

        return None