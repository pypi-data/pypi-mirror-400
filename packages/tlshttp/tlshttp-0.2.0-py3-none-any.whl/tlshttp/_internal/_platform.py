"""Platform detection utilities."""

from __future__ import annotations

import platform
import struct
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OS(Enum):
    """Operating system."""

    LINUX = "linux"
    MACOS = "darwin"
    WINDOWS = "windows"


class Arch(Enum):
    """CPU architecture."""

    AMD64 = "amd64"
    ARM64 = "arm64"
    ARMV7 = "armv7"
    X86 = "x86"


@dataclass(frozen=True)
class PlatformInfo:
    """Platform information."""

    os: OS
    arch: Arch
    is_alpine: bool = False

    @property
    def library_extension(self) -> str:
        """Get the shared library extension for this platform."""
        if self.os == OS.WINDOWS:
            return ".dll"
        elif self.os == OS.MACOS:
            return ".dylib"
        else:
            return ".so"

    @property
    def binary_name(self) -> str:
        """Get the tls-client binary name for this platform."""
        version = "1.12.0"

        if self.os == OS.WINDOWS:
            bits = "64" if self.arch == Arch.AMD64 else "32"
            return f"tls-client-windows-{bits}-{version}.dll"

        elif self.os == OS.MACOS:
            arch = "arm64" if self.arch == Arch.ARM64 else "amd64"
            return f"tls-client-darwin-{arch}-{version}.dylib"

        else:  # Linux
            if self.is_alpine:
                return f"tls-client-linux-alpine-amd64-{version}.so"

            if self.arch == Arch.ARM64:
                return f"tls-client-linux-arm64-{version}.so"
            elif self.arch == Arch.ARMV7:
                return f"tls-client-linux-armv7-{version}.so"
            else:
                return f"tls-client-linux-ubuntu-amd64-{version}.so"


def _detect_os() -> OS:
    """Detect the current operating system."""
    system = platform.system().lower()

    if system == "linux":
        return OS.LINUX
    elif system == "darwin":
        return OS.MACOS
    elif system == "windows":
        return OS.WINDOWS
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


def _detect_arch() -> Arch:
    """Detect the current CPU architecture."""
    machine = platform.machine().lower()

    # Check for ARM64
    if machine in ("arm64", "aarch64"):
        return Arch.ARM64

    # Check for ARMv7
    if machine.startswith("arm") or machine == "armv7l":
        return Arch.ARMV7

    # Check for x86/AMD64
    if machine in ("x86_64", "amd64"):
        return Arch.AMD64

    if machine in ("i386", "i686", "x86"):
        return Arch.X86

    # Fallback: use pointer size
    if struct.calcsize("P") * 8 == 64:
        return Arch.AMD64
    return Arch.X86


def _is_alpine() -> bool:
    """Check if running on Alpine Linux."""
    try:
        os_release = Path("/etc/os-release")
        if os_release.exists():
            content = os_release.read_text().lower()
            return "alpine" in content
    except (OSError, PermissionError):
        pass

    # Alternative: check for musl libc
    try:
        import subprocess
        result = subprocess.run(
            ["ldd", "--version"],
            capture_output=True,
            text=True,
        )
        return "musl" in result.stderr.lower() or "musl" in result.stdout.lower()
    except (FileNotFoundError, subprocess.SubprocessError):
        pass

    return False


def get_platform() -> PlatformInfo:
    """Get information about the current platform."""
    os = _detect_os()
    arch = _detect_arch()
    is_alpine = os == OS.LINUX and _is_alpine()

    return PlatformInfo(os=os, arch=arch, is_alpine=is_alpine)


# Cached platform info
_platform_info: PlatformInfo | None = None


def get_cached_platform() -> PlatformInfo:
    """Get cached platform information."""
    global _platform_info
    if _platform_info is None:
        _platform_info = get_platform()
    return _platform_info
