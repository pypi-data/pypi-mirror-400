# BThome Logger Tools

This directory contains tools for testing and debugging BThome devices.

## 🐍 Python BThome Logger

A reliable Python tool for scanning and displaying BThome v2 advertisements.

### Installation

**From PyPI (recommended):**

```bash
# Install as isolated tool with uv (recommended)
uv tool install bthome-logger

# Or with pipx
pipx install bthome-logger

# Or system-wide with pip
pip install bthome-logger
```

**For development:**

```bash
# Install uv if not already available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Change to tools directory
cd tools

# Install dependencies and run tool
uv run bthome_logger.py
```

**From repository:**

```bash
# Clone repository
git clone https://github.com/the78mole/bthomev2.git
cd bthomev2/tools

# With pip
pip install -e .

# With uv
uv run bthome_logger.py
```

### Usage

```bash
# Basic usage (defaults to filtering devices with "MAKE" in name)
bthome-logger

# Filter by custom device name
bthome-logger --filter ESP32
bthome-logger -f MyDevice

# Show all BLE advertisements (verbose mode)
bthome-logger --verbose
bthome-logger -v

# Show version
bthome-logger --version

# Show help
bthome-logger --help
```

### Features

- ✅ Scans for BLE devices with customizable name filter
- ✅ Detects BThome v2 Company ID (0xFCD2)
- ✅ Decodes all common BThome Object IDs
- ✅ Colorized terminal output for better readability
- ✅ Shows RSSI values with color coding
- ✅ Real-time updates on new advertisements
- ✅ Supports encrypted and unencrypted packets
- ✅ Optional verbose mode to show all BLE advertisements
- ✅ CLI with `--help` and `--version` support

### Output Example

```text
======================================================================
🔵 BThome Logger - Python Edition
Scans for BLE devices with BThome v2 protocol
======================================================================

Filter: Devices with 'MAKE' in name
Press Ctrl+C to exit

✓ Scanner started...

----------------------------------------------------------------------
[14:32:45.123] 📱 MAKE-ESP32-S3-TS (XX:XX:XX:XX:XX:XX)
  RSSI: -65 dBm
  Raw: 40 02 b6 10
  BThome: v2 (unencrypted)
  Values:
    • Temperature: 42.78 °C
```

### Troubleshooting

**Problem:** `bleak` cannot be installed

**Solution:** Make sure you are using Python 3.8+:

```bash
python --version
```

**Problem:** No Bluetooth permissions

**Solution (Linux):**

```bash
# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER
```

Log out and back in, or run `newgrp bluetooth` (only affects current terminal).
