"""Environment metadata collection for benchmark reproducibility."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from cfabric_benchmarks.models.environment import TestEnvironment


def collect_environment() -> TestEnvironment:
    """Collect test environment information from the current system.

    Returns:
        TestEnvironment with hardware and software information
    """
    return TestEnvironment.from_system()


def save_environment(env: TestEnvironment, output_path: Path) -> None:
    """Save environment metadata to a JSON file.

    Args:
        env: TestEnvironment to save
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(env.to_json())


def load_environment(input_path: Path) -> TestEnvironment:
    """Load environment metadata from a JSON file.

    Args:
        input_path: Path to input JSON file

    Returns:
        TestEnvironment loaded from file
    """
    data = json.loads(input_path.read_text())
    return TestEnvironment.model_validate(data)


def create_run_directory(base_dir: Path, prefix: str = "") -> Path:
    """Create a timestamped directory for benchmark results.

    Args:
        base_dir: Base directory for results
        prefix: Optional prefix for the directory name

    Returns:
        Path to created directory
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    dir_name = f"{prefix}_{timestamp}" if prefix else timestamp
    run_dir = base_dir / dir_name
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def format_environment_summary(env: TestEnvironment) -> str:
    """Format environment as a human-readable summary.

    Args:
        env: TestEnvironment to format

    Returns:
        Formatted string summary
    """
    lines = [
        "Test Environment",
        "=" * 50,
        f"Timestamp: {env.timestamp}",
        f"OS: {env.os_name} {env.os_version} ({env.architecture})",
        "",
        "Hardware:",
        f"  CPU: {env.hardware.cpu_model}",
        f"  Cores: {env.hardware.cpu_cores} ({env.hardware.cpu_threads} threads)",
        f"  RAM: {env.hardware.ram_total_gb:.1f} GB",
        f"  Storage: {env.hardware.storage_type}",
        "",
        "Software:",
        f"  Python: {env.software.python_version}",
        f"  NumPy: {env.software.numpy_version}",
        f"  psutil: {env.software.psutil_version}",
        f"  Text-Fabric: {env.software.text_fabric_version}",
        f"  Context-Fabric: {env.software.context_fabric_version}",
        "=" * 50,
    ]
    return "\n".join(lines)
