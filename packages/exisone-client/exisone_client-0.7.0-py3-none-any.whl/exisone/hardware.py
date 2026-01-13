"""Cross-platform hardware ID generation."""

import hashlib
import os
import platform
import socket
import subprocess
import uuid
from typing import List


# Salt for hardware ID generation (matches .NET client)
_HARDWARE_SALT = "ExisOneHardwareSalt_v1"


def generate_hardware_id() -> str:
    """
    Generate a cross-platform hardware fingerprint.

    Collects various hardware identifiers (CPU, disk, MAC addresses, etc.)
    and produces a stable SHA-256 hash. This matches the algorithm used
    by the .NET ExisOne client for compatibility.

    Returns:
        64-character uppercase hex string (SHA-256 hash)
    """
    components: List[str] = []

    system = platform.system()

    # Platform-specific hardware identifiers
    if system == "Windows":
        components.extend(_get_windows_identifiers())
    else:
        components.extend(_get_unix_identifiers())

    # MAC addresses (all platforms)
    components.extend(_get_mac_addresses())

    # Generic system info (all platforms)
    components.append("x64" if platform.machine().endswith("64") else "x86")
    components.append(str(os.cpu_count() or 1))
    components.append(socket.gethostname())
    components.append(platform.platform())

    # Combine and hash
    combined = "".join(components)
    salted = _HARDWARE_SALT + combined

    hash_bytes = hashlib.sha256(salted.encode("utf-8")).digest()
    return hash_bytes.hex().upper()


def _get_windows_identifiers() -> List[str]:
    """Get Windows-specific hardware identifiers via WMI."""
    identifiers: List[str] = []

    wmi_queries = [
        ("Win32_Processor", "ProcessorId"),
        ("Win32_BaseBoard", "SerialNumber"),
        ("Win32_BIOS", "SerialNumber"),
        ("Win32_DiskDrive", "SerialNumber"),
    ]

    for class_name, prop_name in wmi_queries:
        try:
            result = subprocess.run(
                ["wmic", class_name, "get", prop_name],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    value = lines[1].strip()
                    if value and value.lower() not in ("none", "to be filled by o.e.m."):
                        identifiers.append(value)
        except Exception:
            pass

    return identifiers


def _get_unix_identifiers() -> List[str]:
    """Get Linux/macOS hardware identifiers."""
    identifiers: List[str] = []

    # Machine ID files (Linux)
    machine_id_paths = [
        "/etc/machine-id",
        "/var/lib/dbus/machine-id",
        "/sys/class/dmi/id/product_uuid",
    ]

    for path in machine_id_paths:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    content = f.read().strip()
                    if content:
                        identifiers.append(content)
        except Exception:
            pass

    # CPU info (Linux)
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                identifiers.append(f.read())
        elif platform.system() == "Darwin":
            # macOS: get hardware UUID
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "Hardware UUID" in line:
                        uuid_val = line.split(":")[-1].strip()
                        if uuid_val:
                            identifiers.append(uuid_val)
                        break
    except Exception:
        pass

    return identifiers


def _get_mac_addresses() -> List[str]:
    """Get MAC addresses from network interfaces."""
    macs: List[str] = []

    try:
        # Primary method: uuid.getnode() gives one MAC
        node = uuid.getnode()
        mac = ":".join(f"{(node >> i) & 0xff:02X}" for i in range(0, 48, 8)[::-1])
        if mac and not mac.startswith("00:00:00"):
            macs.append(mac.replace(":", ""))
    except Exception:
        pass

    # Try to get additional MACs via system commands
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(
                ["getmac", "/fo", "csv", "/nh"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    parts = line.split(",")
                    if parts:
                        mac = parts[0].strip('"').replace("-", "").upper()
                        if mac and len(mac) == 12 and mac not in macs:
                            macs.append(mac)
        elif system == "Linux":
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "link/ether" in line:
                        parts = line.split()
                        idx = parts.index("link/ether") + 1
                        if idx < len(parts):
                            mac = parts[idx].replace(":", "").upper()
                            if mac and len(mac) == 12 and mac not in macs:
                                macs.append(mac)
        elif system == "Darwin":
            result = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "ether " in line:
                        parts = line.split()
                        idx = parts.index("ether") + 1
                        if idx < len(parts):
                            mac = parts[idx].replace(":", "").upper()
                            if mac and len(mac) == 12 and mac not in macs:
                                macs.append(mac)
    except Exception:
        pass

    # Sort for consistency
    macs.sort()
    return macs
