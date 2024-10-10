import json
from pathlib import Path
import logging



class JsonReader:

    json_file = None

    def __init__(self):
        current_directory = Path(__file__).parent
        self.json_file = str(current_directory) + '/config.json'
        logging.info("JsonReader initialised")

    def read_json_parameters(self, parameters):
        """
        Reads the value of a list of parameters from a JSON file.

        Args:
            json_file: The path to the JSON file.
            parameter: The list of the parameters to read.

        Returns:
            The value of the parameter.
        """

        with open(self.json_file, 'r') as f:
            data = json.load(f)

        results = []
        for parameter in parameters:
            results.append(data[parameter])

        return results
    
    def read_json_parameter(self, parameter):
        """
        Reads the value of a specific parameter from a JSON file.

        Args:
            json_file: The path to the JSON file.
            parameter: The name of the parameter to read.

        Returns:
            The value of the parameter.
        """

        with open(self.json_file, 'r') as f:
            data = json.load(f)

        result = data[parameter]

        return result
    
    # def update_json_value(self, parameter, new_value):
    #     """
    #     Updates the value of a specific parameter in a JSON file.

    #     Args:
    #     json_file: The path to the JSON file.
    #     parameter: The name of the parameter to update.
    #     new_value: The new value for the parameter.
    #     """

    #     with open(self.json_file, 'r') as f:
    #         data = json.load(f)

    #     data[parameter] = new_value

    #     with open(self.json_file, 'w') as f:
    #         json.dump(data, f, indent=4)
    
class JsonWriter:

    json_file = None

    def __init__(self):
        current_directory = Path(__file__).parent
        self.json_file = str(current_directory) + '/config.json'
        logging.info("JsonWriter initialised")

    def update_json_value(self, parameter, new_value):
        """
        Updates the value of a specific parameter in a JSON file.

        Args:
        json_file: The path to the JSON file.
        parameter: The name of the parameter to update.
        new_value: The new value for the parameter.
        """

        with open(self.json_file, 'r') as f:
            data = json.load(f)

        data[parameter] = new_value

        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=4)

class JsonHandler(JsonReader, JsonWriter):

    def __init__(self):
        super().__init__()
        logging.info("JsonHandler initialised")


# class PiManager:
#     def __init__(self):
#         pass

#     # Write a method to shutdown the raspberry pi
#     def shutdown_pi(self):
#         logging.info("User initiated shut down of the raspberry pi")
#         os.system("sudo shutdown -h now")

#         return None
    
#     def restart_pi(self):
#         logging.info("User initiated restart of the raspberry pi")
#         os.system("sudo reboot")

#         return None
    

# """Transfer files from this Raspberry Pi to the server at pi-server@10.42.0.1 at 8:00 PM everyday.
# After the transfer process is completed, delete transferred file from the directory."""
# class FileTransfer:

#     filepath = None
#     destination_path = '/home/pi-server/Desktop/transfered_files'
#     # server_ip = 10.42.0.1
#     server_hostname = 'pi-server'

#     def __init__(self):
#         pass

#     def transfer_file(self, file_path, destination_path):
#         logging.info("Transferring file from {} to {}".format(file_path, destination_path))
#         os.system("scp {} {}".format(file_path, destination_path))

#         return None


# class DisplayWarnings:
#     def __init__(self):
#         pass

#     def display_warning(self, warning):
#         sense = SenseHat()
#         sense.show_message(warning, text_colour=[255, 0, 0])
#         logging.info("Warning displayed on the LED matrix")
#         sense.clear()

#         return None




