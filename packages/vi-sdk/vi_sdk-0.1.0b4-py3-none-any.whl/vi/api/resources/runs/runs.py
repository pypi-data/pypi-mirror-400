#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   runs.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK runs module.
"""

from vi.api.pagination import PaginatedResponse
from vi.api.resources.runs import responses
from vi.api.resources.runs.links import RunLinkParser
from vi.api.resources.runs.types import RunListParams
from vi.api.responses import DeletedResource, Pagination
from vi.api.types import PaginationParams
from vi.client.auth import Authentication
from vi.client.http.requester import Requester
from vi.client.rest.resource import RESTResource
from vi.client.validation import validate_id_param, validate_pagination_params


class Run(RESTResource):
    """Run resource for managing training runs and experiments.

    This class provides methods to list, retrieve, and delete training runs.
    Training runs represent individual training experiments with specific
    configurations and datasets. Each run tracks training
    progress and metrics.

    Example:
        ```python
        import vi

        client = vi.Client()
        runs = client.runs

        # List all training runs
        run_list = runs.list()
        for run in run_list.items:
            print(f"Run: {run.id} - Status: {run.status}")
            print(f"  Dataset: {run.dataset_name}")
            print(f"  Accuracy: {run.best_metrics.accuracy:.3f}")

        # Get a specific training run
        run = runs.get(run_id="run_abc123")
        print(f"Training duration: {run.duration}")
        print(f"Final loss: {run.final_loss}")
        ```

    Note:
        Training runs are created through training workflows (Flows) and cannot
        be created directly through this API. Use this resource to monitor,
        retrieve, and manage existing training runs.

    See Also:
        - [Model Guide](../../guide/models.md): Training and managing models
        - [`Flow`](../../api/resources/flows.md): Training workflow resource
        - [`Model`](../../api/resources/models.md): Trained model resource

    """

    _link_parser: RunLinkParser

    def __init__(self, auth: Authentication, requester: Requester):
        """Initialize the Run resource.

        Args:
            auth: Authentication instance containing credentials.
            requester: HTTP requester instance for making API calls.

        """
        super().__init__(auth, requester)
        self._link_parser = RunLinkParser(auth.organization_id)

    def list(
        self, pagination: PaginationParams | dict = PaginationParams()
    ) -> PaginatedResponse[responses.Run]:
        """List all training runs in the organization.

        Retrieves a paginated list of all training runs accessible to the
        authenticated user within their organization. Runs are ordered by
        creation time with the most recent runs appearing first.

        Args:
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a `PaginationParams` object or a dict with pagination settings.
                Defaults to `PaginationParams()` (first page, default page size).

        Returns:
            PaginatedResponse containing Run objects with navigation support.
            Each Run contains training configuration, status, metrics, and metadata.

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViValidationError: If pagination parameters are invalid.
            ViAuthenticationError: If authentication fails.

        Example:
            ```python
            # List all training runs with default pagination
            runs = client.runs.list()

            # Iterate through runs
            for run in runs.items:
                print(f"Run {run.id}:")
                print(f"  Status: {run.status}")
                print(f"  Dataset: {run.dataset_name}")
                print(f"  Started: {run.start_time}")
                print(f"  Duration: {run.duration}")

                # Check if training completed successfully
                if run.status == "completed":
                    print(f"  Best Accuracy: {run.best_metrics.accuracy:.3f}")
                    print(f"  Final Loss: {run.final_loss:.4f}")

            # Iterate through all runs across pages
            for run in runs.all_items():
                print(f"Processing run: {run.id}")

            # Custom pagination
            runs = client.runs.list(pagination={"page_size": 50, "page": 2})

            # Filter runs by status
            completed_runs = [r for r in runs.items if r.status == "completed"]
            print(f"Completed runs: {len(completed_runs)}")

            # Find best performing run
            if completed_runs:
                best_run = max(completed_runs, key=lambda r: r.best_metrics.accuracy)
                print(
                    f"Best run: {best_run.id} (accuracy: {best_run.best_metrics.accuracy:.3f})"
                )
            ```

        Note:
            Training runs include various statuses: "pending", "running", "completed",
            "failed", or "cancelled". Only completed runs have final metrics and
            trained models available for download.

        See Also:
            - `get()`: Retrieve a specific training run
            - `delete()`: Delete a training run
            - `models.list()`: List models from a run

        """
        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        run_params = RunListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(),
            params=run_params.to_query_params(),
            response_type=Pagination[responses.Run],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={"pagination": pagination},
            )

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def get(self, run_id: str) -> responses.Run:
        """Get detailed information about a specific training run.

        Retrieves comprehensive information about a training run including
        configuration, status, metrics, training progress, and metadata.

        Args:
            run_id: The unique identifier of the training run to retrieve.

        Returns:
            Run object containing all training run information including
            configuration, status, metrics, duration, and model checkpoints.

        Raises:
            ViNotFoundError: If the training run doesn't exist.
            ViValidationError: If the run_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Get a specific training run
            run = client.runs.get(run_id="run_abc123")

            print(f"Run ID: {run.id}")
            print(f"Status: {run.status}")
            print(f"Dataset: {run.dataset_name}")
            print(f"Model Architecture: {run.model_architecture}")
            print(f"Started: {run.start_time}")
            print(f"Duration: {run.duration}")

            # Check training configuration
            print(f"Learning Rate: {run.config.learning_rate}")
            print(f"Batch Size: {run.config.batch_size}")
            print(f"Epochs: {run.config.epochs}")

            # Check training results
            if run.status == "completed":
                print(f"Best Accuracy: {run.best_metrics.accuracy:.3f}")
                print(f"Best F1 Score: {run.best_metrics.f1_score:.3f}")
                print(f"Final Loss: {run.final_loss:.4f}")
                print(f"Total Checkpoints: {run.checkpoint_count}")
            elif run.status == "failed":
                print(f"Failure Reason: {run.error_message}")
            elif run.status == "running":
                print(f"Progress: {run.progress:.1f}%")
                print(f"Current Epoch: {run.current_epoch}")
            ```

        Note:
            The available fields in the Run object depend on the training status.
            Completed runs have full metrics and model information, while running
            runs show progress and current metrics.

        See Also:
            - `list()`: List all training runs
            - `delete()`: Delete a training run
            - `models.get()`: Get models from this run

        """
        validate_id_param(run_id, "run_id")

        response = self._requester.get(
            self._link_parser(run_id), response_type=responses.Run
        )

        if isinstance(response, responses.Run):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def delete(self, run_id: str) -> DeletedResource:
        """Delete a training run by ID.

        Permanently removes a training run including all associated data such as
        training logs, metrics, and model checkpoints. This operation cannot be
        undone and will free up storage space used by the run.

        Args:
            run_id: The unique identifier of the training run to delete.

        Returns:
            DeletedResource object confirming the deletion with the run ID
            and deletion status.

        Raises:
            ViNotFoundError: If the training run doesn't exist.
            ViValidationError: If the run_id format is invalid.
            ViPermissionError: If user lacks permission to delete the run.
            ViOperationError: If the deletion fails or API returns unexpected response.

        Example:
            ```python
            # Delete a specific training run
            result = client.runs.delete(run_id="run_abc123")
            print(f"Deleted run: {result.id}")

            # Safe deletion with error handling
            try:
                result = client.runs.delete(run_id="run_abc123")
                print("Training run deleted successfully")
            except ViNotFoundError:
                print("Training run not found or already deleted")
            except ViPermissionError:
                print("Permission denied - cannot delete training run")

            # Delete multiple runs (be careful!)
            runs_to_delete = ["run_abc123", "run_def456", "run_ghi789"]
            for run_id in runs_to_delete:
                try:
                    client.runs.delete(run_id)
                    print(f"Deleted run: {run_id}")
                except Exception as e:
                    print(f"Failed to delete {run_id}: {e}")
            ```

        Warning:
            This operation is permanent and cannot be undone. All training data
            including logs, metrics, model checkpoints, and configuration will
            be permanently deleted from the platform. Consider downloading
            important models before deletion.

        Note:
            Deleting a training run will also delete all associated model
            checkpoints. If you need to preserve trained models, download them
            using the `models.download()` method before deleting the run.

        See Also:
            - `get()`: Verify run exists before deletion
            - `models.download()`: Download models before deletion
            - [Model Guide](../../guide/models.md#deletion): Best practices for run deletion

        """
        validate_id_param(run_id, "run_id")

        response = self._requester.delete(self._link_parser(run_id))

        if isinstance(response, dict) and response.get("data") == "":
            return DeletedResource(id=run_id, deleted=True)

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def help(self) -> None:
        """Display helpful information about using the Run resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on runs
            client.runs.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           Run Resource - Quick Help                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List all training runs:
    runs = client.runs.list()
    for run in runs.items:
        print(f"{run.id}: {run.status}")

  List with custom pagination:
    runs = client.runs.list(pagination={"page_size": 50})

  Get a specific run:
    run = client.runs.get(run_id="run_abc123")
    run.info()  # Show detailed information
    print(f"Status: {run.status}")
    print(f"Duration: {run.duration}")

  Delete a run:
    result = client.runs.delete(run_id="run_abc123")
    print("Run deleted")

  Iterate over all runs:
    for run in client.runs:
        if run.status == "completed":
            print(f"Completed: {run.id}")

  Get models from a run:
    models = client.models.list(run_id_or_link=run.id)

📖 AVAILABLE METHODS:

  • list(pagination=...)  - List all training runs with pagination
  • get(run_id)           - Get a specific training run
  • delete(run_id)        - Delete a training run (permanent!)

💡 TIPS:

  • Runs represent individual training experiments
  • Check run.info() for metrics and configuration
  • Completed runs have final metrics and models
  • Use natural iteration: `for run in client.runs:`
  • Runs are linked to flows and models

📊 RUN STATUSES:

  • pending    - Queued for training
  • running    - Currently training
  • completed  - Training finished successfully
  • failed     - Training encountered errors
  • cancelled  - Training stopped by user

⚠️  WARNING:

  Deleting a run permanently removes all training data including
  logs, metrics, and model checkpoints!

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-runs

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
