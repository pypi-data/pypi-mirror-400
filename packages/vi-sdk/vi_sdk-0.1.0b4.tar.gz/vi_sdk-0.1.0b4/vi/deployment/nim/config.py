#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   config.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Configuration structs for NIM deployment.
"""

from pathlib import Path

from msgspec import Struct
from vi.consts import DEFAULT_MODEL_DIR


class NIMConfig(Struct, kw_only=True):
    """Configuration for NIM deployment.

    Attributes:
        nvidia_api_key: The NGC API key for authentication with nvcr.io.
        image_name: The NIM image name to pull (without registry prefix).
        tag: The image tag to pull.
        port: Port to expose the container on.
        shm_size: Shared memory size for the container.
        max_model_len: Maximum model length. Defaults to 8192.
        local_cache_dir: Local directory to mount for NIM cache.
            If None, uses default ~/.cache/nim.
        use_existing_container: Whether to reuse existing container with same name.
            Defaults to True.
        auto_kill_existing_container: Whether to automatically stop and remove
            existing containers with the same name. Defaults to False.
        stream_logs: Whether to stream container logs to the terminal during startup.
            Defaults to True.
        force_pull: Whether to pull the image even if it exists locally. Defaults to False.
        secret_key: Your Vi SDK secret key (required for custom weights).
            If None, loads from DATATURE_VI_SECRET_KEY environment variable.
        organization_id: Your organization ID (required for custom weights).
            If None, loads from DATATURE_VI_ORGANIZATION_ID environment variable.
        run_id: The run ID of the trained model to deploy (enables custom weights).
        ckpt: Optional checkpoint identifier for custom weights.
        model_save_path: Directory to save downloaded model files.
        served_model_name: Name to serve the model as (NIM_SERVED_MODEL_NAME).
            If None, defaults to image_name when using custom weights.
        overwrite: If True, re-download the model even if it exists locally.

    """

    nvidia_api_key: str
    image_name: str = "cosmos-reason1-7b"
    tag: str = "latest"
    port: int = 8000
    shm_size: str = "32GB"
    max_model_len: int = 8192
    local_cache_dir: str | None = None
    use_existing_container: bool = True
    auto_kill_existing_container: bool = False
    stream_logs: bool = True
    force_pull: bool = False
    secret_key: str | None = None
    organization_id: str | None = None
    run_id: str | None = None
    ckpt: str | None = None
    model_save_path: Path | str = Path(DEFAULT_MODEL_DIR)
    served_model_name: str | None = None
    overwrite: bool = False


class NIMSamplingParams(Struct, kw_only=True):
    """Configuration for NIM model sampling and guided decoding parameters.

    This class encapsulates all sampling parameters for the NVIDIA NIM API,
    including standard OpenAI parameters, NIM-specific extensions, and
    guided decoding options.

    Attributes:
        temperature: Controls randomness of sampling. Lower values make output more
            deterministic, higher values make it more random. Must be >= 0.
            Set to 0 for greedy sampling. Defaults to 1.0.
        top_p: Controls cumulative probability of top tokens to consider.
            Must be in (0, 1]. Set to 1 to consider all tokens. Defaults to 1.0.
        top_k: Controls number of top tokens to consider. Set to -1 to consider
            all tokens. Must be >= 1 otherwise. Defaults to 50.
        min_p: Minimum probability for a token to be considered, relative to the
            most likely token. Must be in [0, 1]. Set to 0 to disable. Defaults to 0.0.
        presence_penalty: Penalizes tokens based on whether they appear in generated
            text so far. Values > 0 encourage new tokens, < 0 encourage repetition.
            Must be in [-2, 2]. Defaults to 0.0.
        frequency_penalty: Penalizes tokens based on their frequency in generated
            text so far. Values > 0 encourage new tokens, < 0 encourage repetition.
            Must be in [-2, 2]. Defaults to 0.0.
        repetition_penalty: Penalizes tokens based on whether they appear in prompt
            and generated text. Values > 1 encourage new tokens, < 1 encourage
            repetition. Must be in (0, 2]. Defaults to 1.05.
        max_tokens: Maximum number of tokens to generate. Must be >= 1. Defaults to 1024.
        min_tokens: Minimum number of tokens to generate before EOS or stop tokens
            can be generated. Must be >= 0. Defaults to 0.
        stop: String or list of strings that stop generation when generated.
            Returned output will not contain the stop strings. Defaults to None.
        seed: Random seed for generation. Defaults to None.
        ignore_eos: Whether to ignore EOS token and continue generating.
            Useful for performance benchmarking. Defaults to False.
        logprobs: Number of log probabilities to return per output token.
            When None, no probability is returned. Must be >= 0. Defaults to None.
        prompt_logprobs: Number of log probabilities to return per prompt token.
            Must be >= 0. Defaults to None.
        guided_json: JSON schema (as string or dict) to guide output structure.
            If specified, output will follow the JSON schema. Defaults to None.
        guided_regex: Regular expression pattern to guide output format.
            If specified, output will match the regex pattern. Defaults to None.
        guided_choice: List of strings representing valid output choices.
            If specified, output will be exactly one of the choices. Defaults to None.
        guided_grammar: Context-free grammar to guide output structure.
            If specified, output will follow the grammar rules. Defaults to None.

    Example:
        ```python
        from vi.deployment.nim import NIMPredictor, NIMSamplingParams

        # Create custom sampling configuration
        params = NIMSamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=512,
            seed=42,
            guided_choice=["yes", "no", "maybe"],
        )

        predictor = NIMPredictor(
            model_name="cosmos-reason1-7b", task_type="phrase-grounding"
        )

        result = predictor(source="image.jpg", sampling_params=params)
        ```

    """

    temperature: float = 1.0
    top_p: float = 1.0
    top_k: int = 50
    min_p: float = 0.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    repetition_penalty: float = 1.05
    max_tokens: int = 1024
    min_tokens: int = 0
    stop: str | list[str] | None = None
    seed: int | None = None
    ignore_eos: bool = False
    logprobs: int | None = None
    prompt_logprobs: int | None = None
    guided_json: str | dict | None = None
    guided_regex: str | None = None
    guided_choice: list[str] | None = None
    guided_grammar: str | None = None
