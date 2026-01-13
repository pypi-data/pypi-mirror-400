#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   flows.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK flows module.
"""

from vi.api.pagination import PaginatedResponse
from vi.api.resources.flows import responses
from vi.api.resources.flows.links import FlowLinkParser
from vi.api.resources.flows.types import FlowListParams
from vi.api.responses import DeletedResource, Pagination
from vi.api.types import PaginationParams
from vi.client.auth import Authentication
from vi.client.http.requester import Requester
from vi.client.rest.resource import RESTResource
from vi.client.validation import validate_id_param, validate_pagination_params


class Flow(RESTResource):
    """Flow resource for managing training workflows and pipelines.

    This class provides methods to list, retrieve, and delete training flows.
    Flows represent training workflows that define how models are trained,
    including dataset configuration, model architecture, hyperparameters,
    and training schedules. Flows can be executed to create training runs.

    Example:
        ```python
        import vi

        client = vi.Client()
        flows = client.flows

        # List all training flows
        flow_list = flows.list()
        for flow in flow_list.items:
            print(f"Flow: {flow.id} - {flow.name}")
            print(f"  Dataset: {flow.dataset_name}")
            print(f"  Architecture: {flow.model_architecture}")
            print(f"  Status: {flow.status}")

        # Get a specific training flow
        flow = flows.get(flow_id="flow_abc123")
        print(f"Flow Name: {flow.name}")
        print(f"Description: {flow.description}")
        print(f"Training Config: {flow.training_config}")

        # Check flow execution history
        if hasattr(flow, "runs"):
            print(f"Total Runs: {len(flow.runs)}")
            for run in flow.runs:
                print(f"  Run {run.id}: {run.status}")
        ```

    Note:
        Flows define training configurations but don't execute training directly.
        Use the Flow execution API or UI to start training runs from flows.
        This resource is primarily for managing and inspecting flow definitions.

    See Also:
        - [Model Guide](../../guide/models.md): Training models with flows
        - [`Run`](../../api/resources/runs.md): Training run resource created from flows
        - [`Model`](../../api/resources/models.md): Models produced by flow executions

    """

    _link_parser: FlowLinkParser

    def __init__(self, auth: Authentication, requester: Requester):
        """Initialize the Flow resource.

        Args:
            auth: Authentication instance containing credentials.
            requester: HTTP requester instance for making API calls.

        """
        super().__init__(auth, requester)
        self._link_parser = FlowLinkParser(auth.organization_id)

    def list(
        self, pagination: PaginationParams | dict = PaginationParams()
    ) -> PaginatedResponse[responses.Flow]:
        """List all training flows in the organization.

        Retrieves a paginated list of all training flows accessible to the
        authenticated user within their organization. Flows are ordered by
        creation time with the most recent flows appearing first.

        Args:
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a PaginationParams object or dict. Defaults to first page
                with default page size.

        Returns:
            PaginatedResponse containing Flow objects with navigation support.
            Each Flow contains workflow configuration, status, and execution history.

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViValidationError: If pagination parameters are invalid.
            ViAuthenticationError: If authentication fails.

        Example:
            ```python
            # List all training flows
            flows = client.flows.list()

            # Iterate through flows
            for flow in flows.items:
                print(f"Flow {flow.id}: {flow.name}")
                print(f"  Dataset: {flow.dataset_name}")
                print(f"  Architecture: {flow.model_architecture}")
                print(f"  Status: {flow.status}")
                print(f"  Created: {flow.created_at}")

                # Check training configuration
                if hasattr(flow, "training_config"):
                    config = flow.training_config
                    print(f"  Learning Rate: {config.learning_rate}")
                    print(f"  Batch Size: {config.batch_size}")
                    print(f"  Epochs: {config.epochs}")

            # Iterate through all flows across pages
            for flow in flows.all_items():
                print(f"Processing flow: {flow.name}")

            # Custom pagination
            flows = client.flows.list(pagination={"page_size": 50, "page": 2})

            # Filter flows by status
            active_flows = [f for f in flows.items if f.status == "active"]
            print(f"Active flows: {len(active_flows)}")
            ```

        Note:
            Training flows can have various statuses: "draft", "active", "archived",
            or "disabled". Only active flows can be executed to create training runs.

        See Also:
            - `get()`: Retrieve a specific training flow
            - `delete()`: Delete a training flow
            - `Run.list()`: List training runs created from flows

        """
        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        flow_params = FlowListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(),
            params=flow_params.to_query_params(),
            response_type=Pagination[responses.Flow],
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

    def get(self, flow_id: str) -> responses.Flow:
        """Get detailed information about a specific training flow.

        Retrieves comprehensive information about a training flow including
        configuration, dataset settings, model architecture, hyperparameters,
        and execution history.

        Args:
            flow_id: The unique identifier of the training flow to retrieve.

        Returns:
            Flow object containing all flow information including configuration,
            status, training parameters, and execution history.

        Raises:
            ViNotFoundError: If the training flow doesn't exist.
            ViValidationError: If the flow_id format is invalid.
            ViOperationError: If the API returns an unexpected response format.

        Example:
            ```python
            # Get a specific training flow
            flow = client.flows.get(flow_id="flow_abc123")

            print(f"Flow ID: {flow.id}")
            print(f"Name: {flow.name}")
            print(f"Description: {flow.description}")
            print(f"Status: {flow.status}")
            print(f"Created: {flow.created_at}")
            print(f"Updated: {flow.updated_at}")

            # Check dataset configuration
            print(f"Dataset: {flow.dataset_name}")
            print(f"Dataset ID: {flow.dataset_id}")

            # Check model configuration
            print(f"Architecture: {flow.model_architecture}")
            print(f"Model Type: {flow.model_type}")

            # Check training configuration
            if hasattr(flow, "training_config"):
                config = flow.training_config
                print(f"Learning Rate: {config.learning_rate}")
                print(f"Batch Size: {config.batch_size}")
                print(f"Epochs: {config.epochs}")
                print(f"Optimizer: {config.optimizer}")

            # Check execution history
            if hasattr(flow, "runs") and flow.runs:
                print(f"Total Runs: {len(flow.runs)}")
                latest_run = flow.runs[-1]
                print(f"Latest Run: {latest_run.id} ({latest_run.status})")
            else:
                print("No training runs executed yet")
            ```

        Note:
            The Flow object contains the complete workflow definition but doesn't
            include real-time training progress. Use the Run resource to monitor
            active training sessions created from this flow.

        See Also:
            - `list()`: List all training flows
            - `delete()`: Delete a training flow
            - `Run.get()`: Get training runs from this flow

        """
        validate_id_param(flow_id, "flow_id")

        response = self._requester.get(
            self._link_parser(flow_id), response_type=responses.Flow
        )

        if isinstance(response, responses.Flow):
            return response

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def delete(self, flow_id: str) -> DeletedResource:
        """Delete a training flow by ID.

        Permanently removes a training flow including its configuration and
        metadata. This operation cannot be undone. Note that deleting a flow
        does not delete the training runs that were created from it.

        Args:
            flow_id: The unique identifier of the training flow to delete.

        Returns:
            DeletedResource object confirming the deletion with the flow ID
            and deletion status.

        Raises:
            ViNotFoundError: If the training flow doesn't exist.
            ViValidationError: If the flow_id format is invalid.
            ViPermissionError: If user lacks permission to delete the flow.
            ViOperationError: If the deletion fails or API returns unexpected response.

        Example:
            ```python
            # Delete a specific training flow
            result = client.flows.delete(flow_id="flow_abc123")
            print(f"Deleted flow: {result.id}")

            # Safe deletion with error handling
            try:
                result = client.flows.delete(flow_id="flow_abc123")
                print("Training flow deleted successfully")
            except ViNotFoundError:
                print("Training flow not found or already deleted")
            except ViPermissionError:
                print("Permission denied - cannot delete training flow")

            # Delete multiple flows (be careful!)
            flows_to_delete = ["flow_abc123", "flow_def456", "flow_ghi789"]
            for flow_id in flows_to_delete:
                try:
                    client.flows.delete(flow_id)
                    print(f"Deleted flow: {flow_id}")
                except Exception as e:
                    print(f"Failed to delete {flow_id}: {e}")
            ```

        Warning:
            This operation is permanent and cannot be undone. The flow
            configuration and all associated metadata will be permanently
            deleted from the platform. However, training runs and models
            created from this flow will remain available.

        Note:
            Deleting a flow does not affect training runs or models that were
            created from it. Those resources remain available independently.
            Only the flow definition and configuration are removed.

        See Also:
            - `get()`: Verify flow exists before deletion
            - `Run.list()`: Check for training runs created from this flow
            - [Model Guide](../../guide/models.md#deletion): Best practices for flow deletion

        """
        validate_id_param(flow_id, "flow_id")

        response = self._requester.delete(self._link_parser(flow_id))

        if isinstance(response, dict) and response.get("data") == "":
            return DeletedResource(id=flow_id, deleted=True)

        raise ValueError(f"Invalid response {response} with type {type(response)}")

    def help(self) -> None:
        """Display helpful information about using the Flow resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on flows
            client.flows.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           Flow Resource - Quick Help                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List all training flows:
    flows = client.flows.list()
    for flow in flows.items:
        print(f"{flow.id}: {flow.name}")

  Get a specific flow:
    flow = client.flows.get(flow_id="flow_abc123")
    flow.info()  # Show detailed information
    print(f"Name: {flow.name}")
    print(f"Dataset: {flow.dataset_name}")

  Delete a flow:
    result = client.flows.delete(flow_id="flow_abc123")
    print("Flow deleted")

  Iterate over all flows:
    for flow in client.flows:
        if flow.status == "active":
            print(f"Active flow: {flow.name}")

  Get runs from a flow:
    runs = client.runs.list()
    flow_runs = [r for r in runs.items if r.flow_id == flow.id]

📖 AVAILABLE METHODS:

  • list(pagination=...)  - List all training flows
  • get(flow_id)          - Get a specific training flow
  • delete(flow_id)       - Delete a training flow

💡 TIPS:

  • Flows define training configurations
  • Check flow.info() for configuration details
  • Active flows can be executed to create runs
  • Use natural iteration: `for flow in client.flows:`
  • Deleting a flow doesn't delete its runs/models

🔄 FLOW WORKFLOW:

  1. Create flow (via UI/API)
  2. Configure training parameters
  3. Execute flow → Creates training run
  4. Run trains model
  5. Download trained model

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-flows

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
