#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   model_info.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK model information module.
"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelInfo:
    """Model information without loading the full model.

    Provides metadata about a model to help users decide whether to load it,
    check compatibility, and understand resource requirements.

    Attributes:
        model_name: Name or identifier of the model
        model_path: Path or HuggingFace identifier
        architecture: Model architecture (e.g., "Qwen2.5-VL", "NVILA")
        size_gb: Estimated model size in gigabytes
        task_type: Training task type (e.g., "VQA", "phrase_grounding")
        supported_tasks: List of tasks this model supports
        run_id: Datature run ID if available
        adapter_available: Whether PEFT adapter is available
        metadata: Additional metadata from run configuration

    Example:
        ```python
        from vi.inference import ViModel

        # Inspect model before loading
        info = ViModel.inspect(
            secret_key="your-key",
            organization_id="your-org",
            run_id="your-run",
        )

        print(f"Model: {info.model_name}")
        print(f"Architecture: {info.architecture}")
        print(f"Size: {info.size_gb:.2f} GB")
        print(f"Task: {info.task_type}")
        print(f"Supports: {', '.join(info.supported_tasks)}")

        # Decide whether to load based on size
        if info.size_gb < 10:
            model = ViModel.from_info(info)
            result = model(source="image.jpg", user_prompt="Describe")
        else:
            print("Model too large for this device")
        ```

    """

    model_name: str
    model_path: str
    architecture: str
    size_gb: float
    task_type: str | None = None
    supported_tasks: list[str] | None = None
    run_id: str | None = None
    adapter_available: bool = False
    metadata: dict | None = None

    def __str__(self) -> str:
        """Format model info as human-readable string."""
        lines = [
            f"Model: {self.model_name}",
            f"Architecture: {self.architecture}",
            f"Size: {self.size_gb:.2f} GB",
        ]

        if self.task_type:
            lines.append(f"Task Type: {self.task_type}")

        if self.supported_tasks:
            lines.append(f"Supported Tasks: {', '.join(self.supported_tasks)}")

        if self.run_id:
            lines.append(f"Run ID: {self.run_id}")

        if self.adapter_available:
            lines.append("Adapter: Available")

        lines.append(f"Path: {self.model_path}")

        return "\n".join(lines)


def get_directory_size_gb(path: Path) -> float:
    """Calculate directory size in gigabytes.

    Args:
        path: Directory path

    Returns:
        Size in gigabytes

    """
    total_size = 0
    try:
        for filepath in path.rglob("*"):
            if filepath.is_file():
                total_size += filepath.stat().st_size
    except (OSError, PermissionError):
        pass

    return total_size / (1024**3)  # Convert bytes to GB


def inspect_model_from_path(model_path: str | Path) -> ModelInfo:
    """Inspect a local model without loading it.

    Args:
        model_path: Path to model directory

    Returns:
        ModelInfo object with model metadata

    Raises:
        FileNotFoundError: If model path doesn't exist
        ValueError: If model configuration is invalid

    """
    model_path = Path(model_path).expanduser().resolve()

    if not model_path.exists():
        raise FileNotFoundError(f"Model path not found: {model_path}")

    # Read model configuration
    config_path = model_path / "config.json"
    run_config_path = model_path / "run.json"

    model_name = "Unknown"
    architecture = "Unknown"
    task_type = None
    supported_tasks = None
    metadata = None

    # Try to read HuggingFace config
    if config_path.exists():
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Extract architecture info
            if "architectures" in config and config["architectures"]:
                architecture = config["architectures"][0]
            elif "model_type" in config:
                architecture = config["model_type"]

            # Extract model name
            if "_name_or_path" in config:
                model_name = config["_name_or_path"]
            else:
                model_name = model_path.name

        except (json.JSONDecodeError, KeyError):
            pass

    # Try to read Datature run config
    if run_config_path.exists():
        try:
            with open(run_config_path, encoding="utf-8") as f:
                run_config = json.load(f)

            if "flow" in run_config and "spec" in run_config["flow"]:
                spec = run_config["flow"]["spec"]

                # Extract task type
                if "task_type" in spec:
                    task_type = spec["task_type"]

                # Extract model info
                if "model" in spec:
                    model_info = spec["model"]
                    if "name" in model_info:
                        architecture = model_info["name"]

            metadata = run_config

        except (json.JSONDecodeError, KeyError):
            pass

    # Determine supported tasks based on architecture and task type
    if task_type:
        supported_tasks = [task_type]
    elif "qwen" in architecture.lower() or "vl" in architecture.lower():
        supported_tasks = ["VQA", "phrase_grounding"]
    elif "nvila" in architecture.lower():
        supported_tasks = ["VQA", "phrase_grounding"]

    # Calculate model size
    size_gb = get_directory_size_gb(model_path)

    # Check for adapter
    adapter_path = model_path / "adapter"
    adapter_available = adapter_path.exists()

    return ModelInfo(
        model_name=model_name,
        model_path=str(model_path),
        architecture=architecture,
        size_gb=size_gb,
        task_type=task_type,
        supported_tasks=supported_tasks,
        adapter_available=adapter_available,
        metadata=metadata,
    )
