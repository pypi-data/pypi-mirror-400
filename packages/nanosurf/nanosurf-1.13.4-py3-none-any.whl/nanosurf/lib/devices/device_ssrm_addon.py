""" Driver class for the SSRM logarithmic current amplifier addon module for DriveAFM
Copyright Nanosurf AG 2025
License - MIT
"""
import enum

import nanosurf as nsf
from nanosurf.lib.devices.device_driveafm_addon import DeviceDriveAFMAddon
from nanosurf.lib.spm.lowlevel import ctrlunits

class BiasVoltageMode(enum.Enum):
    TipInSampleBias = enum.auto()
    SampleInTipBias = enum.auto()

class DriveAFM_SSRM_Addon(DeviceDriveAFMAddon):
    """ Driver class for the SSRM logarithmic current amplifier addon module for DriveAFM scan head

        Usage:
           Create DriveAFM_SSRM_Addon instance, 
           call connect() once and check if successful
           set desired bias mode with select_bias_voltage_mode()
           set desired bias voltage with set_bias_voltage()
           read actual current measurement with read_input_current()

        Example:
            See main section at bottom of this file
    """

    Assigned_BTNumber = "BT09929"     
    Assigned_SN_Prefix = "126"

    def __init__(self) -> None:
        super().__init__()
        self._v_bias_max  = 5.0 # (V)
        self._v_input_max = 5.0 # (V)
        self._relays_states = {
            BiasVoltageMode.TipInSampleBias: 0b10000101,
            BiasVoltageMode.SampleInTipBias: 0b10001010,
        }
    
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
            self._cx_dac_out = self._spm.lu.ctrlunits.get_dac(ctrlunits.DAC.HiResOut_TIPVOLTAGE)
            self._cx_adc_in_max = self._cx_adc_in.max
            self._chip_gpio.reg_config = 0x00 # all pins are outputs
            self._chip_gpio.reg_polarity = 0x00 
            self.select_bias_voltage_mode(BiasVoltageMode.TipInSampleBias)
        else:
            raise IOError("Not connected.")

    def _read_setup(self):
        pass

    def select_bias_voltage_mode(self, bias_mode:BiasVoltageMode):
        self._chip_gpio.reg_output = self._relays_states[bias_mode]

    def set_bias_voltage(self, bias:float):
        """ set the bias voltage to the selected output. The voltage has to be positive. 
            See also select_bias_voltage_mode() 
        """
        if bias < 0.0:
            raise ValueError("The bias voltage has to be positive. For negativ currents, switch bias mode with select_bias_voltage_mode()")
        self._cx_dac_out.dc_norm = bias / self._v_bias_max

    def get_bias_voltage(self) -> float:
        return self._cx_dac_out.dc_norm * self._v_bias_max

    def read_input_current(self) -> float:
        """ Return actual current input value in (A)"""
        return self.log_v_to_i(self.read_current_amplifier_voltage())
    
    def read_current_amplifier_voltage(self) -> float:
        """ Read the actual amplifiers output voltage.
            The voltage is logarithmic. 0.0V corresponds to 100nA. and change 200mV per decade
        """
        return self._cx_adc_in.dc / self._cx_adc_in_max * self._v_input_max

    def log_v_to_i(self, v_log_amp:float) -> float:
        """ return the current in (A) corresponding to the measured voltage of the logarithmic amplifier"""
        # 0.2 is the voltage per decade, -7 represent the exponent which correspond to 0V -> 100nA -> 10^-7A 
        return 10 ** ((v_log_amp) / 0.2 - 7)


if __name__ == "__main__":
    import time
    spm = nsf.SPM()
    if spm.is_connected():
        ssrm_module = DriveAFM_SSRM_Addon()
        if ssrm_module.connect(spm):
            print("SSRM Module found")
            ssrm_module.select_bias_voltage_mode(BiasVoltageMode.TipInSampleBias)
            ssrm_module.set_bias_voltage(0.5)
            for _ in range(1000):
                print(f"{ssrm_module.read_current_amplifier_voltage():.3f} V = ", nsf.sci_val.convert.to_string(ssrm_module.read_input_current(),"A"))
                time.sleep(0.01)
        else:
            print("SSRM Addon Module not present.")
