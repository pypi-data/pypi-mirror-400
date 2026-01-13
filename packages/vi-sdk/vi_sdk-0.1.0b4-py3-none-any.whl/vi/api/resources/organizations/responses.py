#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK organizations responses module.
"""

from datetime import datetime

from msgspec import field
from vi.api.responses import User, ViResponse


class OrganizationBilling(ViResponse):
    """Organization billing response.

    Attributes:
        payer: The entity responsible for payment.
        email: Billing contact email address.
        subscriber_id: Unique subscriber identifier.
        ledger: List of billing ledger entries.
        tier: Current billing tier or plan level.

    """

    payer: str
    email: str
    subscriber_id: str
    ledger: list
    tier: str


class OrganizationMetadata(ViResponse):
    """Organization metadata response.

    Attributes:
        create_date: Unix timestamp of when the organization was created.
        is_public: Whether the organization is publicly visible.
        account_manager: Name or ID of the assigned account manager.
        sales_engineer: Name or ID of the assigned sales engineer.

    """

    create_date: int | None = None
    is_public: bool | None = None
    account_manager: str | None = None
    sales_engineer: str | None = None


class OrganizationLockStatus(ViResponse):
    """Organization lock status response.

    Attributes:
        is_locked: Whether the organization is currently locked.
        lockDate: Unix timestamp of when the organization was locked, if applicable.

    """

    is_locked: bool
    lockDate: int | None = None


class Organization(ViResponse):
    """Organization response.

    Attributes:
        name: The organization's display name.
        kind: The type or kind of organization.
        organization_id: Unique organization identifier.
        last_access: Unix timestamp of last access to the organization.
        datasets: List of dataset IDs belonging to this organization.
        billing: Organization billing information and status.
        users: Dictionary mapping user IDs to User objects.
        metadata: Organization metadata including creation date and settings.
        features: Dictionary of enabled features for this organization.
        lock_status: Organization lock status information.
        self_link: API link to this organization resource.
        etag: Entity tag for caching and concurrency control.

    """

    name: str
    kind: str
    organization_id: str = field(name="workspaceId")
    last_access: int
    datasets: list[str]
    billing: OrganizationBilling
    users: dict[str, User]
    metadata: OrganizationMetadata
    features: dict
    lock_status: OrganizationLockStatus
    self_link: str
    etag: str

    def __post_init__(self):
        """Post-initialization processing to sanitize dataset IDs.

        Removes organization ID prefixes from all dataset IDs in the list.
        """
        self.datasets = [
            self._sanitize_dataset_id(dataset) for dataset in self.datasets
        ]

    def info(self) -> None:
        """Display rich information about this organization.

        Shows a formatted summary of the organization including plan, billing,
        users, and datasets in an easy-to-read format.

        Example:
            ```python
            org = client.organizations.get(organization_id="org_abc123")
            org.info()
            ```

        """
        created_str = "N/A"
        if self.metadata.create_date:
            created_str = datetime.fromtimestamp(
                self.metadata.create_date / 1000
            ).strftime("%Y-%m-%d %H:%M:%S")

        last_access_str = datetime.fromtimestamp(self.last_access / 1000).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        info_text = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        Organization Information                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📁 BASIC INFO:
   Name:           {self.name}
   ID:             {self.organization_id}
   Type:           {self.kind}
   Public:         {"Yes" if self.metadata.is_public else "No"}

👥 USERS:
   Total Users:    {len(self.users)}
   User IDs:       {", ".join(list(self.users.keys())[:5])}{" ..." if len(self.users) > 5 else ""}

📊 RESOURCES:
   Datasets:       {len(self.datasets)}

💳 BILLING:
   Plan Tier:      {self.billing.tier}
   Billing Email:  {self.billing.email}

📅 DATES:
   Created:        {created_str}
   Last Access:    {last_access_str}

🔒 STATUS:
   Locked:         {"Yes" if self.lock_status.is_locked else "No"}

👨‍💼 ACCOUNT TEAM:
   Account Manager: {self.metadata.account_manager if self.metadata.account_manager else "Not assigned"}
   Sales Engineer:  {self.metadata.sales_engineer if self.metadata.sales_engineer else "Not assigned"}

💡 QUICK ACTIONS:
   List Datasets:  client.datasets.list()
"""
        print(info_text)
