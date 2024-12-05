# BEElogger
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)

**B**eehive **E**ntrance and **E**nvironment Logger *(BEElogger)* is a Raspberry Pi-based system designed for recording video and micro-climatic data at the entrance of a beehive. The BEElogger system is specifically tailored for monitoring stingless bees and assisting beekeepers in observing the activity and environmental conditions of their beehives. By utilising a Raspberry Pi, the system captures video footage and collects data on temperature, humidity, pressure, and light intensity, all of which are relevant to bee activity. This information can be used to analyse the health and behaviour of the bee colony, detect potential issues early, and make informed decisions to improve hive management.

### Features

- High-definition video recording of beehive entrance activity.
- Real-time monitoring of temperature, humidity, pressure, and light intensity.
- Data logging for historical analysis.
- Easy setup and configuration with a Raspberry Pi.
- Open-source software for customisation and extension.
- Support for EcoMotionZip software for video compression to optimise storage resources on the Raspberry Pi.
- Automatic processing of recorded videos using BEETrack software, which leverages AI and deep learning to analyse bee activity.

## Methodology

The BEElogger uses a Raspberry Pi 4-based system to record video and microclimatic data. The system consists of the following components:

- [**Raspberry Pi 4 Model B**](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/): The main processing unit that runs the BEElogger software.
- [**Raspberry Pi Camera Module v2**](https://www.raspberrypi.com/products/camera-module-v2/): A high-definition camera connected to the Raspberry Pi for recording video at the beehive entrance.
- [**Adafruit HTS221**](https://www.adafruit.com/product/4535): Measures the temperature, humidity and pressure levels at the beehive entrance.
- [**Adafruit TSL2591**](https://www.adafruit.com/product/1980): Captures data on the light conditions around the beehive.
- **MicroSD Card**: Used for storing the operating system, software, and recorded data.
- [**Power Supply**](https://www.raspberrypi.com/products/type-c-power-supply/): Provides power to the Raspberry Pi and connected components.
- **Enclosure**: Protects the Raspberry Pi and sensors from environmental elements.

The data collection methodology of the BEElogger system leverages Python's multi-threading capabilities to perform parallel tasks simultaneously. An overview of the data collection pipeline is shown in Figure 1. The BEElogger uses EcoMotionZip software to compress recorded videos before storage, optimising the limited storage capacity of the Raspberry Pi. Users can choose to disable video compression if desired. Additionally, users can customise data sampling durations and intervals, specifying how long videos should be recorded at each interval. They can also set the video sampling hours to capture periods of peak activity. Microclimatic data is collected continuously, 24 hours a day, regardless of the specified video recording durations.

![Overview of the BEElogger Data Collection Pipeline](./docs/figures/BEELogger.jpg)
*Figure 1: Overview of the BEElogger Data Collection Pipeline*

## Installation and Setup

### Prerequisites

Before installing the BEElogger system, ensure you have the following prerequisites:

- A Raspberry Pi 4 Model B with Raspbian OS installed. Use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to install the Raspbian OS. It is recommended to use the 64-bit lite version of the latest software. Configure the following settings under OS Customisation:
    - **Hostname**: `BEElogger`
    - **Username**: `beelogger`
    - **Wireless LAN Configuration**: Add the SSID and Password of the WiFi network.
- A Raspberry Pi Camera Module v2.
- Adafruit [HTS221](https://www.adafruit.com/product/4535) and [TSL2591](https://www.adafruit.com/product/1980) sensors.
- A microSD card with at least 32GB of storage.
- A stable internet connection for downloading dependencies.

### Hardware Setup

1. Connect the Raspberry Pi Camera Module v2 to the Raspberry Pi.
2. Connect the Adafruit [HTS221](https://www.adafruit.com/product/4535) and [TSL2591](https://www.adafruit.com/product/1980) sensors to the Raspberry Pi using the appropriate GPIO pins. More information on pin connections can be found in sensor documentation.
3. Insert the microSD card with Raspbian OS into the Raspberry Pi.
4. Connect the power supply to the Raspberry Pi and power it on.

### Software Setup

The Raspberry Pi can be accessed headlessly through SSH to set up the software and install dependencies. If the Wireless LAN configuration is correctly entered, the Raspberry Pi can be accessed from any device on the same WiFi network.

#### Accessing the Raspberry Pi via SSH

1. Open a terminal on your computer and connect to the Raspberry Pi using SSH.:
    ```bash
    ssh <username>@<hostname>.local
    ```
    Replace `<username>` and `<hostname>` with the actual username and hostname (e.g. `beelogger@BEElogger.local`).
2. Enter the password for the `beelogger` user when prompted. Once connected, you can proceed with the software setup and installation of dependencies. 

#### Installing BEElogger software

Follow these steps to install and set up the BEElogger software.

1. Update the package list and upgrade the installed packages:
    ```bash
    sudo apt-get update
    sudo apt-get upgrade
    ```
2. Install the PiCamera2 library:
    ```bash
    sudo apt install -y python3-picamera2
    ```
3. Install FFMPEG:
    ```bash
    sudo apt install ffmpeg
    ```
4. Install Git:
    ```bash
    sudo apt-get install git
    ```
5. Create a Python virtual environment named `BEElogger-env`:
    ```bash
    python3 -m venv --system-site-packages BEElogger-env
    ```
6. Activate the virtual environment:
    ```bash
    source BEElogger-env/bin/activate
    ```
7. Install `wheel` package.
   ```bash
   pip install wheel
   ```
8. Install the dependencies associated with [Adafruit Sensors](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) and restart when prompted:
    ```bash
    cd ~
    pip3 install --upgrade adafruit-python-shell
    wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
    sudo -E env PATH=$PATH python3 raspi-blinka.py
    ```
9. Activate the virtual environment again:
    ```bash
    source BEElogger-env/bin/activate
    ```
10. Clone the BEElogger repository:
    ```bash
    git clone https://github.com/malikaratnayake/BEElogger.git
    ```
11. Install the EcoMotionZip software:
    ```bash
    git clone https://github.com/malikaratnayake/EcoMotionZip.git
    ```
12. Navigate to the BEElogger directory:
    ```bash
    cd BEElogger
    ```
13. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
## Usage

### Repository Structure
```
├── config/
│   ├── config.json
├── docs/
│   ├── figures
│       ├── BEElogger.jpg
├── src/
│   ├── main.py
│   ├── camera.py
|   ├── sensors.py
|   ├── unitmanager.py
|   ├── writers.py
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
```

- `src/`: Contains the source code for the project.
    - `main.py`: The main entry point for the programme.
    - `camera.py`: Handles camera operations and image capture.
    - `sensors.py`: Manages sensor data collection.
    - `unitmanager.py`: Manages different units and operations of the system.
    - `writers.py`: Handles data writing operations.
- `config/`: Configuration files for the system.
    - `config.json`: Configuration for the system settings.
- `docs/`: Documentation files for the project.
    - `figures/`: Contains images and figures used in the documentation.
        - `BEElogger.jpg`: Overview of the BEElogger Data Collection Pipeline.
- `README.md`: This file.
- `LICENSE`: The licence for the project.
- `requirements.txt`: List of dependencies required for the project.
- `.gitignore`: Specifies files and directories to be ignored by git.

### Configuration Files

This file contains the configuration settings for the BEElogger. Below are the variables and their descriptions:

- `max_operating_temp` (int): Maximum operating temperature in degrees Celsius.
- `min_storage` (int): Minimum storage space in gigabytes.
- `sensor_log_interval` (int): Interval in seconds between sensor logs.
- `video_resolution` (list): Resolution of the videos in the format [width, height].
- `video_duration` (int): Duration of the videos in seconds.
- `video_fps` (int): Frame rate of the videos.
- `video_codec` (str): Codec used for video encoding.
- `video_container` (str): Container format for videos.
- `video_sampling_interval` (int): Interval in seconds between video captures.
- `diagnostic_interval` (int): Interval in seconds between diagnostic checks.
- `streaming_duration` (int): Duration of the video streaming in seconds.
- `recording_start_time` (str): Start time for recording in HH:MM:SS format.
- `recording_end_time` (str): End time for recording in HH:MM:SS format.
- `compress_video` (bool): Whether to compress the video files.
- `EcoMotionZip_path` (str): Path to the EcoMotionZip directory.
- `python_interpreter_path` (str): Path to the Python interpreter.
- `delete_original` (bool): Whether to delete the original video files after processing.


### Running the BEElogger

To run the BEElogger system, follow these steps:

1. **Activate the Virtual Environment**: Activate the virtual environment using the following command:
    ```bash
    source BEElogger-env/bin/activate
    ```

2. **Run the Main Script**: Execute the main script to start the BEElogger system:
    ```bash
    python BEElogger/src/main.py
    ```

3. **Monitor the Output and Access Data**: The system will start recording video and logging environmental data. Monitor the terminal output for any messages or errors. The monitoring data and logs will be saved to the `Monitoring_Data` folder in the home directory.

### Running the BEElogger at Startup

To run the BEElogger system at startup using `cron`, follow these steps:

1. **Open the Crontab File**: Open the crontab file for editing by running:
    ```bash
    crontab -e
    ```

2. **Add a New Cron Job**: Add the following line to the crontab file to run the main script at startup:
    ```bash
    @reboot /bin/sleep 60 && /path/to/BEElogger-env/bin/python3.11 /path/to/BEElogger/src/main.py
    ```
    Make sure to replace `/path/to/BEElogger-env` and `/path/to/BEElogger` with the actual paths to your virtual environment and project directory. With the default directories, the cron job would be as follows:
    ```bash
    @reboot /bin/sleep 60 && /home/beelogger/BEElogger-env/bin/python3.11 /home/beelogger/BEElogger/src/main.py
    ```

3. **Save and Exit**: Save the changes and exit the editor. The script will now run automatically at startup.



## License

This project is licensed under the GNU General Public License Version 3. See the [LICENSE](./LICENSE) file for more details.


## Authors

This project is developed and maintained by:

- **Malika Nisal Ratnayake** - [GitHub](https://github.com/malikaratnayake)
- **Asaduz Zaman** - [GitHub](https://github.com/asadiceiu)

