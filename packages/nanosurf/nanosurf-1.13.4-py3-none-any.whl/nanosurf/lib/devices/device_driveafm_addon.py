""" Driver class for the SSRM logarithmic current amplifier addon module for DriveAFM
Copyright Nanosurf AG 2025
License - MIT
"""

from typing import cast

import nanosurf as nsf
from nanosurf.lib.devices.i2c.bus_access import _I2CBusID
from nanosurf.lib.devices.accessory_interface.accessory_master import GenericIDEEPROM

def abstractmethod(func):
    def wrapper(*args, **kwargs):
        raise NotImplementedError(f"{func.__name__} must be implemented")
    return wrapper

class DeviceDriveAFMAddon:
    """ General driver class for addon modules for DriveAFM scan head
    """
    
    Assigned_BTNumber  = "BT00000"    
    Assigned_SN_Prefix = "000"

    def __init__(self, config:GenericIDEEPROM = None) -> None:
        """ This class stores the information found in the id eeprom of each slave device

            As standard identification a bt-number is read from the device
            Optional a serial number is provided

        Parameters
        ----------
        config : GenericIDEEPROM, optional
            The type of configuration used in the specific device.
            If not provided it is assumed that it represents minimal the GenericIDEEPROM information
            which has a BTNumber and a SerialNo as content.
        """
        if config is None:
            config = GenericIDEEPROM(bus_addr=0x51)
        self.config = config
        self._is_connected = False
    
    def connect(self, spm:nsf.Spm, do_initialize_chip=True) -> bool:
        """ Establish communication, check's module availability and initialize standard mode

            Parameters
             ---------
               spm: nsf.Spm
                    pointer to controller connection
               do_initialize_chip: bool, optional
                    disable this flag if no configuration is desired. Useful to connect to a module if it is configured already
            Returns
            -------
                True if all communication with module could be establish
        """
        self._is_connected = False
        try:
            self._spm = spm
            self._bus_id = nsf.devices.i2c.I2CBusID.ScanHead
            self._bus_master  = nsf.devices.i2c.I2CBusMaster(spm, cast(_I2CBusID, self._bus_id))
            self._bus_master.assign_chip(self.config)
            self._register_chips()
            
            if self.config.is_connected():
                if not self.config.load_config():
                    raise IOError("Error: Module not initialized with SN-Number and BT-Number")
                
                if self.config.bt_number != self.Assigned_BTNumber:
                    raise IOError(f"Error: Wrong module found in Addon-slot: {self.config.bt_number}, {self.config.sn_number}")

                self._is_connected = self._check_chips_available()
                
                if self._is_connected:
                    if do_initialize_chip:
                        self._write_setup()
                    else:
                        self._read_setup()

        except Exception as e:
            print(e)
            self._is_connected = False
        return self._is_connected
    
    def is_connected(self) -> bool:
        if self._is_connected:
            return self._check_chips_available()
        return False 
    
    def is_any_module_attached(self, spm:nsf.Spm) -> bool:
        try:
            self._spm = spm
            self._bus_id = nsf.devices.i2c.I2CBusID.ScanHead
            self._bus_master = nsf.devices.i2c.I2CBusMaster(spm, cast(_I2CBusID, self._bus_id))
            self._bus_master.assign_chip(self.config)
            return self.config.is_connected()
        except Exception as e:
            print(e)  
        return False
    
    def detect_attached_module(self, spm:nsf.Spm) -> str:
        try:
            if self.is_any_module_attached(spm):
                if not self.config.load_config():
                    raise IOError("Error: Module not initialized with SN-Number and BT-Number")
                return self.config.bt_number
        except Exception as e:
            print(e)
        return ""

    def _initialize_id_eeprom(self, serial_no:str, bt_number:str=None, config:GenericIDEEPROM = None) -> bool:
        """ Writes a initial configuration to eeprom. Handle with care!
            If a configuration is passed then this is written to the eeprom, else the own current configuration
        """

        if config is None:
            config = self.config
            
        if bt_number is None:
            bt_number = self.Assigned_BTNumber

        if not bt_number.startswith("BT") or len(bt_number) != 7:
            raise ValueError("bt_number must have the format BT01234")
        if len(serial_no) < 10 or len(serial_no) > 11:
            raise ValueError("serial_no must have the format 000-00-000")
        config.bt_number = bt_number
        config.sn_number = serial_no
            
        print(f"Start initializing eeprom with {config.bt_number} and {config.sn_number}. Please wait...")
        self._bus_master.assign_chip(config)
        done = config.store_config()
        return done

    # ------- the following functions must be reimplemented by implementation classes --------

    @abstractmethod
    def _register_chips(self):
        """This Function must be reimplemented by Device implementation class"""
        pass

    @abstractmethod
    def _check_chips_available(self) -> bool:
        """This Function must be reimplemented by Device implementation class"""
        return True

    @abstractmethod
    def _write_setup(self):
        """This Function must be reimplemented by Device implementation class"""
        pass

    @abstractmethod
    def _read_setup(self):
        """This Function must be reimplemented by Device implementation class"""
        pass
            

if __name__ == "__main__":
    spm = nsf.SPM()
    if spm.is_connected():
        addon_module = DeviceDriveAFMAddon()
        if addon_module.is_any_module_attached(spm):
            print(f"Addon Module {addon_module.detect_attached_module(spm)} found")
        else:
            print("Addon Module not present.")

        if False:
            device_to_init = XXX()
            print(device_to_init.initialize_id_eeprom(serial_no=device_to_init.Assigned_SN_Prefix+"-00-000"))

