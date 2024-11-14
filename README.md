# BEElogger
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)

**B**eehive **E**ntrance and **E**nvironment Logger *(BEElogger)* is a Raspberry Pi-based system designed for recording video and micro-climatic data at the entrance of a beehive. The BEElogger system is specifically tailored for monitoring stingless bees and assisting beekeepers in observing the activity and environmental conditions of their beehives. By utilising a Raspberry Pi, the system captures video footage and collects data on temperature, humidity, pressure, and light intensity, all of which are relevant to bee activity. This information can be used to analyse the health and behaviour of the bee colony, detect potential issues early, and make informed decisions to improve hive management.

### Features

- High-definition video recording of beehive entrance activity.
- Real-time monitoring of temperature, humidity, pressure, and light intensity.
- Data logging for historical analysis.
- Easy setup and configuration with a Raspberry Pi.
- Open-source software for customization and extension.
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
2. Enter the password for the `beelogger` user when prompted.

Once connected, you can proceed with the software setup and installation of dependencies. 

#### Installing BEElogger software

Follow these steps to install and set up the BEElogger software.

1. Update the package list and upgrade the installed packages:
    ```bash
    sudo apt-get update
    sudo apt-get upgrade
    ```
2. Install Git:
    ```bash
    sudo apt-get install git
    ```
3. Clone the repository:
    ```bash
    git clone https://github.com/malikaratnayake/BEElogger.git
    ```
4. Creeate a python virtual environment named `BEElogger-env`.
    ```bash
    python3 -m venv --system-site-packages BEElogger-env
    ```
5. Activate the virtual environment:
    ```bash
    source BEElogger-env/bin/activate
    ```
6. Install EcoMotionZip software:
    ```bash
    git clone https://github.com/malikaratnayake/EcoMotionZip.git
    ```
7. Navigate to the project directory:
    ```bash
    cd BEElogger
    ```
8. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
9. Configure the system settings in the `config.json` file.

10. Run the BEElogger software:
    ```bash
    python /src/main.py
    ```

### Configuration

Edit the `config.json` file to customize the system settings, such as video recording durations, data sampling intervals, and output directories. Refer to the comments in the `config.json` file for detailed instructions on each configuration option.



## Repository Structure


```

### Installation

To install and set up the BEElogger system, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/NatBeeSense.git
    ```
2. Navigate to the project directory:
    ```bash
    cd NatBeeSense
    ```
3. Install the required dependencies:
    ```bash
    sudo ./install_dependencies.sh
    ```
4. Configure the system settings in the `config.json` file.
5. Run the BEElogger software:
    ```bash
    python3 bee_logger.py
    ```

### Usage

Once the system is set up, it will automatically start recording video and logging environmental data. You can access the recorded data and video files in the designated output directory specified in the configuration file.

### Contributing

We welcome contributions to the BEElogger project. If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request on GitHub.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
