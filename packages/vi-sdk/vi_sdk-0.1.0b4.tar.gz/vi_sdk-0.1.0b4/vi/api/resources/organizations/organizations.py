#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   organizations.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK organizations module.
"""

from vi.api.pagination import PaginatedResponse
from vi.api.resources.organizations import responses
from vi.api.resources.organizations.links import OrganizationLinkParser
from vi.api.resources.organizations.types import OrganizationListParams
from vi.api.responses import Pagination
from vi.api.types import PaginationParams
from vi.client.auth import Authentication
from vi.client.errors import ViOperationError
from vi.client.http.requester import Requester
from vi.client.rest.resource import RESTResource
from vi.client.validation import validate_pagination_params


class Organization(RESTResource):
    """Organization resource for managing organization-level operations.

    This class provides methods to access organization information.

    Example:
        ```python
        import vi

        client = vi.Client()
        org = client.organizations

        # Get organization information
        info = org.info()
        print(f"Organization: {info.name}")
        print(f"ID: {info.id}")
        print(f"Plan: {info.plan}")
        ```

    See Also:
        - [Getting Started](../../getting-started/quickstart.md): Initial setup and organization access
        - [`Dataset`](../../api/resources/datasets.md): Dataset management within organization
        - [`Flow`](../../api/resources/flows.md): Training workflow management
        - [`Run`](../../api/resources/runs.md): Training run management

    """

    _link_parser: OrganizationLinkParser

    def __init__(self, auth: Authentication, requester: Requester):
        """Initialize the Organization resource.

        Args:
            auth: Authentication instance containing organization credentials.
            requester: HTTP requester instance for making API calls.

        """
        self._link_parser = OrganizationLinkParser()
        super().__init__(auth, requester)

    def list(
        self, pagination: PaginationParams | dict = PaginationParams()
    ) -> PaginatedResponse[responses.Organization]:
        """List all organizations accessible to the authenticated user.

        Retrieves a paginated list of all organizations that the authenticated
        user has access to. This includes organizations where the user is a
        member, admin, or has been granted specific permissions.

        Args:
            pagination: Pagination parameters for controlling page size and offsets.
                Can be a PaginationParams object or dict. Defaults to first page
                with default page size.

        Returns:
            PaginatedResponse containing Organization objects with navigation support.
            Each Organization contains basic information like name, ID, and plan details.

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViValidationError: If pagination parameters are invalid.
            ViAuthenticationError: If authentication fails.

        Example:
            ```python
            # List all accessible organizations
            orgs = client.organizations.list()

            # Iterate through organizations
            for org in orgs.items:
                print(f"Organization: {org.name}")
                print(f"  ID: {org.id}")
                print(f"  Plan: {org.plan}")
                print(f"  Members: {org.member_count}")
                print(f"  Created: {org.created_at}")

            # Iterate through all organizations across pages
            for org in orgs.all_items():
                print(f"Processing organization: {org.name}")

            # Custom pagination
            orgs = client.organizations.list(pagination={"page_size": 10, "page": 1})

            # Find specific organization
            target_org = None
            for org in orgs.all_items():
                if org.name == "My Company":
                    target_org = org
                    break

            if target_org:
                print(f"Found organization: {target_org.id}")
            ```

        Note:
            Most users will only have access to one organization (their own),
            but enterprise users or consultants may have access to multiple
            organizations. The current organization is determined by the
            authentication credentials.

        See Also:
            - `info()`: Get detailed information about current organization
            - `id`: Get the current organization ID

        """
        if isinstance(pagination, dict):
            validate_pagination_params(**pagination)
            pagination = PaginationParams(**pagination)

        organization_params = OrganizationListParams(pagination=pagination)

        response = self._requester.get(
            self._link_parser(),
            params=organization_params.to_query_params(),
            response_type=Pagination[responses.Organization],
        )

        if isinstance(response, Pagination):
            return PaginatedResponse(
                items=response.items,
                next_page=response.next_page,
                prev_page=response.prev_page,
                list_method=self.list,
                method_kwargs={"pagination": pagination},
            )

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def get(self) -> responses.Organization:
        """Get detailed information about the current organization.

        Retrieves comprehensive information about the organization associated with
        the current authentication credentials. This includes the organization's
        name, ID, plan details, member count, storage usage, and other metadata.

        The current organization is determined by the `organization_id` specified
        during authentication. This method is useful for verifying access, checking
        plan limits, or retrieving organization-specific configuration before
        performing other operations.

        Returns:
            Organization object containing complete information about the current
            organization, including:
            - Basic info: name, ID, description
            - Plan details: plan type, feature limits
            - Statistics: member count, dataset count, project count
            - Usage: storage used, API quota
            - Metadata: creation date, last updated

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViAuthenticationError: If authentication credentials are invalid or expired.
            ViNotFoundError: If the organization doesn't exist or access is denied.

        Example:
            ```python
            import vi

            # Initialize client with credentials
            client = vi.Client(
                secret_key="your_secret_key", organization_id="org_abc123"
            )

            # Get current organization information
            org = client.organizations.get()
            print(f"Organization: {org.name}")
            print(f"ID: {org.id}")
            print(f"Plan: {org.plan}")
            print(f"Members: {org.member_count}")

            # Check storage usage
            if hasattr(org, "storage_used"):
                print(f"Storage: {org.storage_used / (1024**3):.2f} GB")

            # Verify organization before operations
            if org.plan == "enterprise":
                # Perform enterprise-specific operations
                datasets = client.datasets.list()
            ```

        Note:
            This method requires valid authentication credentials. The organization
            returned is determined by the `organization_id` in your authentication
            context. If you have access to multiple organizations, use `list()` to
            see all accessible organizations and their IDs.

        See Also:
            - `list()`: List all accessible organizations
            - `info()`: Display formatted organization information in console
            - [Getting Started](../../getting-started/authentication.md): Authentication setup

        """
        response = self._requester.get(
            self._link_parser(self._auth.organization_id),
            response_type=responses.Organization,
        )

        if isinstance(response, responses.Organization):
            return response

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def info(self) -> None:
        """Display detailed information about the current organization.

        This method makes an API call to retrieve information about the organization
        associated with the current authentication credentials. If successful, it
        displays a formatted summary of the organization's settings, plan, statistics,
        usage, and member information for easy inspection.

        Raises:
            ViOperationError: If the API returns an unexpected response format.
            ViAuthenticationError: If authentication fails.
            ViNotFoundError: If the organization doesn't exist or access is denied.

        Behavior:
            Prints a formatted summary of the organization's information to the console.
            This is intended for interactive/data exploration usage.

        Example:
            ```python
            # Print formatted info for the current organization
            client.organizations.info()
            ```

        Note:
            This method prints the organization information, rather than returning an object.
            To access a specific field programmatically, use the lower-level API:

                org = client.organizations.get(organization_id="org_abc123")
                print(org.billing.tier)
                print(org.billing.email)
                print(org.billing.payer)

        See Also:
            - `list()`: List all accessible organizations.
            - `get(org_id)`: Retrieve organization object (for property access).
            - [Getting Started](../../getting-started/quickstart.md): Organization setup.

        """
        response = self._requester.get(
            self._link_parser(self._auth.organization_id),
            response_type=responses.Organization,
        )

        if isinstance(response, responses.Organization):
            response.info()
            return

        raise ViOperationError(
            f"Invalid response {response} with type {type(response)}"
        )

    def help(self) -> None:
        """Display helpful information about using the Organization resource.

        Shows common usage patterns, available methods, and quick examples
        to help users get started quickly.

        Example:
            ```python
            # Get help on organizations
            client.organizations.help()
            ```

        """
        help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      Organization Resource - Quick Help                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 COMMON OPERATIONS:

  List all accessible organizations:
    orgs = client.organizations.list()
    for org in orgs.items:
        print(f"{org.name}: {org.id}")

  Get current organization info:
    org = client.organizations.info()
    org.info()  # Show detailed information
    print(f"Plan: {org.plan}")
    print(f"Members: {org.member_count}")

  Iterate over all organizations:
    for org in client.organizations:
        print(f"Organization: {org.name}")

📖 AVAILABLE METHODS:

  • list(pagination=...)  - List all accessible organizations
  • info()                - Get current organization information

💡 TIPS:

  • Most users have access to one organization
  • Current org is set via authentication credentials
  • Check org.info() for detailed inspection
  • Organization contains plan limits and usage stats
  • Use natural iteration: `for org in client.organizations:`

📊 ORGANIZATION INFO:

  • Plan type and limits
  • Storage used vs available
  • Member count
  • Dataset count
  • Creation and update dates

📚 Documentation: https://vi.developers.datature.com/docs/vi-sdk-organizations

Need more help? Visit https://vi.developers.datature.com/docs/vi-sdk or contact support@datature.io
"""
        print(help_text)
