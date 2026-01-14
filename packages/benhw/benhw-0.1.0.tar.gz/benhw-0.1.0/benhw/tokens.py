"""BenHW SDK - Token Definitions

Auto-generated from manifest.json by generate.py

Copyright (c) Bentham Instruments Ltd
All Rights Reserved

Usage:
    from benhw import tokens
    value = tokens.ADCVolts
"""

A225fMode = 704
"""Frequency mode setting for the 225 lock-in amplifier. 1 = f mode, 2 = 2f mode (second harmonic detection). Default is 1."""
A225PhaseQuadrant = 702
"""Phase quadrant setting for the 225 lock-in amplifier. Valid values 1-4, corresponding to 0 degrees, 90 degrees, 180 degrees, 270 degrees. Default is 1 (0 degrees)."""
A225PhaseVariable = 701
"""Phase variable setting for the 225 lock-in amplifier. Fine-tune phase within quadrant. Range 0 to 102.4. Default is 0."""
A225TargetRange = 700
"""Target range setting for the 225 lock-in amplifier. Valid values 1-7, where 1 is least sensitive. Default is 1."""
A225TimeConstant = 703
"""Time constant setting for the 225 lock-in amplifier. Valid values 1-7: 10ms, 30ms, 0.1s, 0.3s, 1s, 3s, 10s. Affects signal averaging. Default is 1 (10ms)."""
ADCAdaptiveIntegration = 501
"""Adaptive integration mode for the Analogue-digital Converter (ADC). When enabled, integration time automatically increases as signal weakens to maintain good signal-to-noise ratio. 0 = off, 1 = on."""
ADCAuxInput = 509
"""Select the 487 amplifier auxiliary input channel for reading."""
ADCAuxOffset = 508
"""Get or set the auxiliary input offset for 487 amplifier. Should be manually calibrated. Default is 0."""
ADCAuxVolts = 507
"""Read voltage from a 487 amplifier auxiliary input. Returns value in volts."""
ADCChoppedAverages = 503
"""Analogue-digital Converter (ADC) chopped averages"""
ADCRefFrequency = 511
"""Analogue-digital Converter (ADC) reference frequency"""
ADCSamplePeriod = 502
"""Sample period in milliseconds for Analogue-digital Converter (ADC) readings. For a 228A ADC that produces a new sample every 100ms, setting 10 samples per reading means each reading takes 1 second. Default is 100 ms."""
ADCSamplesPerReading = 500
"""Number of samples integrated for one Analogue-digital Converter (ADC) reading. Indexed 0-6, where 0 is for non-adaptive integration and 1-6 corresponds to amplifier range. Increasing this increases signal-to-noise ratio. Default is 10."""
ADCTimeConstant = 505
"""Time constant setting for use with Stanford Research lock-in amplifier. Affects signal averaging time."""
ADCVolts = 504
"""Take a voltage reading from the Analogue-digital Converter (ADC). This communicates directly with hardware."""
ADCWindowFunction = 510
"""Window function for use with 496 Analogue-digital Converter (ADC). 0 = Rectangular, 1 = Sine, 2 = Triangular, 3 = Hann. Default is 1."""
ADCXYThetaReading = 506
"""X, Y, and Theta reading for use with Stanford Research lock-in amplifier. Provides phase-sensitive detection outputs."""
AmpChannel = 601
"""Input channel selection for 225, 267, and 277 amplifiers. Valid values 1 or 2. Default is 1."""
AmpCurrentChannel = 607
"""Current channel selection for 225, 267, and 277 amplifiers. Setting this via BI_set clears AmpCurrentSetup to 0."""
AmpCurrentRange = 606
"""Current range setting of the amplifier. Setting this via BI_set clears AmpCurrentSetup to 0."""
AmpCurrentSetup = 610
"""Get or set the current setup being used. Valid values: 1-2 for 267/277, 1-4 for 225. Set to 0 when range or channel is manually changed. Default is 0."""
AmpGain = 600
"""Gain value for the amplifier at a specific range. Indexed by range number. Used by SDK when calculating measurement results."""
AmpMaxRange = 603
"""Maximum range setting for the amplifier. Setting this equal to AmpMinRange prevents auto-ranging. Default is 7 for 225, 6 for others."""
AmpMinRange = 602
"""Minimum range setting for the amplifier. Setting this equal to AmpMaxRange prevents auto-ranging. Default is 1."""
AmpOverload = 608
"""Overload flag indicating if the amplifier is overloaded. 0 = not overloaded. Check this if measurements fail or seem incorrect."""
AmpOverrideWl = 609
"""Set group readings to 1 from this wavelength (nm) onwards."""
AmpSetRange = 611
"""Amplifier set range"""
AmpSmallSignalCalibration = 1210
"""Amplifier small signal calibration"""
AmpStartRange = 604
"""Starting range for 265, 267, and 277 amplifiers. BI_initialise sets the amplifier to this range. Default is 1."""
AmpUseSetup = 605
"""Wavelength (nm) to switch to specified setup for 225, 267, and 277 amplifiers. Indexed by setup number. If multiple setups specify same wavelength, the one with lowest setup number is used. Default is 0."""
AmpUseSmallSignalCalibration = 1211
"""Amplifier use small signal calibration"""
BenACAMP = 10006
"""Bentham AC amp hardware type"""
BenADC = 10004
"""Bentham Analogue-digital Converter (ADC) hardware type"""
BenAnonDevice = 10010
"""Bentham anonymous device hardware type"""
BenCamera = 10020
"""Bentham camera hardware type"""
BenChopper = 10024
"""Bentham chopper hardware type"""
BenDCAMP = 10007
"""Bentham DC amp hardware type"""
BenDiodeArray = 10021
"""Bentham diode array hardware type"""
BenEBox_Monitor = 10023
"""Bentham E-box monitor hardware type"""
BenFilterWheel = 10003
"""Bentham filter wheel hardware type"""
BenInterface = 10000
"""Bentham interface hardware type"""
BenMono = 10009
"""Bentham monochromator hardware type"""
BenORM = 10022
"""Bentham ORM hardware type"""
BenPOSTAMP = 10012
"""Bentham post amp hardware type"""
BenPREAMP = 10005
"""Bentham preamp hardware type"""
BenRelayUnit = 10008
"""Bentham relay unit hardware type"""
BenSAM = 10001
"""Bentham Swing Away Mirror (SAM) hardware type"""
BenSlit = 10002
"""Bentham slit hardware type"""
BenSwitch = 10026
"""Bentham switch hardware type"""
BenUnknown = 10011
"""Bentham unknown hardware type"""
BenVC_TE_30 = 10025
"""Bentham VC TE-30 hardware type"""
biCurrentInput = 1005
"""Current input"""
biCurrentRelay = 351
"""Current relay status for the 262 amplifier. Read-only."""
biDescriptor = 1009
"""Component descriptor"""
biHasAdvancedWindow = 1008
"""Has advanced window flag"""
biHasSetupWindow = 1007
"""Has setup window flag"""
biInput = 1004
"""Input selection"""
biMax = 1002
"""Maximum allowable position for motorised stages. Valid when set to value >= 0. Default is -1 (no limit)."""
biMin = 1001
"""Minimum allowable position for motorised stages. Valid when set to value >= 0. Default is -1 (no limit)."""
biMoveWithWavelength = 1006
"""Move with wavelength flag"""
biParkOffset = 1010
"""Park offset"""
biParkPos = 1003
"""Park position"""
biProductName = 1011
"""Product name"""
biRelay = 350
"""Relay status for the 262 amplifier. 0 = relaxed/off, 1 = energised/on. Default is 0."""
biSettleDelay = 1000
"""Recommended settle delay time (ms) after an operation or wavelength change. BI_select_wavelength returns this value if the monochromator has changed position, providing guidance for how long to wait before taking measurements."""
CameraAutoRange = 804
"""Camera auto-range mode"""
CameraAverages = 806
"""Camera averages"""
CameraBeta = 811
"""Camera beta parameter"""
CameraDataLToR = 810
"""Camera data left to right"""
CameraDataSize = 815
"""Camera data size"""
CameraIntegrationTime = 800
"""Camera integration time"""
CameraMaxITime = 808
"""Camera maximum integration time"""
CameraMaxWl = 814
"""Camera maximum wavelength"""
CameraMinITime = 807
"""Camera minimum integration time"""
CameraMinWl = 813
"""Camera minimum wavelength"""
CameraMVSSWidth = 805
"""Camera Motorised Variable Slits (MVSS) width"""
CameraPhi = 812
"""Camera phi parameter"""
CameraSAMState = 803
"""Camera Swing Away Mirror (SAM) state"""
CameraUnitMaxITime = 809
"""Camera unit maximum integration time"""
CameraWidthInMM = 802
"""Camera width in millimeters"""
CameraWidthInPixels = 801
"""Camera width in pixels"""
CameraZCAverages = 817
"""Camera zero calibration averages"""
CameraZCITime = 816
"""Camera zero calibration integration time"""
ChangerZ = 50
"""Grating changer zero order position."""
ChopperDACFromADC = 943
"""Set the DAC by reading the potentiometer for the 418 chopper. Converts potentiometer ADC reading to appropriate DAC value when switching from LOCAL to REMOTE mode."""
ChopperDACValue = 941
"""Get or set DAC value for the 418 chopper. Can be used to manually control chopper frequency. Use with ChopperFrequency to hunt for specific frequency."""
ChopperFrequency = 940
"""Get or set chopper frequency for the 418 chopper. May take up to two minutes to hunt for precise frequency. Returns actual achieved frequency."""
ChopperState = 942
"""Get or set chopper state (On/Off) for the 418 chopper. Values: 0 = OFF, 1 = ON in LOCAL mode, 2 = ON in REMOTE mode, 3 = OFF in REMOTE mode."""
EboxCountsAtTargetHv = 919
"""Analogue-digital Converter (ADC) reading (counts) at target high voltage. Used for HV calibration. Default is 10178."""
EboxCountsAtTargetTemp = 916
"""Analogue-digital Converter (ADC) reading (counts) at target temperature. Used for temperature calibration. Default is 11990."""
EboxGradientHv = 920
"""Gradient of Analogue-digital Converter (ADC) counts vs high voltage. Used to convert raw counts to voltage. Default is -216.76."""
EboxGradientTemp = 917
"""Gradient of Analogue-digital Converter (ADC) counts vs temperature. Used to convert raw counts to temperature. Default is 1288.19."""
EboxReadHv = 910
"""Read high voltage from E-box monitor. Converted to volts using gradient, target, and counts at target calibration values."""
EboxReadHvRaw = 912
"""Read raw high voltage from E-box monitor without converting. Returns ADC counts."""
EboxReadTemp = 911
"""Read temperature from E-box monitor. Converted to degrees Celsius using gradient, target, and counts at target calibration values."""
EboxReadTempRaw = 913
"""Read raw temperature from E-box monitor without converting. Returns ADC counts."""
EboxRepeats = 915
"""Number of repeats for HV and temperature readings. Multiple readings are averaged for better accuracy. Default is 1."""
EboxTargetHv = 921
"""Target high voltage for E-box in volts. Used for HV calibration. Default is 750V."""
EboxTargetTemp = 918
"""Target temperature for E-box in degrees Celsius. Used for temperature calibration. Default is 23 degrees C."""
EboxUsePl1000 = 922
"""E-box use PL1000"""
EboxWait = 914
"""Delay between high voltage or temperature readings in milliseconds. Allows hardware to settle between repeated readings. Default is 5000 ms."""
ExternalADCAutoRange = 930
"""External Analogue-digital Converter (ADC) auto-range"""
ExternalADCComms = 932
"""External Analogue-digital Converter (ADC) communications"""
ExternalADCCurrentCompliance = 934
"""External Analogue-digital Converter (ADC) current compliance"""
ExternalADCCurrentRange = 931
"""External Analogue-digital Converter (ADC) current range"""
ExternalADCFourWireMode = 933
"""External Analogue-digital Converter (ADC) four-wire mode"""
ExternalADCMode = 936
"""External Analogue-digital Converter (ADC) mode"""
ExternalADCVoltageBias = 935
"""External Analogue-digital Converter (ADC) voltage bias"""
FWheelCurrentPosition = 102
"""Current position of the filter wheel. For non-parking M300/DM150 systems this must be set before calling BI_zero_calibration, BI_select_wavelength or BI_close_shutter. Read-only for MAC and MSD controlled monochromators."""
FWheelFilter = 100
"""Filter value at a specific position in the filter wheel. Indexed by position number. Used to select appropriate filter when BI_select_wavelength is called. Positions with no filters should be 0 (default). Default is 0."""
FWheelPositions = 101
"""Total number of positions available in the filter wheel. The last (highest numbered) position is always used as the shutter."""
GratingA = 22
"""Alpha value for a grating in TM/DTM300 monochromators. Default is 1."""
Gratingd = 20
"""Grating line density d (lines per mm) for TM/DTM300 monochromators. Default is 0."""
GratingWLMax = 24
"""Maximum wavelength (nm) that the grating should be used for. Setting to 0 uses a default value chosen by the ruling density."""
GratingWLMin = 23
"""Minimum wavelength (nm) that the grating should be used for. Setting to 0 uses a default value chosen by the ruling density."""
GratingX = 27
"""Grating constant 1 for HR600 gratings."""
GratingX1 = 26
"""Grating constant 2 for HR600 gratings."""
GratingX2 = 25
"""Grating constant 3 for HR600 gratings."""
GratingZ = 21
"""Zero order (zord) value for a grating in TM/DTM300 monochromators. Default is 0."""
LatchState = 1200
"""Latch state"""
MonochromatorCanModeSwitch = 19
"""Boolean flag indicating whether the monochromator can perform mode switching. Default is 1 (true)."""
MonochromatorCosAlpha = 29
"""Monochromator cosine alpha value"""
MonochromatorCurrentDialReading = 12
"""Current dial reading of monochromator. For non-parking M300 and DM150 monochromators this must be set before any calls to BI_select_wavelength. Valid values are 0 to 999.99."""
MonochromatorCurrentGrating = 14
"""Current grating selection (1-3 for TM300, 11-13 or 21-23 for DTM300 dual turret systems)."""
MonochromatorCurrentWL = 11
"""The wavelength (nm) that the monochromator is currently at. This is a read-only attribute."""
MonochromatorModeSwitchNum = 17
"""Double/single Swing Away Mirror (SAM) index for mode switching. Default is -1."""
MonochromatorModeSwitchState = 18
"""Current Swing Away Mirror (SAM) state for mode switching. Default is 0."""
MonochromatorModeSwitchTurret = 30
"""Mode switch turret setting"""
MonochromatorPark = 15
"""Setting this with any value will cause the monochromator to move to its park position."""
MonochromatorParkDialReading = 13
"""Park position dial reading for M300/DM150 monochromators. Default is 0."""
MonochromatorScanDirection = 10
"""Controls when anti-backlash precautions are taken. 1 = approach wavelengths from shorter wavelength (UV to IR scanning), 0 = approach from longer wavelength (IR to UV scanning). If the SDK needs to approach a wavelength in the wrong direction it will overshoot and approach from the correct side to prevent backlash error. Default is 1."""
MonochromatorSelfPark = 16
"""Legacy token for DM150 - indicates whether dial reading is entered by user when monochromator parks, or if the monochromator parks itself. Default is 1."""
MonochromatorZordSwitchSAM = 28
"""Zero order switch Swing Away Mirror (SAM) setting"""
MotorCurrent = 903
"""Motor current"""
MotorMappedPosition = 906
"""Motor mapped position"""
MotorMoving = 902
"""Motor moving flag"""
MotorPosition = 900
"""Get or set the motor position for motorised stages. Value given in steps. Default is 0."""
MotorRunFullSpeed = 904
"""Motor run at full speed"""
MotorStepMapFile = 905
"""Motor step map file"""
MotorStop = 901
"""Tell motor to stop moving immediately. Use with MotorPosition index 1 for non-polling motor control."""
MVSSConstantBandwidth = 405
"""Current constant bandwidth (nm) mode for the Motorised Variable Slits (MVSS). The SDK automatically adjusts slit width to maintain constant bandwidth when gratings change."""
MVSSConstantwidth = 406
"""Current constant width (mm) mode for the Motorised Variable Slits (MVSS). Range 0 to 10 mm."""
MVSSCurrentWidth = 403
"""Current width of the Motorised Variable Slits (MVSS) slit in millimeters."""
MVSSOffset = 409
"""Offset value for the Motorised Variable Slits (MVSS) positioning."""
MVSSPosition = 408
"""Set slit position in monochromator ('entrance', 'exit', or 'middle') for Motorised Variable Slits (MVSS). Default is 'entrance'."""
MVSSSetWidth = 404
"""Move the slit to the specified width (mm). Range 0 to 10 mm for Motorised Variable Slits (MVSS)."""
MVSSSlitMode = 407
"""Current slit drive mode for the Motorised Variable Slits (MVSS). 0 = constant width mode (mm), 1 = constant bandwidth mode (nm)."""
MVSSSwitchWL = 401
"""State change wavelength (nm) for the Motorised Variable Slits (MVSS). Indexed by setup number."""
MVSSWidth = 402
"""Width at specified state for the Motorised Variable Slits (MVSS). Indexed by setup number. Range 0 to 10 mm."""
SAMCurrentState = 303
"""Current state of the Swing Away Mirror (SAM)."""
SAMDeflectName = 304
"""Name for the deflected Swing Away Mirror (SAM) state. Can be customized to indicate detector name. Default is 'Deflect'."""
SAMInitialState = 300
"""Swing Away Mirror (SAM) state after BI_initialise is called. 0 = relaxed, 1 = energised. Default is 0."""
SAMNoDeflectName = 305
"""Name for the undeflected Swing Away Mirror (SAM) state. Can be customized to indicate detector name. Default is 'No Deflect'."""
SAMState = 302
"""Swing Away Mirror (SAM) state at the specified SAMSwitchWL wavelength. Indexed by setup number (1-10). 0 = relaxed, 1 = energised. Default is 0."""
SAMSwitchWL = 301
"""Wavelength (nm) at which the Swing Away Mirror (SAM) should change state. Indexed by setup number (1-10)."""
SOBInitialState = 200
"""Switch-over Box (SOB) state after BI_initialise is called. 0 = relaxed, 1 = energised. Default is 0."""
SOBState = 202
"""Current state of the Switch-over Box (SOB). 0 = relaxed, 1 = energised."""
SSEnergisedSteps = 320
"""Number of steps to energised position for stepper Swing Away Mirror (SAM) motor."""
SSIdleCurrent = 325
"""Motor current when idle for stepper Swing Away Mirror (SAM)."""
SSMaxSteps = 322
"""Maximum number of steps for stepper Swing Away Mirror (SAM) motor."""
SSMoveCurrent = 324
"""Motor current when moving for stepper Swing Away Mirror (SAM)."""
SSRelaxedSteps = 321
"""Number of steps to relaxed position for stepper Swing Away Mirror (SAM) motor."""
SSSpeed = 323
"""Motor speed for stepper Swing Away Mirror (SAM)."""
Sys225_277Input = 9002
"""Which 225 input the 277 output is connected to. SDK uses this to determine which amplifier combination is being used for measurements. Valid values 1 or 2. Default is 1."""
SysDarkCurrent = 9004
"""System dark current"""
SysDarkIIntegrationTime = 9001
"""Integration time (seconds) for dark current reading in DC systems. Equivalent to number of samples * sample period. Default is 5 seconds."""
SysOffset = 9003
"""System offset"""
SysSimulationFixedValue = 9005
"""System simulation fixed value"""
SysStopCount = 9000
"""Autozero stop-count value for AC systems. During zero calibration, ADC is sampled until difference between consecutive readings is <= this value, ensuring system has settled. Default is 1.0."""
TLSCurrentPosition = 150
"""Current light source position in the Tunable Light Source (TLS). Valid values 1-3. Default is 1."""
TLSPOS = 152
"""Light source position to switch to in the Tunable Light Source (TLS). Indexed by setup number (1-10). Valid values 1-3. Default is 0."""
TLSPositionsCommand = 154
"""Command to switch the Tunable Light Source (TLS) light source position."""
TLSSelectWavelength = 153
"""Select the appropriate wavelength for the Tunable Light Source (TLS) to switch light sources."""
TLSWL = 151
"""Wavelength (nm) at which the Tunable Light Source (TLS) should switch light sources. Indexed by setup number (1-10). Default is 0."""
TurretAmplitude = 57
"""Turret amplitude"""
TurretHighCurrentThreshold = 54
"""Turret high current threshold"""
TurretIdleCurrent = 52
"""Turret motor idle current"""
TurretMoveCurrent = 51
"""Turret motor move current"""
TurretMoveSpeed = 53
"""Turret move speed"""
TurretOffset = 56
"""Turret offset"""
TurretPhase = 58
"""Turret phase"""
TurretRange = 55
"""Turret range"""
TurretSineCorrection = 59
"""Turret sine correction"""
VC_TE_30ControlState = 1101
"""VC TE-30 control state"""
VC_TE_30CoolerOn = 1103
"""VC TE-30 cooler on"""
VC_TE_30Measured = 1106
"""VC TE-30 measured value"""
VC_TE_30OperationalState = 1102
"""VC TE-30 operational state"""
VC_TE_30Output = 1108
"""VC TE-30 output"""
VC_TE_30SetPoint = 1105
"""VC TE-30 set point"""
VC_TE_30SetTemp = 1100
"""VC TE-30 set temperature"""
VC_TE_30StandDev = 1107
"""VC TE-30 standard deviation"""
VC_TE_30WaterOn = 1104
"""VC TE-30 water on"""
