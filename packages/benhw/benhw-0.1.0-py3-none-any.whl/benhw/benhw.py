"""BenHW SDK - Python Class Interface

Auto-generated from manifest.json by generate.py

Copyright (c) Bentham Instruments Ltd
All Rights Reserved
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional, Union, Protocol, TYPE_CHECKING, Tuple
from pydantic import BaseModel, ConfigDict
from cffi import FFI

# Import namespaced tokens and exceptions
from . import tokens
from . import exceptions

# Import commonly used error codes for internal use
BI_OK = exceptions.Codes.BI_OK
BI_error = exceptions.Codes.BI_error

# Import exception classes from exceptions module
from .exceptions import (
    SdkException,
    Amp225DeadException,
    Relay262DeadException,
    Amp265DeadException,
    Amp267DeadException,
    Amp277DeadException,
    AdcOverloadException,
    AdcInvalidReadingException,
    AdcReadErrorException,
    AmpInvalidChannelException,
    AmpInvalidWavelengthException,
    ActionTimeoutException,
    CommsTxErrorException,
    ExternalDriverErrorException,
    InvalidCommandErrorException,
    MacInvalidCmdException,
    MacTimeoutException,
    MscTimeoutException,
    MsdTimeoutException,
    MvssInvalidWidthException,
    PmcTimeoutException,
    SamInvalidWavelengthException,
    BenHWException,
    InvalidAttributeException,
    InvalidComponentException,
    InvalidTokenException,
    NoSetupWindowException,
    TurretIncorrectPosException,
    TurretInvalidWavelengthException,
    UndefinedErrorException,
)


def _raise_for_error(error_code: int) -> None:
    """Raise appropriate exception for error code"""
    if error_code == BI_OK:
        return
    
    # List of all error exception classes
    error_classes = [
        Amp225DeadException,
        Relay262DeadException,
        Amp265DeadException,
        Amp267DeadException,
        Amp277DeadException,
        AdcOverloadException,
        AdcInvalidReadingException,
        AdcReadErrorException,
        AmpInvalidChannelException,
        AmpInvalidWavelengthException,
        ActionTimeoutException,
        CommsTxErrorException,
        ExternalDriverErrorException,
        InvalidCommandErrorException,
        MacInvalidCmdException,
        MacTimeoutException,
        MscTimeoutException,
        MsdTimeoutException,
        MvssInvalidWidthException,
        PmcTimeoutException,
        SamInvalidWavelengthException,
        BenHWException,
        InvalidAttributeException,
        InvalidComponentException,
        InvalidTokenException,
        NoSetupWindowException,
        TurretIncorrectPosException,
        TurretInvalidWavelengthException,
        UndefinedErrorException,
    ]
    
    # Find the exception class that matches the error code
    for exception_class in error_classes:
        # Create a temporary instance to check its error code
        temp_instance = exception_class()
        if temp_instance.error_code == error_code:
            raise exception_class()
    
    # If no matching exception class found, raise SdkException
    raise SdkException(error_code, f"Unknown error code: {error_code}")


def _find_dll() -> str:
    """
    Find the appropriate BenHW DLL for the current platform.
    
    Returns:
        str: Path to the DLL file
        
    Raises:
        RuntimeError: if no suitable DLL can be found
    """
    # Determine which DLL to use based on architecture
    is_64bit = platform.architecture()[0] == '64bit'
    dll_name = "benhw64.dll" if is_64bit else "benhw32_cdecl.dll"
    
    # Look in the bundled dlls directory first
    package_dir = Path(__file__).parent
    bundled_dll = package_dir / "dlls" / dll_name
    if bundled_dll.exists():
        return str(bundled_dll)
    
    # Also check for IEEE_32M.dll dependency and add its directory to PATH
    ieee_dll = package_dir / "dlls" / "IEEE_32M.dll"
    if ieee_dll.exists():
        dll_dir = str(package_dir / "dlls")
        current_path = os.environ.get("PATH", "")
        path_dirs = current_path.split(os.pathsep) if current_path else []
        if dll_dir not in path_dirs:
            os.environ["PATH"] = dll_dir + os.pathsep + current_path
    
    # Fall back to checking system PATH
    return dll_name

class BI_camera_measurement_result_protocol(Protocol):
    """
    Protocol interface for BI_camera_measurement result containing multiple output values.
    
    This protocol defines the interface for autocomplete without exposing BaseModel methods.
    
    Attributes:
        wls (list[float]): Array of wavelength values in nanometers
        readings (list[float]): Array of measurement readings
    """
    wls: list[float]
    readings: list[float]


class BI_camera_measurement_result(BaseModel):
    """
    Implementation of BI_camera_measurement result containing multiple output values.
    
    Attributes:
        wls (list[float]): Array of wavelength values in nanometers
        readings (list[float]): Array of measurement readings
    """
    wls: list[float]
    readings: list[float]


class BI_camera_get_zero_calibration_info_result_protocol(Protocol):
    """
    Protocol interface for BI_camera_get_zero_calibration_info result containing multiple output values.
    
    This protocol defines the interface for autocomplete without exposing BaseModel methods.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_camera_get_zero_calibration_info_result(BaseModel):
    """
    Implementation of BI_camera_get_zero_calibration_info result containing multiple output values.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_get_zero_calibration_info_result_protocol(Protocol):
    """
    Protocol interface for BI_get_zero_calibration_info result containing multiple output values.
    
    This protocol defines the interface for autocomplete without exposing BaseModel methods.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_get_zero_calibration_info_result(BaseModel):
    """
    Implementation of BI_get_zero_calibration_info result containing multiple output values.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_multi_get_zero_calibration_info_result_protocol(Protocol):
    """
    Protocol interface for BI_multi_get_zero_calibration_info result containing multiple output values.
    
    This protocol defines the interface for autocomplete without exposing BaseModel methods.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_multi_get_zero_calibration_info_result(BaseModel):
    """
    Implementation of BI_multi_get_zero_calibration_info result containing multiple output values.
    
    Attributes:
        wavelength (list[float]): Wavelength value in nanometers
        DarkCurrent (list[float]): Array of dark current calibration values
        ADCOffset (list[float]): Array of ADC offset calibration values
    """
    wavelength: list[float]
    DarkCurrent: list[float]
    ADCOffset: list[float]


class BI_read_result_protocol(Protocol):
    """
    Protocol interface for BI_read result containing multiple output values.
    
    This protocol defines the interface for autocomplete without exposing BaseModel methods.
    
    Attributes:
        buffer (bytes): Buffer for reading or writing data
        chars_read (int): Number of characters actually read
    """
    buffer: bytes
    chars_read: int


class BI_read_result(BaseModel):
    """
    Implementation of BI_read result containing multiple output values.
    
    Attributes:
        buffer (bytes): Buffer for reading or writing data
        chars_read (int): Number of characters actually read
    """
    buffer: bytes
    chars_read: int


class BenHW:
    """
    Python wrapper for BenHW DLL.
    
    Provides a modern Python interface to the BenHW hardware control library.
    This class automatically loads the DLL on construction using CFFI ABI mode
    and provides type-safe methods that raise exceptions on errors.
    
    The DLL is automatically located from the bundled dlls directory or system PATH.
    
    Example:
        >>> hw = BenHW()
        >>> try:
        ...     hw.build_system_model("system.cfg")
        ...     print("System model built successfully")
        ... except SdkException as e:
        ...     print(f"Error: {e}")
        >>> # DLL is automatically unloaded when hw goes out of scope
    """
    
    def __init__(self, dll_path: Optional[str] = None):
        """
        Construct a BenHW instance and load the DLL.
        
        Args:
            dll_path: Optional path to the BenHW DLL. If not provided, the DLL
                     will be automatically located from the bundled dlls directory
                     or system PATH.
            
        Raises:
            RuntimeError: if the DLL cannot be loaded
        """
        self._ffi = FFI()
        self._lib = None
        self._dll_path = dll_path if dll_path else _find_dll()
        
        # Define C function signatures
        self._ffi.cdef("""
int BI_close(void);
int BI_automeasure(double* reading);
int BI_autorange(void);
int BI_build_group(void);
int BI_build_system_model(char* config_file, char* error);
int BI_close_shutter(void);
int BI_component_select_wl(char* id, double wl, int* settle);
int BI_camera_measurement(char* id, int number, double* wls, double* readings);
int BI_camera_get_wls(char* id, double* wls);
int BI_camera_zero_calibration(char* id, double start_wl, double stop_wl);
int BI_camera_get_zero_calibration_info(char* id, double* wavelength, double* DarkCurrent, double* ADCOffset);
int BI_delete_group(int n);
int BI_display_setup_window(char* id, int hinstance);
int BI_display_advanced_window(char* id, int hinstance);
int BI_get(char* id, int token, int index, double* value);
int BI_get_str(char* id, int token, int index, char* s);
int BI_get_c_group(int* n);
int BI_get_component_list(char* list);
int BI_get_group(int n, char* s);
int BI_get_hardware_type(char* id, int* hardwareType);
int BI_get_log(char* log);
int BI_get_log_size(int* size);
int BI_get_mono_items(char* monoID, char* ItemIDs);
int BI_get_min_step(int group, double start_wl, double stop_wl, double* min_step);
int BI_get_max_bw(int group, double start_wl, double stop_wl, double* bandwidth);
int BI_get_no_of_dark_currents(int* NoOfValues);
int BI_get_n_groups(int* n);
int BI_get_zero_calibration_info(double* wavelength, double* DarkCurrent, double* ADCOffset);
int BI_group_add(char* id, int n);
int BI_group_remove(char* id, int n);
int BI_initialise(void);
int BI_load_setup(char* filename);
int BI_measurement(double* reading);
int BI_multi_automeasure(double* reading);
int BI_multi_autorange(void);
int BI_multi_get_no_of_dark_currents(int group, int* NoOfValues);
int BI_multi_get_zero_calibration_info(int group, double* wavelength, double* DarkCurrent, double* ADCOffset);
int BI_multi_initialise(void);
int BI_multi_measurement(double* reading);
int BI_multi_park(void);
int BI_multi_select_wavelength(double wavelength, int* settle_delay);
int BI_multi_zero_calibration(double start_wavelength, double stop_wavelength);
int BI_park(void);
int BI_read(char* buffer, uint16_t buffer_size, uint16_t* chars_read, char* id);
int BI_report_error(void);
int BI_save_setup(char* filename);
int BI_select_wavelength(double wl, int* settle_delay);
int BI_send(char* msg, char* id);
int BI_set(char* id, int token, int index, double value);
int BI_set_str(char* id, int token, int index, char* s);
int BI_start_log(char* c_list);
int BI_stop_log(char* c_list);
int BI_trace(int i, char* LoggingDir);
void BI_Mapped_Logging(int i);
int BI_use_group(int n);
void BI_version(char* s);
int BI_zero_calibration(double start_wl, double stop_wl);
int BI_SCPI_query(char* id, char* msg, char* reply, int reply_size);
int BI_SCPI_write(char* msg, char* id);
        """)
        
        # Load the DLL
        try:
            self._lib = self._ffi.dlopen(self._dll_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load BenHW DLL '{self._dll_path}': {e}")
    
    def __del__(self):
        """Destructor - unloads the DLL."""
        if self._lib is not None:
            # CFFI automatically handles DLL unloading
            self._lib = None
    
    def is_loaded(self) -> bool:
        """Check if the DLL is loaded."""
        return self._lib is not None
    def close(self) -> None:
        """
        Close and clean up the system model.
        
        Frees the system model and releases all resources. Call this before exiting your application. This function instructs the DLL to destroy the system model and prepare for unloading.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_close()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def automeasure(self) -> float:
        """
        Perform an automatic measurement with autoranging.
        
        Takes a measurement with automatic gain ranging. The detector will automatically adjust its range to get the best reading. Takes the Analogue-digital Converter (ADC) offset and dark current (previously obtained by zero_calibration) into account. Negative values are clamped to zero unless AllowNegative is set.
        
        Returns:
            float: Measurement reading value or array

        
        Raises:
            AdcOverloadException: Specific error condition
            AdcReadErrorException: Specific error condition
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        reading_ptr = self._ffi.new("double*")
        
        try:
            error_code = self._lib.BI_automeasure(reading_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return reading_ptr[0]


    def autorange(self) -> None:
        """
        Automatically adjust the detector range.
        
        Adjusts the amplifier gain range to optimize the signal for measurement. Should be called before taking measurements if the signal level has changed significantly. This auto-ranges the amplifier(s) in the active group.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_autorange()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def build_group(self) -> int:
        """
        Create a new component group.
        
        Creates a new, empty group for organizing components. Groups allow multiple components to be controlled together. The DLL allows up to 10 component groups. Returns the group number if successful.
        
        Returns:
            int: group_number - The newly created group number
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            # Function returns actual output value, not error code
            _return_value = self._lib.BI_build_group()
            # Check for negative values which indicate errors
            if _return_value < 0:
                error_code = _return_value
            else:
                error_code = BI_OK

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        # Return the function's return value (actual output)
        return int(_return_value)


    def build_system_model(self, config_file: str) -> str:
        """
        Load and compile a system configuration file.
        
        Parses the configuration file and builds the system model representing your hardware setup. This must be called before any other operations. If an error occurs, the error message is written to the error buffer. This function must succeed before any other DLL function is called.
        
        Args:
            config_file: Path to the system configuration file        
        Returns:
            str: Error message

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        error_buf = self._ffi.new("char[]", 4096)
        config_file_bytes = config_file.encode('utf-8') if isinstance(config_file, str) else config_file
        
        try:
            error_code = self._lib.BI_build_system_model(config_file_bytes, error_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return self._ffi.string(error_buf).decode('utf-8')


    def close_shutter(self) -> None:
        """
        Close the monochromator shutter.
        
        Closes the shutter on the current monochromator to block light. Useful for taking dark measurements. This function sends the filter wheel in the monochromator of the active group to its shutter position.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_close_shutter()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def component_select_wl(self, id: str, wl: float) -> int:
        """
        Set the wavelength for a specific component.
        
        Sets the wavelength for a named monochromator component. Returns the settle delay time needed before taking measurements. This function sends the specified component to the specified wavelength and recommends a settle delay time before any readings are taken. It does not perform the delay itself.
        
        Args:
            id: Component identifier string            wl: Wavelength value in nanometers        
        Returns:
            int: Settle delay time in milliseconds after wavelength change

        
        Raises:
            BenHWException: Specific error condition
            InvalidComponentException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        settle_ptr = self._ffi.new("int*")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_component_select_wl(id_bytes, wl, settle_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return settle_ptr[0]


    def camera_measurement(self, id: str, number: int) -> BI_camera_measurement_result:
        """
        Take a measurement from a camera/array detector.
        
        Captures spectral data from a camera or diode array detector. Returns wavelengths and intensity readings for each pixel. This function instructs the DLL to take a camera measurement using the camera defined by the id string. The camera measurement itself is performed by the external DLL defined in the system configuration file for the relevant camera.
        
        Args:
            id: Component identifier string            number: Number of data points or pixels        
        Returns:
            BI_camera_measurement_result: Object containing multiple output values

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Array size parameter: number
        wls_ptr = self._ffi.new("double[]", number)
        # Array size parameter: number
        readings_ptr = self._ffi.new("double[]", number)
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_camera_measurement(id_bytes, number, wls_ptr, readings_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return BI_camera_measurement_result(
            wls=list(wls_ptr[0:number]),
            readings=list(readings_ptr[0:number]),
        )


    def camera_get_wls(self, id: str) -> list[float]:
        """
        Get wavelength calibration for camera pixels.
        
        Retrieves the wavelength corresponding to each pixel of the camera or array detector.
        
        Args:
            id: Component identifier string        
        Returns:
            list[float]: Array of wavelength values in nanometers

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get
        _size_BI_get = int(self.get())
        # Array wls sized by BI_get
        wls_ptr = self._ffi.new("double[]", _size_BI_get)
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_camera_get_wls(id_bytes, wls_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return list(wls_ptr[0:_size_BI_get])

    def camera_zero_calibration(self, id: str, start_wl: float, stop_wl: float) -> None:
        """
        Perform zero calibration for camera detector (obsolete).
        
        Legacy function for camera zero calibration. This function is obsolete and does nothing. Kept for backwards compatibility with BenWin+.
        
        Args:
            id: Component identifier string            start_wl: Starting wavelength for the range in nanometers            stop_wl: Ending wavelength for the range in nanometers
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_camera_zero_calibration(id_bytes, start_wl, stop_wl)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def camera_get_zero_calibration_info(self, id: str) -> BI_camera_get_zero_calibration_info_result:
        """
        Get zero calibration data for camera (obsolete).
        
        Legacy function for retrieving camera zero calibration data. This function is obsolete and does nothing. Kept for backwards compatibility with BenWin+.
        
        Args:
            id: Component identifier string        
        Returns:
            BI_camera_get_zero_calibration_info_result: Object containing multiple output values

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get
        _size_BI_get = int(self.get())
        # Array wavelength sized by BI_get
        wavelength_ptr = self._ffi.new("double[]", _size_BI_get)
        # Array DarkCurrent sized by BI_get
        DarkCurrent_ptr = self._ffi.new("double[]", _size_BI_get)
        # Array ADCOffset sized by BI_get
        ADCOffset_ptr = self._ffi.new("double[]", _size_BI_get)
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_camera_get_zero_calibration_info(id_bytes, wavelength_ptr, DarkCurrent_ptr, ADCOffset_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return BI_camera_get_zero_calibration_info_result(
            wavelength=list(wavelength_ptr[0:_size_BI_get]),            DarkCurrent=list(DarkCurrent_ptr[0:_size_BI_get]),            ADCOffset=list(ADCOffset_ptr[0:_size_BI_get]),        )


    def delete_group(self, n: int) -> int:
        """
        Delete a component group.
        
        Removes a previously created group. Returns the number of remaining groups.
        
        Args:
            n: Group number or count value        
        Returns:
            int: remaining_groups - The number of groups remaining after deletion
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            # Function returns actual output value, not error code
            _return_value = self._lib.BI_delete_group(n)
            # Check for negative values which indicate errors
            if _return_value < 0:
                error_code = _return_value
            else:
                error_code = BI_OK

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        # Return the function's return value (actual output)
        return int(_return_value)


    def display_setup_window(self, id: str, hinstance: int) -> None:
        """
        Show the setup window for a component.
        
        Displays the configuration dialog for a hardware component if one is available. Requires a window handle from the calling application.
        
        Args:
            id: Component identifier string            hinstance: Window handle for displaying dialog
        
        Raises:
            InvalidComponentException: Specific error condition
            NoSetupWindowException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_display_setup_window(id_bytes, hinstance)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def display_advanced_window(self, id: str, hinstance: int) -> None:
        """
        Show the advanced setup window for a component.
        
        Displays the advanced configuration dialog for a hardware component if one is available. Requires a window handle from the calling application.
        
        Args:
            id: Component identifier string            hinstance: Window handle for displaying dialog
        
        Raises:
            InvalidComponentException: Specific error condition
            NoSetupWindowException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_display_advanced_window(id_bytes, hinstance)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def get(self, id: str, token: int, index: int) -> float:
        """
        Get a numeric attribute value from a component.
        
        Retrieves a numeric (double) attribute from a hardware component. Use tokens to specify which attribute to read. The index parameter is used for multi-value attributes (usually 0).
        
        Args:
            id: Component identifier string            token: Token identifier for the attribute to access            index: Index for multi-value attributes (usually 0 for single values)        
        Returns:
            float: Numeric value to set or retrieve

        
        Raises:
            BenHWException: Specific error condition
            InvalidAttributeException: Specific error condition
            InvalidComponentException: Specific error condition
            InvalidTokenException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        value_ptr = self._ffi.new("double*")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_get(id_bytes, token, index, value_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return value_ptr[0]


    def get_str(self, id: str, token: int, index: int) -> str:
        """
        Get a string attribute value from a component.
        
        Retrieves a string attribute from a hardware component. Use tokens to specify which attribute to read. Buffer must be pre-allocated (256 bytes recommended).
        
        Args:
            id: Component identifier string            token: Token identifier for the attribute to access            index: Index for multi-value attributes (usually 0 for single values)        
        Returns:
            str: String value or buffer for text data

        
        Raises:
            BenHWException: Specific error condition
            InvalidAttributeException: Specific error condition
            InvalidComponentException: Specific error condition
            InvalidTokenException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        s_buf = self._ffi.new("char[]", 4096)
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_get_str(id_bytes, token, index, s_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return self._ffi.string(s_buf).decode('utf-8')


    def get_c_group(self) -> int:
        """
        Get the current active group number.
        
        Returns the number of the currently active component group.
        
        Returns:
            int: Group number or count value

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        n_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_get_c_group(n_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return n_ptr[0]


    def get_component_list(self) -> str:
        """
        Get a comma-separated list of all components.
        
        Returns a string containing the IDs of all components in the system, separated by commas.
        
        Returns:
            str: Comma-separated list of component IDs

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        list_buf = self._ffi.new("char[]", 4096)
        
        try:
            error_code = self._lib.BI_get_component_list(list_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return self._ffi.string(list_buf).decode('utf-8')


    def get_group(self, n: int) -> str:
        """
        Get the component IDs in a specific group.
        
        Returns a comma-separated string of component IDs that belong to the specified group.
        
        Args:
            n: Group number or count value        
        Returns:
            str: Comma-separated list of component IDs

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        s_buf = self._ffi.new("char[]", 4096)
        
        try:
            error_code = self._lib.BI_get_group(n, s_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return self._ffi.string(s_buf).decode('utf-8')


    def get_hardware_type(self, id: str) -> int:
        """
        Get the hardware type constant for a component.
        
        Returns the hardware type identifier (e.g., BenMono, BenADC) for a component. Use this to determine what kind of hardware a component represents. See Hardware Types in Tokens list.
        
        Args:
            id: Component identifier string        
        Returns:
            int: Hardware type identifier token constant

        
        Raises:
            InvalidComponentException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        hardwareType_ptr = self._ffi.new("int*")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_get_hardware_type(id_bytes, hardwareType_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return hardwareType_ptr[0]


    def get_log(self) -> bytes:
        """
        Retrieve accumulated log messages.
        
        Gets the log messages that have been accumulated during operation.
        
        Returns:
            bytes: Bytes containing log content. May contain \r characters.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get_log_size
        _size_BI_get_log_size = int(self.get_log_size())
        # Array log sized by BI_get_log_size
        log_buf = self._ffi.new("char[]", _size_BI_get_log_size)
        # Fill with dummy character (0xCC) for Pascal DLL compatibility
        self._ffi.buffer(log_buf)[:] = bytes([204]) * _size_BI_get_log_size
        
        try:
            error_code = self._lib.BI_get_log(log_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return bytes(self._ffi.buffer(log_buf))


    def get_log_size(self) -> int:
        """
        Get the size of accumulated log messages.
        
        Returns the number of bytes needed to store the accumulated log messages. Call this before get_log to allocate appropriate buffer size.
        
        Returns:
            int: Number of bytes

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        size_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_get_log_size(size_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return size_ptr[0]


    def get_mono_items(self, monoID: str) -> str:
        """
        List components associated with a monochromator.
        
        Returns a comma-separated list of component IDs that are part of a monochromator (gratings, filters, etc.). Buffer must be pre-allocated.
        
        Args:
            monoID: Monochromator component identifier        
        Returns:
            str: Comma-separated list of item IDs

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        ItemIDs_buf = self._ffi.new("char[]", 4096)
        monoID_bytes = monoID.encode('utf-8') if isinstance(monoID, str) else monoID
        
        try:
            error_code = self._lib.BI_get_mono_items(monoID_bytes, ItemIDs_buf)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return self._ffi.string(ItemIDs_buf).decode('utf-8')


    def get_min_step(self, group: int, start_wl: float, stop_wl: float) -> float:
        """
        Get the minimum wavelength step for a wavelength range.
        
        Calculates the minimum wavelength increment supported by the system for a given wavelength range. Important for scan planning.
        
        Args:
            group: Component group number            start_wl: Starting wavelength for the range in nanometers            stop_wl: Ending wavelength for the range in nanometers        
        Returns:
            float: Minimum wavelength step size in nanometers

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        min_step_ptr = self._ffi.new("double*")
        
        try:
            error_code = self._lib.BI_get_min_step(group, start_wl, stop_wl, min_step_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return min_step_ptr[0]


    def get_max_bw(self, group: int, start_wl: float, stop_wl: float) -> float:
        """
        Get the maximum bandwidth for a wavelength range.
        
        Calculates the maximum spectral bandwidth (slit width equivalent) available for a given wavelength range.
        
        Args:
            group: Component group number            start_wl: Starting wavelength for the range in nanometers            stop_wl: Ending wavelength for the range in nanometers        
        Returns:
            float: Spectral bandwidth value

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        bandwidth_ptr = self._ffi.new("double*")
        
        try:
            error_code = self._lib.BI_get_max_bw(group, start_wl, stop_wl, bandwidth_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return bandwidth_ptr[0]


    def get_no_of_dark_currents(self) -> int:
        """
        Get the number of dark current calibration points.
        
        Returns the count of wavelength points in the dark current calibration table for the current group.
        
        Returns:
            int: Number of calibration values in the arrays

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        NoOfValues_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_get_no_of_dark_currents(NoOfValues_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return NoOfValues_ptr[0]


    def get_n_groups(self) -> int:
        """
        Get the total number of component groups.
        
        Returns the count of all component groups that have been created.
        
        Returns:
            int: Group number or count value

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        n_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_get_n_groups(n_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return n_ptr[0]


    def get_zero_calibration_info(self) -> BI_get_zero_calibration_info_result:
        """
        Get zero calibration data for current group.
        
        Retrieves wavelength, dark current, and Analogue-digital Converter (ADC) offset arrays from the zero calibration table. Arrays must be pre-allocated based on the count from get_no_of_dark_currents.
        
        Returns:
            BI_get_zero_calibration_info_result: Object containing multiple output values

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get_no_of_dark_currents
        _size_BI_get_no_of_dark_currents = int(self.get_no_of_dark_currents())
        # Array wavelength sized by BI_get_no_of_dark_currents
        wavelength_ptr = self._ffi.new("double[]", _size_BI_get_no_of_dark_currents)
        # Array DarkCurrent sized by BI_get_no_of_dark_currents
        DarkCurrent_ptr = self._ffi.new("double[]", _size_BI_get_no_of_dark_currents)
        # Array ADCOffset sized by BI_get_no_of_dark_currents
        ADCOffset_ptr = self._ffi.new("double[]", _size_BI_get_no_of_dark_currents)
        
        try:
            error_code = self._lib.BI_get_zero_calibration_info(wavelength_ptr, DarkCurrent_ptr, ADCOffset_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return BI_get_zero_calibration_info_result(
            wavelength=list(wavelength_ptr[0:_size_BI_get_no_of_dark_currents]),            DarkCurrent=list(DarkCurrent_ptr[0:_size_BI_get_no_of_dark_currents]),            ADCOffset=list(ADCOffset_ptr[0:_size_BI_get_no_of_dark_currents]),        )


    def group_add(self, id: str, n: int) -> None:
        """
        Add a component to a group.
        
        Adds a component (by ID) to an existing group. Components in a group can be controlled together.
        
        Args:
            id: Component identifier string            n: Group number or count value
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_group_add(id_bytes, n)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def group_remove(self, id: str, n: int) -> None:
        """
        Remove a component from a group.
        
        Removes a component (by ID) from a group.
        
        Args:
            id: Component identifier string            n: Group number or count value
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_group_remove(id_bytes, n)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def initialise(self) -> None:
        """
        Initialize the hardware system.
        
        Initializes all hardware components for the current group. Must be called after build_system_model and before taking measurements. This homes monochromators and sets up detectors. The system must be initialized before measurements can be taken.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_initialise()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def load_setup(self, filename: str) -> None:
        """
        Load component settings from a setup file.
        
        Loads previously saved component configurations from a setup file. This restores settings like wavelengths, gains, and other parameters.
        
        Args:
            filename: Path to the configuration or setup file
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        filename_bytes = filename.encode('utf-8') if isinstance(filename, str) else filename
        
        try:
            error_code = self._lib.BI_load_setup(filename_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def measurement(self) -> float:
        """
        Take a measurement without autoranging.
        
        Takes a reading from the detector at the current settings. Unlike automeasure, this does not adjust the gain. Negative values are clamped to zero unless AllowNegative is set. This function returns the reading at the current wavelength for the active group.
        
        Returns:
            float: Measurement reading value or array

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        reading_ptr = self._ffi.new("double*")
        
        try:
            error_code = self._lib.BI_measurement(reading_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return reading_ptr[0]


    def multi_automeasure(self) -> list[float]:
        """
        Take measurements from all groups with autoranging.
        
        Performs automeasure on all component groups simultaneously. Returns an array of readings, one per group. Array must be pre-allocated.
        
        Returns:
            list[float]: Measurement reading value or array

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get_n_groups
        _size_BI_get_n_groups = int(self.get_n_groups())
        # Array reading sized by BI_get_n_groups
        reading_ptr = self._ffi.new("double[]", _size_BI_get_n_groups)
        
        try:
            error_code = self._lib.BI_multi_automeasure(reading_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return list(reading_ptr[0:_size_BI_get_n_groups])

    def multi_autorange(self) -> None:
        """
        Auto-range all groups simultaneously.
        
        Adjusts the amplifier ranges for all component groups at the same time.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_multi_autorange()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def multi_get_no_of_dark_currents(self, group: int) -> int:
        """
        Get dark current calibration point count for a specific group.
        
        Returns the number of wavelength points in the dark current calibration table for the specified group.
        
        Args:
            group: Component group number        
        Returns:
            int: Number of calibration values in the arrays

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        NoOfValues_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_multi_get_no_of_dark_currents(group, NoOfValues_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return NoOfValues_ptr[0]


    def multi_get_zero_calibration_info(self, group: int) -> BI_multi_get_zero_calibration_info_result:
        """
        Get zero calibration data for a specific group.
        
        Retrieves wavelength, dark current, and ADC offset arrays for the specified group. Arrays must be pre-allocated.
        
        Args:
            group: Component group number        
        Returns:
            BI_multi_get_zero_calibration_info_result: Object containing multiple output values

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_multi_get_no_of_dark_currents with forwarded args: group
        _size_BI_multi_get_no_of_dark_currents__FWDARG__group = int(self.multi_get_no_of_dark_currents(group))        # Array wavelength sized by BI_multi_get_no_of_dark_currents (cached)
        wavelength_ptr = self._ffi.new("double[]", _size_BI_multi_get_no_of_dark_currents__FWDARG__group)
        # Array DarkCurrent sized by BI_multi_get_no_of_dark_currents (cached)
        DarkCurrent_ptr = self._ffi.new("double[]", _size_BI_multi_get_no_of_dark_currents__FWDARG__group)
        # Array ADCOffset sized by BI_multi_get_no_of_dark_currents (cached)
        ADCOffset_ptr = self._ffi.new("double[]", _size_BI_multi_get_no_of_dark_currents__FWDARG__group)
        
        try:
            error_code = self._lib.BI_multi_get_zero_calibration_info(group, wavelength_ptr, DarkCurrent_ptr, ADCOffset_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return BI_multi_get_zero_calibration_info_result(
            wavelength=list(wavelength_ptr[0:_size_BI_multi_get_no_of_dark_currents__FWDARG__group]),            DarkCurrent=list(DarkCurrent_ptr[0:_size_BI_multi_get_no_of_dark_currents__FWDARG__group]),            ADCOffset=list(ADCOffset_ptr[0:_size_BI_multi_get_no_of_dark_currents__FWDARG__group]),        )


    def multi_initialise(self) -> None:
        """
        Initialize all groups simultaneously.
        
        Initializes hardware for all component groups at the same time. Faster than initializing each group separately.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_multi_initialise()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def multi_measurement(self) -> list[float]:
        """
        Take measurements from all groups.
        
        Takes readings from all component groups simultaneously. Returns an array of readings. Array must be pre-allocated.
        
        Returns:
            list[float]: Measurement reading value or array

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Get array size from BI_get_n_groups
        _size_BI_get_n_groups = int(self.get_n_groups())
        # Array reading sized by BI_get_n_groups
        reading_ptr = self._ffi.new("double[]", _size_BI_get_n_groups)
        
        try:
            error_code = self._lib.BI_multi_measurement(reading_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return list(reading_ptr[0:_size_BI_get_n_groups])

    def multi_park(self) -> None:
        """
        Park all monochromators in all groups.
        
        Moves all monochromators to their park positions across all groups simultaneously.

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_multi_park()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def multi_select_wavelength(self, wavelength: float) -> int:
        """
        Set wavelength for all groups simultaneously.
        
        Changes the wavelength for monochromators in all groups at the same time. Returns the maximum settle delay needed.
        
        Args:
            wavelength: Wavelength value in nanometers        
        Returns:
            int: Settle delay time in milliseconds after wavelength change

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        settle_delay_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_multi_select_wavelength(wavelength, settle_delay_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return settle_delay_ptr[0]


    def multi_zero_calibration(self, start_wavelength: float, stop_wavelength: float) -> None:
        """
        Perform zero calibration across a wavelength range for all groups.
        
        Runs zero calibration (dark current and offset measurement) for all groups across the specified wavelength range.
        
        Args:
            start_wavelength: Starting wavelength for the range in nanometers            stop_wavelength: Ending wavelength for the range in nanometers
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_multi_zero_calibration(start_wavelength, stop_wavelength)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def park(self) -> None:
        """
        Park the monochromator in the current group.
        
        Moves the monochromator to its park position (usually a safe wavelength or home position).

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_park()

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def read(self, buffer_size: int, id: str) -> BI_read_result:
        """
        Read data from an anonymous device.
        
        Reads raw data from a device like an ADC or serial device. Buffer and size must be specified. Returns the actual number of characters read.
        
        Args:
            buffer_size: Size of the buffer in bytes            id: Component identifier string        
        Returns:
            BI_read_result: Object containing multiple output values

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Array size parameter: buffer_size
        buffer_buf = self._ffi.new("char[]", buffer_size)
        chars_read_ptr = self._ffi.new("uint16_t*")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_read(buffer_buf, buffer_size, chars_read_ptr, id_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return BI_read_result(
            buffer=bytes(self._ffi.buffer(buffer_buf)),
            chars_read=chars_read_ptr[0],
        )


    def report_error(self) -> int:
        """
        Get the last error code.
        
        Returns the most recent error code from hardware operations. Use this to get detailed error information after a function returns an error. See error code definitions for meanings. Calling report_error clears the error code, i.e. subsequent calls will return no error (0) until another hardware error occurs.
        
        Returns:
            int: error_code
        
        Raises:
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            # Function returns actual output value, not error code
            _return_value = self._lib.BI_report_error()
            # Check for negative values which indicate errors
            if _return_value < 0:
                error_code = _return_value
            else:
                error_code = BI_OK

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        
        # Return the function's return value (actual output)
        return int(_return_value)


    def save_setup(self, filename: str) -> None:
        """
        Save current component settings to a file.
        
        Saves the current configuration of all components to a setup file. This includes wavelengths, gains, and other settings that can be restored with load_setup.
        
        Args:
            filename: Path to the configuration or setup file
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        filename_bytes = filename.encode('utf-8') if isinstance(filename, str) else filename
        
        try:
            error_code = self._lib.BI_save_setup(filename_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def select_wavelength(self, wl: float) -> int:
        """
        Set the wavelength for the current group.
        
        Changes the wavelength of monochromators in the current group. Returns the settle delay time needed before taking measurements. The DLL will coordinate the operation of gratings, filter wheels, and SAMs to achieve the target wavelength.
        
        Args:
            wl: Wavelength value in nanometers        
        Returns:
            int: Settle delay time in milliseconds after wavelength change

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        settle_delay_ptr = self._ffi.new("int*")
        
        try:
            error_code = self._lib.BI_select_wavelength(wl, settle_delay_ptr)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return settle_delay_ptr[0]


    def send(self, msg: str, id: str) -> None:
        """
        Send a command to an anonymous device.
        
        Sends a raw command string to a device like a serial instrument or controller.
        
        Args:
            msg: Message string to send or query            id: Component identifier string
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        msg_bytes = msg.encode('utf-8') if isinstance(msg, str) else msg
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_send(msg_bytes, id_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def set(self, id: str, token: int, index: int, value: float) -> None:
        """
        Set a numeric attribute value for a component.
        
        Sets a numeric (double) attribute on a hardware component. Use tokens to specify which attribute to set. The index parameter is used for multi-value attributes (usually 0).
        
        Args:
            id: Component identifier string            token: Token identifier for the attribute to access            index: Index for multi-value attributes (usually 0 for single values)            value: Numeric value to set or retrieve
        
        Raises:
            BenHWException: Specific error condition
            InvalidAttributeException: Specific error condition
            InvalidComponentException: Specific error condition
            InvalidTokenException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_set(id_bytes, token, index, value)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def set_str(self, id: str, token: int, index: int, s: str) -> None:
        """
        Set a string attribute value for a component.
        
        Sets a string attribute on a hardware component. Use tokens to specify which attribute to set.
        
        Args:
            id: Component identifier string            token: Token identifier for the attribute to access            index: Index for multi-value attributes (usually 0 for single values)            s: String value or buffer for text data
        
        Raises:
            BenHWException: Specific error condition
            InvalidAttributeException: Specific error condition
            InvalidComponentException: Specific error condition
            InvalidTokenException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        s_bytes = s.encode('utf-8') if isinstance(s, str) else s
        
        try:
            error_code = self._lib.BI_set_str(id_bytes, token, index, s_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def start_log(self, c_list: str) -> None:
        """
        Start logging for specified components.
        
        Begins accumulating log messages for the specified comma-separated list of component IDs. Useful for debugging and diagnostics.
        
        Args:
            c_list: Comma-separated list of component IDs
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        c_list_bytes = c_list.encode('utf-8') if isinstance(c_list, str) else c_list
        
        try:
            error_code = self._lib.BI_start_log(c_list_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def stop_log(self, c_list: str) -> None:
        """
        Stop logging for specified components.
        
        Stops accumulating log messages for the specified components.
        
        Args:
            c_list: Comma-separated list of component IDs
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        c_list_bytes = c_list.encode('utf-8') if isinstance(c_list, str) else c_list
        
        try:
            error_code = self._lib.BI_stop_log(c_list_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def trace(self, i: int, LoggingDir: str) -> None:
        """
        Enable or disable trace logging.
        
        Controls detailed trace logging to file. Pass 1 to enable and provide a logging directory, or 0 to disable. Trace logs are very detailed and useful for troubleshooting hardware communication issues and debugging applications.
        
        Args:
            i: Integer flag or control value (0=off, 1=on)            LoggingDir: Directory path for logging output
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        LoggingDir_bytes = LoggingDir.encode('utf-8') if isinstance(LoggingDir, str) else LoggingDir
        
        try:
            error_code = self._lib.BI_trace(i, LoggingDir_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def Mapped_Logging(self, i: int) -> None:
        """
        Enable or disable mapped logging.
        
        Controls whether motor position logging uses mapped values. Pass 1 to enable, 0 to disable.
        
        Args:
            i: Integer flag or control value (0=off, 1=on)
        
        Raises:
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            self._lib.BI_Mapped_Logging(i)
            error_code = BI_OK

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        
        return None


    def use_group(self, n: int) -> None:
        """
        Set the current active group.
        
        Changes which component group is active. Subsequent operations will apply to this group.
        
        Args:
            n: Group number or count value
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_use_group(n)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def version(self) -> str:
        """
        Get the DLL version string.
        
        Returns the version of the BenHW DLL as a string (e.g., 'v4.12.0 (32 bit)'). Buffer must be pre-allocated with sufficient space (256 characters recommended).
        
        Returns:
            str: String value or buffer for text data

        
        Raises:
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        s_buf = self._ffi.new("char[]", 4096)
        
        try:
            self._lib.BI_version(s_buf)
            error_code = BI_OK

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        
        return self._ffi.string(s_buf).decode('utf-8')


    def zero_calibration(self, start_wl: float, stop_wl: float) -> None:
        """
        Perform zero calibration across a wavelength range.
        
        Runs zero calibration (dark current and offset measurement) for the current group across the specified wavelength range. Essential for accurate measurements. The system should be in darkness or the shutter closed during this operation.
        
        Args:
            start_wl: Starting wavelength for the range in nanometers            stop_wl: Ending wavelength for the range in nanometers
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        
        try:
            error_code = self._lib.BI_zero_calibration(start_wl, stop_wl)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


    def SCPI_query(self, id: str, msg: str, reply_size: int) -> bytes:
        """
        Send a SCPI query command and read response.
        
        Sends a SCPI (Standard Commands for Programmable Instruments) query to a USB SCPI device and reads the response. Buffer size must be specified.
        
        Args:
            id: Component identifier string            msg: Message string to send or query            reply_size: Maximum size of reply buffer in bytes        
        Returns:
            bytes: Buffer to receive reply data

        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        # Array size parameter: reply_size
        reply_buf = self._ffi.new("char[]", reply_size)
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        msg_bytes = msg.encode('utf-8') if isinstance(msg, str) else msg
        
        try:
            error_code = self._lib.BI_SCPI_query(id_bytes, msg_bytes, reply_buf, reply_size)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return bytes(self._ffi.buffer(reply_buf))


    def SCPI_write(self, msg: str, id: str) -> None:
        """
        Send a SCPI write command.
        
        Sends a SCPI (Standard Commands for Programmable Instruments) command to a USB SCPI device without expecting a response.
        
        Args:
            msg: Message string to send or query            id: Component identifier string
        
        Raises:
            BenHWException: Specific error condition
            SdkException: General error or if an error occurs
        """
        if not self.is_loaded():
            raise SdkException(BI_error, "DLL not loaded")
        msg_bytes = msg.encode('utf-8') if isinstance(msg, str) else msg
        id_bytes = id.encode('utf-8') if isinstance(id, str) else id
        
        try:
            error_code = self._lib.BI_SCPI_write(msg_bytes, id_bytes)

        except Exception as e:
            raise SdkException(BI_error, f"DLL call failed: {e}")        # Raise exception if error occurred
        _raise_for_error(error_code)        
        return None


