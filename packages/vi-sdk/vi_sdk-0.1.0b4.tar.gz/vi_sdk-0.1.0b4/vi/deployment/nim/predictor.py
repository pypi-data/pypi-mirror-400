#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   predictor.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK NIM predictor module.
"""

import base64
import json
from collections.abc import Generator
from pathlib import Path

import msgspec
from openai import OpenAI
from openai._streaming import Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from vi.api.resources.flows.responses import FlowSpec
from vi.consts import DEFAULT_MODEL_DIR, DEFAULT_MODEL_DIR_NAME
from vi.deployment.nim.config import NIMConfig, NIMSamplingParams
from vi.inference.messages import (
    create_system_message,
    create_user_message_with_image_url,
)
from vi.inference.predictors.base_predictor import BasePredictor
from vi.inference.task_types import (
    GenericResponse,
    PredictionResponse,
    TaskAssistant,
    consts,
)
from vi.inference.task_types.phrase_grounding import PhraseGroundingResponse
from vi.inference.task_types.vqa import VQAResponse


class NIMPredictor(BasePredictor):
    """NIM predictor for NIM models.

    This predictor is used to perform inference on images using the NIM model.
    It handles image encoding, message construction, and response parsing.

    Example:
        ```python
        from vi.deployment.nim import NIMDeployer, NIMPredictor, NIMConfig

        # Create shared config
        config = NIMConfig(
            nvidia_api_key="nvapi-...",
            run_id="your-run-id",  # Optional: for Datature Vi models
        )

        # Deploy the model
        deployer = NIMDeployer(config)
        result = deployer.deploy()

        # Create predictor with same config
        predictor = NIMPredictor(task_type="phrase-grounding", config=config)

        # Run inference
        response = predictor(source="image.jpg", stream=False)
        print(response.caption)
        ```

    """

    _model_name: str
    _task_type: str
    _schema: TaskAssistant
    _user_prompt: str | None
    _port: int
    _system_prompt: str

    def __init__(
        self,
        task_type: str,
        config: NIMConfig | None = None,
        model_name: str | None = None,
        port: int | None = None,
    ):
        """Initialize the NIM predictor.

        Args:
            task_type: Type of task (e.g., "phrase-grounding", "vqa").
            config: Optional NIMConfig instance. If provided, extracts model_name,
                port, run_id, and model_save_path from config. This is the recommended
                way to initialize the predictor when used with NIMDeployer.
            model_name: Name of the NIM model to use. Required if config is not provided.
            port: Port where the NIM service is running. Defaults to 8000 if not
                specified in config.

        Raises:
            ValueError: If neither config nor model_name is provided.

        """
        if config is not None:
            self._model_name = config.served_model_name or config.image_name
            self._port = config.port
            run_id = config.run_id
            model_save_path = config.model_save_path
        else:
            if model_name is None:
                raise ValueError(
                    "Either 'config' or 'model_name' must be provided. "
                    "Use config=NIMConfig(...) or model_name='model-name'"
                )
            self._model_name = model_name
            self._port = port if port is not None else 8000
            run_id = None
            model_save_path = DEFAULT_MODEL_DIR

        self._task_type = task_type
        self._schema = consts.TASK_TYPE_TO_ASSISTANT_MAP[consts.TaskType(task_type)]
        self._user_prompt = consts.TASK_TYPE_TO_USER_PROMPT_MAP[
            consts.TaskType(task_type)
        ]
        self._system_prompt = self._load_system_prompt(run_id, model_save_path)

    def _load_system_prompt(
        self, run_id: str | None, model_save_path: Path | str
    ) -> str:
        """Load system prompt from model files.

        Args:
            run_id: Run ID of the Datature Vi trained model.
            model_save_path: Base directory where models are saved.

        Returns:
            System prompt string. Returns default system prompt based on task type
            if run_id is None, if run.json doesn't exist, or if system prompt is not
            found in run.json.

        """
        if run_id is None:
            return self._get_default_system_prompt()

        # Construct model path following the same pattern as deployer
        model_dir = Path(model_save_path) / run_id / DEFAULT_MODEL_DIR_NAME
        run_config_path = model_dir / "run.json"

        if not run_config_path.exists():
            return self._get_default_system_prompt()

        try:
            with open(run_config_path, encoding="utf-8") as f:
                config_data = json.loads(f.read())
                flow_spec = msgspec.convert(config_data["spec"]["flow"], type=FlowSpec)

                # Extract system prompt
                system_prompt_block = next(
                    (
                        block
                        for block in flow_spec.blocks
                        if "system-prompt" in block.block
                    ),
                    None,
                )
                if system_prompt_block:
                    return system_prompt_block.settings["systemPrompt"]

        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass

        return self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt based on task type.

        Returns:
            Default system prompt string, or empty string if no default exists.

        """
        default_prompt = consts.TASK_TYPE_TO_SYSTEM_PROMPT_MAP.get(
            consts.TaskType(self._task_type)
        )
        return default_prompt if default_prompt else ""

    def _parse_result(self, result_json: str, user_prompt: str) -> PredictionResponse:
        """Parse generated JSON into appropriate response type."""
        assistant = self._schema.model_validate_json(result_json)

        if self._task_type == consts.TaskType.PHRASE_GROUNDING.value:
            return PhraseGroundingResponse(
                prompt=user_prompt, result=assistant.phrase_grounding
            )

        if self._task_type == consts.TaskType.VQA.value:
            return VQAResponse(prompt=user_prompt, result=assistant.vqa)

        return GenericResponse(prompt=user_prompt, result=result_json)

    def __call__(
        self,
        source: str,
        user_prompt: str | None = None,
        stream: bool = False,
        sampling_params: NIMSamplingParams | None = None,
    ) -> PredictionResponse | Generator[str, None, PredictionResponse]:
        """Perform inference on an image with optional custom prompt.

        This method processes an image and optional text prompt through the NIM model,
        generating structured output based on the configured task type.
        It handles image encoding, message construction, and response parsing.

        Args:
            source: Path to the input image file
            user_prompt: Optional custom prompt to override the default task prompt
            stream: Whether to stream the response. Defaults to False.
            sampling_params: Optional NIMSamplingParams instance containing all sampling
                and guided decoding parameters. If None, default values are used.

        Returns:
            Task-specific prediction results. The exact format depends on the
            model's training task:
            - Phrase Grounding: PhraseGroundingResponse with bounding boxes
            - VQA: VQAResponse with question-answer pairs
            - Generic: GenericResponse with raw JSON string

        Raises:
            FileNotFoundError: If the image file doesn't exist.
            ValueError: If the image format is not supported.
            RuntimeError: If model inference fails.

        Example:
            ```python
            from vi.deployment.nim import NIMPredictor, NIMConfig

            # Recommended: Use with NIMConfig (shares config with deployer)
            config = NIMConfig(
                nvidia_api_key="nvapi-...",
                run_id="your-run-id",  # System prompt loaded from model files
            )
            predictor = NIMPredictor(task_type="phrase-grounding", config=config)

            # Alternative: Direct initialization for pretrained models
            predictor = NIMPredictor(
                task_type="phrase-grounding",
                model_name="cosmos-reason1-7b",
            )

            # Or with custom port
            predictor = NIMPredictor(
                task_type="phrase-grounding",
                model_name="cosmos-reason1-7b",
                port=8080,
            )

            # Run inference with streaming (default behavior)
            gen = predictor(source="image.jpg")
            for token in gen:
                print(token, end="", flush=True)
            # The final result is in the generator's return value

            # Run inference without streaming - get the parsed PredictionResponse
            result = predictor(source="image.jpg", stream=False)
            print(f"Caption: {result.caption}")
            for phrase in result.phrase_grounding:
                print(f"Phrase: {phrase.phrase}, Bounding Box: {phrase.bounding_box}")

            # Use sampling parameters for more controlled generation
            from vi.deployment.nim.config import NIMSamplingParams

            params = NIMSamplingParams(
                temperature=0.7, top_p=0.9, max_tokens=512, seed=42
            )
            result = predictor(source="image.jpg", stream=False, sampling_params=params)

            # Use guided decoding for structured output
            guided_params = NIMSamplingParams(
                temperature=0.2,
                guided_choice=[
                    "yes",
                    "no",
                    "maybe",
                ],  # Constrain output to these choices
            )
            result = predictor(
                source="image.jpg", stream=False, sampling_params=guided_params
            )
            ```

        """
        if user_prompt:
            self._user_prompt = user_prompt

        # Use default sampling params if not provided
        if sampling_params is None:
            sampling_params = NIMSamplingParams()

        with open(source, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        image_url = f"data:image/jpeg;base64,{image_data}"
        messages = []

        # Only add system message if system_prompt is not empty
        if self._system_prompt:
            messages.append(create_system_message(self._system_prompt))

        messages.append(
            create_user_message_with_image_url(image_url, self._user_prompt)
        )

        base_url = f"http://0.0.0.0:{self._port}/v1"
        client = OpenAI(base_url=base_url, api_key="not-used")

        # Build standard OpenAI API parameters
        api_params = {
            "model": self._model_name,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": self._schema.__name__,
                    "schema": self._schema.model_json_schema(),
                },
            },
            "max_tokens": sampling_params.max_tokens,
            "stream": stream,
            "temperature": sampling_params.temperature,
            "top_p": sampling_params.top_p,
            "presence_penalty": sampling_params.presence_penalty,
            "frequency_penalty": sampling_params.frequency_penalty,
        }

        # Add optional standard parameters only if they are not None
        if sampling_params.stop is not None:
            api_params["stop"] = sampling_params.stop
        if sampling_params.seed is not None:
            api_params["seed"] = sampling_params.seed
        if sampling_params.logprobs is not None:
            api_params["logprobs"] = sampling_params.logprobs

        # Build NIM-specific parameters under nvext
        nvext_params = {
            "top_k": sampling_params.top_k,
            "min_p": sampling_params.min_p,
            "repetition_penalty": sampling_params.repetition_penalty,
            "min_tokens": sampling_params.min_tokens,
            "ignore_eos": sampling_params.ignore_eos,
        }

        # Add optional NIM-specific parameters only if they are not None
        if sampling_params.prompt_logprobs is not None:
            nvext_params["prompt_logprobs"] = sampling_params.prompt_logprobs

        # Add guided decoding parameters if specified
        if sampling_params.guided_json is not None:
            nvext_params["guided_json"] = sampling_params.guided_json
        if sampling_params.guided_regex is not None:
            nvext_params["guided_regex"] = sampling_params.guided_regex
        if sampling_params.guided_choice is not None:
            nvext_params["guided_choice"] = sampling_params.guided_choice
        if sampling_params.guided_grammar is not None:
            nvext_params["guided_grammar"] = sampling_params.guided_grammar

        # Wrap NIM-specific parameters in nvext object
        api_params["extra_body"] = {"nvext": nvext_params}

        response: ChatCompletion | Stream[ChatCompletionChunk] = (
            client.chat.completions.create(**api_params)
        )

        if stream:
            # Collect full output while streaming
            full_output = []
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None and content != "":
                    full_output.append(content)
                    yield content

            # Parse the complete output and return as generator return value
            result_json = "".join(full_output)
            return self._parse_result(result_json, self._user_prompt or "")

        # Non-streaming
        result_json = response.choices[0].message.content
        return self._parse_result(result_json, self._user_prompt or "")
