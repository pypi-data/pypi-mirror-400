"""Codigos de error y descripciones para ID809"""
class Error:
    """Error codes and descriptions"""
    SUCCESS = 0x00
    FAIL = 0x01
    VERIFY = 0x10
    IDENTIFY = 0x11
    TMPL_EMPTY = 0x12
    TMPL_NOT_EMPTY = 0x13
    ALL_TMPL_EMPTY = 0x14
    EMPTY_ID_NOEXIST = 0x15
    BROKEN_ID_NOEXIST = 0x16
    INVALID_TMPL_DATA = 0x17
    DUPLICATION_ID = 0x18
    BAD_QUALITY = 0x19
    MERGE_FAIL = 0x1A
    NOT_AUTHORIZED = 0x1B
    MEMORY = 0x1C
    INVALID_TMPL_NO = 0x1D
    INVALID_PARAM = 0x22
    TIMEOUT = 0x23
    GEN_COUNT = 0x25
    INVALID_BUFFER_ID = 0x26
    FP_NOT_DETECTED = 0x28
    FP_CANCEL = 0x41
    RECV_LENGTH = 0x42
    RECV_CKS = 0x43
    GATHER_OUT = 0x45
    RECV_TIMEOUT = 0x46

    DESCRIPTIONS = {
        0x00: "Command processed successfully",
        0x01: "Command processing failed",
        0x10: "1:1 comparison failed",
        0x11: "Comparison with all fingerprints failed",
        0x12: "No fingerprint in designated ID",
        0x13: "Designated ID has fingerprint",
        0x14: "Module unregistered fingerprint",
        0x15: "No registerable ID here",
        0x16: "No broken fingerprint",
        0x17: "Invalid designated fingerprint data",
        0x18: "The fingerprint has been registered",
        0x19: "Poor quality fingerprint image",
        0x1A: "Fingerprint synthesis failed",
        0x1B: "Communication password not authorized",
        0x1C: "External Flash burning error",
        0x1D: "Invalid designated ID",
        0x22: "Incorrect parameter",
        0x23: "Acquisition timeout",
        0x25: "Invalid number of fingerprint synthesis",
        0x26: "Incorrect Buffer ID value",
        0x28: "No fingerprint input into fingerprint reader",
        0x41: "Command cancelled",
        0x42: "Wrong data length",
        0x43: "Wrong check code",
        0x45: "Exceed upper limit of acquisition times",
        0x46: "Communication timeout",
    }

    @staticmethod
    def get_description(code):
        """get error description"""
        return Error.DESCRIPTIONS.get(code, f"Unknown error: 0x{code:02X}")
