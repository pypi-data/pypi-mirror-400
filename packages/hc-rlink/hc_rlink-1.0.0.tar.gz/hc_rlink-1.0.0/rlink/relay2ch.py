from .module import RLinkModule
import time

# Module type/subtype for 2-channel relay
RLY_TYPE = 0x02
RLY_SUBTYPE_2CH = 0x01

# Register addresses
RLINK_RLY_REG_R0 =          10
RLINK_RLY_REG_R1 =          11
RLINK_RLY_REG_IN_STATE  =   14
RLINK_RLY_REG_IN_ENABLE =   15
RLINK_RLY_REG_R0_ONTIME =   16
RLINK_RLY_REG_R1_ONTIME =   17




class Relay2Ch(RLinkModule):
    """2-channel relay module."""
    
    def __init__(self, bus, address):
        """
        Initialize Relay2Ch module.

        Parameters:
            bus (RLinkBus): Bus object.
            address (int): Module address.
        """
        super().__init__(bus, address, RLY_TYPE, RLY_SUBTYPE_2CH)


 
    def setRelay(self, channel, on):
        """
        Turn a relay on or off.

        Parameters:
            channel (int): Relay number (0 or 1).
            on (bool)   : True=on, False=off.

        Returns:
            None
        """
        if channel == 0:
            reg = RLINK_RLY_REG_R0
        elif channel == 1:
            reg = RLINK_RLY_REG_R1
        else:
            raise ValueError("Invalid relay channel")

        value = 1 if on else 0
        self.writeReg(reg, bytes([value]))



    def setRelayConfirm(self, channel, required_state, timeout_ms=1000, retry_delay_ms=20):
        """
        Set a relay state and confirm it by reading back the register.

        Parameters:
            channel (int): Relay number (0 or 1).
            required_state (bool)    : True=ON, False=OFF.
            timeout_ms (int): Maximum time to wait for confirmation.
            retry_delay_ms (int): Delay between read retries.

        Returns:
            bool: True if relay confirmed to match state, False on timeout.
        """
        start_time = time.monotonic()

        # Send write command
        self.setRelay(channel, required_state)

        while (time.monotonic() - start_time) * 1000 < timeout_ms:
            # Read back the relay state
            state = self.readRelay(channel, timeout_ms=timeout_ms)
            if state is None:
                # Could not read; wait and retry
                time.sleep(retry_delay_ms / 1000.0)
                continue

            if bool(state) == required_state:
                return True  # Confirmed

            # Not yet matching, wait a bit before retrying
            time.sleep(retry_delay_ms / 1000.0)

        # Timeout reached without confirmation
        return False



    def readRelay(self, channel, timeout_ms=100):
        """
        Read the current state of a relay.

        Parameters:
            channel (int)       : Relay number (0 or 1).
            timeout_ms (int)    : Timeout in milliseconds (default 100).

        Returns:
            bool or None        : True=on, False=off, None if error.
        """
        
        # Returns True=on, False=off, None=error
        if channel == 0:
            reg = RLINK_RLY_REG_R0
        elif channel == 1:
            reg = RLINK_RLY_REG_R1
        else:
            raise ValueError("Invalid relay channel")
    
        data = self.readReg(reg, timeout_ms)
        # If read failed, propagate None
        if data is None or len(data) == 0:
            return None

        # Relay is ON if register byte is 1, OFF if 0
        return bool(data[0])



    def setInputs(self, bitmap):
        """
        Enable or disable input pins.

        Parameters:
            bitmap (int): Bitmask of inputs to enable.

        Returns:
            None
        """
        
        self.writeReg(RLINK_RLY_REG_IN_ENABLE, bytes([bitmap]))



    def readInputs(self, timeout_ms=100):
        """
        Read current input states.

        Parameters:
            timeout_ms (int): Timeout in milliseconds.

        Returns:
            int or None: Byte representing input states, or None if read fails.
        """
        
        # Returns byte value or None
        data = self.readReg(RLINK_RLY_REG_IN_STATE, timeout_ms)
        return data[0] if data else None



    def setOnTime(self, relay, time100ms):
        """
        Set on-time for a specific relay.

        Parameters:
            relay (int)       : Relay number (0 or 1).
            time100ms (int)   : On-time in units of 100ms.

        Returns:
            None
        """
        if relay == 0:
            reg = RLINK_RLY_REG_R0_ONTIME
        elif relay == 1:
            reg = RLINK_RLY_REG_R1_ONTIME
        else:
            raise ValueError("Invalid relay number (0–1)")
        
        # Split 16-bit value into low/high bytes
        lo = time100ms & 0xFF
        hi = (time100ms >> 8) & 0xFF
        self.writeReg(reg, bytes([lo, hi]))
        
        # Wait while value is written to NV memory
        time.sleep(0.01)



    def readOnTime(self, relay, timeout_ms=100):
        """
        Read on-time for a specific relay.

        Parameters:
            relay (int)       : Relay number (0 or 1).
            timeout_ms (int)  : Timeout in milliseconds.

        Returns:
            int or None       : On-time in 100ms units, or None if read fails.
        """
        if relay == 0:
            reg = RLINK_RLY_REG_R0_ONTIME
        elif relay == 1:
            reg = RLINK_RLY_REG_R1_ONTIME
        else:
            raise ValueError("Invalid relay number (0–1)")

        data = self.readReg(reg, timeout_ms)
        #print(data)
        if len(data) == 2:
            return data[0] | (data[1] << 8)
        return None

