import ctypes

from sys import modules
from typing import Tuple

import pyhlml.hlml_types as hlml_t

from pyhlml.hlml_lib import LibHLML
from pyhlml.hlml_error import HLMLError, ErrorsAsClass

_hlmlOBJ = None

def _wrapperInit():
    """Initialize module-level HLML object and error classes."""
    ErrorsAsClass()
    setattr(modules[__name__], "_hlmlOBJ", LibHLML())

def check_return(ret):
    """Raise HLMLError if ret is not HLML_SUCCESS, otherwise return ret."""
    if (ret != hlml_t.HLML_RETURN.HLML_SUCCESS ):
        raise HLMLError(ret)
    return ret

def hlmlInit() -> None:
    """Initialize HLML. Must be called before any other API can be used."""
    _wrapperInit()
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_init")
    ret = fn()

    _hlmlOBJ.inc_ref()
    check_return(ret)
    return None

def hlmlInitWithFlags(flags=0) -> None:
    """Initialize HLML with flags. Only the default flag (0) is supported.
    Args:
        flags (int): Initialization flags (default 0).
    """
    _wrapperInit()
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_init_with_flags")
    ret = fn(flags)

    _hlmlOBJ.inc_ref()
    check_return(ret)
    return None

def hlmlShutdown() -> None:
    """Shutdown HLML and release resources. Should be called last."""
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_shutdown")
    ret = fn()

    for _ in range(_hlmlOBJ.ref_count):
        _hlmlOBJ.dec_ref()
    check_return(ret)
    return None

def hlmlDeviceGetCount() -> int:
    """Get the number of Habana devices in the system.
    Returns:
        int: Number of Habana devices.
    """
    global _hlmlOBJ
    count = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_count")
    ret = fn(ctypes.byref(count))

    check_return(ret)
    return count.value

def hlmlDeviceGetHandleByPCIBusID(pci_addr: str) -> hlml_t.HLML_DEVICE.TYPE:
    """Get device handle by PCI address.
        If there is a single domain, the 'domain' part of the PCI address
        is not required.
    Args:
        pci_addr (str): PCI address of the device.
    Returns:
        HLML_DEVICE.TYPE: Device handle.
    """
    global _hlmlOBJ

    device = hlml_t.HLML_DEVICE.TYPE()
    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_handle_by_pci_bus_id")
    ret = fn(str.encode(pci_addr), ctypes.byref(device))

    check_return(ret)
    return device

def hlmlDeviceGetHandleByIndex(index: int) -> hlml_t.HLML_DEVICE.TYPE:
    """Get device handle by index.
    Args:
        index (int): Device index.
    Returns:
        HLML_DEVICE.TYPE: Device handle.
    """
    global _hlmlOBJ
    device = hlml_t.HLML_DEVICE.TYPE()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_handle_by_index")
    ret = fn(index, ctypes.byref(device))

    check_return(ret)
    return device

def hlmlDeviceGetHandleByUUID(uuid: str) -> hlml_t.HLML_DEVICE.TYPE:
    """Get device handle by UUID (Universal Unique ID).
    Args:
        uuid (str): Device UUID.
    Returns:
        HLML_DEVICE.TYPE: Device handle.
    """
    global _hlmlOBJ
    device = hlml_t.HLML_DEVICE.TYPE()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_handle_by_UUID")
    ret = fn(str.encode(uuid), ctypes.byref(device))

    check_return(ret)
    return device

def hlmlDeviceGetName(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get device name from handle.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Device name.
    """
    global _hlmlOBJ
    name = ctypes.create_string_buffer(hlml_t.HLML_DEFINE.HL_FIELD_MAX_SIZE)

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_name")
    ret = fn(
        device, ctypes.byref(name),
        ctypes.c_uint(hlml_t.HLML_DEFINE.HL_FIELD_MAX_SIZE)
    )

    check_return(ret)
    return name.value

def hlmlDeviceGetPCIInfo(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.c_hlml_pci_info:
    """Get PCI attributes of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        c_hlml_pci_info: PCI attributes.
    """
    global _hlmlOBJ
    pci_info = hlml_t.c_hlml_pci_info()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_pci_info")
    ret = fn(
        device, ctypes.byref(pci_info),
        ctypes.c_uint(hlml_t.HLML_DEFINE.HL_FIELD_MAX_SIZE)
    )

    check_return(ret)
    return pci_info

def hlmlDeviceGetClockInfo(device: hlml_t.HLML_DEVICE.TYPE, clock_type=0 ) -> int:
    """Get current speed of the selected clock (MHz).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        clock_type (int): Clock type.
    Returns:
        int: Clock speed in MHz.
    """
    global _hlmlOBJ
    speed = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_clock_info")
    ret = fn(device, clock_type, ctypes.byref(speed))

    check_return(ret)
    return speed.value

def hlmlDeviceGetMaxClockInfo(device: hlml_t.HLML_DEVICE.TYPE, clock_type=0 ) -> int:
    """Get maximum speed of the selected clock (MHz).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        clock_type (int): Clock type.
    Returns:
        int: Maximum clock speed in MHz.
    """
    global _hlmlOBJ
    speed = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_max_clock_info")
    ret = fn(device, clock_type, ctypes.byref(speed))

    check_return(ret)
    return speed.value

def hlmlDeviceGetClockLimitInfo(device: hlml_t.HLML_DEVICE.TYPE, clock_type=0 ) -> int:
    """Get frequency limit of the selected clock (MHz).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        clock_type (int): Clock type.
    Returns:
        int: Frequency limit in MHz.
    """
    global _hlmlOBJ
    speed = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_clock_limit_info")
    ret = fn(device, clock_type, ctypes.byref(speed))

    check_return(ret)
    return speed.value

def hlmlDeviceGetUtilizationRates(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.c_hlml_utilization:
    """Get device utilization rates over the past second.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        c_hlml_utilization: Utilization rates.
    """
    global _hlmlOBJ
    hlml_util = hlml_t.c_hlml_utilization()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_utilization_rates")
    ret = fn(device, ctypes.byref(hlml_util))

    check_return(ret)
    return hlml_util

def hlmlDeviceGetProcessUtilization(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.c_hlml_process_utilization:
    """Get process utilization rates (as a percentage) over the past second.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        c_hlml_process_utilization: Process utilization rates.
    """
    global _hlmlOBJ
    hlml_util = hlml_t.c_hlml_process_utilization()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_process_utilization")
    ret = fn(device, ctypes.byref(hlml_util))

    check_return(ret)
    return hlml_util

def hlmlDeviceGetMemoryInfo(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.c_hlml_memory:
    """Get total, used, and free memory in bytes.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        c_hlml_memory: Memory info.
    """
    global _hlmlOBJ
    hlml_mem = hlml_t.c_hlml_memory()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_memory_info")
    ret = fn(device, ctypes.byref(hlml_mem))

    check_return(ret)
    return hlml_mem

def hlmlDeviceGetTemperature(
        device: hlml_t.HLML_DEVICE.TYPE, sensor_type: hlml_t.HLML_TEMP_SENS.TYPE) -> int:
    """Get current temperature (Celsius) of the selected sensor.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        sensor_type (HLML_TEMP_SENS.TYPE): Sensor type.
    Returns:
        int: Temperature in Celsius.
    """
    global _hlmlOBJ
    temp = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_temperature")
    ret = fn(device, sensor_type, ctypes.byref(temp))

    check_return(ret)
    return temp.value

def hlmlDeviceGetTemperatureThreshold(device: hlml_t.HLML_DEVICE.TYPE, threshold_type: int) -> int:
    """Get temperature threshold (Celsius) of the requested type.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        threshold_type (int): Threshold type.
    Returns:
        int: Threshold temperature in Celsius.
    """
    global _hlmlOBJ
    temp = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_temperature_threshold")
    ret = fn(device, threshold_type, ctypes.byref(temp))

    check_return(ret)
    return temp.value

def hlmlDeviceGetPersistenceMode(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get persistence mode of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Persistence mode.
    """
    global _hlmlOBJ
    mode = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_persistence_mode")
    ret = fn(device, ctypes.byref(mode))

    check_return(ret)
    return mode.value

def hlmlDeviceGetPerformanceState(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get performance state of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Performance state.
    """
    global _hlmlOBJ
    p_state = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_performance_state")
    ret = fn(device, ctypes.byref(p_state))

    check_return(ret)
    return p_state.value

def hlmlDeviceGetSupportedPerformanceStates(device: hlml_t.HLML_DEVICE.TYPE) -> tuple:
    """Get all supported performance states for the device.
        The returned array is of size HLML_PSTATE_NUM_SUPPORTED and contains a contiguous
        list of performance states that the device supports.
        If the number of supported performance states is less than HLML_PSTATE_NUM_SUPPORTED,
        the remaining entries in the array will be set to HLML_PSTATE_UNKNOWN.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        HLML_P_STATES array: Supported performance states.
    """
    global _hlmlOBJ
    p_states = (hlml_t.HLML_P_STATES.TYPE * hlml_t.HLML_PSTATE_NUM_SUPPORTED)()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_supported_performance_states")
    ret = fn(device, ctypes.byref(p_states), hlml_t.HLML_PSTATE_NUM_SUPPORTED)

    check_return(ret)
    return p_states

def hlmlDeviceGetPowerUsage(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get power usage for the device in mW.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Power usage in mW.
    """
    global _hlmlOBJ
    power = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_power_usage")
    ret = fn(device, ctypes.byref(power))

    check_return(ret)
    return power.value

def hlmlDeviceSetPowerManagementLimit(device: hlml_t.HLML_DEVICE.TYPE, limit : ctypes.c_uint) -> None:
    """Set power management limit on this device in mW.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        limit (ctypes.c_uint): Power limit in mW.
    """
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_device_set_power_management_limit")
    ret = fn(device, limit)

    check_return(ret)
    return None

def hlmlDeviceGetPowerManagementDefaultLimit(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get default power management limit on this device in mW.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Default power limit in mW.
    """
    global _hlmlOBJ
    power = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_power_management_default_limit")
    ret = fn(device, ctypes.byref(power))

    check_return(ret)
    return power.value

def hlmlDeviceGetECCMode(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.hlml_ecc_mode:
    """Get current and pending ECC modes of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        hlml_ecc_mode: ECC mode info with 'current' and 'pending' attributes.
    """
    global _hlmlOBJ
    out = hlml_t.hlml_ecc_mode()
    current = ctypes.c_uint()
    pending = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_ecc_mode")
    ret = fn(device, ctypes.byref(current), ctypes.byref(pending))

    check_return(ret)
    setattr(out, "current", current)
    setattr(out, "pending", pending)

    return out

def hlmlDeviceGetTotalECCErrors(device: hlml_t.HLML_DEVICE.TYPE, error_type: hlml_t.HLML_MEMORY_ERROR.TYPE, counter_type: hlml_t.HLML_ECC_COUNTER) -> int:
    """Get number of ECC errors for a device since last reset or driver reinstall.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        error_type (HLML_MEMORY_ERROR.TYPE): Error type to count.
        counter_type (HLML_ECC_COUNTER): Counter type to use.
    Returns:
        int: Number of ECC errors.
    """
    global _hlmlOBJ
    count = ctypes.c_longlong()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_total_ecc_errors")
    ret = fn(device, error_type, counter_type, ctypes.byref(count))

    check_return(ret)
    return count.value

def hlmlDeviceGetMemoryErrorCounter(device: hlml_t.HLML_DEVICE.TYPE, error_type: hlml_t.HLML_MEMORY_ERROR.TYPE, counter_type: hlml_t.HLML_ECC_COUNTER.TYPE, location: hlml_t.HLML_MEMORY_LOCATION.TYPE) -> int:
    """Get number of ECC errors for a device at a specified memory location.
        The number is from the last reset or driver reinstall. Currently, only the
        number of corrected errors is supported.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        error_type (HLML_MEMORY_ERROR.TYPE): Error type to count.
        counter_type (HLML_ECC_COUNTER.TYPE): Counter type to use.
        location (HLML_MEMORY_LOCATION.TYPE): Memory location.
    Returns:
        int: Number of ECC errors.
    """
    global _hlmlOBJ
    ecc_count = ctypes.c_longlong()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_memory_error_counter")
    ret = fn(device, error_type, counter_type, location, ctypes.byref(ecc_count))

    check_return(ret)
    return ecc_count.value

def hlmlDeviceGetUUID(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get UUID (Universal Unique ID) of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Device UUID.
    """
    global _hlmlOBJ
    name_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    name = ctypes.create_string_buffer(name_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_uuid")
    ret = fn(device, ctypes.byref(name), name_len)

    check_return(ret)
    return name.value

def hlmlDeviceGetMinorNumber(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get minor number of the device (maps to device node file
        at /sys/class/accel/accel[minor]).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Minor number.
    """
    global _hlmlOBJ
    number = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_minor_number")
    ret = fn(device, ctypes.byref(number))

    check_return(ret)
    return number.value

def hlmlEventSetCreate() -> hlml_t.HLML_EVENT_SET.TYPE:
    """Create an empty set of events.
    Returns:
        HLML_EVENT_SET.TYPE: Empty event set.
    """
    global _hlmlOBJ
    st = hlml_t.HLML_EVENT_SET.TYPE()

    fn = _hlmlOBJ.get_func_ptr("hlml_event_set_create")
    ret = fn(ctypes.byref(st))

    check_return(ret)
    return st

def hlmlEventSetFree(st: hlml_t.HLML_EVENT_SET.TYPE) -> None:
    """Release a set of events.
    Args:
        st (HLML_EVENT_SET.TYPE): Event set to release.
    """
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_event_set_free")
    ret = fn(st)

    check_return(ret)
    return None

def hlmlDeviceRegisterEvents(
        device: hlml_t.HLML_DEVICE.TYPE, event_types: int,
        st: hlml_t.HLML_EVENT_SET.TYPE
    ) -> None:
    """Start recording events on device and add events to set.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        event_types (int): Event types to record.
        st (HLML_EVENT_SET.TYPE): Event set (buffer) to be written to.
    """
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_device_register_events")
    ret = fn(device, event_types, st)

    check_return(ret)
    return None

def hlmlEventSetWait(st: hlml_t.HLML_EVENT_SET.TYPE, timeout: int) -> hlml_t.c_hlml_event_data:
    """Wait for events and deliver event data.
        If any events are available at the time of the call, function returns immediately.
        If there are no events available, it waits until an event arrives or the specified
        timeout is reached.
    Args:
        st (HLML_EVENT_SET.TYPE): Event set (buffer) to be written to.
        timeout (int): Maximum time to wait for an event.
    Returns:
        c_hlml_event_data: Event data.
    """
    global _hlmlOBJ
    data = hlml_t.c_hlml_event_data()

    fn = _hlmlOBJ.get_func_ptr("hlml_event_set_wait")
    ret = fn(st, ctypes.byref(data), timeout)

    check_return(ret)
    return data

def hlmlDeviceGetMACInfo(
        device: hlml_t.HLML_DEVICE.TYPE, count=20, start=1) -> tuple:
    """Get MAC addresses of device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        count (int): Number of addresses to return.
        start (int): Index to start at.
    Returns:
        c_hlml_mac_info array: MAC addresses.
    """
    global _hlmlOBJ
    mac = (hlml_t.c_hlml_mac_info * count)()
    actual_info_count = ctypes.c_int()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_mac_info")
    ret = fn(device, ctypes.byref(mac), count, start, ctypes.byref(actual_info_count))

    check_return(ret)
    return mac

def hlmlDeviceGetHLRevision(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get HL revision of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: HL revision.
    """
    global _hlmlOBJ
    rev = ctypes.c_int()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_hl_revision")
    ret = fn(device, ctypes.byref(rev))

    check_return(ret)
    return rev.value

def hlmlDeviceGetPCBInfo(device: hlml_t.HLML_DEVICE.TYPE) -> hlml_t.c_hlml_pcb_info:
    """Get PCB info of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        c_hlml_pcb_info: PCB info.
    """
    global _hlmlOBJ
    pcb = hlml_t.c_hlml_pcb_info()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_pcb_info")
    ret = fn(device, ctypes.byref(pcb))

    check_return(ret)
    return pcb

def hlmlDeviceGetSerial(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get unique board serial number.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Serial number.
    """
    global _hlmlOBJ
    ser_len = hlml_t.HLML_DEFINE.HL_FIELD_MAX_SIZE
    ser = ctypes.create_string_buffer(ser_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_serial")
    ret = fn(device, ctypes.byref(ser), ser_len)

    check_return(ret)
    return ser.value

def hlmlDeviceGetModuleID(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get module ID configured on the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Module ID.
    """
    global _hlmlOBJ
    module_id = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_module_id")
    ret = fn(device, ctypes.byref(module_id))

    check_return(ret)
    return module_id.value

def hlmlDeviceGetBoardID(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get device board ID (slot number between 0 and 7).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Board ID.
    """
    global _hlmlOBJ
    brd = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_board_id")
    ret = fn(device, ctypes.byref(brd))

    check_return(ret)
    return brd.value

def hlmlDeviceGetPCIEThroughput(device: hlml_t.HLML_DEVICE.TYPE, counter_type: int) -> int:
    """Get PCIe utilization information (over 10ms interval).
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        counter_type (int): 0 for TX, 1 for RX.
    Returns:
        int: PCIe throughput.
    """
    global _hlmlOBJ
    pcie = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_pcie_throughput")
    ret = fn(device, counter_type, ctypes.byref(pcie))

    check_return(ret)
    return pcie.value

def hlmlDeviceGetPCIEReplayCounter(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get PCIe replay counter.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Replay counter.
    """
    global _hlmlOBJ
    pcie = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_pcie_replay_counter")
    ret = fn(device, ctypes.byref(pcie))

    check_return(ret)
    return pcie.value

def hlmlDeviceGetCurrPCIELinkGeneration(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get current PCIe link generation.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: PCIe link generation.
    """
    global _hlmlOBJ
    link = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_curr_pcie_link_generation")
    ret = fn(device, ctypes.byref(link))

    check_return(ret)
    return link.value

def hlmlDeviceGetCurrPCIELinkWidth(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get current PCIe link width.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: PCIe link width.
    """
    global _hlmlOBJ
    width = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_curr_pcie_link_width")
    ret = fn(device, ctypes.byref(width))

    check_return(ret)
    return width.value

def hlmlDeviceGetCurrentClocksThrottleReasons(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get current clocks throttle reason.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Throttle reason code.
    """
    global _hlmlOBJ
    reason = ctypes.c_ulonglong()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_current_clocks_throttle_reasons")
    ret = fn(device, ctypes.byref(reason))

    check_return(ret)
    return reason.value

def hlmlDeviceGetTotalEnergyConsumption(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get total energy consumption in mJ since last driver reload.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Total energy consumption in mJ.
    """
    global _hlmlOBJ
    energy = ctypes.c_ulonglong()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_total_energy_consumption")
    ret = fn(device, ctypes.byref(energy))

    check_return(ret)
    return energy.value

def hlmlDeviceGetMacAddrInfo(device: hlml_t.HLML_DEVICE.TYPE) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Get masks for supported and external ports.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        Tuple[Tuple[int, int], Tuple[int, int]]: (mask, ext_mask), where:
            mask: Bitmask of supported ports.
            ext_mask: Bitmask of external ports (subset of supported).
    """
    global _hlmlOBJ
    mask = (ctypes.c_uint64 * 2)()
    ext_mask = (ctypes.c_uint64 * 2)()

    fn = _hlmlOBJ.get_func_ptr("hlml_get_mac_addr_info")
    ret = fn(device, ctypes.byref(mask), ctypes.byref(ext_mask))

    check_return(ret)
    return (mask[0], mask[1]), (ext_mask[0], ext_mask[1])

def hlmlDeviceNicGetLink(device: hlml_t.HLML_DEVICE.TYPE, port: int) -> bool:
    """Get NIC link status (up/down) for the requested port.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        port (int): Port number.
    Returns:
        bool: Port status. True if up, False if down.
    """
    global _hlmlOBJ
    up = ctypes.c_bool()

    fn = _hlmlOBJ.get_func_ptr("hlml_nic_get_link")
    ret = fn(device, ctypes.c_uint32(port), ctypes.byref(up))

    check_return(ret)
    return up.value

def hlmlDeviceNicGetStatistics(device: hlml_t.HLML_DEVICE.TYPE, port: int, num_of_counts: int = None) -> hlml_t.c_hlml_nic_stats_info:
    """Get NIC statistics for the requested port.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        port (int): Port number.
        num_of_counts (int, optional): Number of counts to allocate.
    Returns:
        c_hlml_nic_stats_info: NIC statistics.
    """
    global _hlmlOBJ
    nic_stats_info = hlml_t.c_hlml_nic_stats_info(port, num_of_counts)

    fn = _hlmlOBJ.get_func_ptr("hlml_nic_get_statistics")
    ret = fn(device, ctypes.byref(nic_stats_info))

    check_return(ret)
    return nic_stats_info

def hlmlGetHLMLVersion() -> bytes:
    """Get version of HLML library.
    Returns:
        bytes: HLML library version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    version = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_hlml_version")
    ret = fn(version, ctypes.c_uint(ver_len))

    check_return(ret)
    return version.value

def hlmlGetDriverVersion() -> bytes:
    """Get version of driver.
    Returns:
        bytes: Driver version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    version = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_driver_version")
    ret = fn(version, ctypes.c_uint(ver_len))

    check_return(ret)
    return version.value

def hlmlGetNicDriverVersion() -> bytes:
    """Get version of NIC driver.
    Returns:
        bytes: NIC driver version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    version = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_nic_driver_version")
    ret = fn(version, ctypes.c_uint(ver_len))

    check_return(ret)
    return version.value

def hlmlDeviceGetModelNumber(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get model number of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Model number.
    """
    global _hlmlOBJ
    num_len = hlml_t.HLML_DEFINE.HL_FIELD_MAX_SIZE
    num_str = ctypes.create_string_buffer(num_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_model_number")
    ret = fn(device, num_str, ctypes.c_uint(num_len))

    check_return(ret)
    return num_str.value

def hlmlDeviceGetFirmwareFITVersion(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get firmware FIT version.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Firmware FIT version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    ver_str = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_firmware_fit_version")
    ret = fn(device, ver_str, ctypes.c_uint(ver_len))

    check_return(ret)
    return ver_str.value

def hlmlDeviceGetFirmwareSPIVersion(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get firmware SPI version.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Firmware SPI version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    ver_str = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_firmware_spi_version")
    ret = fn(device, ver_str, ctypes.c_uint(ver_len))

    check_return(ret)
    return ver_str.value

def hlmlDeviceGetFWBootVersion(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get firmware boot version.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Firmware boot version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    ver_str = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_fw_boot_version")
    ret = fn(device, ver_str, ctypes.c_uint(ver_len))

    check_return(ret)
    return ver_str.value

def hlmlDeviceGetFWOSVersion(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get firmware OS version.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: Firmware OS version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    ver_str = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_fw_os_version")
    ret = fn(device, ver_str, ctypes.c_uint(ver_len))

    check_return(ret)
    return ver_str.value

def hlmlDeviceGetCPLDVersion(device: hlml_t.HLML_DEVICE.TYPE) -> bytes:
    """Get CPLD version.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        bytes: CPLD version.
    """
    global _hlmlOBJ
    ver_len = hlml_t.COMMON_DEFINE.VERSION_MAX_LEN
    ver_str = ctypes.create_string_buffer(ver_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_get_cpld_version")
    ret = fn(device, ver_str, ctypes.c_uint(ver_len))

    check_return(ret)
    return ver_str.value

def hlmlDeviceClearCpuAffinity(device: hlml_t.HLML_DEVICE.TYPE) -> None:
    """Clear device's CPU affinity.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    """
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_device_clear_cpu_affinity")
    ret = fn(device)

    check_return(ret)
    return None

def hlmlDeviceGetCpuAffinity(device: hlml_t.HLML_DEVICE.TYPE, cpu_set_size: int):
    """Get CPU affinity set associated with a device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        cpu_set_size (int): Size of the CPU set.
    Returns:
        array: CPU set.
    """
    global _hlmlOBJ
    cpu_set = (ctypes.c_ulong * cpu_set_size)()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_cpu_affinity")
    ret = fn(device, cpu_set_size, ctypes.byref(cpu_set))

    check_return(ret)
    return cpu_set

def hlmlDeviceGetCpuAffinityWithinScope(device: hlml_t.HLML_DEVICE.TYPE, cpu_set_size: int, scope: hlml_t.HLML_AFFINITY_SCOPE.TYPE):
    """Get CPU affinity set associated with a device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        cpu_set_size (int): Size of the CPU set.
        scope (HLML_AFFINITY_SCOPE.TYPE): Affinity scope.
    Returns:
        array: CPU set.
    """
    global _hlmlOBJ
    cpu_set = (ctypes.c_ulong * cpu_set_size)()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_cpu_affinity_within_scope")
    ret = fn(device, cpu_set_size, ctypes.byref(cpu_set), scope)

    check_return(ret)
    return cpu_set

def hlmlDeviceGetMemoryAffinity(device: hlml_t.HLML_DEVICE.TYPE, node_set_size: int, scope: hlml_t.HLML_AFFINITY_SCOPE.TYPE):
    """Get memory affinity set associated with a device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        node_set_size (int): Size of the node set.
        scope (HLML_AFFINITY_SCOPE.TYPE): Affinity scope.
    Returns:
        array: Node set.
    """
    global _hlmlOBJ
    node_set = (ctypes.c_ulong * node_set_size)()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_memory_affinity")
    ret = fn(device, node_set_size, ctypes.byref(node_set), scope)

    check_return(ret)
    return node_set

def hlmlDeviceSetCpuAffinity(device: hlml_t.HLML_DEVICE.TYPE) -> None:
    """Set CPU affinity for a device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    """
    global _hlmlOBJ

    fn = _hlmlOBJ.get_func_ptr("hlml_device_set_cpu_affinity")
    ret = fn(device)

    check_return(ret)
    return None

def hlmlDeviceGetViolationStatus(device: hlml_t.HLML_DEVICE.TYPE, perf_policy: hlml_t.HLML_PERF_POLICY.TYPE) -> hlml_t.c_hlml_violation_time:
    """Get violation status of a device for a given performance policy.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        perf_policy (HLML_PERF_POLICY.TYPE): Performance policy type.
    Returns:
        c_hlml_violation_time: Violation status, comprised of reference time and violation time.
    """
    global _hlmlOBJ

    violation_time = hlml_t.c_hlml_violation_time()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_violation_status")
    ret = fn(device, perf_policy, ctypes.byref(violation_time))

    check_return(ret)
    return violation_time

def hlmlDeviceGetReplacedRowsCount(device: hlml_t.HLML_DEVICE.TYPE, cause: hlml_t.HLML_ROW_REPLACEMENT_CAUSE.TYPE) -> int:
    """Get number of replaced rows for a given cause.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        cause (HLML_ROW_REPLACEMENT_CAUSE.TYPE): Replacement cause.
    Returns:
        int: Number of replaced rows.
    """
    global _hlmlOBJ

    row_count = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_replaced_rows")
    ret = fn(device, cause, ctypes.byref(row_count), None)

    check_return(ret)
    return row_count.value

def hlmlDeviceGetReplacedRows(device: hlml_t.HLML_DEVICE.TYPE, cause: hlml_t.HLML_ROW_REPLACEMENT_CAUSE.TYPE, row_count: int):
    """Get array of replaced rows for a given cause.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
        cause (HLML_ROW_REPLACEMENT_CAUSE.TYPE): Replacement cause.
        row_count (int): Number of rows to retrieve.
    Returns:
        array: Array of hlml_t.c_hlml_row_address structures.
    """
    global _hlmlOBJ

    c_row_count = ctypes.c_uint(row_count)
    addresses = (hlml_t.c_hlml_row_address * row_count)()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_replaced_rows")
    ret = fn(device, cause, ctypes.byref(c_row_count), ctypes.byref(addresses))

    check_return(ret)
    return addresses

def hlmlDeviceGetReplacedRowsPendingStatus(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get pending status of replaced rows.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Pending status. True if there are pending replaced rows, False otherwise.
    """
    global _hlmlOBJ

    is_pending = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_replaced_rows_pending_status")
    ret = fn(device, ctypes.byref(is_pending))

    check_return(ret)
    return is_pending.value

def hlmlDeviceGetOperationStatus(device: hlml_t.HLML_DEVICE.TYPE) -> str:
    """Get operation status of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        str: Operation status.
    """
    global _hlmlOBJ
    sts_len = hlml_t.COMMON_DEFINE.STATUS_MAX_LEN
    sts_str = ctypes.create_string_buffer(sts_len)

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_oper_status")
    ret = fn(device, sts_str, ctypes.c_uint(sts_len))

    check_return(ret)
    return sts_str.value

def hlmlDeviceGetPowerManagementMode(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get power management mode of the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Power management mode.
    """
    global _hlmlOBJ
    mode = ctypes.c_uint()
    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_power_management_mode")
    ret = fn(device, ctypes.byref(mode))

    check_return(ret)
    return mode.value

def hlmlDeviceGetPowerManagementLimit(device: hlml_t.HLML_DEVICE.TYPE) -> int:
    """Get power management limit of the device in mW.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        int: Power management limit in mW.
    """
    global _hlmlOBJ
    power_max = ctypes.c_uint()
    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_power_management_limit")
    ret = fn(device, ctypes.byref(power_max))

    check_return(ret)
    return power_max.value

def hlmlDeviceGetPowerManagementLimitConstraints(device: hlml_t.HLML_DEVICE.TYPE) -> Tuple[int, int]:
    """Get power management limit constraints (min, max) for the device.
    Args:
        device (HLML_DEVICE.TYPE): Device handle.
    Returns:
        Tuple[int, int]: (min_limit, max_limit)
    """
    global _hlmlOBJ
    min_limit = ctypes.c_uint()
    max_limit = ctypes.c_uint()

    fn = _hlmlOBJ.get_func_ptr("hlml_device_get_power_management_limit_constraints")
    ret = fn(device, ctypes.byref(min_limit), ctypes.byref(max_limit))

    check_return(ret)
    return min_limit.value, max_limit.value
