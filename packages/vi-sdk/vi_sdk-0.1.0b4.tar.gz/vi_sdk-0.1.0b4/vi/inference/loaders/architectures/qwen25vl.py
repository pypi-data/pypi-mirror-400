#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   qwen25vl.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK Qwen2.5-VL loader module.
"""

from rich import print as rprint
from vi.inference.loaders.loader_registry import LoaderRegistry
from vi.inference.utils.module_import import check_imports

try:
    check_imports(
        packages=["torch", "transformers", "xgrammar", "qwen_vl_utils"],
        dependency_group="qwen",
        auto_install=True,
    )
except ImportError as e:
    rprint(f"[red]Error: {e}[/red]")
    raise

# Import after check to ensure packages are available
from transformers import AutoModelForImageTextToText, AutoProcessor
from vi.inference.config.qwen25vl import Qwen25VLGenerationConfig
from vi.inference.loaders.hf import HFLoader


@LoaderRegistry.register(
    loader_key="qwen25vl",
    model_types=["qwen2_5_vl"],
    architectures=["Qwen2_5_VLForConditionalGeneration"],
)
@LoaderRegistry.register(
    loader_key="cosmosreason1",
    model_types=["qwen2_5_vl"],
    architectures=["Qwen2_5_VLForConditionalGeneration"],
)
@LoaderRegistry.register(
    loader_key="internvl35",
    model_types=["internvl"],
    architectures=["InternVLForConditionalGeneration"],
)
@LoaderRegistry.register(
    loader_key="llavanext",
    model_types=["llava_next"],
    architectures=["LlavaNextForConditionalGeneration"],
)
class Qwen25VLLoader(HFLoader):
    """Loader for Qwen2.5-VL compatible vision-language models.

    Handles loading of vision-language models from HuggingFace Hub, local paths,
    or Datature Vi fine-tuned models. Supports optional PEFT adapters,
    quantization, and structured output generation via xgrammar.

    Supported model architectures:
        - Qwen2.5-VL (Qwen2_5_VLForConditionalGeneration)
        - InternVL 3.5 (InternVLForConditionalGeneration)
        - Cosmos Reason1 (Qwen2_5_VLForConditionalGeneration)
        - LLaVA-NeXT (LlavaNextForConditionalGeneration)

    Supported configurations:
        - Pretrained models from HuggingFace:
            - "Qwen/Qwen2.5-VL-7B-Instruct"
            - "OpenGVLab/InternVL3.5-8B"
            - "llava-hf/llama3-llava-next-8b-hf"
        - Fine-tuned models from Datature Vi platform
        - Local model directories with standard HuggingFace structure
        - 4-bit and 8-bit quantization for memory efficiency
        - PEFT adapters (LoRA, QLoRA)
        - Structured output generation (requires xgrammar)

    Example:
        ```python
        from vi.inference.loaders import Qwen25VLLoader
        from vi.api.resources.models.results import ModelDownloadResult

        # Load Qwen2.5-VL from HuggingFace
        model_meta = ModelDownloadResult(
            model_path="Qwen/Qwen2.5-VL-7B-Instruct",
            adapter_path=None,
            run_config_path=None,
        )
        loader = Qwen25VLLoader(
            model_meta=model_meta,
            trust_remote_code=True,
        )

        # Load InternVL 3.5 from HuggingFace
        model_meta = ModelDownloadResult(
            model_path="OpenGVLab/InternVL3.5-8B",
            adapter_path=None,
            run_config_path=None,
        )
        loader = Qwen25VLLoader(
            model_meta=model_meta,
            trust_remote_code=True,
        )

        # Load fine-tuned Datature model
        model_meta = ModelDownloadResult(
            model_path="./models/run_123/model_full",
            adapter_path="./models/run_123/model_adapter",
            run_config_path="./models/run_123/model_full/run.json",
        )
        loader = Qwen25VLLoader(model_meta=model_meta)

        # Access components
        print(f"Model: {loader.model}")
        print(f"Processor: {loader.processor}")
        print(f"Compiler: {loader.compiler}")
        ```

    """

    _generation_config_class = Qwen25VLGenerationConfig
    _model_class = AutoModelForImageTextToText
    _processor_class = AutoProcessor
