"""Test environment documentation models."""

from __future__ import annotations

import platform
import subprocess
from datetime import datetime

from pydantic import BaseModel, Field


class HardwareInfo(BaseModel):
    """Hardware specification."""

    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    ram_total_gb: float
    storage_type: str  # "SSD" | "HDD" | "Unknown"

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()


class SoftwareInfo(BaseModel):
    """Software versions."""

    python_version: str
    numpy_version: str
    psutil_version: str
    text_fabric_version: str
    context_fabric_version: str

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump()

    @classmethod
    def from_environment(cls) -> SoftwareInfo:
        """Create SoftwareInfo from the current environment."""
        import numpy as np
        import psutil

        return cls(
            python_version=platform.python_version(),
            numpy_version=np.__version__,
            psutil_version=psutil.__version__,
            text_fabric_version=_get_tf_version(),
            context_fabric_version=_get_cf_version(),
        )


class TestEnvironment(BaseModel):
    """Complete test environment documentation."""

    timestamp: datetime = Field(default_factory=datetime.now)
    os_name: str = Field(default_factory=lambda: platform.system())
    os_version: str = Field(default_factory=platform.release)
    architecture: str = Field(default_factory=lambda: platform.machine())
    hardware: HardwareInfo
    software: SoftwareInfo

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json(indent=2)

    @classmethod
    def from_system(cls) -> TestEnvironment:
        """Create TestEnvironment from the current system."""
        return cls(
            hardware=_collect_hardware_info(),
            software=SoftwareInfo.from_environment(),
        )


def _get_tf_version() -> str:
    """Get Text-Fabric version."""
    try:
        from tf.fabric import Fabric

        return getattr(Fabric, "__version__", "unknown")
    except ImportError:
        try:
            import tf

            return getattr(tf, "__version__", "unknown")
        except (ImportError, AttributeError):
            return "unknown"


def _get_cf_version() -> str:
    """Get Context-Fabric version."""
    try:
        import cfabric

        return getattr(cfabric, "__version__", "unknown")
    except ImportError:
        return "unknown"


def _collect_hardware_info() -> HardwareInfo:
    """Collect hardware information from the current system."""
    import os

    import psutil

    # CPU info
    cpu_count = os.cpu_count() or 1
    cpu_model = _get_cpu_model()

    # RAM info
    ram_bytes = psutil.virtual_memory().total
    ram_gb = ram_bytes / (1024**3)

    # Storage type detection (best effort)
    storage_type = _detect_storage_type()

    return HardwareInfo(
        cpu_model=cpu_model,
        cpu_cores=psutil.cpu_count(logical=False) or cpu_count,
        cpu_threads=cpu_count,
        ram_total_gb=round(ram_gb, 1),
        storage_type=storage_type,
    )


def _get_cpu_model() -> str:
    """Get CPU model name."""
    system = platform.system()

    if system == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        # Try Apple Silicon
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.chip"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    elif system == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":")[1].strip()
        except (OSError, IndexError):
            pass

    return platform.processor() or "Unknown"


def _detect_storage_type() -> str:
    """Detect storage type (SSD/HDD)."""
    system = platform.system()

    if system == "Darwin":
        # macOS - check for NVMe or SSD in disk info
        try:
            result = subprocess.run(
                ["system_profiler", "SPNVMeDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "NVMe" in result.stdout:
                return "SSD"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return "SSD"  # Most Macs use SSDs

    elif system == "Linux":
        try:
            # Check for rotational flag
            result = subprocess.run(
                ["lsblk", "-d", "-o", "name,rota"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        if parts[1] == "0":
                            return "SSD"
                        elif parts[1] == "1":
                            return "HDD"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    return "Unknown"
