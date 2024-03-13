"""The main script for the pi-cam-dev project. 
This script is used to record video and sensor readings to a file all day."""

import time
from threading import Thread, Event
import argparse
from Sensors import Sensors
from Displays import Displays
from RaspberryPi import  FileTransfer, UnitManager
# from Transceiver import Transmitter, Reciever
from Writers import Writers
import Camera
import Initialiser
import logging
from datetime import datetime
from queue import Queue, Empty
from VideoStreamer import CameraStream
LOGGER = logging.getLogger()


class CameraThread(Thread):
    def __init__(
            self, 
            camera: Camera,
            sensors: Sensors,
            unitmanager: UnitManager,
            streamer: CameraStream,
            name: str,
            stop_signal: Event,
            ) -> None:
        
        super().__init__(name=name)
        self.camera = camera
        self.sensors = sensors 
        self.stop_signal = stop_signal
        self.unitmanager = unitmanager
        self.streamer = streamer
        self.video_end_time = None
        

    def run(self):
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            if self.camera.get_recording_status() is True:
                self.camera.record_video()
                self.video_end_time = time.time()
                # print("Recording")
                # self.streamer.start_streaming()

            elif self.streamer.get_streaming_status() is True:
                self.camera.set_recording_status(False)
                self.streamer.start_streaming()
              

            elif self.unitmanager.get_menu_mode() is False and self.unitmanager.get_unit_operational_status() is True:
                if self.camera.get_recording_status() is False:
                    recording_status = self.camera.schedule_video_recording(self.video_end_time, self.camera.get_recording_status())
                    self.camera.set_recording_status(recording_status)
                else:
                    pass

            else:
                pass
                # time.sleep(2)
                # self.camera.record_video()
                # self.video_end_time = time.time()





class SensorLoggingThread(Thread):
    def __init__(
        self, 
        sensors: Sensors,
        camera: Camera,
        data_logger,
        unit_display,
        unitmanager,
        name: str,
        stop_signal: Event,
        streamer: CameraStream,
        ) -> None:
        
        super().__init__(name=name)
        self.camera = camera
        self.sensors = sensors
        self.data_logger = data_logger
        self.unit_display = unit_display
        self.unitmanager = unitmanager
        self.stop_signal = stop_signal
        self.streamer = streamer



    def run(self):
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

                        

            if self.camera.get_recording_status() is True: # Add testing status true
                current_time = round(time.time()) 
                if self.sensors.time_to_record(current_time):        
                    self.unit_display.data_logging_led(True)
                    sensor_data = self.sensors.read_sensors()
                    self.data_logger.log_sensor_data(current_time,
                                                     sensor_data=sensor_data)
                    self.unit_display.data_logging_led(False)
                else:
                    pass
            else:
                self.sensors.reset_recording_times() 

class UnitManagerThread(Thread):
    def __init__(
        self, 
        unitmanager: UnitManager,
        camera: Camera,
        streaming: CameraStream,
        stop_signal: Event,
        filetransfer: FileTransfer,
        start_time: float,
        name: str,
        ) -> None:
        
        super().__init__(name=name)
        self.unitmanager = unitmanager
        self.stop_signal = stop_signal
        self.camera = camera
        self.streaming = streaming
        self.filetransfer = filetransfer

    def run(self):
        while True:
            if self.stop_signal.is_set():
                LOGGER.info(f"Stopping {self.name}. Stop signal received")
                break

            
            if self.unitmanager.get_menu_mode() is True:
                if self.streaming.get_streaming_status() is True:
                    self.streaming.set_streaming_status(False)
                    time.sleep(1)
                    self.streaming.stop_streaming()

                
                while self.camera.get_recording_status() is True:
                    time.sleep(1)
                    
                self.camera.set_recording_status(False)
                selected_option = self.unitmanager.select_option()
                stay_in_menu = self.unitmanager.execute_option(selected_option, self.camera, self.streaming, self.filetransfer, self.stop_signal)
                self.unitmanager.set_menu_mode(self.unitmanager.exit_menu(stay_in_menu))

            else:
                menu_mode = self.unitmanager.enter_menu()
                self.unitmanager.set_menu_mode(menu_mode)

                self.unitmanager.run_diagnostics(self.camera, self.stop_signal)
          
            # time.sleep(0.002)             


def main():
    # Setup
    startup_time = time.time()
    Initialiser.SetupMonitoring()

    # Create instances of required classes
    filetransfer = FileTransfer()
    camera = Camera.VideoRecorder()
    sensors = Sensors()
    unit_display = Displays()
    unitmanager = UnitManager()
    data_logger = Writers()
    streamer = CameraStream()

    stop_signal = Event()
    transmit_queue = Queue(maxsize=10)
    

    # Parse command line arguments
    ap = argparse.ArgumentParser(prog='Pollinator Monitoring System',
                                 description='This program records pollinator data')
    ap.add_argument("--camera_mode", nargs='?', dest='camera_mode', default="interval",
                    help="Please set the camera mode", type=str, choices=['continuous', 'interval', 'stream'])
    args = ap.parse_args()
    camera_mode = args.camera_mode

    LOGGER.info(f"Starting processing at :  {datetime.fromtimestamp(startup_time)}")

    # Create threads
    threads = (
        camera_recoding := CameraThread(
            camera = camera,
            sensors = sensors,
            stop_signal = stop_signal,
            unitmanager = unitmanager,
            streamer = streamer,
            name = "CameraThread",
            ),
        unit_manager := UnitManagerThread( 
            unitmanager = unitmanager,
            stop_signal = stop_signal,
            camera = camera,
            streaming = streamer,
            filetransfer = filetransfer,
            start_time = startup_time,
            name = "UnitManagerThread",
            ),
        sensor_logging := SensorLoggingThread(
            sensors = sensors, 
            camera = camera,
            data_logger = data_logger, 
            unit_display = unit_display, 
            unitmanager = unitmanager,
            stop_signal = stop_signal,
            streamer = streamer,
            name = "SensorLoggingThread",
            ),
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
        unit_display.clear_leds()

    # Transfer recorded files to the server
    filetransfer.transfer_data()
    # LOGGER.info("Data transfer complete")

    #  # Add any extra stats/metadata to output too
    end = time.time()
    LOGGER.info(f"Finished processing at :  {datetime.fromtimestamp(end)}")

    # Shut down the Raspberry Pi
    LOGGER.info("Shutting down the Raspberry Pi")
    unitmanager.schedule_unit_turnoff()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.warning("Program terminated by user")
        exit()
