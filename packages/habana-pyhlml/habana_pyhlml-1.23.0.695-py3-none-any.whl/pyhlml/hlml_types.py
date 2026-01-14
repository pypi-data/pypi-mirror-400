"""
Python bindings for HLML types
"""
import warnings
warnings.warn(
    "pyhlml.hlml_types is deprecated and will be removed in a future release. "
    "Please use pyhlml.pyhlml_types_generated directly.",
    DeprecationWarning,
    stacklevel=2    # Level 2 to point to the import statement in the user's code
)

import ctypes

import pyhlml.pyhlml_types_generated as newpy

class HLML_DEVICE:
    TYPE                                    = ctypes.c_void_p

class HLML_DEFINE:
    PCI_DOMAIN_LEN                          = newpy.HLML_DEFINES.PCI_DOMAIN_LEN
    PCI_ADDR_LEN                            = newpy.HLML_DEFINES.PCI_ADDR_LEN
    PCI_LINK_INFO_LEN                       = newpy.HLML_DEFINES.PCI_LINK_INFO_LEN
    HL_FIELD_MAX_SIZE                       = newpy.HLML_DEFINES.HL_FIELD_MAX_SIZE
    PORTS_ARR_SIZE                          = newpy.HLML_DEFINES.PORTS_ARR_SIZE
    HLML_DEVICE_ROW_RPL_MAX                 = newpy.HLML_DEFINES.HLML_DEVICE_ROW_RPL_MAX
    HLML_DEVICE_MAC_MAX_ADDRESSES           = newpy.HLML_DEFINES.HLML_DEVICE_MAC_MAX_ADDRESSES
    HLML_EVENT_ECC_ERR                      = newpy.HLML_DEFINES.HLML_EVENT_ECC_ERR
    HLML_EVENT_ECC_DERR                     = newpy.HLML_DEFINES.HLML_EVENT_ECC_DERR
    HLML_EVENT_CRITICAL_ERR                 = newpy.HLML_DEFINES.HLML_EVENT_CRITICAL_ERR
    HLML_EVENT_CLOCK_RATE                   = newpy.HLML_DEFINES.HLML_EVENT_CLOCK_RATE
    HLML_EVENT_DRAM_ERR                     = newpy.HLML_DEFINES.HLML_EVENT_DRAM_ERR
    HLML_EVENT_DRAM_DERR                    = newpy.HLML_DEFINES.HLML_EVENT_DRAM_DERR
    HLML_EVENT_ECC_SERR                     = newpy.HLML_DEFINES.HLML_EVENT_ECC_SERR
    HLML_EVENT_DRAM_SERR                    = newpy.HLML_DEFINES.HLML_EVENT_DRAM_SERR
    HLML_CLOCKS_THROTTLE_REASON_POWER       = newpy.HLML_DEFINES.HLML_CLOCKS_THROTTLE_REASON_POWER
    HLML_CLOCKS_THROTTLE_REASON_THERMAL     = newpy.HLML_DEFINES.HLML_CLOCKS_THROTTLE_REASON_THERMAL
    HLML_AFFINITY_SCOPE_NODE                = newpy.HLML_DEFINES.HLML_AFFINITY_SCOPE_NODE
    HLML_AFFINITY_SCOPE_SOCKET              = newpy.HLML_DEFINES.HLML_AFFINITY_SCOPE_SOCKET

class COMMON_DEFINE:
    VERSION_MAX_LEN                         = 128
    ETHER_ADDR_LEN                          = 6
    HABANA_LINK_CNT_MAX_NUM                 = 256
    STATUS_MAX_LEN                          = 30

# Duplicate values from "defines" class, kept for legacy reasons
class HLML_AFFINITY_SCOPE:
    TYPE                                    = ctypes.c_uint
    HLML_AFFINITY_SCOPE_NODE                = newpy.HLML_DEFINES.HLML_AFFINITY_SCOPE_NODE
    HLML_AFFINITY_SCOPE_SOCKET              = newpy.HLML_DEFINES.HLML_AFFINITY_SCOPE_SOCKET

class HLML_RETURN:
    TYPE                                    = ctypes.c_uint
    HLML_SUCCESS                            = newpy.HLML_RETURN.HLML_SUCCESS
    HLML_ERROR_UNINITIALIZED                = newpy.HLML_RETURN.HLML_ERROR_UNINITIALIZED
    HLML_ERROR_INVALID_ARGUMENT             = newpy.HLML_RETURN.HLML_ERROR_INVALID_ARGUMENT
    HLML_ERROR_NOT_SUPPORTED                = newpy.HLML_RETURN.HLML_ERROR_NOT_SUPPORTED
    HLML_ERROR_ALREADY_INITIALIZED          = newpy.HLML_RETURN.HLML_ERROR_ALREADY_INITIALIZED
    HLML_ERROR_NOT_FOUND                    = newpy.HLML_RETURN.HLML_ERROR_NOT_FOUND
    HLML_ERROR_INSUFFICIENT_SIZE            = newpy.HLML_RETURN.HLML_ERROR_INSUFFICIENT_SIZE
    HLML_ERROR_DRIVER_NOT_LOADED            = newpy.HLML_RETURN.HLML_ERROR_DRIVER_NOT_LOADED
    HLML_ERROR_TIMEOUT                      = newpy.HLML_RETURN.HLML_ERROR_TIMEOUT
    HLML_ERROR_AIP_IS_LOST                  = newpy.HLML_RETURN.HLML_ERROR_AIP_IS_LOST
    HLML_ERROR_MEMORY                       = newpy.HLML_RETURN.HLML_ERROR_MEMORY
    HLML_ERROR_NO_DATA                      = newpy.HLML_RETURN.HLML_ERROR_NO_DATA
    HLML_ERROR_UNKNOWN                      = newpy.HLML_RETURN.HLML_ERROR_UNKNOWN

class HLML_CLOCK_TYPE:
    TYPE                                    = ctypes.c_uint
    HLML_CLOCK_SOC                          = newpy.HLML_CLOCK_TYPE.HLML_CLOCK_SOC
    HLML_CLOCK_IC                           = newpy.HLML_CLOCK_TYPE.HLML_CLOCK_IC
    HLML_CLOCK_MME                          = newpy.HLML_CLOCK_TYPE.HLML_CLOCK_MME
    HLML_CLOCK_TPC                          = newpy.HLML_CLOCK_TYPE.HLML_CLOCK_TPC
    HLML_CLOCK_COUNT                        = newpy.HLML_CLOCK_TYPE.HLML_CLOCK_COUNT

class HLML_TEMP_SENS:
    TYPE                                    = ctypes.c_uint
    HLML_TEMPERATURE_ON_AIP                 = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_ON_AIP
    HLML_TEMPERATURE_ON_BOARD               = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_ON_BOARD
    HLML_TEMPERATURE_OTHER                  = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_OTHER
    HLML_TEMPERATURE_HBM                    = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_HBM
    HLML_TEMPERATURE_VRM                    = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_VRM
    HLML_TEMPERATURE_CTEMP                  = newpy.HLML_TEMPERATURE_SENSORS.HLML_TEMPERATURE_CTEMP

class HLML_TEMP_THRESH:
    TYPE                                    = ctypes.c_uint
    HLML_TEMPERATURE_THRESHOLD_SHUTDOWN     = newpy.HLML_TEMPERATURE_THRESHOLDS.HLML_TEMPERATURE_THRESHOLD_SHUTDOWN
    HLML_TEMPERATURE_THRESHOLD_SLOWDOWN     = newpy.HLML_TEMPERATURE_THRESHOLDS.HLML_TEMPERATURE_THRESHOLD_SLOWDOWN
    HLML_TEMPERATURE_THRESHOLD_MEM_MAX      = newpy.HLML_TEMPERATURE_THRESHOLDS.HLML_TEMPERATURE_THRESHOLD_MEM_MAX
    HLML_TEMPERATURE_THRESHOLD_GPU_MAX      = newpy.HLML_TEMPERATURE_THRESHOLDS.HLML_TEMPERATURE_THRESHOLD_GPU_MAX
    HLML_TEMPERATURE_THRESHOLD_COUNT        = newpy.HLML_TEMPERATURE_THRESHOLDS.HLML_TEMPERATURE_THRESHOLD_COUNT

class HLML_ENABLE_STATE:
    TYPE                                    = ctypes.c_uint
    HLML_FEATURE_DISABLED                   = newpy.HLML_ENABLE_STATE.HLML_FEATURE_DISABLED
    HLML_FEATURE_ENABLED                    = newpy.HLML_ENABLE_STATE.HLML_FEATURE_ENABLED

class HLML_P_STATES:
    TYPE                                    = ctypes.c_uint
    HLML_PSTATE_0                           = newpy.HLML_P_STATES.HLML_PSTATE_0
    HLML_PSTATE_1                           = newpy.HLML_P_STATES.HLML_PSTATE_1
    HLML_PSTATE_2                           = newpy.HLML_P_STATES.HLML_PSTATE_2
    HLML_PSTATE_3                           = newpy.HLML_P_STATES.HLML_PSTATE_3
    HLML_PSTATE_4                           = newpy.HLML_P_STATES.HLML_PSTATE_4
    HLML_PSTATE_5                           = newpy.HLML_P_STATES.HLML_PSTATE_5
    HLML_PSTATE_6                           = newpy.HLML_P_STATES.HLML_PSTATE_6
    HLML_PSTATE_7                           = newpy.HLML_P_STATES.HLML_PSTATE_7
    HLML_PSTATE_8                           = newpy.HLML_P_STATES.HLML_PSTATE_8
    HLML_PSTATE_9                           = newpy.HLML_P_STATES.HLML_PSTATE_9
    HLML_PSTATE_10                          = newpy.HLML_P_STATES.HLML_PSTATE_10
    HLML_PSTATE_11                          = newpy.HLML_P_STATES.HLML_PSTATE_11
    HLML_PSTATE_12                          = newpy.HLML_P_STATES.HLML_PSTATE_12
    HLML_PSTATE_13                          = newpy.HLML_P_STATES.HLML_PSTATE_13
    HLML_PSTATE_14                          = newpy.HLML_P_STATES.HLML_PSTATE_14
    HLML_PSTATE_15                          = newpy.HLML_P_STATES.HLML_PSTATE_15
    HLML_PSTATE_SENTINEL                    = newpy.HLML_P_STATES.HLML_PSTATE_SENTINEL
    HLML_PSTATE_UNKNOWN                     = newpy.HLML_P_STATES.HLML_PSTATE_UNKNOWN

HLML_PSTATE_NUM_SUPPORTED = newpy.HLML_P_STATES.HLML_PSTATE_SENTINEL

class HLML_MEMORY_ERROR:
    TYPE                                    = ctypes.c_uint
    HLML_MEMORY_ERROR_TYPE_CORRECTED        = newpy.HLML_MEMORY_ERROR_TYPE.HLML_MEMORY_ERROR_TYPE_CORRECTED
    HLML_MEMORY_ERROR_TYPE_UNCORRECTED      = newpy.HLML_MEMORY_ERROR_TYPE.HLML_MEMORY_ERROR_TYPE_UNCORRECTED
    HLML_MEMORY_ERROR_TYPE_COUNT            = newpy.HLML_MEMORY_ERROR_TYPE.HLML_MEMORY_ERROR_TYPE_COUNT

class HLML_MEMORY_LOCATION:
    TYPE                                    = ctypes.c_uint
    HLML_MEMORY_LOCATION_SRAM               = newpy.HLML_MEMORY_LOCATION_TYPE.HLML_MEMORY_LOCATION_SRAM
    HLML_MEMORY_LOCATION_DRAM               = newpy.HLML_MEMORY_LOCATION_TYPE.HLML_MEMORY_LOCATION_DRAM
    HLML_MEMORY_LOCATION_ALL                = newpy.HLML_MEMORY_LOCATION_TYPE.HLML_MEMORY_LOCATION_ALL
    HLML_MEMORY_LOCATION_COUNT              = newpy.HLML_MEMORY_LOCATION_TYPE.HLML_MEMORY_LOCATION_COUNT

class HLML_ECC_COUNTER:
    TYPE                                    = ctypes.c_uint
    HLML_VOLATILE_ECC                       = newpy.HLML_ECC_COUNTER_TYPE.HLML_VOLATILE_ECC
    HLML_AGGREGATE_ECC                      = newpy.HLML_ECC_COUNTER_TYPE.HLML_AGGREGATE_ECC
    HLML_ECC_COUNTER_TYPE_COUNT             = newpy.HLML_ECC_COUNTER_TYPE.HLML_ECC_COUNTER_TYPE_COUNT

class HLML_PCIE_UTIL_COUNTER:
    TYPE                                    = ctypes.c_uint
    HLML_PCIE_UTIL_TX_BYTES                 = newpy.HLML_PCIE_UTIL_COUNTER.HLML_PCIE_UTIL_TX_BYTES
    HLML_PCIE_UTIL_RX_BYTES                 = newpy.HLML_PCIE_UTIL_COUNTER.HLML_PCIE_UTIL_RX_BYTES
    HLML_PCIE_UTIL_COUNT                    = newpy.HLML_PCIE_UTIL_COUNTER.HLML_PCIE_UTIL_COUNT

class HLML_EVENT_SET:
    TYPE                                    = ctypes.c_void_p

class HLML_ROW_REPLACEMENT_CAUSE:
    TYPE                                                      = ctypes.c_uint
    HLML_ROW_REPLACEMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = newpy.HLML_ROW_REPLACEMENT_CAUSE.HLML_ROW_REPLACEMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS
    HLML_ROW_REPLACEMENT_CAUSE_DOUBLE_BIT_ECC_ERROR           = newpy.HLML_ROW_REPLACEMENT_CAUSE.HLML_ROW_REPLACEMENT_CAUSE_DOUBLE_BIT_ECC_ERROR
    HLML_ROW_REPLACEMENT_CAUSE_COUNT                          = newpy.HLML_ROW_REPLACEMENT_CAUSE.HLML_ROW_REPLACEMENT_CAUSE_COUNT

class HLML_PERF_POLICY:
    TYPE                                    = ctypes.c_uint
    HLML_PERF_POLICY_POWER                  = newpy.HLML_PERF_POLICY_TYPE.HLML_PERF_POLICY_POWER
    HLML_PERF_POLICY_THERMAL                = newpy.HLML_PERF_POLICY_TYPE.HLML_PERF_POLICY_THERMAL
    HLML_PERF_POLICY_COUNT                  = newpy.HLML_PERF_POLICY_TYPE.HLML_PERF_POLICY_COUNT

# Legacy
class _struct_c_hlml_unit(ctypes.Structure):
    pass # opaque handle

# Legacy
class HLML_UNIT:
    TYPE                                    = _struct_c_hlml_unit

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
    _fields_ = newpy.c_hlml_pci_cap._fields_

class c_hlml_pci_info(_PrintS):
    _fields_ = newpy.c_hlml_pci_info._fields_

class c_hlml_utilization(_PrintS):
    _fields_ = newpy.c_hlml_utilization._fields_

class c_hlml_process_utilization(_PrintS):
    _fields_ = newpy.c_hlml_process_utilization_sample._fields_

class c_hlml_memory(_PrintS):
    _fields_ = newpy.c_hlml_memory._fields_

class c_hlml_pcb_info(_PrintS):
    _fields_ = newpy.c_hlml_pcb_info._fields_

class c_hlml_event_data(_PrintS):
    _fields_ = newpy.c_hlml_event_data._fields_

class c_hlml_mac_info(_PrintS):
    _fields_ = newpy.c_hlml_mac_info._fields_

class c_hlml_nic_stats_info(_PrintS):
    _fields_ = newpy.c_hlml_nic_stats_info._fields_

    def __init__(self, port: int, num_of_counters: int = None):
        num_of_counters = num_of_counters or COMMON_DEFINE.HABANA_LINK_CNT_MAX_NUM
        self.port = port

        str_buf_size = num_of_counters * 32
        self.str_buf = ctypes.cast(ctypes.create_string_buffer(str_buf_size), ctypes.POINTER(ctypes.c_char))

        val_buf_size = num_of_counters * ctypes.sizeof(ctypes.c_uint64)
        self.val_buf = (ctypes.c_uint64 * val_buf_size)()

        self.num_of_counters_out = (ctypes.c_uint32 * 1)()

class c_hlml_violation_time(_PrintS):
    _fields_ = newpy.c_hlml_violation_time._fields_

class c_hlml_row_address(_PrintS):
    _fields_ = newpy.c_hlml_row_address._fields_

# Legacy
class hlml_ecc_mode(_PrintS):
    _fields_ = [("current", ctypes.c_uint),
                ("pending", ctypes.c_uint)
               ]

## Alternative object
# Allows the object to be printed
# Allows mismatched types to be assigned
#  - like None when the Structure variant requires c_uint

class hlml_friendly_obj(object):
    def __init__(self, dic):
        for x in dic:
            setattr(self, x, dic[x])
    def __str__(self):
        return self.__dict__.__str__()

def hlml_struct_to_friendly(struct):
    dic = {}
    for x in struct._fields_:
        key = x[0]
        value = getattr(struct, key)
        dic[key] = value
    obj = hlml_friendly_obj(dic)
    return obj

def hlml_friendly_to_struct(obj, model):
    for x in model._fields_:
        key = x[0]
        value = obj.__dict__[key]
        setattr(model, key, value)
    return model
