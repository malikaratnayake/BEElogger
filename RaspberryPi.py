import os
from datetime import datetime, timezone, timedelta
from typing import Any
import logging
from Utilities import JsonHandler
import time
import shutil
import subprocess
from Initialiser import DirectoryInfo
from Sensors import Sensors
import time

logger = logging.getLogger()
jsonreader = JsonHandler()
directory_info = DirectoryInfo()
piSensor= Sensors()

class VideoCompression:
    video_directory = None
    output_directory = None

    def __init__(self):
        pass


    def run_EcomotionZip(self, video_directory):
        self.output_directory = directory_info.get_video_folder()
        self.delete_original = jsonreader.read_json_parameter('delete_original')
    
        # try:
        home_directory = os.path.expanduser("~")
        ecomotionzip_path = os.path.join(home_directory, "EcoMotionZip", "EcoMotionZip", "app.py")

        logger.info("Compressing video files")
        os.system("/home/pi-cam43/pi-dev/bin/python {} --video_source {} --output_directory {}".format(ecomotionzip_path, video_directory, self.output_directory))
        logger.info("Video files compressed successfully. Output directory is: " + self.output_directory)
        # except:
        #     logger.error("Error in compressing video files")

        return None



class FileTransfer:
    source_dir = None
    destination_dir = None
    destination = None
    destination_subdir = None
    desination_subdir_video = None

    def __init__(self):
        self.source_dir = directory_info.get_daily_logging_folder()
        self.destination_dir = jsonreader.read_json_parameter('destination_dir')
        self.destination = jsonreader.read_json_parameter('destination')
    
    def create_destination_folder(self):

        try:
            # Get the daily loging directory name from the source directory
            daily_logging_dir = os.path.split(self.source_dir)[1]

            # Create the destination directory path
            destination_subdir = os.path.join(self.destination_dir, daily_logging_dir)

            # Create the destination directory
            os.system("ssh {} mkdir -p {}".format(self.destination, destination_subdir))

            logger.info("Destination directory created: " + destination_subdir)

            # Create a destination directory for the video files
            video_subdir = os.path.join(destination_subdir, "Video_recordings")

            os.system("ssh {} mkdir -p {}".format(self.destination, video_subdir))

            logger.info("Destination video directory created: " + video_subdir)
            
            return destination_subdir, video_subdir

        except:
            logger.error("Error in creating destination directory")
            return None, None

    def transfer_logs(self, _destination_subdir):
        try:
            # Log transfer details
            logger.info("Transferring log files from: " + self.source_dir + " to: " + self.destination + ":" + _destination_subdir)

            file_extensions = ["log", "csv", "txt"]
            # Get the list of files in the source directory.

            files = subprocess.check_output(["ls", self.source_dir]).decode().strip().split("\n")

            # Filter the list of files to only include files with the specified extensions.
            files = [file for file in files if file.endswith(tuple(file_extensions))]

            # Create the scp command to transfer the files to the remote host.
            scp_command = ["scp"]
            for file in files:
                scp_command.append(f"{self.source_dir}/{file}")
            
            scp_command.append(f"{self.destination}:{_destination_subdir}")

            # Run the scp command.
            subprocess.run(scp_command)

            logger.info("Files transferred successfully")

        except:
            logger.error("Error in transferring files")

        return None


    def transfer_a_video(self, _desination_subdir_video, video_file_name ,test_run = False):

        #Log the starting time for the video transfer process
        trasfer_start_time = datetime.now()

        try:

            logger.info("Transferring video file from: " + video_file_name + " to: " + self.destination + ":" + _desination_subdir_video)

            # #Read video_list files to get the list of video files to be transferred
            # if test_run is True:
            #     video_list_file = os.path.join(self.source_dir, os.path.split(self.source_dir)[1] + "_test_video_list.txt")
            # else:
            #     video_list_file = os.path.join(self.source_dir, os.path.split(self.source_dir)[1] + "_video_list.txt")

            # with open(video_list_file, "r") as f:
            #     video_list = f.readlines()
            #     video_list = [file.strip() for file in video_list]

            # # Create the scp command to transfer the files to the remote host.
            
            # for video_file in video_list:
            video_transfer_scp= ["scp"]
            video_transfer_scp.append(f"{video_file_name}")
            video_transfer_scp.append(f"{self.destination}:{_desination_subdir_video}")

            # Run the scp command.
            subprocess.run(video_transfer_scp)
            logger.info("Transfering video file" + video_file_name)

            #Log the ending time for the video transfer process

            transfer_end_time = datetime.now()
            transfer_time = transfer_end_time - trasfer_start_time
            logger.info("Video files transferred successfully in: " + str(transfer_time))

        except:
            logger.error("Error in transferring video files")
           
        return None
    
    def transfer_video_files(self, _desination_subdir_video, test_run = False):

        #Log the starting time for the video transfer process
        trasfer_start_time = datetime.now()

        try:

            logger.info("Transferring video files from: " + self.source_dir + " to: " + self.destination + ":" + _desination_subdir_video)

            #Read video_list files to get the list of video files to be transferred
            if test_run is True:
                video_list_file = os.path.join(self.source_dir, os.path.split(self.source_dir)[1] + "_test_video_list.txt")
            else:
                video_list_file = os.path.join(self.source_dir, os.path.split(self.source_dir)[1] + "_video_list.txt")

            with open(video_list_file, "r") as f:
                video_list = f.readlines()
                video_list = [file.strip() for file in video_list]

            # Create the scp command to transfer the files to the remote host.
            
            for video_file in video_list:
                video_transfer_scp= ["scp"]
                video_transfer_scp.append(f"{video_file}")
                video_transfer_scp.append(f"{self.destination}:{_desination_subdir_video}")

                # Run the scp command.
                subprocess.run(video_transfer_scp)
                logger.info("Transfering video file" + video_file)

            #Log the ending time for the video transfer process

            transfer_end_time = datetime.now()
            transfer_time = transfer_end_time - trasfer_start_time
            logger.info("Video files transferred successfully in: " + str(transfer_time))

        except:
            logger.error("Error in transferring video files")
           
        return None


    
    def check_transfer_status(self,_video_subdir, delete_original = False):
        """Check whether the file has been transferred to the destination."""

        # Get the list of files in the remote _video_subdir directory.
        transferred_files = subprocess.check_output(["ssh", self.destination, "ls", _video_subdir]).decode().strip().split("\n")

        #Get the list of files in the source directory.
        source_files = subprocess.check_output(["ls", os.path.join(self.source_dir,"Video_recordings")]).decode().strip().split("\n")


        # Compare the list of files in the source directory with the list of files in the remote _video_subdir directory.
        # If the file has been transferred to the destination, delete it from the source directory.
        if delete_original is True:
            for file in source_files:
                if file in transferred_files:
                    os.remove(os.path.join(self.source_dir,"Video_recordings",file))
                    logger.info("File deleted from source directory: " + file)
                else:
                    logger.info("File not deleted from source directory: " + file)

        else:
            logger.info("Files not deleted from source directory")

        return None

    def delete_a_file(self, file_name):
        """Deletes a file from the source directory when a file name is provided.

        Args:
            file_name: The name of the file to delete.
        """

        if os.path.isfile(file_name):
            os.remove(file_name)
            logger.info("File deleted from source directory: " + file_name)
        else:
            raise FileNotFoundError(f"File not found: {file_name}")



    def transfer_data(self ,test_run=False):


        # Create folders at destination for the data transfer
        destination_subdir, video_subdir = self.create_destination_folder()

        #Transfer video files
        # hat_display.show_letter("V")
        self.transfer_video_files(video_subdir ,test_run=test_run)

        # Check transfer status and delete transffered files from source directory
        # hat_display.show_letter("C")
        self.check_transfer_status(video_subdir, delete_original=False)

        #Transfer log files
        # hat_display.show_letter("L")
        self.transfer_logs(destination_subdir)

        logger.info("Data transfer completed successfully")

        return None





    

    def remove_video_file(filepath):
        """Removes a file from a directory when a filepath is provided.

        Args:
            filepath: The filepath of the file to remove.
        """

        if os.path.isfile(filepath):
            os.remove(filepath)
        else:
            raise FileNotFoundError(f"File not found: {filepath}")


    # def transfer_files(self):
    #     try:
    #         logger.info("Transferring files from: " + self.source_dir + " to: " + self.destination + ":" + self.destination_dir)

    #         files_and_folders = os.listdir(self.source_dir)

    #         for file_or_folder in files_and_folders:
    #             logger.info("Transferring file or folder: %s", file_or_folder)
    #             os.system("scp -r {} {}:{}".format(os.path.join(self.source_dir, file_or_folder,'*'), self.destination, self.destination_dir))

    #         logger.info("Files transferred successfully")

    #         return True
    
    #     except:
    #         logger.error("Error in transferring files")
    #         return False


    
    def delete_video_files(self, directory_path, subdirectory_name):
        """Deletes all subdirectories with a specific name in a given directory.

        Args:
            directory_path: The path to the directory containing the subdirectories to
            be deleted.
            subdirectory_name: The name of the subdirectories to be deleted.
        """

        # Use the os.walk() function to iterate over the directory and all of its
        # subdirectories.
        logger.info("Deleting files from: " + self.source_dir)
        for root, dirs, files in os.walk(directory_path):
            # If a subdirectory matches the given name, delete it using the
            # os.rmdir() function.
            for dir in dirs:
                if dir == subdirectory_name:
                    shutil.rmtree(os.path.join(root, dir))
                    # os.rmdir(os.path.join(root, dir))


    
    # def transfer_and_delete_files(self):
    #     transer_successful = self.transfer_files()
    #     # transer_successful = self.transfer_files_new(self.source_dir, self.destination, self.destination_dir)
    #     if transer_successful is True:
    #         self.delete_video_files(self.source_dir, 'Video_recordings')
    #     else:
    #         logger.error("Files were not deleted due to an error in transferring files")

    #     return None


# class PiDiagnosis:
#     def __init__(self) -> None:
#         pass

    # def get_battery_charge(self):
    #     battery_charge = pijuice.status.GetChargeLevel().get('data')
    #     return battery_charge
    
    # def get_battery_temperature(self):
    #     battery_temperature = pijuice.status.GetBatteryTemperature().get('data')
    #     return battery_temperature
    
    # def get_charging_status(self):
    #     if (pijuice.status.GetStatus().get('data').get('battery') == "CHARGING_FROM_5V_IO") or (pijuice.status.GetStatus().get('data').get('battery') == "CHARGING_FROM_IN"):
    #         return True
    #     else:
    #         return False
        
    # def get_power_connection_status(self):
    #     if pijuice.status.GetStatus().get('data').get('powerInput5vIo') == "PRESENT" or pijuice.status.GetStatus().get('data').get('powerInput') == "PRESENT":
    #         return True
    #     else:
    #         return False

        
class SystemTasks():

    latest_diagnosis = None

    def __init__(self) -> None:
        self.max_operating_temp = jsonreader.read_json_parameter('max_operating_temp')
        self.min_storage = jsonreader.read_json_parameter('min_storage')
        self.unit_turnoff_time = jsonreader.read_json_parameter('unit_turnoff_time')
        self.unit_turnon_time = jsonreader.read_json_parameter('unit_turnon_time')
        self.diagnostic_interval = jsonreader.read_json_parameter('diagnostic_interval')
        self.last_recording_status = False
        self.unit_is_operational = True
        self.next_diagonistic_run = None
        self.in_recording_period = False

         
    def set_unit_operational_status(self, _status):
        self.unit_is_operational = _status
        return None

    def get_unit_operational_status(self):
        return self.unit_is_operational 


    def get_unit_status(self):
        current_time = time.time()
        free_space = piSensor.read_free_space()
        cpu_temp = piSensor.read_cpu_temp()

        self.latest_diagnosis = {"recorded_time": current_time, 
                                 "free_space": free_space,
                                 "cpu_temp": cpu_temp}


        return self.latest_diagnosis
    
    def assess_recording_capability(self):
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
        _unit_status = self.latest_diagnosis
        if _unit_status["free_space"] < self.min_storage:
            logger.warning("Free space is low: " + str(_unit_status["free_space"]))
            return True
        else:
            return False
        

        
    def schedule_unit_turnoff(self):
       # turn_off_duration = self.calculate_unit_off_duration(self.unit_turnon_time)
        #logger.info("Scheduling unit turnoff for: " + str(turn_off_duration) + " seconds")
        # pijuice.power.SetPowerOff(30)
        time.sleep(2)
        os.system("sudo shutdown now")

    def run_diagnostics(self, camera, stop_signal):
        diagnostic_run = False 
        recording_capability = True
        if self.latest_diagnosis is None:
            recording_capability = self.assess_recording_capability()
            diagnostic_run = True
            self.next_diagonistic_run = time.time() + self.diagnostic_interval
        else:
            if time.time() > self.next_diagonistic_run:
                recording_capability = self.assess_recording_capability()
                diagnostic_run = True
                self.next_diagonistic_run = time.time() + self.diagnostic_interval

        if diagnostic_run is True: 
            if recording_capability is False:
                shutdown_requirement = self.assess_shutdown_requirement()
            else:
                shutdown_requirement = False
                if self.assess_recording_schedule() is False:
                    camera.set_recording_status(False)
                else:
                    if self.in_recording_period is False:
                        self.in_recording_period = True
                        camera.set_recording_status(True)
                    else:
                        pass

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

        else:
            pass




    def assess_recording_schedule(self):
        if (datetime.fromtimestamp(time.time()).strftime("%H:%M:%S") >= self.unit_turnoff_time) or (datetime.fromtimestamp(time.time()).strftime("%H:%M:%S") < self.unit_turnon_time):
            self.in_recording_period = False
            logger.warning("Current time is out of recording schedule")
            return False
        else:
            return True


        

        

        
    # def calculate_unit_off_duration(self, scheduled_turn_on_time):
    #     current_time = datetime.now()

    #     if current_time.strftime("%H:%M:%S") > scheduled_turn_on_time:
    #         turn_on_time = datetime.combine(datetime.now().date()+ timedelta(days=1), datetime.strptime(scheduled_turn_on_time, "%H:%M:%S").time())
    #     else:
    #         turn_on_time = datetime.combine(datetime.now().date(), datetime.strptime(scheduled_turn_on_time, "%H:%M:%S").time())
    #     duration = turn_on_time - current_time

    #     return round(duration.total_seconds())
    
    # def assess_ready_to_record(self, _sensor_data):
    #     cpu_temp = _sensor_data["cpu_temp"]
    #     free_space = _sensor_data["free_space"]

    #     if (cpu_temp > self.max_operating_temp) or (free_space < self.min_storage):
    #         return False
    #     else:
    #         return True
        
    # def restart_unit(self):
    #     # unit_display.show_restart_message()
    #     logging.info("User initiated restart of the raspberry pi")
    #     os.system("sudo reboot")

    #     return None



class UnitManager(SystemTasks, FileTransfer, VideoCompression):

    def __init__(self) -> None:
        VideoCompression().__init__()
        super().__init__()
        pass
