#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   streaming.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference streaming module.
"""

import threading
from collections.abc import Callable, Generator
from typing import Any

import msgspec
import torch
from transformers import TextIteratorStreamer
from vi.inference.loaders.base_loader import BaseLoader
from vi.inference.task_types.assistant import PredictionResponse

# Disable inductor async compile workers to prevent hanging on exit
torch._inductor.config.compile_threads = 1


class StreamingMixin:
    """Mixin class providing streaming generation capabilities for predictors.

    This mixin provides common streaming functionality that can be added to
    any predictor class through multiple inheritance. It handles:
    - Threaded model generation for non-blocking streaming
    - Token-by-token output

    Example:
        ```python
        class MyPredictor(BasePredictor, StreamingMixin):
            def __call__(self, source: str, stream: bool = False):
                # ... setup code ...
                if stream:
                    return self._stream_generator(...)
                # ... non-streaming code ...
        ```

    Note:
        This is designed as a mixin and should be used alongside BasePredictor
        or similar base classes that define the core prediction interface.

    """

    def _run_generation(
        self,
        model: Any,
        inputs: dict,
        gen_kwargs: dict,
        streamer: TextIteratorStreamer,
        exception_holder: list,
    ) -> None:
        """Run model generation in a background thread.

        Args:
            model: The model to run generation on
            inputs: Model inputs
            gen_kwargs: Generation keyword arguments
            streamer: The streamer to signal end on exception
            exception_holder: List to store exception for propagation to main thread

        """
        try:
            with torch.no_grad():
                model.generate(**inputs, **gen_kwargs)
        except KeyboardInterrupt:
            streamer.end()
        except Exception as e:
            exception_holder.append(e)
            streamer.end()

    def _stream_generator(
        self,
        loader: BaseLoader,
        inputs: dict,
        generation_config: Any,
        user_prompt: str,
        parse_result_fn: Callable[[str, str], PredictionResponse],
    ) -> Generator[str, None, PredictionResponse]:
        """Generate streaming output.

        Token generation is guided by xgrammar logits processors (configured
        in the predictor) to coax the model toward valid structured output.
        Final validation is performed once after all tokens are generated,
        using the same logic as non-streaming mode. If validation fails,
        returns GenericResponse instead of raising an error.

        Args:
            loader: Model loader with processor and model
            inputs: Model inputs
            generation_config: Generation configuration
            user_prompt: User prompt for parsing
            parse_result_fn: Function to parse final JSON result.
                This function handles validation and falls back to
                GenericResponse on failure.

        Yields:
            Tokens as strings during generation

        Returns:
            Final PredictionResponse when complete

        """
        # Set up streamer
        streamer = TextIteratorStreamer(
            loader.processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
            timeout=120.0,
        )
        gen_kwargs = msgspec.structs.asdict(generation_config)
        gen_kwargs.pop("seed", None)
        gen_kwargs["streamer"] = streamer

        if gen_kwargs.get("stop_strings"):
            gen_kwargs["tokenizer"] = loader.processor.tokenizer

        # Start generation in background thread
        exception_holder: list[Exception] = []
        thread = threading.Thread(
            target=self._run_generation,
            args=(loader.model, inputs, gen_kwargs, streamer, exception_holder),
            daemon=True,
        )
        thread.start()

        full_output: list[str] = []

        try:
            for text in streamer:
                if not text:
                    continue

                full_output.append(text)
                yield text

            if exception_holder:
                raise exception_holder[0]

            # Finalize output
            result_json = "".join(full_output)
            if generation_config.stop_strings:
                for stop_string in generation_config.stop_strings:
                    if result_json.endswith(stop_string):
                        result_json = result_json[: -len(stop_string)]
                        break

            # Wait for generation thread to complete (should be nearly instant
            # since streamer is exhausted)
            thread.join()

            # Parse and validate result - uses same logic as non-streaming mode.
            # Falls back to GenericResponse if validation fails.
            return parse_result_fn(result_json, user_prompt)

        except (KeyboardInterrupt, SystemExit):
            try:
                streamer.end()
            except Exception:
                pass
            raise
        except Exception:
            if thread.is_alive():
                thread.join(timeout=1.0)
            raise
