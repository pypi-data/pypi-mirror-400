"""Clase base para el sensor de huellas SEN0359"""

import time

from .constants import (
    FINGERPRINT_CAPACITY,
    CMD_TYPE,
    RCM_TYPE,
    DATA_TYPE,
    CMD_PREFIX_CODE,
    RCM_PREFIX_CODE,
    CMD_DATA_PREFIX_CODE,
    RCM_DATA_PREFIX_CODE,
    CMD_TEST_CONNECTION,
    CMD_SET_PARAM,
    CMD_GET_PARAM,
    CMD_DEVICE_INFO,
    CMD_ENTER_STANDBY_STATE,
    CMD_GET_IMAGE,
    CMD_FINGER_DETECT,
    CMD_SLED_CTRL,
    CMD_STORE_CHAR,
    CMD_DEL_CHAR,
    CMD_GET_EMPTY_ID,
    CMD_GET_STATUS,
    CMD_GET_ENROLL_COUNT,
    CMD_GENERATE,
    CMD_MERGE,
    CMD_MATCH,
    CMD_SEARCH,
    CMD_VERIFY,
    ERR_SUCCESS,
    ERR_ID809,
    DELALL,
)
from .errors import Error
from .led import LEDMode, LEDColor


class DFRobot_ID809:
    """Base class for ID809 fingerprint sensor"""

    def __init__(self):
        self._packet_size = 0
        self._buf = bytearray(20)
        self._number = 0  # Fingerprint acquisition times
        self._state = 0   # Collect fingerprint state
        self._error = Error.SUCCESS
        self.fingerprint_capacity = FINGERPRINT_CAPACITY
        self.ISIIC = True

    # metodos abstractos
    def send_packet(self, packet):
        """Send packet to sensor"""
        raise NotImplementedError

    def read_n(self, size):
        """Read n bytes from sensor"""
        raise NotImplementedError

    def begin(self):
        """Initialize sensor"""
        raise NotImplementedError

    def is_connected(self):
        """Check if module is connected"""
        header = self._pack(CMD_TYPE, CMD_TEST_CONNECTION, None, 0)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        ret = self._response_payload()
        return ret == ERR_SUCCESS

    def set_device_id(self, device_id):
        """Set device ID"""
        data = bytearray(5)
        data[1] = device_id
        return self._set_param(data)

    def set_security_level(self, level):
        """Set security level"""
        data = bytearray(5)
        data[0] = 1
        data[1] = level
        return self._set_param(data)

    def set_duplication_check(self, check):
        """Enable/disable duplicate check"""
        data = bytearray(5)
        data[0] = 2
        data[1] = check
        return self._set_param(data)

    def set_self_learn(self, enabled):
        """Enable/disable self-learning"""
        data = bytearray(5)
        data[0] = 4
        data[1] = enabled
        return self._set_param(data)

    def get_device_id(self):
        """Get device ID"""
        return self._get_param(0)

    def get_security_level(self):
        """Get security level"""
        return self._get_param(1)

    def get_duplication_check(self):
        """Get duplicate check status"""
        return self._get_param(2)

    def get_baudrate(self):
        """Get baudrate"""
        return self._get_param(3)

    def get_self_learn(self):
        """Get self-learning status"""
        return self._get_param(4)

    def get_device_info(self):
        """Get device information string"""
        header = self._pack(CMD_TYPE, CMD_DEVICE_INFO, None, 0)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        result = self._response_payload()
        if result != ERR_SUCCESS:
            return ""

        # lenght dle dato
        data_len = self._buf[0] + (self._buf[1] << 8) + 1

        data = self.read_n(data_len)
        if data:
            try:
                return data.decode("utf-8").rstrip("\x00")
            except (UnicodeDecodeError, AttributeError):
                return ""
        return ""

    def ctrl_led(self, mode, color, blink_count=0):
        """
        Control LED

        Args:
            mode: LEDMode constant
            color: LEDColor constant
            blink_count: Nº of blinks (0 = infinite)
        """
        data = bytearray(4)

        if self.fingerprint_capacity == 80:
            data[0] = mode
            data[1] = color
            data[2] = color
            data[3] = blink_count
        else:

            mode_map = {1: 2, 2: 4, 3: 1, 4: 0, 5: 3}
            data[0] = mode_map.get(mode, mode)

            color_map = {
                LEDColor.GREEN: 0x84,
                LEDColor.RED: 0x82,
                LEDColor.YELLOW: 0x86,
                LEDColor.BLUE: 0x81,
                LEDColor.CYAN: 0x85,
                LEDColor.MAGENTA: 0x83,
                LEDColor.WHITE: 0x87,
            }
            data[1] = data[2] = color_map.get(color, 0x87)

        header = self._pack(CMD_TYPE, CMD_SLED_CTRL, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        return self._response_payload()

    def detect_finger(self):
        """Detect if finger is on sensor"""
        header = self._pack(CMD_TYPE, CMD_FINGER_DETECT, None, 0)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(240)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return ret

    def get_empty_id(self):
        """Get first available ID for enrollment"""
        data = bytearray(4)
        data[0] = 1
        data[2] = self.fingerprint_capacity

        header = self._pack(CMD_TYPE, CMD_GET_EMPTY_ID, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(100)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return ret

    def get_status_id(self, id):
        """Check if ID is registered"""
        data = bytearray(2)
        data[0] = id

        header = self._pack(CMD_TYPE, CMD_GET_STATUS, data, 2)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return ret

    def get_enroll_count(self):
        """Get number of enrolled fingerprints"""
        data = bytearray(4)
        data[0] = 1
        data[2] = self.fingerprint_capacity

        header = self._pack(CMD_TYPE, CMD_GET_ENROLL_COUNT, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(80)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return ret

    def collection_fingerprint(self, timeout=5000):
        """
        Capture a fingerprint

        Args:
            timeout: Maximum wait time in ms

        Returns:
            ERR_SUCCESS or ERR_ID809
        """
        if self._number > 2:
            self._error = Error.GATHER_OUT
            return ERR_ID809

        i = 0
        while not self.detect_finger():
            time.sleep_ms(10)
            i += 1
            if i > timeout // 10:
                self._error = Error.TIMEOUT
                self._state = 0
                return ERR_ID809

        ret = self._get_image()
        if ret != ERR_SUCCESS:
            self._state = 0
            return ERR_ID809

        ret = self._generate(self._number)
        if ret != ERR_SUCCESS:
            self._state = 0
            return ERR_ID809

        self._number += 1
        self._state = 1
        return ret

    def store_fingerprint(self, id):
        """Store fingerprint at specified ID"""
        ret = self._merge()
        if ret != ERR_SUCCESS:
            return ERR_ID809

        self._number = 0
        data = bytearray(4)
        data[0] = id

        header = self._pack(CMD_TYPE, CMD_STORE_CHAR, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        return self._response_payload()

    def del_fingerprint(self, id):
        """Delete fingerprint (id) or all (DELALL)"""
        data = bytearray(4)
        if id == DELALL:
            data[0] = 1
            data[2] = self.fingerprint_capacity
        else:
            data[0] = data[2] = id

        header = self._pack(CMD_TYPE, CMD_DEL_CHAR, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        return self._response_payload()

    def search(self):
        """Search captured fingerprint in database"""
        if self._state != 1:
            return 0

        data = bytearray(6)
        data[2] = 1
        data[4] = self.fingerprint_capacity
        self._number = 0

        header = self._pack(CMD_TYPE, CMD_SEARCH, data, 6)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return 0

    def verify(self, id):
        """Verify captured fingerprint against specific ID"""
        if self._state != 1:
            return 0

        data = bytearray(4)
        data[0] = id
        self._number = 0

        header = self._pack(CMD_TYPE, CMD_VERIFY, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return 0

    def match(self, ram_buffer_id0, ram_buffer_id1):
        """Compare templates in two RAM buffers"""
        data = bytearray(4)
        data[0] = ram_buffer_id0
        data[2] = ram_buffer_id1

        header = self._pack(CMD_TYPE, CMD_MATCH, data, 4)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(100)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return 0

    def enter_sleep_state(self):
        """Enter low power mode"""
        header = self._pack(CMD_TYPE, CMD_ENTER_STANDBY_STATE, None, 0)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        return self._response_payload()

    def get_error_description(self):
        """Get description of last error"""
        return Error.get_description(self._error)

    
    def _set_param(self, data):
        header = self._pack(CMD_TYPE, CMD_SET_PARAM, data, 5)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(240)

        return self._response_payload()

    def _get_param(self, param_type):
        data = bytearray([param_type])
        header = self._pack(CMD_TYPE, CMD_GET_PARAM, data, 1)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(50)

        ret = self._response_payload()
        if ret == ERR_SUCCESS:
            return self._buf[0]
        return ret

    def _get_image(self):
        header = self._pack(CMD_TYPE, CMD_GET_IMAGE, None, 0)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        return self._response_payload()

    def _generate(self, ram_buffer_id):
        data = bytearray(2)
        data[0] = ram_buffer_id

        header = self._pack(CMD_TYPE, CMD_GENERATE, data, 2)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        return self._response_payload()

    def _merge(self):
        data = bytearray(3)
        data[2] = self._number

        header = self._pack(CMD_TYPE, CMD_MERGE, data, 3)
        self.send_packet(header)

        if self.ISIIC:
            time.sleep_ms(360)

        return self._response_payload()

    def _pack(self, pkt_type, cmd, payload, length):
        """
        Build command packet
        Structure: PREFIX(2) + SID(1) + DID(1) + CMD(2) + LEN(2) + PAYLOAD + CKS(2)
        """
        if pkt_type == CMD_TYPE:
            data_len = 16
            packet = bytearray(10 + data_len + 2)
            prefix = CMD_PREFIX_CODE
        else:
            data_len = length
            packet = bytearray(10 + data_len + 2)
            prefix = CMD_DATA_PREFIX_CODE

        # PREFIX 
        packet[0] = prefix & 0xFF
        packet[1] = (prefix >> 8) & 0xFF

        # SID, DID
        packet[2] = 0  # SID
        packet[3] = 0  # DID

        # CMD 
        packet[4] = cmd & 0xFF
        packet[5] = (cmd >> 8) & 0xFF

        # LEN 
        packet[6] = length & 0xFF
        packet[7] = (length >> 8) & 0xFF

        # Payload
        if payload and length > 0:
            for i in range(min(length, len(payload))):
                packet[8 + i] = payload[i]

        # Calcula CKS
        cks = self._calc_cmd_cks(packet, data_len)
        packet[8 + data_len] = cks & 0xFF
        packet[9 + data_len] = (cks >> 8) & 0xFF

        self._packet_size = 10 + data_len + 2
        return packet

    def _calc_cmd_cks(self, packet, data_len):
        """Calculate command checksum"""
        cks = 0xFF
        cks += packet[2]  # SID
        cks += packet[3]  # DID
        cks += packet[4]  # CMD low
        cks += packet[5]  # CMD high
        cks += packet[6]  # LEN low
        cks += packet[7]  # LEN high

        length = packet[6] + (packet[7] << 8)
        for i in range(length):
            cks += packet[8 + i]

        return cks & 0xFFFF

    def _calc_rcm_cks(self, sid, did, rcm, length, ret, payload):
        """Calculate response checksum"""
        cks = 0xFF
        cks += sid
        cks += did
        cks += rcm & 0xFF
        cks += (rcm >> 8) & 0xFF
        cks += length & 0xFF
        cks += (length >> 8) & 0xFF
        cks += ret & 0xFF
        cks += (ret >> 8) & 0xFF

        if payload and length > 0:
            for i in range(length - 2):
                cks += payload[i]

        return cks & 0xFFFF

    def _read_prefix(self):
        """
        Read and parse response prefix
        Returns: (type, header_dict) or (1, None) on timeout
        """
        RECV_HEADER_INIT = 0
        RECV_HEADER_AA = 1
        RECV_HEADER_A5 = 2
        RECV_HEADER_OK = 3

        state = RECV_HEADER_INIT
        ret_type = None
        start = time.ticks_ms()

        while state != RECV_HEADER_OK:
            data = self.read_n(1)
            if not data or len(data) != 1:
                return (1, None)

            ch = data[0]

            if ch == 0xAA and state == RECV_HEADER_INIT:
                state = RECV_HEADER_AA
            elif ch == 0xA5 and state == RECV_HEADER_INIT:
                state = RECV_HEADER_A5
            elif ch == 0x55 and state == RECV_HEADER_AA:
                state = RECV_HEADER_OK
                ret_type = RCM_TYPE
            elif ch == 0x5A and state == RECV_HEADER_A5:
                state = RECV_HEADER_OK
                ret_type = DATA_TYPE
            else:
                state = RECV_HEADER_INIT
                if ch == 0xAA:
                    state = RECV_HEADER_AA
                elif ch == 0xA5:
                    state = RECV_HEADER_A5

                if time.ticks_diff(time.ticks_ms(), start) > 2000:
                    return (1, None)

        # lee el resto d el acabecera
        header_data = self.read_n(8)
        if not header_data or len(header_data) != 8:
            return (1, None)

        header = {
            "PREFIX": RCM_PREFIX_CODE if ret_type == RCM_TYPE else RCM_DATA_PREFIX_CODE,
            "SID": header_data[0],
            "DID": header_data[1],
            "RCM": header_data[2] + (header_data[3] << 8),
            "LEN": header_data[4] + (header_data[5] << 8),
            "RET": header_data[6] + (header_data[7] << 8),
        }

        return (ret_type, header)

    def _response_payload(self):
        """Read and process sensor response"""
        ret_type, header = self._read_prefix()

        if ret_type == 1 or header is None:
            self._error = Error.RECV_TIMEOUT
            return ERR_ID809

        if ret_type == RCM_TYPE:
            data_len = 14 + 2  
        else:
            data_len = header["LEN"]

        # lee payload
        payload = self.read_n(data_len)
        if not payload or len(payload) != data_len:
            self._error = Error.RECV_LENGTH
            return ERR_ID809

        # verifica CKS
        cks_received = payload[data_len - 2] + (payload[data_len - 1] << 8)
        cks_calculated = self._calc_rcm_cks(
            header["SID"],
            header["DID"],
            header["RCM"],
            header["LEN"],
            header["RET"],
            payload,
        )

        ret = header["RET"] & 0xFF
        self._error = ret

        if ret != ERR_SUCCESS:
            return ERR_ID809
        elif cks_received != cks_calculated:
            self._error = Error.RECV_CKS
            return ERR_ID809
        else:
            # volcar al buffer
            for i in range(min(len(self._buf), data_len)):
                self._buf[i] = payload[i]
            return ERR_SUCCESS
