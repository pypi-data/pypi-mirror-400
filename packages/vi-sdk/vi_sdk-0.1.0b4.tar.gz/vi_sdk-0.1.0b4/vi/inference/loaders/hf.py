#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   hf.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK HuggingFace loader module.
"""

from pathlib import Path
from typing import Any

import msgspec
import torch
import xgrammar as xgr
from rich import print as rprint
from rich.progress import BarColumn, SpinnerColumn, TimeElapsedColumn
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.utils.module_import import check_imports
from vi.utils.progress import ViProgress

try:
    check_imports(
        packages=[
            "transformers",
        ],
        dependency_group="inference",
        auto_install=False,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

from transformers import AutoConfig, BitsAndBytesConfig, GenerationConfig
from vi.inference.config.base_config import ViGenerationConfig

# Constants
DEFAULT_CONFIG_FILE_NAME = "config.json"
DEFAULT_ATTN_IMPLEMENTATION = "eager"
DEFAULT_DEVICE_MAP = "auto"
MAX_THREADS = 8

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1  # type: ignore[attr-defined]


class HFLoader(BaseLoader):
    """Base loader for HuggingFace vision-language models.

    Provides common functionality for loading HuggingFace models with support for:
    - Multiple model architectures via configurable model class
    - PEFT adapters (LoRA, QLoRA)
    - Quantization (4-bit, 8-bit)
    - xgrammar compiler for structured outputs
    - Custom processors/tokenizers

    Subclasses only need to specify:
    - `_model_class`: The AutoModel class to use for loading
    - `_processor_class`: The processor/tokenizer class to use
    - `_generation_config_class`: The generation config class

    Attributes:
        model: The loaded model instance.
        processor: The processor for input preprocessing (optional).
        compiler: The compiler for structured outputs (optional).
        generation_config: Generation config.
        metadata: Dictionary containing model metadata.

    """

    _generation_config_class: type[ViGenerationConfig] = ViGenerationConfig
    _model_class: type
    _processor_class: type
    _quantization_config: BitsAndBytesConfig | None = None

    def __init__(
        self,
        model_meta: ModelDownloadResult,
        attn_implementation: str = DEFAULT_ATTN_IMPLEMENTATION,
        device_map: dict | str = DEFAULT_DEVICE_MAP,
        low_cpu_mem_usage: bool = False,
        trust_remote_code: bool = False,
        max_threads: int = MAX_THREADS,
    ):
        """Initialize HuggingFace model loader.

        Args:
            model_meta: Downloaded model metadata containing paths to model files,
                optional adapter, and run configuration.
            attn_implementation: Attention implementation to use. Options:
                - "eager": Standard PyTorch attention (default, most compatible)
                - "flash_attention_2": Flash Attention 2 (faster, requires flash-attn)
                - "sdpa": Scaled Dot Product Attention (PyTorch 2.0+)
            device_map: Device mapping for model placement. Options:
                - "auto": Automatic placement across available devices
                - "cpu": Force CPU placement
                - "cuda": Force GPU placement
                - dict: Custom layer-to-device mapping
            low_cpu_mem_usage: Whether to use low CPU memory during loading.
                Useful for large models on memory-constrained systems.
            trust_remote_code: Whether to trust remote code in model repositories.
                Required for some custom models. Set to False for security.
            max_threads: Maximum number of threads for xgrammar compiler operations.
                Only used if xgrammar is available and model has run configuration.

        Raises:
            ImportError: If required dependencies are not installed.
            FileNotFoundError: If model files don't exist at specified paths.
            ValueError: If model format is not supported or configuration is invalid.
            RuntimeError: If model loading fails due to hardware constraints.

        """
        super().__init__()
        try:
            with ViProgress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.2f}%",
                TimeElapsedColumn(),
                redirect_console_output=True,
            ) as progress:
                main_task = progress.add_task("Loading model...", total=100)

                # Load metadata
                progress.update(
                    main_task, advance=20, description="Loading model metadata..."
                )

                if model_meta.run_config_path:
                    self._load_generation_config_from_run_json(model_meta)
                    self._load_metadata_from_run_json(model_meta)
                else:
                    try:
                        self._load_huggingface_generation_config(model_meta)
                        self._load_huggingface_model_config(model_meta)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to load model configuration from "
                            f"'{model_meta.model_path}': {e}"
                        ) from e

                # Setup quantization if enabled
                if self._metadata.get("quantization_enabled"):
                    quant_type = self._metadata.get("quantization_type", "nf4")
                    compute_dtype = self._metadata.get(
                        "compute_precision_type", torch.bfloat16
                    )

                    self._quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_quant_type=quant_type,
                        bnb_4bit_compute_dtype=compute_dtype,
                        bnb_4bit_use_double_quant=True,
                    )

                # Load model
                progress.update(main_task, description="Loading pretrained weights...")
                model_dtype = self._metadata.get(
                    "compute_precision_type", torch.bfloat16
                )
                self._load_model(
                    model_meta,
                    attn_implementation,
                    device_map,
                    model_dtype,
                    low_cpu_mem_usage,
                    trust_remote_code,
                )

                # Load adapter if present
                progress.update(main_task, advance=20, description="Loading adapter...")
                if model_meta.adapter_path:
                    self._model.load_adapter(model_meta.adapter_path)

                self._model.eval()

                # Load processor
                progress.update(
                    main_task, advance=20, description="Loading processor..."
                )
                self._load_processor(model_meta, trust_remote_code)

                # Load compiler if xgrammar available
                progress.update(
                    main_task, advance=20, description="Loading compiler..."
                )
                self._load_xgrammar_compiler(max_threads)

                progress.update(
                    main_task, completed=100, description="Model loaded successfully"
                )

        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Model loading cancelled by user[/yellow]")
            raise

    def _load_model(
        self,
        model_meta: ModelDownloadResult,
        attn_implementation: str,
        device_map: dict | str,
        model_dtype: Any,
        low_cpu_mem_usage: bool,
        trust_remote_code: bool,
    ) -> None:
        """Load the model using the configured model class.

        Subclasses can override _model_class to use different AutoModel variants.
        """
        self._model = self._model_class.from_pretrained(
            model_meta.model_path,
            attn_implementation=attn_implementation,
            device_map=device_map,
            dtype=model_dtype,
            low_cpu_mem_usage=low_cpu_mem_usage,
            trust_remote_code=trust_remote_code,
            config=(
                str(Path(model_meta.model_path) / DEFAULT_CONFIG_FILE_NAME)
                if model_meta.run_config_path
                else None
            ),
            quantization_config=self._quantization_config,
        )

    def _load_processor(
        self, model_meta: ModelDownloadResult, trust_remote_code: bool
    ) -> None:
        """Load the processor using the configured processor class.

        Subclasses can override _processor_class to use AutoTokenizer vs AutoProcessor.
        """
        self._processor = self._processor_class.from_pretrained(
            model_meta.model_path,
            use_fast=True,
            trust_remote_code=trust_remote_code,
        )

    def _load_xgrammar_compiler(self, max_threads: int) -> None:
        """Load xgrammar compiler for structured output generation."""
        if not self._processor:
            return

        tokenizer = getattr(self._processor, "tokenizer", self._processor)
        full_vocab_size = len(tokenizer.get_vocab())
        config_vocab_size = tokenizer.vocab_size
        actual_vocab_size = max(full_vocab_size, config_vocab_size)

        tokenizer_info = xgr.TokenizerInfo.from_huggingface(
            tokenizer, vocab_size=actual_vocab_size
        )
        self._compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=max_threads)

    def _load_huggingface_generation_config(
        self, model_meta: ModelDownloadResult
    ) -> None:
        """Load generation config from HuggingFace config.json."""
        generation_config = GenerationConfig.from_pretrained(model_meta.model_path)
        self._generation_config = msgspec.convert(
            generation_config.to_dict(), type=self._generation_config_class
        )

    def _load_huggingface_model_config(self, model_meta: ModelDownloadResult) -> None:
        """Load model configuration from HuggingFace config.json.

        Extracts model configuration from the HuggingFace model's config.json file
        and populates the metadata dictionary with model type, architectures,
        compute precision, and other relevant information.

        Args:
            model_meta: Model metadata containing the model path where config.json
                is located. The model_path should point to a directory containing
                the HuggingFace model files.

        Raises:
            FileNotFoundError: If config.json is not found in the model directory.
            ValueError: If the config.json file is malformed or missing required fields.
            ImportError: If transformers library is not available.

        Note:
            This method sets default values for task_type, system_prompt, and
            quantization_enabled if they are not present in the configuration.

        """
        config = AutoConfig.from_pretrained(model_meta.model_path)
        self._metadata["model_type"] = config.model_type
        self._metadata["architectures"] = config.architectures
        self._metadata["compute_precision_type"] = config.dtype

        # Set defaults for pretrained models
        self._metadata.setdefault("task_type", "generic")
        self._metadata.setdefault("system_prompt", "")
        self._metadata.setdefault("quantization_enabled", False)
