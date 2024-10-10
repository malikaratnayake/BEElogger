
import time
import os
import logging
from datetime import datetime
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from libcamera import Transform
import socketserver
from threading import Condition
from http import server
import io

logger = logging.getLogger()

class VideoRecorder:

    def __init__(self,
                 video_duration: int,
                 video_resolution: tuple,   
                 video_fps: int,
                 video_container: str,
                 video_codec: str,
                 video_sampling_interval: int,
                 recording_start_time: str,
                 recording_end_time: str,
                 directory_info,
                 video_file_logger
                 ) -> None:
        
        self.video_duration = video_duration
        self.video_resolution = video_resolution
        self.video_fps = video_fps
        self.video_container = video_container
        self.video_codec = video_codec
        self.recording_start_time = recording_start_time
        self.recording_end_time = recording_end_time
        self.video_sampling_interval = video_sampling_interval
        self.directory_info = directory_info
        self.video_file_logger = video_file_logger
        # self.record_to_log()
        self.video_file_list = self.video_file_logger.create_video_list_file()
        self.set_recording_status(False)

        logger.info('Camera initialised with following parameters: ')
        logger.info('Video duration: ' + str(self.video_duration))
        logger.info('Video resolution: ' + str(self.video_resolution))
        logger.info('Video fps: ' + str(self.video_fps))
        logger.info('Video codec: ' + str(self.video_codec))
        logger.info('Video container: ' + str(self.video_container))
        logger.info('Video directory: ' + str(self.directory_info.get_video_folder()))
        logger.info('Recording start time: ' + str(self.recording_start_time))
        logger.info('Recording end time: ' + str(self.recording_end_time))
        logger.info('Video sampling interval: ' + str(self.video_sampling_interval))


    def set_recording_status(self, _status):
        self.recording_status = _status

    def get_recording_status(self):
        return self.recording_status


    def generate_video_name(self):
        time_string = time.strftime("%H%M%S", time.localtime())
        name_prefix = self.directory_info.get_filename_prefix()

        video_filename = name_prefix + '_' + time_string + '.' + self.video_container
        
        return self.directory_info.get_video_folder() + video_filename



    def record_video(self):
        if self.assess_recording_schedule() is True:
 
            duration = self.video_duration*1000
            video_filename = self.generate_video_name()
            video_file_list = self.video_file_list

            self.video_file_logger.add_video_to_list(video_file_list, video_filename)
            logger.info('Started Video recording: ' + video_filename)
            # unit_display.video_recording_led(recording = True)

            os.system("libcamera-vid -v 0 -n --vflip --hflip -t {} --framerate {} --width {} --height {} --codec {} -o {}".format(duration, 
                                                                                                            self.video_fps, 
                                                                                                            self.video_resolution[0], 
                                                                                                            self.video_resolution[1], 
                                                                                                            self.video_codec, 
                                                                                                            video_filename))
            logger.info('Video saved to ' + video_filename)
            time.sleep(2)
            self.recording_status = False

            return video_filename

        else:

            return None
        


    def schedule_video_recording(self, video_end_time, current_status):
        if video_end_time is None:
            return current_status
        else:
            if time.time() > video_end_time + self.video_sampling_interval:
                return True
            else:
                return False


    def process_camera_mode(self, camara_mode, camera, streamer):
        if camara_mode == 'stream':
            camera.set_recording_status(False)
            streamer.set_streaming_status(True)
        else:
            camera.set_recording_status(True)

    def assess_recording_schedule(self):
        if (datetime.fromtimestamp(time.time()).strftime("%H:%M:%S") >= self.recording_start_time) and (datetime.fromtimestamp(time.time()).strftime("%H:%M:%S") < self.recording_end_time):
            logger.info('Current time is within recoring time.')
            return True
        else:
            logger.info('Current time is NOT within recording schedule. Sleeping camera for ' + str(self.video_duration) + ' seconds.')
            time.sleep(self.video_duration)
            return False

class VideoProcessor:

    def __init__(self, 
                 video_fps: int,
                 directory_info
                 ) -> None: 
        
        self.video_fps = video_fps
        self.directory_info = directory_info
        
    def convert_to_mp4(self, video_filename):
        # Extract the video filename before extension
        input_video_filename = video_filename.split('.')[0]

        #add mp4 as extnsion for the output video filename
        output_video_filename = input_video_filename + '.mp4'

        os.system("ffmpeg -framerate {} -i {} -c copy {}".format(self.video_fps, video_filename, output_video_filename))

        return output_video_filename

    def run_EcomotionZip(self, video_directory):
        output_directory = self.directory_info.get_video_folder()
    
        home_directory = os.path.expanduser("~")
        ecomotionzip_path = os.path.join(home_directory, "EcoMotionZip", "EcoMotionZip", "app.py")

        logger.info("Compressing video files")
        os.system("/home/pi-cam43/pi-dev/bin/python {} --video_source {} --output_directory {}".format(ecomotionzip_path, video_directory, output_directory))
        logger.info("Video files compressed successfully. Output directory is: " + output_directory)

        return None
    
    def delete_video(self, video_name):
        """Deletes a file from the source directory when a file name is provided.

        Args:
            file_name: The name of the file to delete.
        """

        if os.path.isfile(video_name):
            os.remove(video_name)
            logger.info("File deleted from source directory: " + video_name)
        else:
            raise FileNotFoundError(f"File not found: {video_name}")
        
        return None
    

'''Methods and functions for the camera streaming functionality'''


PAGE = """\
<html>
<head>
<title>NatBeeSense Hive Monitoring Preview </title>
<meta http-equiv="refresh" content="10">  <!-- Auto-refresh the page every 1 second -->
</head>
<body>
<h1>NatBeeSense Hive Monitoring Preview</h1>
<button onclick="window.open('/stream.mjpg')">Open Stream in a separate tab</button>
<br></br>

<img src="stream.mjpg" width="640" height="360" />

</body>
</html>
"""


class StreamingOutput(io.BufferedIOBase):
    def __init__(self, condition):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = condition

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with condition:
                        condition.wait()
                        frame = stream.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


condition = Condition()
stream = StreamingOutput(condition=condition)
output = FileOutput(file=stream)

class VideoStreamer:

    def __init__(self,
                 video_resolution: tuple,
                 streaming_duration: int,
                 pisensor) -> None:
        
        self.video_resolution = video_resolution
        self.streaming_duration = streaming_duration
        self.server = None
        self.stream_camera = None
        self.stream_encoder = None
        self.streaming_status = False
        self.piSensor = pisensor
        self.ip_address = self.piSensor.get_ip_address('wlan0')
        self.port = 7000

    def set_streaming_status(self, status):
        self.streaming_status = status

    def get_streaming_status(self):
        return self.streaming_status
    

    def setup_server(self):
        _server = StreamingServer(('', self.port), StreamingHandler)

        return _server

    def setup_camera(self):

        _camera = Picamera2()
        video_config = _camera.create_video_configuration(main={"size": self.video_resolution}, transform=Transform(vflip=True, hflip =True))
        _camera.configure(video_config)

        return _camera
    
    def setup_encoder(self):
        _encoder = JpegEncoder()

        return _encoder

    def start_streaming(self):
        if self.server is None:
            self.server = self.setup_server()
            
        self.stream_camera = self.setup_camera()
        self.stream_encoder = self.setup_encoder()

        try:
            self.stream_camera.start_recording(self.stream_encoder, output)
            self.server.serve_forever()

        except:
            self.stream_camera.stop_recording()
            self.server.shutdown()
            
    def stop_streaming(self):
        
        self.set_streaming_status(False)
        self.stream_camera.stop_recording()
        self.stream_camera.stop()
        self.stream_camera.close()
        
        self.server.shutdown()
        

        return None
    
    def get_streaming_duration(self):
        return self.streaming_duration



        


        
    






        

    

        