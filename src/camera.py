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

# Initialize the logger
logger = logging.getLogger()

class VideoRecorder:
    """
    Class to handle video recording functionality.
    """

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
        """
        Initialize the VideoRecorder with the given parameters.
        """
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
        self.video_file_list = self.video_file_logger.create_video_list_file()
        self.set_recording_status(False)

        # Log the initialization parameters
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
        """
        Set the recording status.
        """
        self.recording_status = _status

    def get_recording_status(self):
        """
        Get the current recording status.
        """
        return self.recording_status

    def generate_video_name(self):
        """
        Generate a unique video filename based on the current time and directory info.
        """
        time_string = time.strftime("%H%M%S", time.localtime())
        name_prefix = self.directory_info.get_filename_prefix()
        video_filename = name_prefix + '_' + time_string + '.' + self.video_container
        return self.directory_info.get_video_folder() + video_filename

    def record_video(self):
        """
        Record a video if the current time is within the recording schedule.
        """
        if self.assess_recording_schedule() is True:
            duration = self.video_duration * 1000
            video_filename = self.generate_video_name()
            video_file_list = self.video_file_list

            # Log the video recording start
            self.video_file_logger.add_video_to_list(video_file_list, video_filename)
            logger.info('Started Video recording: ' + video_filename)

            # Execute the video recording command
            os.system("libcamera-vid -v 0 -n --vflip --hflip -t {} --framerate {} --width {} --height {} --codec {} -o {}".format(
                duration, self.video_fps, self.video_resolution[0], self.video_resolution[1], self.video_codec, video_filename))

            # Log the video recording end
            logger.info('Video saved to ' + video_filename)
            time.sleep(2)
            self.recording_status = False

            return video_filename
        else:
            return None

    def schedule_video_recording(self, video_end_time, current_status):
        """
        Schedule the next video recording based on the end time and sampling interval.
        """
        if video_end_time is None:
            return current_status
        else:
            if time.time() > video_end_time + self.video_sampling_interval:
                return True
            else:
                return False

    def process_camera_mode(self, camara_mode, camera, streamer):
        """
        Process the camera mode to switch between streaming and recording.
        """
        if camara_mode == 'stream':
            camera.set_recording_status(False)
            streamer.set_streaming_status(True)
        else:
            camera.set_recording_status(True)

    def assess_recording_schedule(self):
        """
        Assess if the current time is within the recording schedule.
        """
        current_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S")
        if self.recording_start_time <= current_time < self.recording_end_time:
            logger.info('Current time is within recording time.')
            return True
        else:
            logger.info('Current time is NOT within recording schedule. Sleeping camera for ' + str(self.video_duration) + ' seconds.')
            time.sleep(self.video_duration)
            return False

class VideoProcessor:
    """
    Class to handle video processing tasks such as conversion and compression.
    """

    def __init__(self, 
                 video_fps: int,
                 EcoMotionZip_path: str,
                 python_interpreter_path: str,
                 delete_original: bool,
                 directory_info
                 ) -> None: 
        """
        Initialize the VideoProcessor with the given parameters.
        """
        self.video_fps = video_fps
        self.directory_info = directory_info
        self.EcoMotionZip = f"{EcoMotionZip_path}EcoMotionZip/app.py"
        self.python_interpreter = f"{python_interpreter_path}bin/python"
        self.delete_original = delete_original
        
    def convert_to_mp4(self, video_filename):
        """
        Convert the given video file to MP4 format.
        """
        input_video_filename = video_filename.split('.')[0]
        output_video_filename = input_video_filename + '.mp4'

        # Execute the conversion command
        os.system("ffmpeg -framerate {} -i {} -c copy {}".format(self.video_fps, video_filename, output_video_filename))

        return output_video_filename

    def run_EcomotionZip(self, video_directory, upload_to_aws):
        """
        Compress video files using the EcoMotionZip tool.
        """
        video_base_name = os.path.basename(video_directory)[:-4] # Get the base name of the video directory: ../dagh/hdsgah/68675.mp4 to 68675.mp4
        output_directory = self.directory_info.get_video_folder()
        compressed_file_name = f"{output_directory}/EcoMotionZip/{video_base_name}/{video_base_name}.avi"

        # home_directory = os.path.expanduser("~")
        # os.path.join(home_directory, "EcoMotionZip", "EcoMotionZip", "app.py")

        logger.info("Compressing video files")
        try:
            os.system("{} {} --video_source {} --output_directory {} --delete_original {}".format(self.python_interpreter, self.EcoMotionZip, video_directory, output_directory, self.delete_original))
            logger.info("Video files compressed successfully. Output file is: " + compressed_file_name)


            # Upload the processed video files to AWS S3 bucket
            if upload_to_aws is True:
                self.upload_to_aws(compressed_file_name)

        except Exception as e:
            logger.warning("Error compressing video files: " + str(e))

        return None

    
    def delete_video(self, video_name):
        """
        Delete the specified video file from the source directory.
        """
        if os.path.isfile(video_name):
            os.remove(video_name)
            logger.info("File deleted from source directory: " + video_name)
        else:
            raise FileNotFoundError(f"File not found: {video_name}")
        
        return None
    
    def read_dotenv(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            self.aws_bucket_name = os.getenv("AWS_BUCKET_NAME")
            self.aws_region = os.getenv("AWS_DEFAULT_REGION")
        except Exception as e:
            logger.warning("Error reading .env file: " + str(e))
            self.aws_access_key_id = None
            self.aws_secret_access_key = None
            self.aws_bucket_name = None
            self.aws_region = None

    
    def upload_to_aws(self, compressed_file_name):
        """
        Upload the video file to AWS S3 bucket.
        """

        self.read_dotenv()
        if self.aws_access_key_id is None:
            logger.warning("AWS credentials not found. Skipping upload to AWS S3 bucket.")
            return None
        else:
            try:
                import boto3
                logger.info("Uploading video to AWS S3 bucket")
                s3 = boto3.client('s3', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.aws_region)
                s3.upload_file(compressed_file_name, self.aws_bucket_name, "uploads/"+compressed_file_name.split('/')[-1])
                logger.info("Video uploaded to AWS S3 bucket: " + compressed_file_name)
            except Exception as e:
                logger.warning("Error uploading video to AWS S3 bucket: " + str(e))
            
            return None

# HTML page for the camera streaming functionality
PAGE = """\
<html>
<head>
<title>NatBeeSense Hive Monitoring Preview </title>
<meta http-equiv="refresh" content="10">  <!-- Auto-refresh the page every 10 seconds -->
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
    """
    Class to handle the streaming output.
    """

    def __init__(self, condition):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = condition

    def write(self, buf):
        """
        Write the buffer to the streaming output.
        """
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    """
    HTTP request handler for streaming.
    """

    def do_GET(self):
        """
        Handle GET requests for streaming.
        """
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
    """
    HTTP server for streaming with threading support.
    """
    allow_reuse_address = True
    daemon_threads = True

# Condition object for thread synchronization
condition = Condition()
# Streaming output object
stream = StreamingOutput(condition=condition)
# File output object for the stream
output = FileOutput(file=stream)

class VideoStreamer:
    """
    Class to handle video streaming functionality.
    """

    def __init__(self,
                 video_resolution: tuple,
                 streaming_duration: int,
                 pisensor) -> None:
        """
        Initialize the VideoStreamer with the given parameters.
        """
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
        """
        Set the streaming status.
        """
        self.streaming_status = status

    def get_streaming_status(self):
        """
        Get the current streaming status.
        """
        return self.streaming_status

    def setup_server(self):
        """
        Setup the streaming server.
        """
        _server = StreamingServer(('', self.port), StreamingHandler)
        return _server

    def setup_camera(self):
        """
        Setup the camera for streaming.
        """
        _camera = Picamera2()
        video_config = _camera.create_video_configuration(main={"size": self.video_resolution}, transform=Transform(vflip=True, hflip=True))
        _camera.configure(video_config)
        return _camera
    
    def setup_encoder(self):
        """
        Setup the encoder for streaming.
        """
        _encoder = JpegEncoder()
        return _encoder

    def start_streaming(self):
        """
        Start the video streaming.
        """
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
        """
        Stop the video streaming.
        """
        self.set_streaming_status(False)
        self.stream_camera.stop_recording()
        self.stream_camera.stop()
        self.stream_camera.close()
        self.server.shutdown()
        
        return None
    
    def get_streaming_duration(self):
        """
        Get the streaming duration.
        """
        return self.streaming_duration