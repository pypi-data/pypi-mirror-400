import ctypes
from enum import IntEnum

# Typedefs

class HLML_AFFINITY_SCOPE_T:
	TYPE = ctypes.c_uint

class HLML_DEVICE_T:
	TYPE = ctypes.c_void_p

class HLML_EVENT_SET_T:
	TYPE = ctypes.c_void_p


# Enums

class HLML_RETURN(IntEnum):
	HLML_SUCCESS = 0
	HLML_ERROR_UNINITIALIZED = 1
	HLML_ERROR_INVALID_ARGUMENT = 2
	HLML_ERROR_NOT_SUPPORTED = 3
	HLML_ERROR_ALREADY_INITIALIZED = 5
	HLML_ERROR_NOT_FOUND = 6
	HLML_ERROR_INSUFFICIENT_SIZE = 7
	HLML_ERROR_DRIVER_NOT_LOADED = 9
	HLML_ERROR_TIMEOUT = 10
	HLML_ERROR_AIP_IS_LOST = 15
	HLML_ERROR_MEMORY = 20
	HLML_ERROR_NO_DATA = 21
	HLML_ERROR_UNKNOWN = 49

class HLML_CLOCK_TYPE(IntEnum):
	HLML_CLOCK_SOC = 0
	HLML_CLOCK_IC = 1
	HLML_CLOCK_MME = 2
	HLML_CLOCK_TPC = 3
	HLML_CLOCK_COUNT = 4

class HLML_TEMPERATURE_SENSORS(IntEnum):
	HLML_TEMPERATURE_ON_AIP = 0
	HLML_TEMPERATURE_ON_BOARD = 1
	HLML_TEMPERATURE_OTHER = 2
	HLML_TEMPERATURE_HBM = 3
	HLML_TEMPERATURE_VRM = 4
	HLML_TEMPERATURE_CTEMP = 5

class HLML_TEMPERATURE_THRESHOLDS(IntEnum):
	HLML_TEMPERATURE_THRESHOLD_SHUTDOWN = 0
	HLML_TEMPERATURE_THRESHOLD_SLOWDOWN = 1
	HLML_TEMPERATURE_THRESHOLD_MEM_MAX = 2
	HLML_TEMPERATURE_THRESHOLD_GPU_MAX = 3
	HLML_TEMPERATURE_THRESHOLD_COUNT = 4

class HLML_ENABLE_STATE(IntEnum):
	HLML_FEATURE_DISABLED = 0
	HLML_FEATURE_ENABLED = 1

class HLML_P_STATES(IntEnum):
	HLML_PSTATE_0 = 0
	HLML_PSTATE_1 = 1
	HLML_PSTATE_2 = 2
	HLML_PSTATE_3 = 3
	HLML_PSTATE_4 = 4
	HLML_PSTATE_5 = 5
	HLML_PSTATE_6 = 6
	HLML_PSTATE_7 = 7
	HLML_PSTATE_8 = 8
	HLML_PSTATE_9 = 9
	HLML_PSTATE_10 = 10
	HLML_PSTATE_11 = 11
	HLML_PSTATE_12 = 12
	HLML_PSTATE_13 = 13
	HLML_PSTATE_14 = 14
	HLML_PSTATE_15 = 15
	HLML_PSTATE_SENTINEL = 16
	HLML_PSTATE_UNKNOWN = 32

class HLML_MEMORY_ERROR_TYPE(IntEnum):
	HLML_MEMORY_ERROR_TYPE_CORRECTED = 0
	HLML_MEMORY_ERROR_TYPE_UNCORRECTED = 1
	HLML_MEMORY_ERROR_TYPE_COUNT = 2

class HLML_MEMORY_LOCATION_TYPE(IntEnum):
	HLML_MEMORY_LOCATION_SRAM = 0
	HLML_MEMORY_LOCATION_DRAM = 1
	HLML_MEMORY_LOCATION_ALL = 2
	HLML_MEMORY_LOCATION_COUNT = 3

class HLML_ECC_COUNTER_TYPE(IntEnum):
	HLML_VOLATILE_ECC = 0
	HLML_AGGREGATE_ECC = 1
	HLML_ECC_COUNTER_TYPE_COUNT = 2

class HLML_ERR_COUNTER_IDX(IntEnum):
	HLML_ECC_SERR_COUNTER_IDX = 0
	HLML_ECC_DERR_COUNTER_IDX = 1
	HLML_ECC_HBM_SERR_COUNTER_IDX = 2
	HLML_ECC_HBM_DERR_COUNTER_IDX = 3
	HLML_ECC_CRITICAL_COUNTER_IDX = 4
	HLML_ECC_ERR_COUNTER_MAX = 5

class HLML_PCIE_UTIL_COUNTER(IntEnum):
	HLML_PCIE_UTIL_TX_BYTES = 0
	HLML_PCIE_UTIL_RX_BYTES = 1
	HLML_PCIE_UTIL_COUNT = 2

class HLML_PERF_POLICY_TYPE(IntEnum):
	HLML_PERF_POLICY_POWER = 0
	HLML_PERF_POLICY_THERMAL = 1
	HLML_PERF_POLICY_COUNT = 2

class HLML_ROW_REPLACEMENT_CAUSE(IntEnum):
	HLML_ROW_REPLACEMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = 0
	HLML_ROW_REPLACEMENT_CAUSE_DOUBLE_BIT_ECC_ERROR = 1
	HLML_ROW_REPLACEMENT_CAUSE_COUNT = 2


# Structs

class _PrintS(ctypes.Structure):
    """
    Produces nicer __str__ output than ctypes.Structure.

    e.g. instead of:

    > print str(obj)
    <class_name object at 0x7fdf82fef9e0>

    this class will print...

    > print str(obj)
    class_name(field_name: formatted_value, field_name: formatted_value)
    _fmt_ dictionary of <str _field_ name> -> <str format>

    Default formatting string for all fields can be set with key "<default>" like:
      _fmt_ = {"<default>" : "%d MHz"} # e.g all values are numbers in MHz.

    If not set it's assumed to be just "%s"

    e.g. class that has _field_ 'hex_value', c_uint could be formatted with
      _fmt_ = {"hex_value" : "%08X"}
    to produce nicer output.
    """
    _fmt_ = {}
    def __str__(self):
        result = []
        for x in self._fields_:
            key = x[0]
            value = getattr(self, key)
            fmt = "%s"
            if key in self._fmt_:
                fmt = self._fmt_[key]
            elif "<default>" in self._fmt_:
                fmt = self._fmt_["<default>"]
            result.append(("%s: " + fmt) % (key, value))
        return self.__class__.__name__ + "(" +  ", ".join(result) + ")"

class c_hlml_pci_cap(_PrintS):
    _fields_ = [
        ("link_speed", (ctypes.c_char * 10)),
        ("link_width", (ctypes.c_char * 10)),
        ("link_max_speed", (ctypes.c_char * 10)),
        ("link_max_width", (ctypes.c_char * 10))
    ]

class c_hlml_pci_info(_PrintS):
    _fields_ = [
        ("bus", ctypes.c_uint),
        ("bus_id", (ctypes.c_char * 19)),
        ("device", ctypes.c_uint),
        ("domain", ctypes.c_uint),
        ("pci_device_id", ctypes.c_uint),
        ("caps", c_hlml_pci_cap),
        ("pci_rev", ctypes.c_uint),
        ("pci_subsys_id", ctypes.c_uint)
    ]

class c_hlml_utilization(_PrintS):
    _fields_ = [
        ("aip", ctypes.c_uint),
        ("memory", ctypes.c_uint)
    ]

class c_hlml_memory(_PrintS):
    _fields_ = [
        ("free", ctypes.c_ulonglong),
        ("total", ctypes.c_ulonglong),
        ("used", ctypes.c_ulonglong)
    ]

class c_hlml_pcb_info(_PrintS):
    _fields_ = [
        ("pcb_ver", (ctypes.c_char * 32)),
        ("pcb_assembly_ver", (ctypes.c_char * 32))
    ]

class c_hlml_event_data(_PrintS):
    _fields_ = [
        ("device", ctypes.c_void_p),
        ("event_type", ctypes.c_ulonglong)
    ]

class c_hlml_mac_info(_PrintS):
    _fields_ = [
        ("addr", (ctypes.c_ubyte * 6)),
        ("id", ctypes.c_int)
    ]

class c_hlml_nic_stats_info(_PrintS):
    _fields_ = [
        ("port", ctypes.c_uint32),
        ("str_buf", ctypes.POINTER(ctypes.c_char)),
        ("val_buf", ctypes.POINTER(ctypes.c_uint64)),
        ("num_of_counters_out", ctypes.POINTER(ctypes.c_uint32))
    ]

class c_hlml_violation_time(_PrintS):
    _fields_ = [
        ("reference_time", ctypes.c_ulonglong),
        ("violation_time", ctypes.c_ulonglong)
    ]

class c_hlml_row_address(_PrintS):
    _fields_ = [
        ("hbm_idx", ctypes.c_uint8),
        ("pc", ctypes.c_uint8),
        ("sid", ctypes.c_uint8),
        ("bank_idx", ctypes.c_uint8),
        ("row_addr", ctypes.c_uint16)
    ]

class c_hlml_aip_error_counters(_PrintS):
    _fields_ = [
        ("err_counters", (ctypes.c_ulonglong * HLML_ERR_COUNTER_IDX.HLML_ECC_ERR_COUNTER_MAX)),
        ("index", ctypes.c_uint)
    ]

class c_hlml_process_utilization_sample(_PrintS):
    _fields_ = [
        ("aip_util", ctypes.c_uint)
    ]


 # Defines

class HLML_DEFINES:
	PCI_DOMAIN_LEN = 9
	PCI_ADDR_LEN = ((PCI_DOMAIN_LEN) + 10)
	PCI_LINK_INFO_LEN = 10
	HL_FIELD_MAX_SIZE = 32
	ETHER_ADDR_LEN = 6
	PORTS_ARR_SIZE = 2
	HLML_DEVICE_MAC_MAX_ADDRESSES = 48
	HLML_DEVICE_ROW_RPL_MAX = 32
	HLML_EVENT_ECC_ERR = (1 << 0)
	HLML_EVENT_ECC_DERR = (1 << 0)
	HLML_EVENT_CRITICAL_ERR = (1 << 1)
	HLML_EVENT_CLOCK_RATE = (1 << 2)
	HLML_EVENT_DRAM_ERR = (1 << 3)
	HLML_EVENT_DRAM_DERR = (1 << 3)
	HLML_EVENT_ECC_SERR = (1 << 4)
	HLML_EVENT_DRAM_SERR = (1 << 5)
	HLML_CLOCKS_THROTTLE_REASON_POWER = (1 << 0)
	HLML_CLOCKS_THROTTLE_REASON_THERMAL = (1 << 1)
	HLML_AFFINITY_SCOPE_NODE = 0
	HLML_AFFINITY_SCOPE_SOCKET = 1
	HLML_PSTATE_NUM_SUPPORTED = HLML_P_STATES.HLML_PSTATE_SENTINEL