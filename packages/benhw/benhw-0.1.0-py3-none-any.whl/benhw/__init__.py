"""BenHW SDK - Python Interface

Auto-generated from manifest.json by generate.py

Copyright (c) Bentham Instruments Ltd
All Rights Reserved

Usage:
    from benhw import BenHW, tokens, exceptions, SdkException
    
    hw = BenHW()
    try:
        value = hw.get("mono1", tokens.MonochromatorCurrentWL, 0)
        print(f"Wavelength: {value}")
    except SdkException as e:
        print(f"Error: {e}")
"""

from .benhw import BenHW
from . import tokens
from . import exceptions

# Re-export exception classes from exceptions module
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

# Re-export result models from benhw for type hints
from .benhw import *  # noqa: F401,F403

__all__ = ['BenHW', 'tokens', 'exceptions', 'SdkException', 'BI_error', 'BI_invalid_token', 'BI_invalid_component', 'BI_invalid_attribute', 'BI_no_setup_window', 'BI_PMC_timeout', 'BI_MSC_timeout', 'BI_MSD_timeout', 'BI_MAC_timeout', 'BI_MAC_invalid_cmd', 'BI_225_dead', 'BI_265_dead', 'BI_267_dead', 'BI_277_dead', 'BI_262_dead', 'BI_ADC_read_error', 'BI_ADC_invalid_reading', 'BI_ADC_Overload', 'BI_AMP_invalid_channel', 'BI_AMP_invalid_wavelength', 'BI_SAM_invalid_wavelength', 'BI_turret_invalid_wavelength', 'BI_turret_incorrect_pos', 'BI_MVSS_invalid_width', 'BI_Comms_TX_error', 'BI_Action_Timeout', 'BI_Invalid_Command_error', 'BI_External_Driver_error', 'BI_undefined_error', 'BI_camera_measurement_result_protocol', 'BI_camera_measurement_result', 'BI_camera_get_zero_calibration_info_result_protocol', 'BI_camera_get_zero_calibration_info_result', 'BI_get_zero_calibration_info_result_protocol', 'BI_get_zero_calibration_info_result', 'BI_multi_get_zero_calibration_info_result_protocol', 'BI_multi_get_zero_calibration_info_result', 'BI_read_result_protocol', 'BI_read_result']