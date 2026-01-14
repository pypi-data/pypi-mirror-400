"""BenHW SDK - Error Code Definitions and Exceptions

Auto-generated from manifest.json by generate.py

Copyright (c) Bentham Instruments Ltd
All Rights Reserved

Usage:
    from benhw import exceptions
    if result == exceptions.Codes.BI_OK:
        print("Success!")
    
    # Or use the convenience constants
    if result == exceptions.OK:
        print("Success!")
    
    # Catch exceptions
    try:
        hw.some_operation()
    except exceptions.BI_error as e:
        print(f"Error: {e}")
"""


class Codes:
    """Error code constants returned by BenHW DLL functions.
    
    These integer constants represent the status codes that can be returned
    by BenHW DLL functions. A value of 0 (BI_OK) indicates success, while
    negative values indicate errors.
    """

    BI_OK=0
    BI_225_dead = 10
    """225 lock-in amplifier is not responding to commands."""
    BI_262_dead = 14
    """262 relay unit is not responding to commands."""
    BI_265_dead = 11
    """265 DC amplifier is not responding to commands."""
    BI_267_dead = 12
    """267 amplifier is not responding to commands."""
    BI_277_dead = 13
    """277 amplifier is not responding to commands."""
    BI_ADC_Overload = 22
    """Analogue-digital Converter (ADC) overload detected - the input signal is too strong for the current range setting."""
    BI_ADC_invalid_reading = 21
    """Could not obtain a valid reading from the Analogue-digital Converter (ADC). The reading may be out of range or corrupted."""
    BI_ADC_read_error = 20
    """Analogue-digital Converter (ADC) is not responding or failed to complete a read operation."""
    BI_AMP_invalid_channel = 30
    """Invalid amplifier channel specified. Check the channel number is valid for your amplifier model."""
    BI_AMP_invalid_wavelength = 31
    """Invalid wavelength specified for amplifier operation. The wavelength may be outside the valid range."""
    BI_Action_Timeout = 50
    """Hardware action timed out before completing. The operation took longer than the maximum allowed time."""
    BI_Comms_TX_error = 40
    """Communication transmission error occurred during data transfer to hardware."""
    BI_External_Driver_error = 61
    """Error occurred in external driver or DLL used to communicate with hardware."""
    BI_Invalid_Command_error = 60
    """Invalid command was sent to the hardware or received an unexpected response."""
    BI_MAC_invalid_cmd = 5
    """Error in communication with MAC - invalid command was sent or received."""
    BI_MAC_timeout = 4
    """MAC (Motor & Accessory Controller) is not responding to commands."""
    BI_MSC_timeout = 2
    """MSC1 (Motor & Stepper Controller) is not responding to commands."""
    BI_MSD_timeout = 3
    """MSD (Motor & Stepper Driver) is not responding to commands."""
    BI_MVSS_invalid_width = 35
    """Invalid slit width specified for Motorised Variable Slits (MVSS). Width must be in valid range."""
    BI_PMC_timeout = 1
    """PMC (Power & Motor Controller) is not responding to commands."""
    BI_SAM_invalid_wavelength = 32
    """Invalid wavelength specified for Swing Away Mirror (SAM) operation."""
    BI_error = -1
    """Function call failed. Use BI_report_error to get detailed hardware error code."""
    BI_invalid_attribute = -4
    """The function was passed an attribute token referring to an attribute that does not exist or is inaccessible for the specified component."""
    BI_invalid_component = -3
    """The function was passed a component identifier that does not exist in the system model."""
    BI_invalid_token = -2
    """The function was passed an invalid attribute token that is not recognized."""
    BI_no_setup_window = -5
    """No setup window is available for the specified component."""
    BI_turret_incorrect_pos = 34
    """Turret is not in the expected position. Error in communication with MAC or mechanical fault."""
    BI_turret_invalid_wavelength = 33
    """Attempt to send monochromator beyond its valid wavelength range for the current grating."""
    BI_undefined_error = 100
    """An undefined error occurred. The error code is not recognized or has not been categorized."""


# Commonly used error codes for convenience
OK = Codes.BI_OK
ERROR = Codes.BI_error


# Exception classes for BenHW exceptions
class SdkException(Exception):
    """Base exception for all BenHW exceptions"""
    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(f"[Error {error_code}] {message}")


class Amp225DeadException(SdkException):
    """225 lock-in amplifier is not responding to commands."""
    def __init__(self):
        super().__init__(10, "225 lock-in amplifier is not responding to commands.")

class Relay262DeadException(SdkException):
    """262 relay unit is not responding to commands."""
    def __init__(self):
        super().__init__(14, "262 relay unit is not responding to commands.")

class Amp265DeadException(SdkException):
    """265 DC amplifier is not responding to commands."""
    def __init__(self):
        super().__init__(11, "265 DC amplifier is not responding to commands.")

class Amp267DeadException(SdkException):
    """267 amplifier is not responding to commands."""
    def __init__(self):
        super().__init__(12, "267 amplifier is not responding to commands.")

class Amp277DeadException(SdkException):
    """277 amplifier is not responding to commands."""
    def __init__(self):
        super().__init__(13, "277 amplifier is not responding to commands.")

class AdcOverloadException(SdkException):
    """Analogue-digital Converter (ADC) overload detected - the input signal is too strong for the current range setting."""
    def __init__(self):
        super().__init__(22, "Analogue-digital Converter (ADC) overload detected - the input signal is too strong for the current range setting.")

class AdcInvalidReadingException(SdkException):
    """Could not obtain a valid reading from the Analogue-digital Converter (ADC). The reading may be out of range or corrupted."""
    def __init__(self):
        super().__init__(21, "Could not obtain a valid reading from the Analogue-digital Converter (ADC). The reading may be out of range or corrupted.")

class AdcReadErrorException(SdkException):
    """Analogue-digital Converter (ADC) is not responding or failed to complete a read operation."""
    def __init__(self):
        super().__init__(20, "Analogue-digital Converter (ADC) is not responding or failed to complete a read operation.")

class AmpInvalidChannelException(SdkException):
    """Invalid amplifier channel specified. Check the channel number is valid for your amplifier model."""
    def __init__(self):
        super().__init__(30, "Invalid amplifier channel specified. Check the channel number is valid for your amplifier model.")

class AmpInvalidWavelengthException(SdkException):
    """Invalid wavelength specified for amplifier operation. The wavelength may be outside the valid range."""
    def __init__(self):
        super().__init__(31, "Invalid wavelength specified for amplifier operation. The wavelength may be outside the valid range.")

class ActionTimeoutException(SdkException):
    """Hardware action timed out before completing. The operation took longer than the maximum allowed time."""
    def __init__(self):
        super().__init__(50, "Hardware action timed out before completing. The operation took longer than the maximum allowed time.")

class CommsTxErrorException(SdkException):
    """Communication transmission error occurred during data transfer to hardware."""
    def __init__(self):
        super().__init__(40, "Communication transmission error occurred during data transfer to hardware.")

class ExternalDriverErrorException(SdkException):
    """Error occurred in external driver or DLL used to communicate with hardware."""
    def __init__(self):
        super().__init__(61, "Error occurred in external driver or DLL used to communicate with hardware.")

class InvalidCommandErrorException(SdkException):
    """Invalid command was sent to the hardware or received an unexpected response."""
    def __init__(self):
        super().__init__(60, "Invalid command was sent to the hardware or received an unexpected response.")

class MacInvalidCmdException(SdkException):
    """Error in communication with MAC - invalid command was sent or received."""
    def __init__(self):
        super().__init__(5, "Error in communication with MAC - invalid command was sent or received.")

class MacTimeoutException(SdkException):
    """MAC (Motor & Accessory Controller) is not responding to commands."""
    def __init__(self):
        super().__init__(4, "MAC (Motor & Accessory Controller) is not responding to commands.")

class MscTimeoutException(SdkException):
    """MSC1 (Motor & Stepper Controller) is not responding to commands."""
    def __init__(self):
        super().__init__(2, "MSC1 (Motor & Stepper Controller) is not responding to commands.")

class MsdTimeoutException(SdkException):
    """MSD (Motor & Stepper Driver) is not responding to commands."""
    def __init__(self):
        super().__init__(3, "MSD (Motor & Stepper Driver) is not responding to commands.")

class MvssInvalidWidthException(SdkException):
    """Invalid slit width specified for Motorised Variable Slits (MVSS). Width must be in valid range."""
    def __init__(self):
        super().__init__(35, "Invalid slit width specified for Motorised Variable Slits (MVSS). Width must be in valid range.")

class PmcTimeoutException(SdkException):
    """PMC (Power & Motor Controller) is not responding to commands."""
    def __init__(self):
        super().__init__(1, "PMC (Power & Motor Controller) is not responding to commands.")

class SamInvalidWavelengthException(SdkException):
    """Invalid wavelength specified for Swing Away Mirror (SAM) operation."""
    def __init__(self):
        super().__init__(32, "Invalid wavelength specified for Swing Away Mirror (SAM) operation.")

class BenHWException(SdkException):
    """Function call failed. Use BI_report_error to get detailed hardware error code."""
    def __init__(self):
        super().__init__(-1, "Function call failed. Use BI_report_error to get detailed hardware error code.")

class InvalidAttributeException(SdkException):
    """The function was passed an attribute token referring to an attribute that does not exist or is inaccessible for the specified component."""
    def __init__(self):
        super().__init__(-4, "The function was passed an attribute token referring to an attribute that does not exist or is inaccessible for the specified component.")

class InvalidComponentException(SdkException):
    """The function was passed a component identifier that does not exist in the system model."""
    def __init__(self):
        super().__init__(-3, "The function was passed a component identifier that does not exist in the system model.")

class InvalidTokenException(SdkException):
    """The function was passed an invalid attribute token that is not recognized."""
    def __init__(self):
        super().__init__(-2, "The function was passed an invalid attribute token that is not recognized.")

class NoSetupWindowException(SdkException):
    """No setup window is available for the specified component."""
    def __init__(self):
        super().__init__(-5, "No setup window is available for the specified component.")

class TurretIncorrectPosException(SdkException):
    """Turret is not in the expected position. Error in communication with MAC or mechanical fault."""
    def __init__(self):
        super().__init__(34, "Turret is not in the expected position. Error in communication with MAC or mechanical fault.")

class TurretInvalidWavelengthException(SdkException):
    """Attempt to send monochromator beyond its valid wavelength range for the current grating."""
    def __init__(self):
        super().__init__(33, "Attempt to send monochromator beyond its valid wavelength range for the current grating.")

class UndefinedErrorException(SdkException):
    """An undefined error occurred. The error code is not recognized or has not been categorized."""
    def __init__(self):
        super().__init__(100, "An undefined error occurred. The error code is not recognized or has not been categorized.")
