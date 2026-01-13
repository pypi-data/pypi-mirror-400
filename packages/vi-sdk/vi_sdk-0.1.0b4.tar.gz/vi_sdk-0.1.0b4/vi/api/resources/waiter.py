#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   waiter.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK resource waiter module.
"""

import time
from collections.abc import Callable
from typing import Any

from rich.progress import SpinnerColumn, TimeElapsedColumn
from vi.api.responses import Condition, ConditionStatus, ResourceCondition
from vi.client.errors import ViOperationError
from vi.utils.graceful_exit import graceful_exit
from vi.utils.progress import ViProgress


class ResourceWaiter:
    """Resource waiter with timeline tracking."""

    def __init__(self):
        """Initialize the resource waiter with status messages and icons.

        Sets up message templates and icons for different resource conditions.
        """
        self.status_messages = {
            (Condition.STARTED, ConditionStatus.WAITING): "🚀 Preparing to start...",
            (
                Condition.STARTED,
                ConditionStatus.REACHED,
            ): "✅ Process started successfully",
            (
                Condition.STARTED,
                ConditionStatus.FAILED_REACH,
            ): "❌ Failed to start process",
            (
                Condition.FINISHED,
                ConditionStatus.WAITING,
            ): "⏳ Processing in progress...",
            (
                Condition.FINISHED,
                ConditionStatus.REACHED,
            ): "🎉 Process completed successfully",
            (
                Condition.FINISHED,
                ConditionStatus.FAILED_REACH,
            ): "💥 Process failed with errors",
        }

    def _build_progress_chain(
        self, resource_conditions: list[ResourceCondition]
    ) -> str:
        """Build a progress chain showing the journey through conditions.

        Args:
            resource_conditions: List of resource conditions to display.

        Returns:
            A formatted string showing the progress chain with icons and messages.

        """
        if not resource_conditions:
            return "🔄 Initializing process..."

        # Reverse to chronological order
        chronological = list(reversed(resource_conditions))

        progress_parts = []
        for condition in chronological:
            condition_str = (
                condition.condition.value
                if isinstance(condition.condition, Condition)
                else condition.condition
            )
            # Create proper key for status_messages lookup
            condition_key = (
                condition.condition
                if isinstance(condition.condition, Condition)
                else condition_str
            )
            message = self.status_messages.get(
                (condition_key, condition.status),
                f"🔄 {condition_str} - {condition.status.value.lower()}",
            )

            progress_parts.append(message)

        return " → ".join(progress_parts)

    def wait_until_done(
        self,
        callback: Callable[..., Any],
        condition: Condition | str = Condition.ALL,
        status: ConditionStatus = ConditionStatus.REACHED,
    ) -> Any:
        """Wait for an async operation to complete with detailed progress tracking.

        Args:
            callback: Function to call repeatedly to check operation status.
            condition: The condition to wait for (default: Condition.ALL for all conditions).
            status: The status to wait for (default: ConditionStatus.REACHED).

        Returns:
            The final response from the callback when the condition is met.

        Raises:
            ViOperationError: If the operation fails.

        """
        with graceful_exit("Waiting operation cancelled by user") as handler:
            with ViProgress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                TimeElapsedColumn(),
            ) as progress:
                task = progress.add_task(description="🔄 Starting process...")

                while True:
                    # Check for keyboard interrupt
                    if handler.exit_now:
                        return None

                    response = callback()
                    resource_conditions: list[ResourceCondition] = (
                        response.status.conditions
                    )

                    progress_chain = self._build_progress_chain(resource_conditions)
                    progress.update(task, description=progress_chain)

                    # Check conditions in a single loop
                    conditions_met = 0
                    target_condition_found = False

                    for resource_condition in resource_conditions:
                        # Check for any failed conditions first
                        if resource_condition.status == ConditionStatus.FAILED_REACH:
                            error_chain = self._build_progress_chain(
                                resource_conditions
                            )
                            raise ViOperationError(f"Process failed at: {error_chain}")

                        # Count conditions that have reached the target status
                        if resource_condition.status == status:
                            conditions_met += 1

                        # Check if specific condition is met (for non-ALL cases)
                        if (
                            condition != Condition.ALL
                            and resource_condition.condition == condition
                            and resource_condition.status == status
                        ):
                            target_condition_found = True

                    # Determine if completion criteria are met
                    completion_met = False
                    if condition == Condition.ALL:
                        # All conditions must reach the target status
                        completion_met = bool(
                            resource_conditions
                        ) and conditions_met == len(resource_conditions)
                    else:
                        # Specific condition must reach the target status
                        completion_met = target_condition_found

                    if completion_met:
                        progress.update(
                            task,
                            description="✅ Process completed successfully!",
                        )
                        # This is to properly render the completion status
                        # in Jupyter notebooks before closing
                        time.sleep(0.5)
                        return response

                    time.sleep(1)
