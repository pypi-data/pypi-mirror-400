"""Implementación I2C para el sensor SEN0359"""

import time
from machine import I2C, Pin

from .base import DFRobot_ID809


# Direccion I2C por default
ID809_I2C_ADDR = 0x1F


class DFRobot_ID809_I2C(DFRobot_ID809):
    """I2C implementation for ID809 fingerprint sensor"""

    DEFAULT_ADDRESS = ID809_I2C_ADDR

    def __init__(self, i2c, addr=ID809_I2C_ADDR):
        """
        Initialize I2C sensor

        Args:
            i2c: I2C object
            addr: I2C address (default 0x1F)
        """
        super().__init__()
        self._i2c = i2c
        self._addr = addr
        self.ISIIC = True

    def begin(self):
        """
        Initialize communication with sensor

        Returns:
            bool: True if initialization successful
        """
        # comprobamos si el sensor esta en el bus i2c
        devices = self._i2c.scan()
        if self._addr not in devices:
            print(f"Sensor not found at 0x{self._addr:02X}")
            print(f"Devices found: {[hex(d) for d in devices]}")
            return False

        # informe de la capacidad segun el modelo
        info = self.get_device_info()
        if info:
            if len(info) > 0 and info[-1] == "4":
                self.fingerprint_capacity = 80
            elif len(info) > 0 and info[-1] == "3":
                self.fingerprint_capacity = 200

        return True

    def send_packet(self, packet):
        """
        send packet to sensor

        Args:
            packet: bytearray with packet to send
        """
        if packet is None:
            return

        # Wait until sensor is ready 
        max_retries = 100
        for _ in range(max_retries):
            try:
                data = self._i2c.readfrom(self._addr, 1)
                if data[0] == 0xEE:
                    # sensor busy, keep waiting
                    continue
                else:
                    # sensor ready or has data
                    break
            except OSError:
                pass
            time.sleep_ms(10)

        
        try:
            self._i2c.readfrom(self._addr, 1) # read any pending data
        except OSError:
            pass

        # send packet
        try:
            self._i2c.writeto(self._addr, packet)
        except OSError as e:
            print(f"Error sending packet: {e}")

    def read_n(self, size):
        """
        Read n bytes from sensor

        Args:
            size: Number of bytes to read

        Returns:
            bytearray with data read or None on error
        """
        result = bytearray(size)
        idx = 0

        try:
            # read in chunks of 32 bytes max (I2C limitation)
            remaining = size
            while remaining > 32:
                chunk = self._i2c.readfrom(self._addr, 32)
                for b in chunk:
                    if idx < size:
                        result[idx] = b
                        idx += 1
                remaining -= 32

            # read remaining bytes one by one (as in original library)
            for i in range(remaining):
                data = self._i2c.readfrom(self._addr, 1)
                if idx < size:
                    result[idx] = data[0]
                    idx += 1

            return result

        except OSError as e:
            print(f"Error reading data: {e}")
            return None


def create_sensor(scl_pin, sda_pin, i2c_id=1, freq=100000, addr=ID809_I2C_ADDR):
    """
    Factory function to create sensor with new I2C bus

    Args:
        scl_pin: SCL pin number
        sda_pin: SDA pin number
        i2c_id: I2C peripheral ID (0 or 1)
        freq: I2C frequency (default 100kHz)
        addr: Sensor I2C address

    Returns:
        DFRobot_ID809_I2C instance or None on failure
    """
    try:
        i2c = I2C(i2c_id, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=freq)
        sensor = DFRobot_ID809_I2C(i2c, addr)

        if sensor.begin():
            return sensor
        else:
            return None

    except Exception as e:
        print(f"Error creating sensor: {e}")
        return None
