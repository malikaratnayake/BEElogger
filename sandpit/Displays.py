from PiicoDev_RGB import PiicoDev_RGB
# from PiicoDev_SSD1306 import *
import time
from Utilities import JsonReader
import logging
from datetime import datetime, timedelta

# display = create_PiicoDev_SSD1306()
leds = PiicoDev_RGB()
jsonreader = JsonReader()
logger = logging.getLogger()


class LEDs:
    red = [255,0,0]
    green =[0,255,0]
    blue = [0,0,255]
    white = [255,255,255]
    amber = [225,165,0]
    purple = [128,0,128]
    cyan = [0,255,255]
    wait_time = 2

    off = [0,0,0]

    def __init__(self):
        leds.setBrightness(jsonreader.read_json_parameter('brightness'))
    

    def video_recording_led(self, recording = True):

        try:
            if recording is True:
                leds.setPixel(0, self.red); leds.show()
            else:
                leds.setPixel(0, self.off); leds.show()
        except:
            logger.error("Error setting the video recording LED")

        return None
    
    def motor_motion_status_led(self, recording = True):

        try:
            if recording is True:
                leds.setPixel(0, self.amber); leds.show()
            else:
                leds.setPixel(0, self.off); leds.show()
        except:
            logger.error("Error setting the motor motion LED")

        return None
    
    def data_logging_led(self, logging = True):
        try:
            if logging is True:
                leds.setPixel(1, self.green); leds.show()
            else:
                leds.setPixel(1, self.off); leds.show()
        except:
            logger.error("Error setting the data logging LED")

        return None
    
    def streaming_led(self, movement = True):
        try:
            if movement is True:
                leds.setPixel(1, self.blue); leds.show()
            else:
                leds.setPixel(2, self.off); leds.show()
        except:
            logger.error("Error setting the streaming indication LED")
            
        return None
    
    def transferring_led(self, transferring = True):
        try:
            if transferring is True:
                leds.setPixel(0, self.purple); leds.show()
            else:
                leds.setPixel(0, self.off); leds.show()
        except:
            logger.error("Error setting the transferring indication LED")
            
        return None

    def communication_indication_led(self, communication = True):

        try:
            if communication is True:
                # print("Communication indication LED ON")
                leds.setPixel(1, self.white)
                leds.show()
            else:
                leds.setPixel(1, self.off)
                leds.show()
                # print("Communication indication LED off")
        except:
            logger.error("Error setting the communication indication LED")
            
        return None
    
    def enter_menu_led(self):
        try:
            leds.setPixel(0, self.red)
            leds.setPixel(1, self.blue)
            leds.setPixel(2, self.green)
            leds.show()
        except:
            logger.error("Error setting the enter menu LED")
            
        return None
    
    def confirm_selection(self, option):
        try:
            if option == 1:
                leds.setPixel(0, self.red)
                leds.setPixel(1, self.red)
                leds.setPixel(2, self.red)
            elif option == 2:
                leds.setPixel(0, self.blue)
                leds.setPixel(1, self.blue)
                leds.setPixel(2, self.blue)
            elif option == 3:
                leds.setPixel(0, self.green)
                leds.setPixel(1, self.green)
                leds.setPixel(2, self.green)
            elif option == 4:
                leds.setPixel(0, self.purple)
                leds.setPixel(1, self.purple)
                leds.setPixel(2, self.purple)
            elif option == 5:
                leds.setPixel(0, self.amber)
                leds.setPixel(1, self.amber)
                leds.setPixel(2, self.amber)
            elif option == 6:
                leds.setPixel(0, self.cyan)
                leds.setPixel(1, self.cyan)
                leds.setPixel(2, self.cyan)
        
            else:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.off)

            leds.show()
            time.sleep(self.wait_time)
            leds.clear()

        except:
            logger.error("Error setting the confirm selection LED")
    
    def menu_option_display(self, option = 0):
        try:
            if option == 0:
                leds.setPixel(0, self.red)
                leds.setPixel(1, self.green)
                leds.setPixel(2, self.blue)
            elif option == 1:
                leds.setPixel(0, self.red)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.off)
            elif option == 2:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.blue)
                leds.setPixel(2, self.off)
            elif option == 3:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.green)
            elif option == 4:
                leds.setPixel(0, self.purple)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.off)
            elif option == 5:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.amber)
                leds.setPixel(2, self.off)
            elif option == 6:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.cyan)
        
            else:
                leds.setPixel(0, self.off)
                leds.setPixel(1, self.off)
                leds.setPixel(2, self.off)

            leds.show()

        except:
            logger.error("Error setting the menu option LED")
            
        return None
        
    def clear_leds(self):

        try:
            leds.clear()
        except:
            logger.error("Error clearing the LEDs")

        return None


class OLEDDisplay:
    line1 = 0
    line2 = 17
    line3 = 34
    line_gap = 17
    colour = 1
    column = 0
    lines = [0,17,34]

    def __init__(self):
        return None
    
    # def update_display_messages(self, messages):

    #     try:
    #         display.fill(0)
    #         print(messages, self.lines)
    #         for message in messages:
    #             line = self.lines[messages.index(message)]
    #             message = str(message)
    #             display.text(message, self.column, line, self.colour)
    #             print(message, self.column, line, self.colour)
    #         # else:
    #         #     message = str(messages)
    #         #     display.text(message, self.column, line, self.colour)

    #         display.show()
    #     except Exception as e:
    #         logger.error("Error updating display messages: " + str(e))

    #     return None

    def show_messages(self, messages):
        display.fill(0)
        if isinstance(messages, list):
            line = 0
            for message in messages:
                message = str(message)
                display.text(message, 0, line, 1)
                line += 17
        else:
            message = str(messages)
            display.text(message, 0, line, 1)

        display.show()

        return None

    def clear_oled_display(self):
        display.fill(0)
        display.show()
        return None
    
    # def clear_display(self, first_line=0, no_of_lines=5):
    #     try:
    #         display.fill_rect(0, first_line, 128, no_of_lines * 17, 0)
    #         display.show()
    #     except Exception as e:
    #         logger.error("Error clearing the display: " + str(e))

    #     return None
    

# OLEDDisplay().show_messages(["Hello World", "Mammmmlika", "Nisal", "Malika", "Nisal"])

class Displays(LEDs):
    current_oled_message = ["","","",""]
    def __init__(self):
        LEDs.__init__(self)
        # OLEDDisplay.__init__(self)
        # self.display = display

        return None
    
    def clear_all_displays(self):
        try:
            self.clear_leds()
            # self.clear_display()
        except Exception as e:
            logger.error("Error clearing LEDs and display: " + str(e))

        return None
    
    # def update_pi_info_display(self, pi_data):

    #     _cpu_temp = pi_data["cpu_temp"]
    #     _free_space = pi_data["free_space"]
    #     _total_space = pi_data["total_space"]
    #     _free_space_percentage = round(((_total_space -_free_space) / _total_space) * 100)

    #     self.current_oled_message[0]  = "Temp: " + str(_cpu_temp) + "C"
    #     self.current_oled_message[1]  = "Disk: " + str(_free_space_percentage) + "%"

    #     return None
    

    # def show_video_recording_start(self, video_duration, end_time, test=False):
    #     self.video_recording_led(True)
    #     if test is True:
    #         self.current_oled_message[0]= "Test Recording"
    #     else:
    #         self.current_oled_message[0]= "Recording"

    #     self.current_oled_message[1]= "Duration: " + str(video_duration/1000)
    #     self.current_oled_message[2]= "End: " + str(end_time)

    #     self.show_messages(self.current_oled_message)
    
    #     return None
    
    # def video_recording_end(self):
    #     self.video_recording_led(False)
    #     self.clear_oled_display()
    
    #     return None
    
    def show_video_recording(self, video_duration= None, end_time = None, recording =True ,testing=False, oled = False):
        if recording is True:
            self.video_recording_led(True)
            if oled is True:
                if testing is True:
                    pass
                else:
                    self.clear_oled_display()
                    self.current_oled_message[0]= "Recording"
                    self.current_oled_message[1]= "Duration: " + str(video_duration/1000)
                    self.current_oled_message[2]= "End: " + str(end_time)
                    self.show_messages(self.current_oled_message)
            else:
                pass
        else:
            self.video_recording_led(False)
            if oled is True:
                self.clear_oled_display()
            # self.clear_oled_display()

        return None
    


    
    def show_streaming_info(self, ip_address, port, oled = False):
        if ip_address is None or port is None:
            self.streaming_led(False)
            if oled is True:
                self.clear_oled_display()
        else:
            self.streaming_led(True)
            if oled is True:
                self.current_oled_message[0]= "Streaming"
                self.current_oled_message[1]= "IP: " + str(ip_address)
                self.current_oled_message[2]= "Port: " + str(port)
                self.show_messages(self.current_oled_message)

        return None
            
    

    def show_data_transfer(self, transferring = True, testing = False, oled = False):
        if transferring is True:
            self.transferring_led(True)
            if oled is True:
                if testing is True:
                    pass
                else:
                    self.clear_oled_display()
                    self.current_oled_message[0]= "Transferring"
                    self.show_messages(self.current_oled_message)
        else:
            self.transferring_led(False)
            if oled is True:
                self.clear_oled_display()
        
        return None
    

    def show_testing(self, testing = True, oled = False):
        if oled is True:
            if testing is True:
                self.current_oled_message[0]= "Testing"
                self.show_messages(self.current_oled_message)
            else:
                self.clear_oled_display()
        
        return None
    
    def show_scheduled_shutdown(self, time, oled = False):
        if oled is True:
            self.current_oled_message[0]= "Scheduled Shutdown"
            self.current_oled_message[1]= "Turn On: " + str(time)
            self.show_messages(self.current_oled_message)
        
        return None
    
    def show_restart_message(self, oled = False):
        if oled is True:
            self.clear_oled_display()
            self.current_oled_message[0]= "Restarting"
            self.show_messages(self.current_oled_message)
        
        return None
    
    
    # def show_video_recording_end(self):
        
    #     self.current_oled_message[2]= "" 
    #     self.current_oled_message[3]= ""
    #     self.update_display_messages(self.current_oled_message)
    #     self.video_recording_led(False)
    
    #     return None
    
 
