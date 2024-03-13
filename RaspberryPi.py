import os
from datetime import datetime, timezone, timedelta
from typing import Any
from pijuice import PiJuice # Import pijuice module
import logging
from Utilities import JsonHandler
import time
import shutil
import subprocess
from Initialiser import DirectoryInfo
from Displays import Displays
from Sensors import PiSensor
import time
from PiicoDev_Switch import PiicoDev_Switch 

logger = logging.getLogger()
jsonreader = JsonHandler()
pijuice = PiJuice(1, 0x14) # Instantiate PiJuice interface object
directory_info = DirectoryInfo()
unit_display = Displays()
piSensor= PiSensor()
button = PiicoDev_Switch(double_press_duration=700, ema_parameter=73, ema_period=10)


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



    def transfer_data(self, test_run=False):

        unit_display.show_data_transfer(transferring=True, testing=test_run)

        # Create folders at destination for the data transfer
        destination_subdir, video_subdir = self.create_destination_folder()

        #Transfer video files
        # hat_display.show_letter("V")
        self.transfer_video_files(video_subdir, test_run=test_run)

        # Check transfer status and delete transffered files from source directory
        # hat_display.show_letter("C")
        self.check_transfer_status(video_subdir, delete_original=False)

        #Transfer log files
        # hat_display.show_letter("L")
        self.transfer_logs(destination_subdir)

        unit_display.show_data_transfer(transferring= False)



    

    def remove_video_file(filepath):
        """Removes a file from a directory when a filepath is provided.

        Args:
            filepath: The filepath of the file to remove.
        """

        if os.path.isfile(filepath):
            os.remove(filepath)
        else:
            raise FileNotFoundError(f"File not found: {filepath}")


    def transfer_files(self):
        try:
            logger.info("Transferring files from: " + self.source_dir + " to: " + self.destination + ":" + self.destination_dir)

            files_and_folders = os.listdir(self.source_dir)

            for file_or_folder in files_and_folders:
                logger.info("Transferring file or folder: %s", file_or_folder)
                os.system("scp -r {} {}:{}".format(os.path.join(self.source_dir, file_or_folder,'*'), self.destination, self.destination_dir))

            logger.info("Files transferred successfully")

            return True
    
        except:
            logger.error("Error in transferring files")
            return False


    
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


    
    def transfer_and_delete_files(self):
        transer_successful = self.transfer_files()
        # transer_successful = self.transfer_files_new(self.source_dir, self.destination, self.destination_dir)
        if transer_successful is True:
            self.delete_video_files(self.source_dir, 'Video_recordings')
        else:
            logger.error("Files were not deleted due to an error in transferring files")

        return None


class PiDiagnosis:
    def __init__(self) -> None:
        pass

    def get_battery_charge(self):
        battery_charge = pijuice.status.GetChargeLevel().get('data')
        return battery_charge
    
    def get_battery_temperature(self):
        battery_temperature = pijuice.status.GetBatteryTemperature().get('data')
        return battery_temperature
    
    def get_charging_status(self):
        if (pijuice.status.GetStatus().get('data').get('battery') == "CHARGING_FROM_5V_IO") or (pijuice.status.GetStatus().get('data').get('battery') == "CHARGING_FROM_IN"):
            return True
        else:
            return False
        
    def get_power_connection_status(self):
        if pijuice.status.GetStatus().get('data').get('powerInput5vIo') == "PRESENT" or pijuice.status.GetStatus().get('data').get('powerInput') == "PRESENT":
            return True
        else:
            return False

        
class SystemTasks(PiDiagnosis):

    latest_diagnosis = None

    def __init__(self) -> None:
        super().__init__()
        self.max_operating_temp = jsonreader.read_json_parameter('max_operating_temp')
        self.min_storage = jsonreader.read_json_parameter('min_storage')
        self.min_battery = jsonreader.read_json_parameter('min_battery')
        self.unit_turnoff_time = jsonreader.read_json_parameter('unit_turnoff_time')
        self.unit_turnon_time = jsonreader.read_json_parameter('unit_turnon_time')
        self.diagnostic_interval = jsonreader.read_json_parameter('diagnostic_interval')
        self.base_station = min(jsonreader.read_json_parameter('stopping_stations'))
        self.docking_required = False
        self.last_recording_status = False
        self.unit_is_operational = True
        self.next_diagonistic_run = None

         
    def set_unit_operational_status(self, _status):
        self.unit_is_operational = _status
        return None

    def get_unit_operational_status(self):
        return self.unit_is_operational 

    def set_docking_requirement(self, _status):
        self.docking_required = _status
        return None
    
    def get_docking_requirement(self):
        return self.docking_required
        

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

        if _unit_status["cpu_temp"] > self.max_operating_temp:
            logger.warning("Battery temperature is high: " + str(_unit_status["battery_temperature"]))
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
        elif datetime.fromtimestamp(time.time()).strftime("%H:%M:%S") >= self.unit_turnoff_time:
            logger.warning("Unit turnoff time reached: " + self.unit_turnoff_time)
            return True
        else:
            return False
        

        
    def schedule_unit_turnoff(self):
        unit_display.show_scheduled_shutdown(self.unit_turnon_time)
        turn_off_duration = self.calculate_unit_off_duration(self.unit_turnon_time)
        logger.info("Scheduling unit turnoff for: " + str(turn_off_duration) + " seconds")
        # pijuice.power.SetPowerOff(30)

        os.system("echo 0 | sudo tee /sys/class/rtc/rtc0/wakealarm")
        time.sleep(2)
        os.system("echo +{} | sudo tee /sys/class/rtc/rtc0/wakealarm".format(turn_off_duration))
        os.system("sudo halt")

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


        

        
    def calculate_unit_off_duration(self, scheduled_turn_on_time):
        current_time = datetime.now()

        if current_time.strftime("%H:%M:%S") > scheduled_turn_on_time:
            turn_on_time = datetime.combine(datetime.now().date()+ timedelta(days=1), datetime.strptime(scheduled_turn_on_time, "%H:%M:%S").time())
        else:
            turn_on_time = datetime.combine(datetime.now().date(), datetime.strptime(scheduled_turn_on_time, "%H:%M:%S").time())
        duration = turn_on_time - current_time

        return round(duration.total_seconds())
    
    def assess_ready_to_record(self, _sensor_data):
        cpu_temp = _sensor_data["cpu_temp"]
        free_space = _sensor_data["free_space"]

        if (cpu_temp > self.max_operating_temp) or (free_space < self.min_storage):
            return False
        else:
            return True
        
    def restart_unit(self):
        # unit_display.show_restart_message()
        logging.info("User initiated restart of the raspberry pi")
        os.system("sudo reboot")

        return None



class UnitManager(SystemTasks, FileTransfer):
    long_press_duration = 3
    last_pressed = False
    first_press_time = None
    option_counter = 0
    menu_mode = True
    startup_record_delay = None
    user_interaction = False
    unit_start_time = time.time()


    def __init__(self) -> None:
        super().__init__()
        self.startup_record_delay = jsonreader.read_json_parameter('startup_record_delay')
        pass

    def set_user_interaction(self, _status):
        self.user_interaction = _status
        return None
    
    def get_user_interaction(self):
        return self.user_interaction

    def set_menu_mode(self, _status):
        self.menu_mode = _status
        return None
    
    def get_menu_mode(self):
        return self.menu_mode

    def enter_menu(self):
        menu_mode = False
        if button.is_pressed is True and self.last_pressed is False:
            self.first_press = time.time()
            self.last_pressed = True
        elif button.is_pressed is True and self.last_pressed is True:
            if time.time() - self.first_press > self.long_press_duration:
                menu_mode = True
                self.last_recording_status = False
                self.option_counter = 0
                unit_display.menu_option_display(self.option_counter)
                time.sleep(1)
                # unit_display.enter_menu_led()
            else:
                pass
        else:
            self.last_pressed = False 
            self.first_press = None

        return menu_mode

    def exit_menu(self, _stay_in_menu):
        self.last_pressed = False
        self.first_press = None
        self.option_counter = 0

        if _stay_in_menu is True:
            return True
        else:
            return False
        
    
    def go_to_next_item(self, _counter):
        _counter = _counter + 1
        if _counter >= 7:
            _counter = 0

        return _counter
    
    def go_to_previous_item(self, _counter):
        _counter = _counter - 1
        if _counter <= 0:
            _counter = 4

        return _counter



    def select_option(self):

        self.option_counter= 0
        unit_display.menu_option_display(self.option_counter)
        while True:
            if button.was_pressed:
                self.set_user_interaction(True)
                if button.was_double_pressed:
                    unit_display.confirm_selection(self.option_counter)
                    break
                else:

                    self.option_counter = self.go_to_next_item(self.option_counter)
                    unit_display.menu_option_display(self.option_counter)

            else:
                if self.get_user_interaction() is False:
                    if time.time() > self.unit_start_time + self.startup_record_delay:
                        self.option_counter = 1
                        unit_display.confirm_selection(self.option_counter)
                        break

            time.sleep(0.001)
        

        return self.option_counter
    

    def execute_option(self, _selected_option, _camera, _streamer, _data_trasfer, _stop_signal):
        return_back_to_menu = False
        if _selected_option == 1: # record video
            _camera.set_recording_status(True)
            _streamer.set_streaming_status(False)

        elif _selected_option == 2: # stream video
            _camera.set_recording_status(False)
            time.sleep(2)
            _streamer.set_streaming_status(True)

        elif _selected_option == 3: # test_system
            _camera.set_recording_status(False)
            _streamer.set_streaming_status(False)
            _camera.record_video(test = True)
            _data_trasfer.transfer_data(test_run=True)
            return_back_to_menu  = True

        elif _selected_option == 4: # Transfer data to the  drive
            _data_trasfer.transfer_data()
            return_back_to_menu = True

        elif _selected_option == 5: # Shutdown
            self.schedule_unit_turnoff()

        elif _selected_option == 6: # Restart
            self.restart_unit()

        else:
            return_back_to_menu = True
        
        return return_back_to_menu
    

    def run_test_mode(self, _camera):
        _camera.record_video(test = True)
        return None





        
        


        



# class ManagePi:

#     max_cpu_temp = None
#     min_storage = None
#     turnoff_time = None
#     turnon_time = None
#     turnoff_delay = None
#     min_light_gain = None

#     def __init__(self) -> None:
#         self.max_cpu_temp = jsonreader.read_json_parameter('max_operating_temp')
#         self.min_storage = jsonreader.read_json_parameter('min_storage')
#         self.turnoff_time = jsonreader.read_json_parameter('turnoff_time')
#         self.turnon_time = jsonreader.read_json_parameter('turnon_time')
#         self.turnoff_delay = jsonreader.read_json_parameter('turnoff_delay')
#         self.schedule_pi_turnon(self.turnon_time)
#         self.min_light_gain = jsonreader.read_json_parameter('min_light_gain')
        
        
#     def monitor_and_schedule(self, _current_time ,_pi_data, _env_data):
#         _light = _env_data.get("light")
#         _current_time_str = datetime.fromtimestamp(_current_time).strftime("%H:%M:%S")
#         if _pi_data is not None:
#             cpu_temp = _pi_data["cpu_temp"]
#             free_space = _pi_data["free_space"]

#             if cpu_temp > self.max_cpu_temp:
#                 temp_warning = True
#             else:
#                 temp_warning = False

#             if free_space < self.min_storage:
#                 storage_warning = True
#             else:
#                 storage_warning = False        
#         else:
#             logging.error("No data received from the pi")
#             temp_warning = False
#             storage_warning = False

#         # if (_current_time_str >= self.turnoff_time) and (_light < self.min_light_gain):
#         if (_current_time_str >= self.turnoff_time):

#             logging.info("Scheduled shut down of the raspberry pi at " + self.turnoff_time +". Light level: " + str(_light))
#             shutdown_warning =  True

#         else:
#             shutdown_warning = False

#         return {"temp_warning": temp_warning, "storage_warning": storage_warning, "shutdown_warning": shutdown_warning}
        

#     def shutdown_pi(self):
#         unit_display.show_message("Shutting Down", 0)
#         unit_display.clear_display()
#         logger.info("User initiated shut down of the raspberry pi")
#         logger.shutdown()

#         os.system("sudo shutdown -h now")

#         return None
    
#     def restart_pi(self):
#         logging.info("User initiated restart of the raspberry pi")
#         logger.shutdown()
#         os.system("sudo reboot")

#         return None
    
#     def schedule_pi_turnon(self, turn_on_time):
#         logging.info("User initiated scheduled turn on of the raspberry pi")
    
#         turnon_time_utc = self.convert_local_time_to_utc(turn_on_time)

#         # pijuice.rtcAlarm.SetAlarm({'second': turnon_time_utc.get("seconds"), 
#         #                            'minute': turnon_time_utc.get("minutes"), 
#         #                            'hour': turnon_time_utc.get("hours"), 
#         #                            'day': 'EVERY_DAY'})
        
#         # pijuice.rtcAlarm.SetWakeupEnabled(True)

#         return None
    

#     def convert_local_time_to_utc(self, local_time):
#         """Converts a given local time in HH:MM:SS format to UTC time in HH:MM:SS format.

#         Args:
#             local_time: A string representing the local time in HH:MM:SS format.

#         Returns:
#             A string representing the UTC time in HH:MM:SS format.
#         """

#         # Parse the local time.
#         local_time_datetime = datetime.strptime(local_time, "%H:%M:%S")

#         # Convert the local time to UTC.
#         utc_time_datetime = local_time_datetime.astimezone(timezone.utc)

#         # Format the UTC time as a string.
#         utc_time_hours = int(utc_time_datetime.hour)
#         utc_time_minutes = int(utc_time_datetime.minute)
#         utc_time_seconds = int(utc_time_datetime.second)

#         return {"hours": utc_time_hours, "minutes": utc_time_minutes, "seconds": utc_time_seconds}

#     def initiate_shutdown(self):
#         logging.info("User initiated shut down of the raspberry pi")
#         # pijuice.rtcAlarm.SetAlarm({'second': 0, 'minute': 0, 'hour': 21, 'day': 'EVERY_DAY'})
#         # self.schedule_pi_turnon(self.turnon_time)
#         print("Shutting down ---------------------")
#         # pijuice.power.SetPowerOff(60)
#         self.shutdown_pi()
        

#         return None
    
#     def check_camera_availability(self,_pi_status):
#         if _pi_status is None:
#             return False
#         elif (_pi_status["temp_warning"] == True) or (_pi_status["storage_warning"] == True):
#             return False
#         else:
#             return True


#     def assess_pi_status(self, _pi_status):

#         if _pi_status["shutdown_warning"] == True:
#             return False

#         else:
#             return True

#     def assess_ready_to_record(self, _sensor_data):
#         cpu_temp = _sensor_data["cpu_temp"]
#         free_space = _sensor_data["free_space"]

#         if (cpu_temp > self.max_cpu_temp) or (free_space < self.min_storage):
#             return False
#         else:
#             return True
        

    
    # def assess_pi_status(self, _pi_status, recording):
    #     if _pi_status["temp_warning"] == True:
    #         _recording = False
    #         _operational_time = True
    #         _camera_available = False

    #     elif _pi_status["storage_warning"] == True:
    #         _recording = False
    #         _operational_time = True
    #         _camera_available = False

    #     elif _pi_status["shutdown_warning"] == True:
    #         _recording = False
    #         _operational_time = False
    #         _camera_available = False

    #     else:
    #         _recording = recording
    #         _operational_time = True
    #         _camera_available = True


    #     return _operational_time, _camera_available , _recording
    


    





# class SystemSetup(ManagePi):
#     max_cam_num = 9
#     cam_number = 0
#     press_time = 0
#     menu_hold_delay = 3
#     total_menu_options = 5
#     # sense = hat_display.sense

#     def __init__(self):
#         super().__init__()
#         self.menu_hold_delay = jsonreader.read_json_parameter('menu_hold_delay')
#         self.cam_number = jsonreader.read_json_parameter('cam_number')
#         self.max_cam_num = jsonreader.read_json_parameter('max_cam_number')

#     def enter_setup_mode(self, event):
#         setup_mode = False
#         if event.action == "pressed":
#             self.press_time = round(time.monotonic())
#         elif event.action == "held":
#             hold_time = round(time.monotonic())
#             if (hold_time - self.press_time) == self.menu_hold_delay:
#                 setup_mode = True
#             else:
#                 pass
#         else:
#             pass
#         return setup_mode
    

#     def select_mode(self):
#         # hat_display.clear_display()
#         system_setup = True
#         while system_setup is True:
#             menu_option = 1
#             # hat_display.show_message("Mode")
#             # hat_display.show_letter(menu_option)
#             selected_menu_option = self.navigate_menu(menu_option, self.total_menu_options)
#             system_modes = self.process_mode(selected_menu_option)




#             # mode_configured = False

#             # while mode_configured is False:
            
#             #     for event in self.sense.stick.get_events():
#             #         if event.action == "pressed":
#             #             if (event.direction == "up") or (event.direction == "right"):
#             #                 menu_option = self.goto_next_option(menu_option, self.total_menu_options)
#             #                 hat_display.show_letter(menu_option)
#             #             elif (event.direction == "down") or (event.direction == "left"):
#             #                 menu_option = self.goto_previous_option(menu_option, self.total_menu_options)
#             #                 hat_display.show_letter(menu_option)
#             #             elif event.direction == "middle":
#             #                 hat_display.show_letter(menu_option, type='accept')
#             #                 time.sleep(1)
#             #                 system_modes, mode_configured = self.process_mode(menu_option)
#             #             else:
#             #                 pass

#             #         else:
#             #             pass

#             system_setup = system_modes["system_setup"]

#         recording, streaming = system_modes["recording"], system_modes["streaming"]
            

#         return recording, streaming
    
#     def goto_next_option(self, _current_option, max_option, min_option = 0):
#         if _current_option != max_option:
#             _next_option = _current_option + 1
#         else:
#             _next_option = min_option

#         return _next_option

#     def goto_previous_option(self, _current_option, max_option, min_option = 0):
#         if _current_option != min_option:
#             _previous_option = _current_option - 1
#         else:
#             _previous_option = max_option

#         return _previous_option
    
#     def process_mode(self, _menu_option):
#         system_modes = {"system_setup": False, "recording": False, "streaming": False}
#         if _menu_option == 0:
#             # hat_display.show_message("Standby", type="info")
#             pass
#         elif _menu_option == 1:
#             # hat_display.show_message("Recording", type="error")
#             system_modes["recording"] = True
#         elif _menu_option == 2:
#             # hat_display.show_message("Streaming", type="info")
#             system_modes["streaming"] = True
#         elif _menu_option == 3:
#             # hat_display.show_message("Select Cam#", type="info")
#             self.select_cam_number()
#             system_modes["system_setup"] = True
#         elif _menu_option == 4:
#             # hat_display.show_message("Shutting Down", type="error")
#             self.initiate_shutdown()
#         else:
#             # hat_display.show_message("Restarting", type="error")
#             self.restart_pi()

#         return system_modes
    


#     def select_cam_number(self):
#         # hat_display.show_letter(cam_number)
#         cam_number = self.navigate_menu(self.cam_number, self.max_cam_num)   
#         self.cam_number = self.update_cam_number(cam_number)
#             # for event in self.sense.stick.get_events():
#             #     if event.action == "pressed":
#             #         if (event.direction == "up") or (event.direction == "right"):
#             #             cam_number = self.goto_next_option(cam_number, self.max_cam_num)
#             #             hat_display.show_letter(cam_number, type='warning')
#             #         elif (event.direction == "down") or (event.direction == "left"):
#             #             cam_number = self.goto_previous_option(cam_number, self.max_cam_num)
#             #             hat_display.show_letter(cam_number, type='warning')
#             #         elif event.direction == "middle":
#             #             hat_display.show_letter(cam_number, type= 'accept')
#             #             time.sleep(1)
#             #             self.cam_number = self.update_cam_number(cam_number)
#             #             hat_display.clear_display()
#             #             set_cam_number = True
#             #         else:
#             #             pass

#             #     else:
#             #         pass

#     def navigate_menu(self, selected_option, max_option, min_option = 0):
#         in_selection = True
#         while in_selection is True:
#             for event in self.sense.stick.get_events():
#                 if event.action == "pressed":
#                     if (event.direction == "up") or (event.direction == "right"):
#                         selected_option = self.goto_next_option(selected_option, max_option, min_option)
#                         # hat_display.show_letter(selected_option)
#                     elif (event.direction == "down") or (event.direction == "left"):
#                         selected_option = self.goto_previous_option(selected_option, max_option, min_option)
#                         # hat_display.show_letter(selected_option)
#                     elif event.direction == "middle":
#                         # hat_display.show_letter(selected_option, type= 'accept')
#                         time.sleep(1)
#                         final_selection = selected_option
#                         # hat_display.clear_display()
#                         in_selection = False
#                     else:
#                         pass
#                 else:
#                     pass

#         return final_selection

            
    

#     def update_cam_number(self, _cam_number):
#         logger.info("Updating camera number to: " + str(_cam_number) + " in the json file)")
#         jsonreader.update_json_value('cam_number', _cam_number)
        
#         return _cam_number






    

                
        



        
        
    

