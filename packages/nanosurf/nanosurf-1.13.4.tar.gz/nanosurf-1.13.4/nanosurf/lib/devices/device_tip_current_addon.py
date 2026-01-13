""" This device controls the TipCurrent Addon Module for the DriveAFM
Copyright Nanosurf AG 2023
License - MIT
"""
import enum

import nanosurf as nsf
from nanosurf.lib.devices.device_driveafm_addon import DeviceDriveAFMAddon
from nanosurf.lib.spm.lowlevel import ctrlunits

class AmplifierGain(enum.Enum):
    Gain_10k = enum.auto()
    Gain_1Meg = enum.auto()
    Gain_100Meg = enum.auto()

class DriveAFM_Tip_Current_Addon(DeviceDriveAFMAddon):
    """ Driver class for the TipCurrent addon module for DriveAFM scan head

        Usage:
           Create DriveAFM_Tip_Current_Addon instance, 
           call connect() once and check if successful
           set desired current measurement range with set_gain()
           set tip voltage with set_tip_bias_voltage()
           set sample voltage wit set_sample_bias_voltage()
           read tip current with read_input_current()

        Example:
            See main section at bottom of this file
    """

    Assigned_BTNumber = "BT08508"     
    Assigned_SN_Prefix = "124"

    def __init__(self) -> None:
        super().__init__()
        self._current_gain = AmplifierGain.Gain_10k
        self._v_bias_max  = 5.0 # (V)
        self._v_input_max = 5.0 # (V)

    def _register_chips(self):
        self._chip_gpio = nsf.devices.i2c.Chip_PCA9534(bus_addr=0x27)
        self._bus_master.assign_chip(self._chip_gpio)

    def _check_chips_available(self) -> bool:
        if not self._chip_gpio.is_connected():
            raise IOError(f"Error: GPIO chip at {self._chip_gpio.bus_address} could not be detected") 
        return True

    def _write_setup(self):
        if self._is_connected:
            self._cx_adc_in  = self._spm.lu.ctrlunits.get_adc(ctrlunits.ADC.HiResIn_TIPCURRENT)
            self._cx_tip_bias_out = self._spm.lu.ctrlunits.get_dac(ctrlunits.DAC.HiResOut_TIPVOLTAGE)
            self._cx_sample_bias_out = self._spm.lu.ctrlunits.get_dac(ctrlunits.DAC.HiResOut_OUT6)
            self._cx_adc_in_max = self._cx_adc_in.max
            self._chip_gpio.reg_config   = 0x00
            self._chip_gpio.reg_polarity = 0x00
            self.set_gain(AmplifierGain.Gain_10k)
        else:
            raise IOError("Not connected.")
           
    def _read_setup(self):
        if self._is_connected:
            match self._chip_gpio.reg_output:
                case 0b10000101:
                    self._current_gain = AmplifierGain.Gain_10k
                case 0b10000110:
                    self._current_gain = AmplifierGain.Gain_1Meg
                case 0b10000000:
                    self._current_gain = AmplifierGain.Gain_100Meg
                case _:
                    raise ValueError("Unknown gain setting")
        else:
            raise IOError("Not connected.")             
        
    def set_gain(self, gain_id:AmplifierGain):
        """ select the amplification of the tip current """
        if self._is_connected:
            match gain_id:
                case AmplifierGain.Gain_10k:
                    self._chip_gpio.reg_output = 0b10000101
                    self._v_to_i_conversion_factor = 1.0 / 10.0e3
                case AmplifierGain.Gain_1Meg:
                    self._chip_gpio.reg_output = 0b10000110
                    self._v_to_i_conversion_factor = 1.0 / 1.0e6
                case AmplifierGain.Gain_100Meg:
                    self._chip_gpio.reg_output = 0b10000000
                    self._v_to_i_conversion_factor = 1.0 / 100.0e6
                case _:
                    raise ValueError(f"Unknown gain setting selected: {gain_id}")
            self._current_gain = gain_id
        else:
            raise IOError("Not connected.")   
            
    def get_gain(self) -> AmplifierGain:
        return self._current_gain
    
    def read_input_current(self) -> float:
        """ Return actual current input value in (A)"""
        return self.amp_v_to_i(self.read_current_amplifier_voltage())
    
    def read_current_amplifier_voltage(self) -> float:
        """ Read the actual amplifiers output voltage.
        """
        return self._cx_adc_in.dc / self._cx_adc_in_max * self._v_input_max

    def amp_v_to_i(self, v_amp:float) -> float:
        """ return the current in (A) corresponding to the measured voltage of the logarithmic amplifier"""
        return v_amp * self._v_to_i_conversion_factor

    def set_tip_bias_voltage(self, bias:float):
        """ set the bias voltage to the tip input.  """
        self._cx_tip_bias_out.dc_norm = bias / self._v_bias_max

    def set_sample_bias_voltage(self, bias:float):
        """ set the bias voltage to the sample output connector. """
        self._cx_sample_bias_out.dc_norm = bias / self._v_bias_max

    
if __name__ == "__main__":
    import time
    spm = nsf.SPM()
    if spm.is_connected():
        tip_current_module = DriveAFM_Tip_Current_Addon()
        if tip_current_module.connect(spm):
            print("Module found")
            tip_current_module.set_gain(AmplifierGain.Gain_1Meg)
            tip_current_module.set_sample_bias_voltage(0.0)
            tip_current_module.set_tip_bias_voltage(1.0)
            for _ in range(1000):
                print(f"{tip_current_module.read_current_amplifier_voltage():.3f} V = ", nsf.sci_val.convert.to_string(tip_current_module.read_input_current(),"A"))
                time.sleep(0.01)            
        else:
            print("Addon Module not present.")
