#!/usr/bin/env python3
"""
BThome Logger - Python Edition
Scans for BLE devices and displays BThome v2 advertisements
"""

import asyncio
import struct
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

import typer
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

# Global variable for device name filter
DEVICE_NAME_FILTER = "MAKE"

# Global variable for verbose mode
VERBOSE = False


def get_version() -> str:
    """Get the package version"""
    try:
        return version("bthome-logger")
    except PackageNotFoundError:
        return "dev"


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


# BThome v2 Object IDs with factors and units
BTHOME_OBJECTS = {
    0x00: {"name": "Packet ID", "factor": 1, "unit": "", "size": 1},
    0x01: {"name": "Battery", "factor": 1, "unit": "%", "size": 1},
    0x02: {
        "name": "Temperature",
        "factor": 0.01,
        "unit": "°C",
        "signed": True,
        "size": 2,
    },
    0x03: {"name": "Humidity", "factor": 0.01, "unit": "%", "size": 2},
    0x04: {"name": "Pressure", "factor": 0.01, "unit": "hPa", "size": 3},
    0x05: {"name": "Illuminance", "factor": 0.01, "unit": "lux", "size": 3},
    0x06: {"name": "Mass", "factor": 0.01, "unit": "kg", "signed": True, "size": 2},
    0x07: {
        "name": "Mass (lbs)",
        "factor": 0.01,
        "unit": "lbs",
        "signed": True,
        "size": 2,
    },
    0x08: {
        "name": "Dew Point",
        "factor": 0.01,
        "unit": "°C",
        "signed": True,
        "size": 2,
    },
    0x09: {"name": "Count", "factor": 1, "unit": "", "size": 1},
    0x0A: {"name": "Energy", "factor": 0.001, "unit": "kWh", "size": 3},
    0x0B: {"name": "Power", "factor": 0.01, "unit": "W", "size": 3},
    0x0C: {"name": "Voltage", "factor": 0.001, "unit": "V", "size": 2},
    0x0D: {"name": "PM2.5", "factor": 1, "unit": "µg/m³", "size": 2},
    0x0E: {"name": "PM10", "factor": 1, "unit": "µg/m³", "size": 2},
    0x0F: {"name": "Boolean", "factor": 1, "unit": "", "size": 1},
    0x10: {"name": "Power (On)", "factor": 1, "unit": "", "size": 1},
    0x11: {"name": "Opening", "factor": 1, "unit": "", "size": 1},
    0x12: {"name": "CO2", "factor": 1, "unit": "ppm", "size": 2},
    0x13: {"name": "TVOC", "factor": 1, "unit": "µg/m³", "size": 2},
    0x14: {"name": "Moisture", "factor": 0.01, "unit": "%", "size": 2},
    0x15: {"name": "Battery Low", "factor": 1, "unit": "", "size": 1},
    0x16: {"name": "Battery Charging", "factor": 1, "unit": "", "size": 1},
    0x17: {"name": "CO", "factor": 1, "unit": "", "size": 1},
    0x18: {"name": "Cold", "factor": 1, "unit": "", "size": 1},
    0x19: {"name": "Connectivity", "factor": 1, "unit": "", "size": 1},
    0x1A: {"name": "Door", "factor": 1, "unit": "", "size": 1},
    0x1B: {"name": "Garage Door", "factor": 1, "unit": "", "size": 1},
    0x1C: {"name": "Gas", "factor": 1, "unit": "", "size": 1},
    0x1D: {"name": "Heat", "factor": 1, "unit": "", "size": 1},
    0x1E: {"name": "Light", "factor": 1, "unit": "", "size": 1},
    0x1F: {"name": "Lock", "factor": 1, "unit": "", "size": 1},
    0x20: {"name": "Moisture (Binary)", "factor": 1, "unit": "", "size": 1},
    0x21: {"name": "Motion", "factor": 1, "unit": "", "size": 1},
    0x22: {"name": "Moving", "factor": 1, "unit": "", "size": 1},
    0x23: {"name": "Occupancy", "factor": 1, "unit": "", "size": 1},
    0x24: {"name": "Plug", "factor": 1, "unit": "", "size": 1},
    0x25: {"name": "Presence", "factor": 1, "unit": "", "size": 1},
    0x26: {"name": "Problem", "factor": 1, "unit": "", "size": 1},
    0x27: {"name": "Running", "factor": 1, "unit": "", "size": 1},
    0x28: {"name": "Safety", "factor": 1, "unit": "", "size": 1},
    0x29: {"name": "Smoke", "factor": 1, "unit": "", "size": 1},
    0x2A: {"name": "Sound", "factor": 1, "unit": "", "size": 1},
    0x2B: {"name": "Tamper", "factor": 1, "unit": "", "size": 1},
    0x2C: {"name": "Vibration", "factor": 1, "unit": "", "size": 1},
    0x2D: {"name": "Window", "factor": 1, "unit": "", "size": 1},
    0x3A: {"name": "Button", "factor": 1, "unit": "", "size": 1},
    0x3C: {"name": "Dimmer", "factor": 1, "unit": "", "size": 2},
}

# BThome Service UUID (16-bit UUID: 0xFCD2)
BTHOME_SERVICE_UUID = "0000fcd2-0000-1000-8000-00805f9b34fb"


def parse_bthome_packet(data: bytes) -> dict:
    """
    Parses a BThome v2 packet and returns decoded values

    Args:
        data: Raw manufacturer data without company ID

    Returns:
        Dictionary with device info and decoded values
    """
    if len(data) < 1:
        return None

    result = {
        "device_info": data[0],
        "encrypted": bool(data[0] & 0x01),
        "version": "v2",
        "values": [],
    }

    index = 1

    # Decode objects
    while index < len(data):
        object_id = data[index]
        index += 1

        if object_id not in BTHOME_OBJECTS:
            # Unbekanntes Object ID - abbrechen
            result["values"].append(
                {
                    "name": f"Unbekannt (0x{object_id:02X})",
                    "object_id": object_id,
                    "raw_bytes": bytes(),
                    "raw_value": None,
                    "value": None,
                    "unit": "",
                }
            )
            break

        obj_def = BTHOME_OBJECTS[object_id]
        size = obj_def["size"]

        if index + size > len(data):
            # Nicht genug Daten
            break

        # Wert auslesen
        raw_bytes = data[index : index + size]
        index += size

        # Wert dekodieren (Little Endian)
        if size == 1:
            raw_value = raw_bytes[0]
        elif size == 2:
            raw_value = struct.unpack("<H", raw_bytes)[0]
            # Signed?
            if obj_def.get("signed", False) and raw_value >= 0x8000:
                raw_value = raw_value - 0x10000
        elif size == 3:
            # 3 Bytes zu int (Little Endian)
            raw_value = raw_bytes[0] | (raw_bytes[1] << 8) | (raw_bytes[2] << 16)
            if obj_def.get("signed", False) and raw_value >= 0x800000:
                raw_value = raw_value - 0x1000000
        else:
            raw_value = 0

        # Faktor anwenden
        value = raw_value * obj_def["factor"]

        result["values"].append(
            {
                "name": obj_def["name"],
                "object_id": object_id,
                "raw_bytes": raw_bytes,
                "raw_value": raw_value,
                "value": value,
                "unit": obj_def["unit"],
            }
        )

    return result


def format_timestamp() -> str:
    """Formats the current timestamp"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def print_header():
    """Prints the program header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🔵 BThome Logger - Python Edition{Colors.RESET}")
    print(f"{Colors.CYAN}Scans for BLE devices with BThome v2 protocol{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    print(
        f"{Colors.YELLOW}Filter: Devices with '{DEVICE_NAME_FILTER}' in name{Colors.RESET}"
    )
    print(f"{Colors.GRAY}Press Ctrl+C to exit{Colors.RESET}\n")


def print_separator():
    """Prints a separator line"""
    print(f"{Colors.GRAY}{'-'*70}{Colors.RESET}")


def advertisement_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    """Called when a BLE advertisement is received"""

    # Apply device name filter
    if device.name and DEVICE_NAME_FILTER not in device.name:
        return

    # Only show devices with service data
    if not advertisement_data.service_data:
        return

    # Check if it's BThome data (Service UUID 0xFCD2)
    if BTHOME_SERVICE_UUID not in advertisement_data.service_data:
        # Show other service data only in verbose mode
        if VERBOSE:
            for service_uuid, data in advertisement_data.service_data.items():
                hex_data = " ".join(f"{b:02x}" for b in data)
                print(
                    f"{Colors.GRAY}[{format_timestamp()}]{Colors.RESET} "
                    f"{Colors.BLUE}{device.name}{Colors.RESET} "
                    f"({Colors.GRAY}{device.address}{Colors.RESET}) "
                    f"| Service UUID: {service_uuid} | Data: {hex_data} | "
                    f"RSSI: {advertisement_data.rssi} dBm"
                )
        return

    # BThome data found!
    raw_data = advertisement_data.service_data[BTHOME_SERVICE_UUID]
    hex_data = " ".join(f"{b:02x}" for b in raw_data)

    # Header with device name and timestamp
    print_separator()
    print(
        f"{Colors.GRAY}[{format_timestamp()}]{Colors.RESET} "
        f"{Colors.BOLD}{Colors.GREEN}📱 {device.name}{Colors.RESET} "
        f"({Colors.GRAY}{device.address}{Colors.RESET})"
    )

    # RSSI
    if advertisement_data.rssi > -70:
        rssi_color = Colors.GREEN
    elif advertisement_data.rssi > -85:
        rssi_color = Colors.YELLOW
    else:
        rssi_color = Colors.RED

    rssi_text = f"{rssi_color}{advertisement_data.rssi} dBm{Colors.RESET}"
    print(f"  {Colors.GRAY}RSSI:{Colors.RESET} {rssi_text}")

    # Raw Data
    print(f"  {Colors.GRAY}Raw:{Colors.RESET} {Colors.CYAN}{hex_data}{Colors.RESET}")

    # Parse BThome packet
    parsed = parse_bthome_packet(raw_data)

    if parsed:
        # Device Info
        encrypted_str = (
            f"{Colors.RED}encrypted{Colors.RESET}"
            if parsed["encrypted"]
            else f"{Colors.GREEN}unencrypted{Colors.RESET}"
        )
        print(
            f"  {Colors.GRAY}BThome:{Colors.RESET} {parsed['version']} ({encrypted_str})"
        )

        # Decoded values
        if parsed["values"]:
            print(f"  {Colors.GRAY}Values:{Colors.RESET}")
            for val in parsed["values"]:
                # Format raw bytes as hex
                raw_hex = " ".join(f"{b:02x}" for b in val["raw_bytes"])

                if val["unit"]:
                    value_str = f"{val['value']:.2f} {val['unit']}"
                else:
                    value_str = f"{val['value']}"

                print(
                    f"    {Colors.BOLD}{Colors.MAGENTA}• {val['name']}{Colors.RESET} "
                    f"{Colors.GRAY}(0x{val['object_id']:02x}){Colors.RESET}: "
                    f"{Colors.YELLOW}{value_str}{Colors.RESET} "
                    f"{Colors.GRAY}[{raw_hex}]{Colors.RESET}"
                )
        else:
            print(f"    {Colors.GRAY}(No decoded values){Colors.RESET}")
    else:
        print(f"  {Colors.RED}Error parsing BThome packet{Colors.RESET}")

    print()  # Leerzeile


async def scan_forever():
    """Scans continuously for BLE devices"""
    print(f"{Colors.GREEN}✓ Scanner started...{Colors.RESET}\n")

    scanner = BleakScanner(detection_callback=advertisement_callback)

    try:
        await scanner.start()

        # Scan forever (or until Ctrl+C)
        while True:
            await asyncio.sleep(1.0)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Stopping scanner...{Colors.RESET}")
    finally:
        await scanner.stop()
        print(f"{Colors.GREEN}✓ Scanner stopped{Colors.RESET}\n")


app = typer.Typer(
    help="BThome v2 BLE Advertisement Logger - Scans and displays BThome devices"
)


@app.command()
def main(
    device_filter: str = typer.Option(
        "MAKE",
        "--filter",
        "-f",
        help="Filter BLE devices by this name (substring matching)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show all BLE advertisements, not just BThome devices",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        is_flag=True,
        help="Show version and exit",
    ),
):
    """
    Continuously scans for BLE devices and displays BThome v2 advertisements.

    The scanner filters devices by the specified name (substring matching).
    Press Ctrl+C to exit.
    """
    if version:
        print(f"bthome-logger {get_version()}")
        return

    global DEVICE_NAME_FILTER, VERBOSE
    DEVICE_NAME_FILTER = device_filter
    VERBOSE = verbose

    # Print header after filter is set
    print_header()

    try:
        asyncio.run(scan_forever())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app()
