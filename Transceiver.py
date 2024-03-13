import time
from Utilities import JsonReader
import logging
from PiicoDev_Transceiver import PiicoDev_Transceiver
from PiicoDev_Unified import sleep_ms
from Displays import LEDs
from Sensors import Sensors

jsonreader = JsonReader()
group_no = jsonreader.read_json_parameter('transmission_group')
this_radio_address = jsonreader.read_json_parameter('this_radio_address')
reciever_address = jsonreader.read_json_parameter('reciever_address')
radio = PiicoDev_Transceiver(group=group_no, radio_address=this_radio_address)
display = LEDs()
sensors = Sensors()
LOGGER = logging.getLogger()


    

class Transmitter:

    def __init__(self):
        self.originating_device_code = 'M'
        self.camera_code = 'C'
        self.station_code = 'S'
        self.battery_code = 'B'
        self.motor_code = 'M'
        self.docking_code = 'D'
    

    def compile_message(self, _originating_device, _message_type, _message):
        message = str(_originating_device) + str(_message_type) + str(_message)
        return message
    
    def compile_recording_message(self, recording):
        if recording is True:
            recording_status = str(1)
        else:
            recording_status = str(0)

        message = self.compile_message(self.originating_device_code, self.camera_code, recording_status)

        return message
    
    def compile_station_info_message(self, station):
        message = self.compile_message(self.originating_device_code, self.station_code, station)
        return message
    
    def compile_station_detection_message(self, station_detection_status):
        if station_detection_status is True:
            motor_instruction = str(0)
        else:
            motor_instruction = str(1)
    
        message = self.compile_message(self.originating_device_code, self.motor_code, motor_instruction)
        return message
    
    def compile_docking_request_message(self):
        message = self.compile_message(self.originating_device_code, self.docking_code, '1')
        return message
    


    def compile_battery_info_message(self, battery_level):
        message = self.compile_message(self.originating_device_code, self.battery_code, battery_level)
        return message
    
    def transmit_message(self, message):
        display.communication_indication_led(True)

        try:
            radio.send(message, address= reciever_address)
            LOGGER.info(f"Message Sent: {message}")
            time.sleep(1)
        except:
            LOGGER.error(f"Message not sent: {message}")

        display.communication_indication_led(False)

        return None
    
    def send_connection_verification(self):
        display.communication_indication_led(True)
        message = self.compile_message(self.originating_device_code, 'V', '1')
        self.transmit_message(message)
        display.communication_indication_led(False)

        return None
    


    

class Reciever:
    def __init__(self):
        self.base_unit_code = 'B'
        self.camera_code = 'C'
        self.motor_code = 'M'
        self.station_code = 'S'
        self.battery_code = 'B'
        self.verification_code = 'V'

    def _verify_message(self, _message):
        if len(_message) == 3:
            return True
        else:
            return False
        
    def check_connection_message(self, message):
        display.communication_indication_led(True)
        verified = False
        try:
            originating_device = message[0]
            message_type = message[1]
            message = message[2]

            if originating_device == self.base_unit_code:
                if message_type == self.verification_code:
                    if message == '1':
                        verified = True
                        LOGGER.debug("Connection Verification Message Recieved.")

                    else:
                        pass

                else:
                    pass

            else:
                pass

        except:
            pass
            
        display.communication_indication_led(False)

        return verified


    def listen_to_radio(self):

        try:
            if radio.receive():
                message = radio.message
                try:
                    verification =  self._verify_message(message)
                except:
                    verification = False

            else:
                message = None
                verification = False
        except:
            message = None
            verification = False

        return verification, message

    def process_message(self, message):
        recording = False 
        motor_direction = None     
        try:
            originating_device = message[0]
            message_type = message[1]
            message_details = message[2]

            if originating_device == self.base_unit_code:
                if message_type == self.camera_code:
                    if message_details == '1':
                        recording = True
                        LOGGER.debug("Message recieved: Recording True")
                        

                    elif message_details == '0':
                        recording = False
                        LOGGER.debug("Message recieved: Recording False")

                    else:
                        LOGGER.error("Message not recognised")

                elif message_type == self.motor_code:
                    print(message)
                    if message_details == 'F':
                        motor_direction = 'forward'
                        LOGGER.debug("Message recieved: Motor Direction: Forward")
                    elif message_details == 'B':
                        motor_direction = 'backward'
                        LOGGER.debug("Message recieved: Motor Direction: Backwards")
                    else:
                        LOGGER.error("Message not recognised")

            else:
                LOGGER.error("Message not recognised")

        except:
            LOGGER.error("Message not recognised")


        return recording, motor_direction
            
        
        









