
"""Copyright (C) Nanosurf AG - All Rights Reserved (2025)
License - MIT"""

import nanosurf.lib.devices.i2c.bus_master as i2c 
import enum

class Chip_PCA9536(i2c.I2CChip):
    """ 4-bit I2C-bus and SMBus I/O port chip"""

    class Register(enum.IntEnum):
        """The register addresses of the chip"""
        INPUT    = 0x00   #Input Port register (R)
        OUTPUT   = 0x01   #Output Port register (R/W)
        POLARITY = 0x02   #Polarity Inversion register (R/W)
        CONFIG   = 0x03   #Configuration register (R/W)

    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)

    @property
    def reg_input(self) -> int:
        """Returns the current value of the input pins."""
        return self.read_byte_with_offset(self.Register.INPUT)
        
    
    @property
    def reg_output(self) -> int:
        """Returns the current value of the output pins."""
        return self.read_byte_with_offset(self.Register.OUTPUT)

    @reg_output.setter
    def reg_output(self, output_mask: int):
        """Sets the values of the output pins"""
        self.write_bytes([self.Register.OUTPUT, output_mask])
        

    @property
    def reg_polarity(self) -> int:
        """Returns the invert polarity state of Input Port register data.
            \n0 = Input Port register data retained (default value)
            \n1 = Input Port register data inverted"""
        return self.read_byte_with_offset(self.Register.POLARITY)

    @reg_polarity.setter
    def reg_polarity(self, polarity_mask: int):
        """inverts polarity of Input Port register data.
            \n0 = Input Port register data retained (default value)
            \n1 = Input Port register data inverted"""
        self.write_bytes([self.Register.POLARITY, polarity_mask])

    @property
    def reg_config(self) -> int:
        """Returns the configuration of the pins.
            \n0 = corresponding port pin enabled as an output
            \n1 = corresponding port pin configured as input (default value)"""
        return self.read_byte_with_offset(self.Register.CONFIG)
    
    @reg_config.setter
    def reg_config(self, config_mask: int):
        """Sets the configuration of the pins.
            \n0 = corresponding port pin enabled as an output
            \n1 = corresponding port pin configured as input (default value)"""
        self.write_bytes([self.Register.CONFIG, config_mask])

