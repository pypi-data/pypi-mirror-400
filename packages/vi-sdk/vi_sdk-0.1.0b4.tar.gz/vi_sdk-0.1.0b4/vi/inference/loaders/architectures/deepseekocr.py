#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   deepseekocr.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK DeepSeekOCR loader module.
"""

from rich import print as rprint
from vi.inference.loaders.loader_registry import LoaderRegistry
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=["torch", "transformers", "xgrammar"],
        dependency_group="deepseekocr",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

# Import after check to ensure packages are available
from transformers import AutoModel, AutoTokenizer
from vi.inference.config.deepseekocr import DeepSeekOCRGenerationConfig
from vi.inference.loaders.hf import HFLoader


@LoaderRegistry.register(
    loader_key="deepseekocr",
    model_types=["deepseek_vl_v2"],
    architectures=["DeepseekOCRForCausalLM"],
)
class DeepSeekOCRLoader(HFLoader):
    """Loader for DeepSeekOCR vision-language models.

    Handles loading of DeepSeekOCR models from HuggingFace Hub, local paths,
    or Datature Vi fine-tuned models. Supports optional PEFT adapters,
    quantization, and structured output generation via xgrammar.

    Supported model architectures:
        - DeepSeekOCR (DeepseekOCRForCausalLM via AutoModel)

    Supported configurations:
        - Pretrained models from HuggingFace:
            - "deepseek-ai/DeepSeek-OCR"
        - Fine-tuned models from Datature Vi platform
        - Local model directories with standard HuggingFace structure
        - 4-bit and 8-bit quantization for memory efficiency
        - PEFT adapters (LoRA, QLoRA)
        - Structured output generation (requires xgrammar)

    Note:
        DeepSeekOCR uses AutoModel.from_pretrained() which automatically loads
        DeepseekOCRForCausalLM via the auto_map in config.json. This is the
        recommended loading method from HuggingFace.

    Example:
        ```python
        from vi.inference.loaders import DeepSeekOCRLoader
        from vi.api.resources.models.results import ModelDownloadResult

        # Load DeepSeekOCR from HuggingFace
        model_meta = ModelDownloadResult(
            model_path="deepseek-ai/DeepSeek-OCR",
            adapter_path=None,
            run_config_path=None,
        )
        loader = DeepSeekOCRLoader(
            model_meta=model_meta,
            trust_remote_code=True,
        )

        # Load fine-tuned Datature model
        model_meta = ModelDownloadResult(
            model_path="./models/run_123/model_full",
            adapter_path="./models/run_123/model_adapter",
            run_config_path="./models/run_123/model_full/run.json",
        )
        loader = DeepSeekOCRLoader(model_meta=model_meta)

        # Access components
        print(f"Model: {loader.model}")
        print(f"Processor: {loader.processor}")
        print(f"Compiler: {loader.compiler}")
        ```

    """

    _generation_config_class = DeepSeekOCRGenerationConfig
    _model_class = AutoModel
    _processor_class = AutoTokenizer
