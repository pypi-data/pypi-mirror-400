""" This device controls the TipAccess Addon Module for the DriveAFM
Copyright Nanosurf AG 2023
License - MIT
"""
import enum

import nanosurf as nsf
from nanosurf.lib.devices.device_driveafm_addon import DeviceDriveAFMAddon

class TipConnection(enum.Enum):
    Open     = enum.auto()
    Internal = enum.auto()
    External = enum.auto()

class DriveAFM_Tip_Access_Addon(DeviceDriveAFMAddon):
    """ Driver class for the TipAccess addon module for DriveAFM scan head

        Usage:
           Create DriveAFM_Tip_Access_Addon instance, 
           call connect() once and check if successful
           set desired connection to the tip with set_tip_connection()

        Example:
            See main section at bottom of this file
    """

    Assigned_BTNumber = "BT08509"     
    Assigned_SN_Prefix = "000"

    class _RelaysMask(enum.IntEnum):
        AllOff = 0x00
        Intern = 0x02
        Extern = 0x01

    def __init__(self) -> None:
        super().__init__()

    def _register_chips(self):
        self._chip_gpio = nsf.devices.i2c.Chip_PCA9534(bus_addr=0x27)
        self._bus_master.assign_chip(self._chip_gpio)

    def _check_chips_available(self) -> bool:
        if not self._chip_gpio.is_connected():
            raise IOError(f"Error: GPIO chip at {self._chip_gpio.bus_address} could not be detected") 
        return True

    def _write_setup(self):
        if self._is_connected:
            self._chip_gpio.reg_config   = 0x00
            self._chip_gpio.reg_polarity = 0x00
            self.set_tip_connection(TipConnection.Internal)
        else:
            raise IOError("Not connected.")

    def _read_setup(self):
        self.get_tip_connection()

    def set_tip_connection(self, connection_id:TipConnection):
        """ select the source which is connected to the cantilever tip """
        if self._is_connected:
            match connection_id:
                case TipConnection.Internal:
                    self._chip_gpio.reg_output = self._RelaysMask.AllOff # break before make
                    self._chip_gpio.reg_output = self._RelaysMask.Intern
                case TipConnection.External:
                    self._chip_gpio.reg_output = self._RelaysMask.AllOff  # break before make
                    self._chip_gpio.reg_output = self._RelaysMask.Extern
                case TipConnection.Open:
                    self._chip_gpio.reg_output = self._RelaysMask.AllOff
                case _:
                    raise ValueError(f"Unknown connection selected: {connection_id}")
        else:
            raise IOError("Not connected.")
        
    def get_tip_connection(self) -> TipConnection:
        if self._is_connected:
            match self._chip_gpio.reg_output:
                case self._RelaysMask.Intern:
                    return TipConnection.Internal
                case self._RelaysMask.Extern:
                    return TipConnection.External
                case self._RelaysMask.AllOff:
                    return TipConnection.Open
                case _:
                    raise IOError(f"Illegal Relay state found. 0x{self._chip_gpio.reg_output:02x}")
        else:
            raise IOError("Not connected.")
        
if __name__ == "__main__":
    spm = nsf.SPM()
    if spm.is_connected():
        tip_access_module = DriveAFM_Tip_Access_Addon()
        if tip_access_module.connect(spm):
            print("Module found")
            tip_access_module.set_tip_connection(TipConnection.Internal)
        else:
            print("Addon Module not present.")
