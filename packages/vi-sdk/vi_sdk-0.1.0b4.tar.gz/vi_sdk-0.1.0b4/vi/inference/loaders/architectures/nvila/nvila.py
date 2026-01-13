#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   nvila.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NVILA loader module.
"""

from pathlib import Path

import torch
from rich import print as rprint
from rich.progress import BarColumn, SpinnerColumn, TimeElapsedColumn
from transformers.utils.quantization_config import BitsAndBytesConfig
from vi.api.resources.models.results import ModelDownloadResult
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.loaders.loader_registry import LoaderRegistry
from vi.inference.utils.module_import import check_imports
from vi.utils.progress import ViProgress

try:
    check_imports(
        packages=["einops", "torch", "transformers", "xgrammar", "qwen_vl_utils"],
        dependency_group="nvila",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

import xgrammar as xgr
from vi.inference.config.nvila import NVILAGenerationConfig
from vi.inference.loaders.architectures.nvila.modeling import (
    NVILALiteForConditionalGeneration,
)
from vi.inference.loaders.architectures.nvila.processing import NVILALiteProcessor

# Constants
DEFAULT_CONFIG_FILE_NAME = "config.json"  # Default configuration file name
DEFAULT_ATTN_IMPLEMENTATION = "eager"  # Default attention implementation
DEFAULT_DEVICE_MAP = "auto"  # Default device mapping strategy
MAX_THREADS = 8  # Maximum number of threads for xgrammar compiler

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1


@LoaderRegistry.register(
    loader_key="nvila",
    model_types=["nvila"],
    architectures=["NVILALiteForConditionalGeneration"],
)
class NVILALoader(BaseLoader):
    """NVILA model loader for multimodal vision-language tasks.

    This loader handles the initialization and configuration of NVILA models,
    including support for quantization, adapters, and structured output generation.
    It integrates with the Vi SDK framework and provides comprehensive model
    management capabilities.

    The loader supports:
    - Model loading with various attention implementations
    - Quantization configuration (4-bit, 8-bit)
    - Adapter loading for fine-tuned models
    - Device mapping and memory optimization
    - xgrammar integration for structured outputs

    Attributes:
        _model: Loaded NVILA model instance
        _processor: NVILA processor for input preprocessing
        _compiler: xgrammar compiler for structured output generation
        _quantization_config: Quantization configuration if enabled
        _metadata: Model metadata from run configuration

    """

    _generation_config_class = NVILAGenerationConfig
    _quantization_config: BitsAndBytesConfig | None = None

    def __init__(
        self,
        model_meta: ModelDownloadResult,
        attn_implementation: str = DEFAULT_ATTN_IMPLEMENTATION,
        device_map: dict | str = DEFAULT_DEVICE_MAP,
        low_cpu_mem_usage: bool = False,
        trust_remote_code: bool = True,
        max_threads: int = MAX_THREADS,
    ):
        """Initialize the NVILA loader.

        This method loads the NVILA model with the specified configuration,
        including quantization settings, device mapping, and adapter loading.
        It also initializes the processor and xgrammar compiler for
        structured output generation.

        Args:
            model_meta: Downloaded model metadata containing paths and configuration
            attn_implementation: Attention implementation to use (eager, flash_attention_2, etc.)
            device_map: Device mapping strategy for model placement
            low_cpu_mem_usage: Whether to use low CPU memory usage during loading
            trust_remote_code: Whether to trust remote code in model files
            max_threads: Maximum number of threads for xgrammar compiler
            **kwargs: Additional arguments passed to the model loader

        Raises:
            KeyboardInterrupt: If model loading is cancelled by user
            ImportError: If required dependencies are not available

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

                progress.update(
                    main_task, advance=50, description="Loading model metadata..."
                )

                if model_meta.run_config_path:
                    self._load_generation_config_from_run_json(model_meta)
                self._load_metadata_from_run_json(model_meta)

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
                    )

                progress.update(main_task, description="Loading pretrained weights...")

                model_dtype = self._metadata.get(
                    "compute_precision_type", torch.bfloat16
                )

                self._model = NVILALiteForConditionalGeneration.from_pretrained(
                    model_meta.model_path,
                    attn_implementation=attn_implementation,
                    device_map=device_map,
                    dtype=model_dtype,
                    low_cpu_mem_usage=low_cpu_mem_usage,
                    trust_remote_code=trust_remote_code,
                    config=(
                        Path(model_meta.model_path) / DEFAULT_CONFIG_FILE_NAME
                        if model_meta.run_config_path
                        else None
                    ),
                    quantization_config=self._quantization_config,
                )

                # Load adapter if present
                progress.update(main_task, advance=20, description="Loading adapter...")
                if model_meta.adapter_path:
                    self._model.load_adapter(model_meta.adapter_path)

                self._model.eval()

                # Load processor for Datature models
                progress.update(
                    main_task, advance=20, description="Loading processor..."
                )

                self._processor = NVILALiteProcessor.from_pretrained(
                    model_meta.model_path,
                    use_fast=True,
                    trust_remote_code=trust_remote_code,
                )

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

    def _load_xgrammar_compiler(self, max_threads: int) -> None:
        """Load xgrammar compiler for structured output generation.

        This method initializes the xgrammar compiler which enables structured
        output generation for the NVILA model. The compiler is configured with
        the model's tokenizer information and thread limits.

        Args:
            max_threads: Maximum number of threads for the compiler

        Note:
            This method requires the processor to be loaded first. If no processor
            is available, the method returns without initializing the compiler.

        """
        if not self._processor:
            return

        tokenizer = self._processor.tokenizer
        full_vocab_size = len(tokenizer.get_vocab())
        config_vocab_size = tokenizer.vocab_size
        actual_vocab_size = max(full_vocab_size, config_vocab_size)

        tokenizer_info = xgr.TokenizerInfo.from_huggingface(
            tokenizer, vocab_size=actual_vocab_size
        )
        self._compiler = xgr.GrammarCompiler(tokenizer_info, max_threads=max_threads)
