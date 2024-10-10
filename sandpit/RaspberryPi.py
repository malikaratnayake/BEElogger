import os
from typing import Any
import logging
import time

logger = logging.getLogger()


class HealthManager:

    def __init__(self,
                 max_operating_temp: int,
                 min_storage: int,
                 unit_turnoff_time: str,
                 unit_turnon_time: str,
                 diagnostic_interval: int,
                 pisensor,
                 directory_info) -> None:
        
        self.max_operating_temp = max_operating_temp
        self.min_storage = min_storage
        self.unit_turnoff_time = unit_turnoff_time
        self.unit_turnon_time = unit_turnon_time
        self.diagnostic_interval = diagnostic_interval
        self.pisensor = pisensor
        self.directory_info = directory_info
        
        logger.info("UnitManager initialised with parameters:")
        logger.info("Max operating temperature: " + str(self.max_operating_temp))
        logger.info("Minimum storage: " + str(self.min_storage))
        logger.info("Unit turnoff time: " + str(self.unit_turnoff_time))
        logger.info("Unit turnon time: " + str(self.unit_turnon_time))
        logger.info("Diagnostic interval: " + str(self.diagnostic_interval))

        self.last_recording_status = False
        self.unit_is_operational = True
        self.next_diagonistic_run = None
        self.in_recording_period = False
        self.latest_diagnosis = None

         
    def set_unit_operational_status(self, _status):
        self.unit_is_operational = _status
        return None

    def get_unit_operational_status(self):
        return self.unit_is_operational 


    def get_unit_status(self):
        current_time = time.time()
        free_space = self.pisensor.read_free_space()
        cpu_temp = self.pisensor.read_cpu_temp()

        self.latest_diagnosis = {"recorded_time": current_time, 
                                 "free_space": free_space,
                                 "cpu_temp": cpu_temp}


        return self.latest_diagnosis
    
    def assess_recording_capability(self):
        _unit_status = self.get_unit_status()
        logger.info("Unit status: " + str(_unit_status))

        if _unit_status["cpu_temp"] > self.max_operating_temp:
            logger.warning("Battery temperature is high: " + str(_unit_status["cpu_temp"]))
            return False
     
        elif self.assess_shutdown_requirement() is True:
            return False
    
        else:
            logger.info("Unit is operational")
            return True
        
    def assess_shutdown_requirement(self):
        _unit_status = self.latest_diagnosis
        if _unit_status["free_space"] < self.min_storage:
            logger.warning("Free space is low: " + str(_unit_status["free_space"]))
            return True
        else:
            return False
        

    def assess_restart_requirement(self):
        recorded_date = self.directory_info.get_current_date()
        date_now = time.strftime("%Y%m%d", time.localtime())

        if recorded_date != date_now:
            logger.info("Restarting unit as current date has changed")
            return True
        else:
            return False

        
    def schedule_unit_turnoff(self):
       # turn_off_duration = self.calculate_unit_off_duration(self.unit_turnon_time)
        #logger.info("Scheduling unit turnoff for: " + str(turn_off_duration) + " seconds")
        # pijuice.power.SetPowerOff(30)
        time.sleep(2)
        os.system("sudo shutdown now")

    def run_diagnostics(self, camera, stop_signal):
        diagnostic_run = False 
        recording_capability = True
        if self.latest_diagnosis is None:
            recording_capability = self.assess_recording_capability()
            restart_requirement = self.assess_restart_requirement()
            diagnostic_run = True
            self.next_diagonistic_run = time.time() + self.diagnostic_interval
        else:
            if time.time() > self.next_diagonistic_run:
                recording_capability = self.assess_recording_capability()
                restart_requirement = self.assess_restart_requirement()
                diagnostic_run = True
                self.next_diagonistic_run = time.time() + self.diagnostic_interval

        if diagnostic_run is True:
            if restart_requirement is True:
                self.schedule_restart()
                # print("funny")
            else:
                pass


            if recording_capability is False:
                shutdown_requirement = self.assess_shutdown_requirement()
            else:
                shutdown_requirement = False


            if shutdown_requirement is True:
                stop_signal.set()
            elif shutdown_requirement is False and recording_capability is False:
                self.last_recording_status = camera.get_recording_status()
                self.set_unit_operational_status(False)
                camera.set_recording_status(False)
                logger.warning("Recording stopped due to heating issues")
            else:
                self.set_unit_operational_status(True)
                if self.last_recording_status is True and camera.get_recording_status() is False:
                    camera.set_recording_status(True)
                    logger.info("Recording restarted after heating issues")
                else:
                    pass

        else:
            pass


        
    def schedule_restart(self):
        logger.info("Scheduling unit restart")
        os.system("sudo reboot")
        return None


        

        

