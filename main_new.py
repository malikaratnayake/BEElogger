"""The main script for the pi-cam-dev project. 
This script is used to record video and sensor readings to a file all day."""

import time
from threading import Thread, Event
import argparse
from RaspberryPi import  FileTransfer, UnitManager
from Writers import Writers
import Camera
import Initialiser
import logging
from datetime import datetime
from queue import Queue, Empty
from VideoStreamer import CameraStream
from Sensors import Sensors
LOGGER = logging.getLogger()


class CameraThread(Thread):
    def __init__(
            self, 
            camera: Camera,
            streamer: CameraStream,
            unitmanager: UnitManager,
            name: str,
            stop_signal: Event,
            video_file_queue: Queue,
            camera_mode: str,
            ) -> None:
        
        super().__init__(name=name)
        self.camera = camera
        self.stop_signal = stop_signal
        self.unitmanager = unitmanager
        self.streamer = streamer
        self.video_end_time = None
        self.video_file_queue = video_file_queue
        self.camera.process_camera_mode(camera_mode, self.camera, self.streamer)
        

    def run(self):
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            self.unitmanager.run_diagnostics(self.camera, self.stop_signal)

            if self.camera.get_recording_status() is True:
                recorded_video_file = self.camera.record_video()
                if recorded_video_file is not None:
                    self.video_file_queue.put(recorded_video_file)
                self.video_end_time = time.time()

            elif self.streamer.get_streaming_status() is True:
                self.camera.set_recording_status(False)
                self.streamer.start_streaming()
              
            elif self.unitmanager.get_unit_operational_status() is True:
                if self.camera.get_recording_status() is False:
                    recording_status = self.camera.schedule_video_recording(self.video_end_time, self.camera.get_recording_status())
                    self.camera.set_recording_status(recording_status)
                else:
                    pass

            else:
                pass
 

class UnitManagerThread(Thread):
    def __init__(
        self, 
        unitmanager: UnitManager,
        camera: Camera,
        streamer: CameraStream,
        streaming_duration: int,
        stop_signal: Event,
        filetransfer: FileTransfer,
        data_logger: Writers,
        video_file_queue: Queue,
        sensors: Sensors,
        name: str,
        ) -> None:
        
        super().__init__(name=name)
        self.unitmanager = unitmanager
        self.stop_signal = stop_signal
        self.camera = camera
        self.filetransfer = filetransfer
        self.data_logger = data_logger
        self.video_file_queue = video_file_queue
        self.streaming_duration = streaming_duration
        self.streamer = streamer
        self.sensors = sensors

    def run(self):
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            if not self.video_file_queue.empty():
                time.sleep(10)
                video_file = self.video_file_queue.get()
                output_video = self.camera.convert_to_mp4(video_file)
                self.unitmanager.delete_a_file(video_file)
                self.unitmanager.run_EcomotionZip(output_video)
                self.video_file_queue.task_done()


            if self.streamer.get_streaming_status() is True:
                if self.streaming_duration is None:
                    self.streaming_duration = self.streamer.get_streaming_duration()
                time.sleep(self.streaming_duration)
                self.streamer.stop_streaming()
                self.streamer.set_streaming_status(False)
                time.sleep(2)
                self.camera.set_recording_status(True)

            current_time = round(time.time()) 
            if self.sensors.time_to_record(current_time):       
                    sensor_data = self.sensors.read_sensors()
                    self.data_logger.log_sensor_data(current_time,
                                                     sensor_data=sensor_data)
            else:
                pass

            


def main():
    # Setup
    startup_time = time.time()

    # Parse command line arguments
    ap = argparse.ArgumentParser(prog='Pollinator Monitoring System',
                                 description='This program records pollinator data')
    ap.add_argument("--camera_mode", nargs='?', dest='camera_mode', default="record",
                    help="Please set the camera mode", type=str, choices=['record', 'stream'])
    ap.add_argument("--camera_number", nargs='?', dest='camera_number', default=None,
                help="Please set the camera number", type=int)
    ap.add_argument("--duration", nargs='?', dest='stream_duration', default=None,
                help="Please set the duration to stream video", type=int)
    args = ap.parse_args()
    camera_mode = args.camera_mode
    camera_number = args.camera_number
    stream_duration = args.stream_duration

    

    Initialiser.SetupMonitoring(camera_number)
    LOGGER.info(f"Starting processing at :  {datetime.fromtimestamp(startup_time)}")
    time.sleep(5)


    filetransfer = FileTransfer()
    camera = Camera.VideoRecorder()
    unitmanager = UnitManager()
    streamer = CameraStream()
    data_logger = Writers()
    stop_signal = Event()
    video_file_queue = Queue(maxsize=10)
    sensors = Sensors()
    



    # Create threads
    threads = (
        camera_recoding := CameraThread(
            camera = camera,
            unitmanager = unitmanager,
            stop_signal = stop_signal,
            streamer = streamer,
            video_file_queue = video_file_queue,
            camera_mode = camera_mode,
            name = "CameraThread",
            ),
        unit_manager := UnitManagerThread( 
            unitmanager = unitmanager,
            stop_signal = stop_signal,
            camera = camera,
            streamer = streamer,
            streaming_duration = stream_duration,
            filetransfer = filetransfer,
            data_logger = data_logger,
            video_file_queue = video_file_queue,
            sensors = sensors,
            name = "UnitManagerThread",
            )

    )


    for thread in threads:
        LOGGER.info(f"Starting {thread.name}")
        thread.start()

        # Regularly poll to check if all threads have finished. If they haven't finished,
    # just sleep a little and check later
    while True:
        try:
            time.sleep(1)
            if not any([thread.is_alive() for thread in threads]):
                LOGGER.info(
                    "All child processes appear to have finished! Exiting infinite loop..."
                )
                break

        except (KeyboardInterrupt, Exception) as e :
            LOGGER.exception(
                "Received KeyboardInterrupt or some kind of Exception. Setting interrupt event and breaking out of infinite loop...",
            )
            LOGGER.warning(
                "You may have to wait a minute for all child processes to gracefully exit!",
            )
            stop_signal.set()
            break

    for thread in threads:
        LOGGER.info(f"Joining {thread.name}")
        thread.join()

    # unitmanager.run_EcomotionZip()

    # Transfer recorded files to the server
    # try:
    #     filetransfer.transfer_data()
    # except:
    #     LOGGER.info("Error transferring data to the server")

    #  # Add any extra stats/metadata to output too
    end = time.time()
    LOGGER.info(f"Finished processing at :  {datetime.fromtimestamp(end)}")

    # Shut down the Raspberry Pi
    # LOGGER.info("Shutting down the Raspberry Pi")
    # unitmanager.schedule_unit_turnoff()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.warning("Program terminated by user")
        exit()
