import time
import json
from threading import Thread, Event
import argparse
from Writers import Writers
from Camera import VideoRecorder, VideoProcessor, VideoStreamer
from UnitManager import SetupMonitoring, DirectoryInfo, SetupVideoFileList, HealthManager
import logging
from datetime import datetime
from queue import Queue
from Sensors import Sensors

# Initialize the logger
LOGGER = logging.getLogger()

class Config:
    """
    Configuration class to hold various settings for the system.
    """
    def __init__(self,
                 video_resolution: int,
                 video_fps: int,
                 video_duration: int,
                 video_container: str,
                 video_codec: str,
                 video_sampling_interval: int,
                 diagnostic_interval: int,
                 unit_turnon_time: str,
                 unit_turnoff_time: str,
                 recording_start_time: str,
                 recording_end_time: str,
                 streaming_duration: int,
                 max_operating_temp: int,
                 min_storage: int,
                 data_log_interval: int,
                 startup_record_delay: int,
                 compress_video: bool,
                 delete_original: bool,
                 ) -> None:
        """
        Initialize the Config class with the given parameters.
        """
        self.video_resolution = video_resolution
        self.video_fps = video_fps
        self.video_duration = video_duration
        self.video_container = video_container
        self.video_codec = video_codec
        self.video_sampling_interval = video_sampling_interval
        self.diagnostic_interval = diagnostic_interval
        self.unit_turnon_time = unit_turnon_time
        self.unit_turnoff_time = unit_turnoff_time
        self.recording_start_time = recording_start_time
        self.recording_end_time = recording_end_time
        self.streaming_duration = streaming_duration
        self.max_operating_temp = max_operating_temp
        self.min_storage = min_storage
        self.data_log_interval = data_log_interval
        self.startup_record_delay = startup_record_delay
        self.compress_video = compress_video
        self.delete_original = delete_original

# Load configuration from JSON file
with open('config.json', 'r') as f:
    __config_dict = json.load(f)

CONFIG = Config(**__config_dict)

class VideoRecordingThread(Thread):
    """
    Thread class to handle video recording.
    """
    def __init__(
            self, 
            videorecorder: VideoRecorder,
            streamer: VideoStreamer,
            healthmanager: HealthManager,
            name: str,
            stop_signal: Event,
            video_file_queue: Queue,
            camera_mode: str,
            ) -> None:
        """
        Initialize the VideoRecordingThread with the given parameters.
        """
        super().__init__(name=name)
        self.videorecorder = videorecorder
        self.stop_signal = stop_signal
        self.healthmanager = healthmanager
        self.streamer = streamer
        self.video_end_time = None
        self.video_file_queue = video_file_queue
        self.videorecorder.process_camera_mode(camera_mode, self.videorecorder, self.streamer)
        
    def run(self):
        """
        Run the video recording thread.
        """
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            if self.videorecorder.get_recording_status() is True:
                recorded_video_file = self.videorecorder.record_video()
                if recorded_video_file is not None:
                    self.video_file_queue.put(recorded_video_file)
                self.video_end_time = time.time()

            elif self.streamer.get_streaming_status() is True:
                self.videorecorder.set_recording_status(False)
                self.streamer.start_streaming()
              
            elif self.healthmanager.get_unit_operational_status() is True:
                if self.videorecorder.get_recording_status() is False:
                    recording_status = self.videorecorder.schedule_video_recording(self.video_end_time, self.videorecorder.get_recording_status())
                    self.videorecorder.set_recording_status(recording_status)
                else:
                    pass

            else:
                pass

class VideoProcessingThread(Thread):
    """
    Thread class to handle video processing.
    """
    def __init__(
        self, 
        videoprocessor: VideoProcessor,
        stop_signal: Event,
        video_file_queue: Queue,
        name: str,
        ) -> None:
        """
        Initialize the VideoProcessingThread with the given parameters.
        """
        super().__init__(name=name)
        self.stop_signal = stop_signal
        self.videoprocessor = videoprocessor
        self.video_file_queue = video_file_queue

    def run(self):
        """
        Run the video processing thread.
        """
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            if not self.video_file_queue.empty():
                time.sleep(10)
                video_file = self.video_file_queue.get()
                output_video = self.videoprocessor.convert_to_mp4(video_file)
                self.videoprocessor.delete_video(video_file)
                if CONFIG.compress_video is True:
                    self.videoprocessor.run_EcomotionZip(output_video, CONFIG.delete_original)
                self.video_file_queue.task_done()
            else:
                pass

class UnitManagerThread(Thread):
    """
    Thread class to manage the overall unit operations.
    """
    def __init__(
        self, 
        healthmanager: HealthManager,
        videorecorder: VideoRecorder,
        streamer: VideoStreamer,
        streaming_duration: int,
        stop_signal: Event,
        data_logger: Writers,
        sensors: Sensors,
        name: str,
        ) -> None:
        """
        Initialize the UnitManagerThread with the given parameters.
        """
        super().__init__(name=name)
        self.healthmanager = healthmanager
        self.stop_signal = stop_signal
        self.videorecorder = videorecorder
        self.data_logger = data_logger
        self.streaming_duration = streaming_duration
        self.streamer = streamer
        self.sensors = sensors

    def run(self):
        """
        Run the unit manager thread.
        """
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            if self.streamer.get_streaming_status() is True:
                if self.streaming_duration is None:
                    self.streaming_duration = self.streamer.get_streaming_duration()
                time.sleep(self.streaming_duration)
                self.streamer.stop_streaming()
                self.streamer.set_streaming_status(False)
                time.sleep(2)
                self.videorecorder.set_recording_status(True)

            current_time = round(time.time()) 
            if self.sensors.time_to_record(current_time):       
                    sensor_data = self.sensors.read_sensors()
                    self.data_logger.log_sensor_data(current_time, sensor_data=sensor_data)
                    self.healthmanager.run_diagnostics(self.videorecorder, self.stop_signal)
            else:
                pass

def main():
    """
    Main function to setup and start the monitoring system.
    """
    # Setup
    startup_time = time.time()

    # Parse command line arguments
    ap = argparse.ArgumentParser(prog='NatBeeSense Hive Monitoring System',
                                 description='This program records native beehive monitoring data')
    ap.add_argument("--camera_mode", nargs='?', dest='camera_mode', default="record",
                    help="Please set the camera mode", type=str, choices=['record', 'stream'])
    ap.add_argument("--duration", nargs='?', dest='stream_duration', default=None,
                help="Please set the duration to stream video", type=int)
    args = ap.parse_args()
    camera_mode = args.camera_mode
    stream_duration = args.stream_duration

    # Setup monitoring
    SetupMonitoring()
    LOGGER.info(f"Starting processing at :  {datetime.fromtimestamp(startup_time)}")

    # Initialize directory information and video file logger
    directory_info = DirectoryInfo()
    video_file_logger = SetupVideoFileList()

    # Initialize sensors
    sensors = Sensors(
        data_log_interval=CONFIG.data_log_interval
    )

    # Initialize video recorder
    videorecorder = VideoRecorder(
        video_resolution=CONFIG.video_resolution,
        video_fps=CONFIG.video_fps,
        video_duration=CONFIG.video_duration,
        video_container=CONFIG.video_container,
        video_codec=CONFIG.video_codec,
        video_sampling_interval=CONFIG.video_sampling_interval,
        recording_start_time=CONFIG.recording_start_time,
        recording_end_time=CONFIG.recording_end_time,
        directory_info=directory_info,
        video_file_logger=video_file_logger)
    
    # Initialize video processor
    videoprocessor = VideoProcessor(
        video_fps=CONFIG.video_fps,
        directory_info=directory_info
    )

    # Initialize health manager
    healthmanager = HealthManager(
        max_operating_temp=CONFIG.max_operating_temp,
        min_storage=CONFIG.min_storage,
        unit_turnon_time=CONFIG.unit_turnon_time,
        unit_turnoff_time=CONFIG.unit_turnoff_time,
        diagnostic_interval=CONFIG.diagnostic_interval,
        pisensor=sensors,
        directory_info=directory_info)
    
    # Initialize video streamer
    streamer = VideoStreamer(
        video_resolution=CONFIG.video_resolution,
        streaming_duration=CONFIG.streaming_duration,
        pisensor=sensors,
    )

    # Initialize data logger
    data_logger = Writers(
        directory_info=directory_info
    )

    # Initialize stop signal and video file queue
    stop_signal = Event()
    video_file_queue = Queue(maxsize=10)

    # Create threads
    threads = (
        video_recoding := VideoRecordingThread(
            videorecorder=videorecorder,
            healthmanager=healthmanager,
            stop_signal=stop_signal,
            streamer=streamer,
            video_file_queue=video_file_queue,
            camera_mode=camera_mode,
            name="CameraThread",
            ),
        unit_manager := UnitManagerThread( 
            healthmanager=healthmanager,
            stop_signal=stop_signal,
            videorecorder=videorecorder,
            streamer=streamer,
            streaming_duration=stream_duration,
            data_logger=data_logger,
            sensors=sensors,
            name="UnitManagerThread",
            ),
        video_processor := VideoProcessingThread( 
            stop_signal=stop_signal,
            videoprocessor=videoprocessor,
            video_file_queue=video_file_queue,
            name="VideoProcessingThread",
            )
    )

    # Start threads
    for thread in threads:
        LOGGER.info(f"Starting {thread.name}")
        thread.start()

    # Monitor threads
    while True:
        try:
            time.sleep(1)
            if not any([thread.is_alive() for thread in threads]):
                LOGGER.info("All child processes appear to have finished! Exiting infinite loop...")
                break
        except (KeyboardInterrupt, Exception) as e:
            LOGGER.exception("Received KeyboardInterrupt or some kind of Exception. Setting interrupt event and breaking out of infinite loop...")
            LOGGER.warning("You may have to wait a minute for all child processes to gracefully exit!")
            stop_signal.set()
            break

    # Join threads
    for thread in threads:
        LOGGER.info(f"Joining {thread.name}")
        thread.join()

    # Log completion time
    end = time.time()
    LOGGER.info(f"Finished processing at :  {datetime.fromtimestamp(end)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.warning("Program terminated by user")
        exit()