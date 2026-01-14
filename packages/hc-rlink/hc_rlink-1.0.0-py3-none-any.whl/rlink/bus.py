import RPi.GPIO as GPIO
import serial
import time

# Mapping from baud index (0–7) to actual baud rate
BAUD_INDEX_TO_RATE = {
    0: 1200,
    1: 2400,
    2: 4800,
    3: 9600,
    4: 19200,
    5: 38400,
    6: 57600,
    7: 115200,
}



def crc8(data: bytes) -> int:
    """
    Compute CRC-8 using polynomial 0x07.

    Parameters:
        data (bytes): Data over which to compute CRC.

    Returns:
        int: CRC-8 value.
    """

    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc



class RLinkBus:
    """Handles RS485 serial communication and optional TX/RX direction control."""

    CMD_WRITE = 0x01
    CMD_READ =  0x02
    CMD_REPLY = 0x03
    CMD_ERROR = 0xFF

    def __init__(self, port, dir_pin=None, baud_index=3):
        """
        Initialize the RLinkBus.

        Parameters:
            port (str): Serial port device name.
            dir_pin (int or None): GPIO pin for TX/RX direction (optional).
            baud_index (int): Index into BAUD_INDEX_TO_RATE (default 3 = 9600).
        """
        
        # Validate baud index
        if baud_index not in BAUD_INDEX_TO_RATE:
            raise ValueError("Invalid baud index (0–7)")

        self.baud_index = baud_index
        baudrate = BAUD_INDEX_TO_RATE[baud_index]
        
        # Open serial port
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.dir_pin = dir_pin
        
        # Configure GPIO for TX/RX direction if provided
        if dir_pin is not None:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(dir_pin, GPIO.OUT)
            GPIO.output(dir_pin, GPIO.LOW)  # Receive mode



    def send(self, frame: bytes):
        """
        Send a frame over the bus, appending CRC, and toggling TX/RX direction.

        Parameters:
            frame (bytes): Bytes to send (without CRC).

        Returns:
            None
        """
        # Clear any pending input
        self.ser.reset_input_buffer()
        # Enable transmit
        #self._tx_enable()
        if self.dir_pin is not None:
            GPIO.output(self.dir_pin, GPIO.HIGH)

        # 1ms settling time
        time.sleep(0.001)

        # Append CRC8 (excluding SOF)
        crc = crc8(frame[1:])
        frame = frame + bytes([crc])

        # Send the frame
        self.ser.write(frame)

        #self.ser.flush()  #Flushing takes ~30ms - too long!
        
        # Approximate time to send frame at current baud rate
        # Each byte ≈ 10 bits (start + 8 data + stop)
        approx_time = len(frame) * 10 / self.ser.baudrate
        
        # Add 10% safety margin or 1 ms minimum
        approx_time = max(approx_time * 1.1, 0.001)

        time.sleep(approx_time)

        # Re-enable receive mode
        #self._rx_enable()
        if self.dir_pin is not None:
            GPIO.output(self.dir_pin, GPIO.LOW)
        
 
 
    def request(self, addr, typ, sub, reg):
        """
        Send a READ request frame to a module.

        Parameters:
            addr (int): Module address (0–127 or 0xFF for wildcard)
           typ (int): Module type (or 0xFF if unknown)
            sub (int): Module subtype (or 0xFF if unknown)
            reg (int): Register to read
        """
        
        # READ command = 0x02, payload length = 0
        frame = bytes([
            0x55,            # SOF
            addr,
            typ,
            sub,
            self.CMD_READ,   # CMD_READ
            reg,
            0x00             # LEN
        ])

        self.send(frame)
    


    def receive(self, expect_addr, expect_type, expect_subtype,
            expect_reg, timeout_ms=100):
        """
        Receive a frame from the bus, resyncing on CRC/header errors.

        Accepts:
          - CMD_REPLY (0x03)
          - CMD_ERROR (0xFF)

        Wildcards (0xFF) may be used for address, type, or subtype.

        Returns:
            bytes | None: Full frame if valid reply or error, otherwise None.
        """
        self.ser.reset_input_buffer()
        deadline = time.monotonic() + (timeout_ms / 1000.0)
        frame = b''
        size = None

        while time.monotonic() < deadline:
            b = self.ser.read(1)
            if not b:
                continue

            # Start of new frame
            if not frame and b[0] != 0x55:
                continue
            frame += b

            # Once header is complete, calculate full frame size
            if len(frame) == 7:
                size = frame[6] + 8
                #print(f"DEBUG: Expected frame size = {size}")

            # Once full frame is collected
            if size is not None and len(frame) >= size:
                #print("DEBUG: Full frame received:")
                #print(" ".join(f"0x{b:02X}" for b in frame[:size]))

                # CRC check
                calc_crc = crc8(frame[1:size-1])
                recv_crc = frame[size-1]
                if calc_crc != recv_crc:
                    #print(f"DEBUG: CRC FAIL (calc=0x{calc_crc:02X}, recv=0x{recv_crc:02X})")
                    
                    # CRC not valid so search for next SOF in the remainder
                    remainder = frame[1:]
                    next_sof_index = remainder.find(b'\x55')
                    if next_sof_index >= 0:
                        frame = remainder[next_sof_index:]
                        size = None
                    else:
                        frame = b''
                        size = None
                    continue
                #else:
                #    print("DEBUG: CRC OK")

                # Header checks
                addr, typ, sub, cmd, reg, length = frame[1:7]
                if ((expect_addr != 0xFF and addr != expect_addr) or
                    (expect_type != 0xFF and typ != expect_type) or
                    (expect_subtype != 0xFF and sub != expect_subtype) or
                    (reg != expect_reg) or
                    (cmd not in (self.CMD_REPLY, 0xFF))):
                    
                    #print("DEBUG: Header mismatch, resyncing...")
                    # Frame not valid so search for next SOF in the remainder
                    remainder = frame[1:]
                    next_sof_index = remainder.find(b'\x55')
                    if next_sof_index >= 0:
                        frame = remainder[next_sof_index:]
                        size = None
                    else:
                        frame = b''
                        size = None
                    continue

                # Valid frame
                return frame[:size]

        #print("DEBUG: Timeout waiting for full frame")
        return None



    def read(self, addr, typ, sub, reg, timeout_ms=100):
        """
        Send a READ request and wait for a validated reply.

        Returns:
            bytes | None: Payload bytes if successful, otherwise None.
        """
        self.request(addr, typ, sub, reg)

        frame = self.receive(
            expect_addr=addr,
            expect_type=typ,
            expect_subtype=sub,
            expect_reg=reg,
            timeout_ms=timeout_ms
        )

        if frame is None:
            return None

        length = frame[6]
        payload_start = 7
        return frame[payload_start:payload_start + length]




    def set_baud(self, baud_index: int):
        """
        Change the bus baud rate (for communication). Does not affect modules.

        Parameters:
            baud_index (int): Index into BAUD_INDEX_TO_RATE (0–7).

        Returns:
            None
        """
        if baud_index not in BAUD_INDEX_TO_RATE:
            raise ValueError("Invalid baud index (0–7)")

        self.ser.baudrate = BAUD_INDEX_TO_RATE[baud_index]

