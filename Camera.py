"""This python script uses the Raspberry Pi camera to record videos. Also, EnvironmentSensor.py is used to sense the environment to record temperature,
is used to record environment data while the video is being recorded. The video is recorded in a loop and the environment data is recorded in a separate thread."""
# Path: pi-cam-dev/codebase/VideoRecorder.py

# Import dependeancies including the sense hat library
import time
import os
import logging
from Utilities import JsonReader
from Initialiser import DirectoryInfo, SetupVideoFileList

logger = logging.getLogger()
jsonreader = JsonReader()
directory_info = DirectoryInfo()
video_file_logger = SetupVideoFileList()

class VideoRecorder:

    video_duration =None
    video_resolution = None
    video_fps = None
    video_quality = None
    video_bitrate = None
    video_container = None
    video_codec = None
    video_directory = None
    video_file_list = None
    recording_status  = False


    def __init__(self):
        req_video_info = ['video_duration', 'video_resolution', 'video_fps', 'video_quality', 'video_bitrate', 'video_container', 'video_codec', 'test_video_duration']
        self.video_sampling_interval = jsonreader.read_json_parameter('video_sampling_interval')
        video_info = jsonreader.read_json_parameters(req_video_info)
        self.video_duration = video_info[0]*1000
        self.test_video_duration = video_info[7]*1000
        self.video_resolution = video_info[1]
        self.video_fps = video_info[2]
        self.video_quality = video_info[3]
        self.video_bitrate = video_info[4]
        self.video_container = video_info[5]
        self.video_codec = video_info[6]
        self.record_end_time = jsonreader.read_json_parameter('unit_turnon_time')
        self.video_directory = directory_info.get_video_folder()
        self.record_to_log()
        self.video_file_list = video_file_logger.create_video_list_file()
        self.test_video_file_list = None
        self.set_recording_status(False)


    def set_recording_status(self, _status):
        self.recording_status = _status

    def get_recording_status(self):
        return self.recording_status
    
    # def set_current_station(self, _station):
    #     self.current_station = _station

    # def get_current_station_prefix(self, _station):
    #     # Return the current station prefix in format "Station_1"
    #     return "Station_" + str(_station)
        
    def record_to_log(self):
        logger.info('Video duration: ' + str(self.video_duration))
        logger.info('Video resolution: ' + str(self.video_resolution))
        logger.info('Video fps: ' + str(self.video_fps))
        logger.info('Video codec: ' + str(self.video_codec))
        logger.info('Video bitrate: ' + str(self.video_bitrate))
        logger.info('Video container: ' + str(self.video_container))
        logger.info('Video directory: ' + str(self.video_directory))


    def generate_video_name(self, test=False):
        time_string = time.strftime("%H%M%S", time.localtime())
        name_prefix = directory_info.get_filename_prefix()

        if test is True:
            video_filename = name_prefix + '_' + time_string + '_test' + '.' + self.video_container
        else:
            video_filename = name_prefix + '_' + time_string + '.' + self.video_container
        # station_prefix = self.get_current_station_prefix(self.current_station)

        # video_filename = name_prefix + '_' + time_string + '.' + self.video_container

        #return the filename in the string format /video_directory/Camera_1_YYYYMMDD_HHMMSS
        
        return self.video_directory + video_filename



    def record_video(self, test = False):
        if test is True:
            if self.test_video_file_list is None:
                self.test_video_file_list = video_file_logger.create_video_list_file(test=True)

            duration = self.test_video_duration
            video_filename = self.generate_video_name(test = True)
            video_file_list = self.test_video_file_list
        else:
            duration = self.video_duration
            video_filename = self.generate_video_name(test = False)
            video_file_list = self.video_file_list

        video_file_logger.add_video_to_list(video_file_list, video_filename)
        logger.info('Started Video recording: ' + video_filename)
        # unit_display.video_recording_led(recording = True)

        os.system("libcamera-vid -v 0 -n --vflip -t {} --framerate {} --width {} --height {} --codec {} -o {}".format(duration, 
                                                                                                           self.video_fps, 
                                                                                                           self.video_resolution[0], 
                                                                                                           self.video_resolution[1], 
                                                                                                           self.video_codec, 
                                                                                                           video_filename))
        logger.info('Video saved to ' + video_filename)
        time.sleep(2)
        self.recording_status = False


        return video_filename
    


    def schedule_video_recording(self, video_end_time, current_status):
        if video_end_time is None:
            return current_status
        else:
            if time.time() > video_end_time + self.video_sampling_interval:
                return True
            else:
                return False

    
    def convert_to_mp4(self, video_filename):
        # Extract the video filename before extension
        input_video_filename = video_filename.split('.')[0]

        #add mp4 as extnsion for the output video filename
        output_video_filename = input_video_filename + '.mp4'

        os.system("ffmpeg -framerate {} -i {} -c copy {}".format(self.video_fps, video_filename, output_video_filename))

        return output_video_filename
    

    def process_camera_mode(self, camara_mode, camera, streamer):
        if camara_mode == 'stream':
            camera.set_recording_status(False)
            streamer.set_streaming_status(True)
        else:
            camera.set_recording_status(True)
                                                                                                          



        


        
    






        

    

        