
class RLinkModule:
    """Base class for all rLink modules."""
    
    # ===============================
    # Common registers
    # ===============================
    REG_STATUS         = 0x00
    REG_ADDRESS        = 0x01
    REG_TYPE           = 0x02
    REG_SUBTYPE        = 0x03
    REG_VERSION        = 0x04
    REG_COM_LED        = 0x05
    REG_BAUD           = 0x06
    REG_REPLYDELAY     = 0x07

    # ===============================
    # Common commands
    # ===============================
    CMD_WRITE          = 0x01
    CMD_READ           = 0x02
    CMD_REPLY          = 0x03
    CMD_ERROR          = 0xFF
    
    # ===============================
    # COM LED modes
    # ===============================
    COMLED_BLINK_OFF   = 0
    COMLED_BLINK_ON    = 1
    COMLED_ALWAYS_ON   = 2
    COMLED_ALWAYS_OFF  = 3

    # ===============================
    # Baud rate indices
    # ===============================
    BAUD_1200    = 0
    BAUD_2400    = 1
    BAUD_4800    = 2
    BAUD_9600    = 3
    BAUD_19200   = 4
    BAUD_38400   = 5
    BAUD_57600   = 6
    BAUD_115200  = 7
    

    @staticmethod
    def get_module_type_name(type_id):
        """
        Return a human-readable name for a module type.
        """
        if type_id == 0x02:
            return "Relay"
        return "Unknown"

    @staticmethod
    def get_module_subtype_name(type_id, subtype_id):
        """
        Return a human-readable name for a module subtype.
        Requires the type_id to determine which subtype mapping to use.
        """
        if type_id == 0x02 and subtype_id == 0x01:
            return "2 Channel"
        return "Unknown"



    def __init__(self, bus, address, module_type, sub_type):
        """
        Initialize the module.

        Parameters:
            bus (RLinkBus): Bus object to communicate over.
            address (int): Module address (0–127).
            module_type (int): Module type ID.
            sub_type (int): Module subtype ID.
        """
        
        # Initialize module with bus, address, type, and subtype
        self.bus = bus
        self.addr = address
        self.type = module_type
        self.subType = sub_type



    def setCOMLED(self, mode: int):
        """
        Set the COM LED operating mode.

        Parameters:
            mode (int): COM LED mode (0=blink off, 1=blink on, 2=always on, 3=always off).

        Returns:
            None
        """
        
        # mode: 0=blink off, 1=blink on, 2=always on, 3=always off
        self.writeReg(self.REG_COM_LED, bytes([mode]))



    def setAddress(self, new_addr: int):
        """
        Permanently change the module address.

        Parameters:
            new_addr (int): New module address (0–127).

        Returns:
            None
        """

        # Address must be 0–127
        if not (0 <= new_addr <= 127):
            raise ValueError("Address must be 0–127")

        # Unlock sequence: AA 55 AA + new address
        unlock = bytes([0xAA, 0x55, 0xAA, new_addr])
        self.writeReg(self.REG_ADDRESS, unlock)

        # Update local address
        self.addr = new_addr



    def useAddress(self, new_addr: int):
        """
        Temporarily override the module address for subsequent commands.

        Parameters:
            new_addr (int): Temporary address to use.

        Returns:
            None
        """
        self.addr = new_addr


   
    def setBAUDRate(self, baud_index: int):
        """
        Set the module baud rate (does NOT change bus speed).

        Parameters:
            baud_index (int): Index of baud rate (0–7).

        Returns:
            None
        """
        if not (0 <= baud_index <= 7):
            raise ValueError("Baud index must be 0–7")

        # Unlock sequence: AA 55 AA + baud index
        self.writeReg(self.REG_BAUD, bytes([0xAA, 0x55, 0xAA, baud_index]))



    def readVersion(self, timeout_ms=100):
        """
        Read the module firmware version.

        Parameters:
            timeout_ms (int, optional): Timeout in milliseconds (default 100).

        Returns:
            tuple: (major, minor) version numbers, or None if read fails.
        """
        
        # Returns (major, minor) tuple, or None if read fails
        data = self.readReg(self.REG_VERSION, timeout_ms)
        if not data or len(data) < 1:
            return None

        byte = data[0]
        major = (byte >> 4) & 0x0F
        minor = byte & 0x0F
        return (major, minor)



    def readReg(self, reg, timeout_ms=100):
        """
        Read a register from the module.

        Parameters:
            reg (int): Register address to read.
            timeout_ms (int): Timeout in milliseconds.

        Returns:
            bytes | None: Register payload, or None on failure.
        """
        data = self.bus.read(
            self.addr,
            self.type,
            self.subType,
            reg,
            timeout_ms
        )

        return data

 
 
    def writeReg(self, reg, data: bytes):
        """
        Write data to a register.

        Parameters:
            reg (int): Register address.
            data (bytes): Data to write.

        Returns:
            None
        """
        frame = self._build_write_frame(reg, data)
        self.bus.send(frame)



    def _build_write_frame(self, reg, data):
        """
        Build a write frame for a register and data.

        Parameters:
            reg (int): Register address to write.
            data (bytes): Data payload.

        Returns:
            bytes: Write frame bytes.
        """
        return bytes([0x55, self.addr, self.type, self.subType, self.CMD_WRITE, reg, len(data)]) + data



    def setReplyDelay(self, delay_ms: int):
        """
        Set the module reply delay time.

        This is the delay (in milliseconds) the module will wait
        before replying to a read request.

        Parameters:
            delay_ms (int): Delay time in milliseconds (0–255).

        Returns:
            None

        Raises:
            ValueError: If delay_ms is not in the 0–255 range.
        """
        
        if not (0 <= delay_ms <= 255):
            raise ValueError("Reply delay must be 0–255 ms")
        self.writeReg(self.REG_REPLYDELAY, bytes([delay_ms]))



    def readReplyDelay(self, timeout_ms=100):
        """
        Read the reply delay time (in ms) from the module.

        Returns:
            int | None: Delay in milliseconds, or None on timeout/failure.
        """
        data = self.bus.read(
            self.addr,
            self.type,
            self.subType,
            self.REG_REPLYDELAY,
            timeout_ms
        )

        if data is None or len(data) != 1:
            return None

        return data[0]

