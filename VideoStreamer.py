from picamera2.encoders import MJPEGEncoder
from picamera2 import Picamera2
from picamera2.outputs import FileOutput, FfmpegOutput, Output
import time
import io
import logging
import socketserver
from threading import Condition
from http import server
from Sensors import PiSensor
from Utilities import JsonHandler

piSensor= PiSensor()
jsonreader = JsonHandler()

cam_res  = (1920, 1080)


PAGE = """\
<html>
<head>
<title>Monitoring Unit {cam_number} Preview </title>
<meta http-equiv="refresh" content="10">  <!-- Auto-refresh the page every 1 second -->
</head>
<body>
<h1>Monitoring Unit {cam_number} Preview </h1>
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

    cam_number = jsonreader.read_json_parameter('cam_number')

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.format(cam_number=self.cam_number).encode('utf-8')
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

class CameraStream:

    server = None
    stream_camera = None
    stream_encoder = None
    streaming_status = False
    ip_address = piSensor.get_ip_address('wlan0')
    port = 7000
    camera_resolutions = jsonreader.read_json_parameter('video_resolution')

    def set_streaming_status(self, status):
        self.streaming_status = status

    def get_streaming_status(self):
        return self.streaming_status
    

    def setup_server(self):
        _server = StreamingServer(('', self.port), StreamingHandler)

        return _server

    def setup_camera(self):

        _camera = Picamera2()
        video_config = _camera.create_video_configuration(main={"size": cam_res})
        _camera.configure(video_config)

        return _camera
    
    def setup_encoder(self):
        _encoder = MJPEGEncoder(bitrate=10000000)

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








    #     self.server = StreamingServer(address, StreamingHandler)
    #     picam2 = Picamera2()
    #     video_config = picam2.create_video_configuration(main={"size": cam_res})
    #     picam2.configure(video_config)
    #     encoder = MJPEGEncoder(bitrate=1000000)

    #     condition = Condition()

    #     stream = StreamingOutput(condition=condition)
    #     output = FileOutput(file=stream)

    
    #     return None


    # def start_streaming_server(self):
        



    #     self.server.serve_forever()


    # # picam2 = Picamera2()
    # # video_config = picam2.create_video_configuration(main={"size": cam_res})
    # # picam2.configure(video_config)
    # # encoder = MJPEGEncoder(bitrate=10000000)

    # # This condition is used so we know when exactly a full frame has been
    # # written to the buffer
    # condition = Condition()
    # # `stream` is where we actually retrieve the frames from, it's a wrapper
    # # for a BytesIO
    # stream = StreamingOutput(condition=condition)
    # output = FileOutput(file=stream)

    # picam2.start_recording(encoder, output)
    # try:
    #     address = ('', 7000)
    #     server = StreamingServer(address, StreamingHandler)
    #     server.serve_forever()
    # finally:
    #     picam2.stop_recording()