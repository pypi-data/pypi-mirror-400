
"""Copyright (C) Nanosurf AG - All Rights Reserved (2025)
License - MIT"""

import time
import nanosurf as nsf
import nanosurf.lib.devices.accessory_interface.accessory_master as am
from nanosurf.lib.devices.i2c.chip_TMP119 import Chip_TMP119
from nanosurf.lib.devices.i2c.chip_SHT45 import Chip_SHT4x
from nanosurf.lib.devices.i2c.chip_PCA9536 import Chip_PCA9536

class GSSClimateSensor(am.AccessoryDevice):
    
    Assigned_BTNumber = "BT10224"
    
    def __init__(self, serial_no:str = ""):
        super().__init__(serial_no=serial_no, bt_number=self.Assigned_BTNumber)
        self.chip_sht  = Chip_SHT4x(bus_addr=0x44)
        self.chip_temp = Chip_TMP119(bus_addr=0x48)
        self.chip_gpio = Chip_PCA9536(bus_addr=0x41)

    def register_chips(self):
        self.assign_chip(self.chip_sht)
        self.assign_chip(self.chip_temp)
        self.assign_chip(self.chip_gpio)
    
    def init_device(self):
        self.chip_sht.reset()
        self.chip_sht.set_heating_power(self.chip_sht.HeatingPower.Power_110mW_1s)
        self.chip_sht.set_measure_mode(self.chip_sht.MeasureMode.Without_Heating)

        self.chip_temp.reset()
        self.chip_temp.set_average_mode(self.chip_temp.AverageMode.Averages_8)
        self.chip_temp.set_conversion_cycle(self.chip_temp.ConversionCycle.ms_250)
        self.chip_temp.start_continuous_mode()

        self.chip_gpio.reg_config = 0xFE
        
    def get_body_temperature(self) -> float:
        return self.chip_temp.read_temperature()
    
    def get_air_temperature(self) -> float:
        temp, _ = self.chip_sht.read_temp_and_humidity()
        return temp
    
    def get_air_humidity(self) -> float:
        _, humidity = self.chip_sht.read_temp_and_humidity()
        return humidity
    
    # def check_temp_alarm(self) -> bool:
    #     return (self.chip_gpio.reg_input & 0b00000010) != 0b00000010
        
    def set_device_led(self, state: bool):
        if state is True:
            self.chip_gpio.reg_output &= ~0b00000001
        else:
            self.chip_gpio.reg_output |= 0b00000001

    def blink(self, number_of_cycles: int, interval = 1.0):
        for _ in range(number_of_cycles):
            self.set_device_led(True)
            time.sleep(interval)
            self.set_device_led(False)
            time.sleep(interval)