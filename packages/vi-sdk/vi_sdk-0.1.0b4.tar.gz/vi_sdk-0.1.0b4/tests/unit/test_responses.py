#!/usr/bin/env python3
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_responses.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Tests for API response types and structures.
"""

import pytest
from vi.api.responses import (
    Condition,
    ConditionStatus,
    DeletedResource,
    Pagination,
    ResourceCondition,
    ResourceMetadata,
    User,
    ViResponse,
)


@pytest.mark.unit
@pytest.mark.responses
class TestViResponse:
    """Test ViResponse base class."""

    def test_response_creation(self) -> None:
        """Test creating a ViResponse instance."""

        class TestResponse(ViResponse):
            """Test response structure."""

            test_field: str

        response = TestResponse(test_field="value")
        assert response.test_field == "value"

    def test_sanitize_dataset_id_with_prefix(self) -> None:
        """Test sanitizing dataset ID with organization prefix."""
        result = ViResponse._sanitize_dataset_id("org123_dataset456")
        assert result == "dataset456"

    def test_sanitize_dataset_id_without_prefix(self) -> None:
        """Test sanitizing dataset ID without organization prefix."""
        result = ViResponse._sanitize_dataset_id("dataset456")
        assert result == "dataset456"

    def test_sanitize_dataset_id_multiple_underscores(self) -> None:
        """Test sanitizing dataset ID with multiple underscores."""
        result = ViResponse._sanitize_dataset_id("org_123_dataset_456")
        assert result == "456"

    def test_sanitize_dataset_id_empty(self) -> None:
        """Test sanitizing empty dataset ID."""
        result = ViResponse._sanitize_dataset_id("")
        assert result == ""


@pytest.mark.unit
@pytest.mark.responses
class TestPagination:
    """Test Pagination response structure."""

    def test_pagination_basic(self) -> None:
        """Test basic pagination structure."""
        items = [{"id": "1"}, {"id": "2"}]
        pagination = Pagination(items=items)

        assert pagination.items == items
        assert pagination.next_page is None
        assert pagination.prev_page is None

    def test_pagination_with_links(self) -> None:
        """Test pagination with next/prev links."""
        items = [{"id": "1"}]
        pagination = Pagination(
            items=items, next_page="next_token", prev_page="prev_token"
        )

        assert pagination.next_page == "next_token"
        assert pagination.prev_page == "prev_token"

    def test_pagination_empty_items(self) -> None:
        """Test pagination with empty items."""
        pagination = Pagination(items=[])
        assert pagination.items == []

    def test_pagination_with_typed_items(self) -> None:
        """Test pagination with typed items."""

        class Item(ViResponse):
            """Test item type."""

            id: str
            name: str

        item = Item(id="1", name="Test")
        pagination: Pagination[Item] = Pagination(items=[item])

        assert len(pagination.items) == 1
        assert pagination.items[0].id == "1"
        assert pagination.items[0].name == "Test"


@pytest.mark.unit
@pytest.mark.responses
class TestCondition:
    """Test Condition enum."""

    def test_condition_values(self) -> None:
        """Test Condition enum values."""
        assert Condition.FINISHED.value == "Finished"
        assert Condition.STARTED.value == "Started"
        assert Condition.ALL.value == "All"

    def test_condition_missing_value(self) -> None:
        """Test _missing_ method for unknown values."""
        # Should create a new enum member for unknown values
        new_condition = Condition._missing_("InProgress")
        assert new_condition.value == "InProgress"

    def test_pascal_to_snake_conversion(self) -> None:
        """Test PascalCase to snake_case conversion."""
        assert Condition._pascal_to_snake("Finished") == "Finished"
        assert Condition._pascal_to_snake("InProgress") == "In_Progress"
        assert Condition._pascal_to_snake("TestCaseExample") == "Test_Case_Example"
        assert Condition._pascal_to_snake("HTTPError") == "HTTP_Error"


@pytest.mark.unit
@pytest.mark.responses
class TestConditionStatus:
    """Test ConditionStatus enum."""

    def test_condition_status_values(self) -> None:
        """Test ConditionStatus enum values."""
        assert ConditionStatus.WAITING.value == "Waiting"
        assert ConditionStatus.REACHED.value == "Reached"
        assert ConditionStatus.FAILED_REACH.value == "FailedReach"


@pytest.mark.unit
@pytest.mark.responses
class TestResourceCondition:
    """Test ResourceCondition response."""

    def test_resource_condition_basic(self) -> None:
        """Test basic resource condition."""
        condition = ResourceCondition(
            condition=Condition.FINISHED,
            status=ConditionStatus.REACHED,
            last_transition_time=1234567890,
        )

        assert condition.condition == Condition.FINISHED
        assert condition.status == ConditionStatus.REACHED
        assert condition.last_transition_time == 1234567890
        assert condition.reason is None
        assert condition.message is None

    def test_resource_condition_with_reason_and_message(self) -> None:
        """Test resource condition with reason and message."""
        condition = ResourceCondition(
            condition=Condition.STARTED,
            status=ConditionStatus.WAITING,
            last_transition_time=1234567890,
            reason="ProcessStarted",
            message="Process has started successfully",
        )

        assert condition.reason == "ProcessStarted"
        assert condition.message == "Process has started successfully"

    def test_resource_condition_failed_reach(self) -> None:
        """Test resource condition with failed status."""
        condition = ResourceCondition(
            condition=Condition.FINISHED,
            status=ConditionStatus.FAILED_REACH,
            last_transition_time=1234567890,
            reason="TimeoutError",
            message="Operation timed out",
        )

        assert condition.status == ConditionStatus.FAILED_REACH
        assert condition.reason == "TimeoutError"


@pytest.mark.unit
@pytest.mark.responses
class TestResourceMetadata:
    """Test ResourceMetadata response."""

    def test_resource_metadata_basic(self) -> None:
        """Test basic resource metadata."""
        metadata = ResourceMetadata(
            time_created=1234567890,
            last_updated=1234567900,
            generation=1,
            attributes={"key": "value"},
        )

        assert metadata.time_created == 1234567890
        assert metadata.last_updated == 1234567900
        assert metadata.generation == 1
        assert metadata.attributes == {"key": "value"}

    def test_resource_metadata_empty_attributes(self) -> None:
        """Test resource metadata with empty attributes."""
        metadata = ResourceMetadata(
            time_created=1234567890,
            last_updated=1234567900,
            generation=1,
            attributes={},
        )

        assert metadata.attributes == {}

    def test_resource_metadata_multiple_attributes(self) -> None:
        """Test resource metadata with multiple attributes."""
        attrs = {"env": "production", "region": "us-west-1", "version": "1.0.0"}
        metadata = ResourceMetadata(
            time_created=1234567890,
            last_updated=1234567900,
            generation=2,
            attributes=attrs,
        )

        assert len(metadata.attributes) == 3
        assert metadata.attributes["env"] == "production"


@pytest.mark.unit
@pytest.mark.responses
class TestUser:
    """Test User response."""

    def test_user_basic(self) -> None:
        """Test basic user response."""
        user = User(workspace_role="admin", datasets={"dataset1": "owner"})

        assert user.workspace_role == "admin"
        assert user.datasets == {"dataset1": "owner"}

    def test_user_sanitizes_dataset_ids(self) -> None:
        """Test that User post_init sanitizes dataset IDs."""
        # User should sanitize dataset IDs in __post_init__
        user = User(
            workspace_role="viewer",
            datasets={"org123_dataset1": "viewer", "org123_dataset2": "editor"},
        )

        # Dataset IDs should be sanitized
        assert "dataset1" in user.datasets
        assert "dataset2" in user.datasets
        assert user.datasets["dataset1"] == "viewer"
        assert user.datasets["dataset2"] == "editor"

    def test_user_multiple_roles(self) -> None:
        """Test user with multiple dataset roles."""
        datasets = {
            "org_ds1": "owner",
            "org_ds2": "editor",
            "org_ds3": "viewer",
        }
        user = User(workspace_role="admin", datasets=datasets)

        assert "ds1" in user.datasets
        assert "ds2" in user.datasets
        assert "ds3" in user.datasets

    def test_user_empty_datasets(self) -> None:
        """Test user with no datasets."""
        user = User(workspace_role="viewer", datasets={})
        assert user.datasets == {}

    def test_user_dataset_without_prefix(self) -> None:
        """Test user with dataset IDs without organization prefix."""
        user = User(
            workspace_role="admin", datasets={"dataset1": "owner", "dataset2": "editor"}
        )

        assert user.datasets["dataset1"] == "owner"
        assert user.datasets["dataset2"] == "editor"


@pytest.mark.unit
@pytest.mark.responses
class TestDeletedResource:
    """Test DeletedResource response."""

    def test_deleted_resource_basic(self) -> None:
        """Test basic deleted resource."""
        deleted = DeletedResource(id="resource_123")

        assert deleted.id == "resource_123"
        assert deleted.deleted is True

    def test_deleted_resource_explicit_false(self) -> None:
        """Test deleted resource with explicit deleted=False."""
        deleted = DeletedResource(id="resource_456", deleted=False)

        assert deleted.id == "resource_456"
        assert deleted.deleted is False

    def test_deleted_resource_various_ids(self) -> None:
        """Test deleted resource with various ID formats."""
        # Dataset ID
        deleted = DeletedResource(id="dataset_123")
        assert deleted.id == "dataset_123"

        # Asset ID
        deleted = DeletedResource(id="asset_abc")
        assert deleted.id == "asset_abc"

        # Run ID
        deleted = DeletedResource(id="run_xyz")
        assert deleted.id == "run_xyz"


@pytest.mark.unit
@pytest.mark.responses
class TestResponsesEdgeCases:
    """Test edge cases for response structures."""

    def test_pagination_with_null_pages(self) -> None:
        """Test pagination with explicitly None page links."""
        pagination = Pagination(items=[{"id": "1"}], next_page=None, prev_page=None)

        assert pagination.next_page is None
        assert pagination.prev_page is None

    def test_resource_metadata_generation_increment(self) -> None:
        """Test resource metadata with incremented generation."""
        metadata1 = ResourceMetadata(
            time_created=1000, last_updated=1000, generation=1, attributes={}
        )
        metadata2 = ResourceMetadata(
            time_created=1000, last_updated=2000, generation=2, attributes={}
        )

        assert metadata2.generation > metadata1.generation
        assert metadata2.last_updated > metadata1.last_updated

    def test_condition_enum_case_sensitivity(self) -> None:
        """Test Condition enum with different cases."""
        # Standard values
        assert Condition.FINISHED.value == "Finished"

        # _missing_ should handle new values
        new_val = Condition._missing_("finished")
        assert new_val.value == "finished"

    def test_user_mixed_dataset_id_formats(self) -> None:
        """Test User with mixed dataset ID formats."""
        user = User(
            workspace_role="admin",
            datasets={
                "org1_dataset1": "owner",  # With prefix
                "dataset2": "editor",  # Without prefix
                "org2_dataset_with_underscores": "viewer",  # Multiple underscores
            },
        )

        assert "dataset1" in user.datasets
        assert "dataset2" in user.datasets
        # For multiple underscores, takes last part
        assert "underscores" in user.datasets

    def test_resource_condition_zero_timestamp(self) -> None:
        """Test resource condition with zero timestamp."""
        condition = ResourceCondition(
            condition=Condition.STARTED,
            status=ConditionStatus.WAITING,
            last_transition_time=0,
        )

        assert condition.last_transition_time == 0

    def test_deleted_resource_default_deleted_value(self) -> None:
        """Test that DeletedResource has deleted=True by default."""
        # When not specified, deleted should default to True
        deleted = DeletedResource(id="test_id")
        assert deleted.deleted is True
