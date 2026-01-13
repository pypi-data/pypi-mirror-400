#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK inference response wrappers.
"""

from collections.abc import Callable, Generator
from typing import Any

from rich import print as rprint


class Stream:
    r"""OpenAI-style streaming response wrapper.

    Provides a clean iterator interface for streaming tokens while handling
    background thread execution and error propagation properly.

    This is similar to OpenAI's Stream class but adapted for local model inference.

    Example:
        ```python
        from vi.inference import ViModel

        model = ViModel(run_id="your-run")
        stream = model(source="image.jpg")  # Returns Stream

        # Stream tokens in real-time (OpenAI-style)
        for chunk in stream:
            print(chunk, end="", flush=True)

        # Get the final parsed result
        print(f"\nFinal result: {stream.get_final_completion()}")
        ```

    """

    def __init__(
        self,
        stream_func: Callable[[], Generator[str, None, Any]],
    ):
        """Initialize stream with a generator function.

        Args:
            stream_func: Function that returns a generator yielding tokens
                and returning the final result

        """
        self._stream_func = stream_func
        self._generator = None
        self._result = None
        self._error = None
        self._consumed = False

    def __iter__(self):
        """Iterate over streamed tokens.

        Yields:
            Tokens as strings

        Raises:
            Exception: If an error occurred during generation

        """
        if self._consumed:
            raise RuntimeError("Stream has already been consumed")

        self._consumed = True
        self._generator = self._stream_func()

        try:
            # Manually iterate to capture generator's return value
            while True:
                try:
                    token = next(self._generator)
                except StopIteration as e:
                    # Capture the return value from the generator
                    self._result = e.value
                    break
                yield token
            # Print newline after last token
            print()
        except KeyboardInterrupt:
            rprint("\n[yellow]⚠ Streaming cancelled by user[/yellow]")
            self._error = KeyboardInterrupt("Streaming cancelled by user")
            raise
        except Exception as e:
            self._error = e
            raise

    def get_final_completion(self) -> Any:
        """Get the final parsed result after streaming completes.

        This method will consume the stream if it hasn't been consumed yet.

        Returns:
            The final parsed PredictionResponse

        Raises:
            Exception: If an error occurred during streaming

        """
        if not self._consumed:
            # Consume the stream
            for _ in self:
                pass

        if self._error:
            raise self._error

        return self._result
