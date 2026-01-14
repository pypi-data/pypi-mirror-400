# BenHW SDK - Python Interface

Python interface for Bentham Instruments Hardware Control DLL.

## Installation

```bash
pip install benhw
```


## Usage

### Example

```python
from benhw import BenHW, exceptions, tokens

hw = BenHW()

try:
  hw.build_system_model("system.cfg")
  hw.load_setup("setup.atr")
  hw.initialise()
  hw.park()
  hw.select_wavelength(wl=555)
  hw.set("motor1", tokens.MotorPosition, 0, 4455)
  signal = hw.automeasure()
  print(f"signal: {signal}")
except exceptions.BenHWException as e:
  print(f"BenHW error: {e}")

```

### Accessing Tokens and Errors

```python
from benhw import tokens, errors

# Access tokens via namespace
print(tokens.ADCVolts)           # 504
print(tokens.MonochromatorCurrentWL)  # 11

# Access error codes via namespace
print(errors.BI_OK)      # 0
print(errors.BI_error)   # -1
```

## Requirements

- Python 3.12+
- Windows operating system