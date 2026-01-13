#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_runs_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Run API.
"""

# import os

# import pytest

# from .conftest import skip_if_no_credentials


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestRunsList:
#     """Test run listing functionality."""

#     def test_list_runs(self, integration_client):
#         """Test listing all runs."""
#         print("\n🏃 Listing runs...")

#         runs = integration_client.organizations.list_runs()

#         print(f"✅ Found {len(runs.items)} run(s)")

#         for i, run in enumerate(runs.items[:3], 1):
#             print(f"   {i}. {run.name} - {run.status}")

#         assert runs is not None
#         assert hasattr(runs, "items")

#     def test_list_runs_pagination(self, integration_client):
#         """Test run listing with pagination."""
#         print("\n📄 Testing run pagination...")

#         page1 = integration_client.organizations.list_runs(page_size=5)

#         print(f"✅ Retrieved page with {len(page1.items)} run(s)")

#         assert page1 is not None

#     def test_list_runs_iteration(self, integration_client):
#         """Test iterating over all runs."""
#         print("\n🔄 Iterating over runs...")

#         runs = integration_client.organizations.list_runs()
#         count = 0

#         for run in runs:
#             count += 1
#             if count <= 3:
#                 print(
#                     f"   Run {count}: {run.get('name', 'N/A')} ({run.get('status', 'N/A')})"
#                 )

#         print(f"✅ Iterated over {count} run(s)")

#         assert count >= 0


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestRunGet:
#     """Test getting individual run information."""

#     def test_get_run_by_id(self, integration_client, test_run_id):
#         """Test getting a run by ID."""
#         print(f"\n🏃 Fetching run: {test_run_id}")

#         run = integration_client.organizations.get_run(test_run_id)

#         print("✅ Run retrieved")
#         print(f"   Name: {run.get('name', 'N/A')}")
#         print(f"   ID: {run.get('run_id', 'N/A')[:20]}...")
#         print(f"   Status: {run.get('status', 'N/A')}")

#         assert run is not None
#         assert run.get("run_id") == test_run_id

#     def test_run_has_required_fields(self, integration_client, test_run_id):
#         """Test that run has all required fields."""
#         print("\n📋 Validating run fields...")

#         run = integration_client.organizations.get_run(test_run_id)

#         required_fields = ["run_id", "name", "organization_id", "created_at"]

#         for field in required_fields:
#             assert field in run, f"Missing required field: {field}"
#             print(f"   ✓ {field}")

#         print("✅ All required fields present")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestRunStatus:
#     """Test run status and lifecycle."""

#     def test_run_status_field(self, integration_client, test_run_id):
#         """Test that run has proper status."""
#         print("\n📊 Checking run status...")

#         run = integration_client.organizations.get_run(test_run_id)

#         if "status" in run:
#             status = run["status"]
#             print(f"✅ Run status: {status}")

#             # Common statuses
#             valid_statuses = [
#                 "pending",
#                 "running",
#                 "completed",
#                 "failed",
#                 "cancelled",
#                 "queued",
#             ]

#             if status.lower() in valid_statuses:
#                 print(f"   Status is valid: {status}")

#         else:
#             print("ℹ️  No status field in run")

#     def test_run_timestamps(self, integration_client, test_run_id):
#         """Test run timestamp fields."""
#         print("\n⏰ Checking run timestamps...")

#         run = integration_client.organizations.get_run(test_run_id)

#         timestamp_fields = ["created_at", "updated_at", "started_at", "completed_at"]

#         for field in timestamp_fields:
#             if field in run:
#                 print(f"   ✓ {field}: {run[field]}")

#         print("✅ Timestamp check complete")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestRunModels:
#     """Test accessing models through runs."""

#     def test_list_run_models(self, integration_client, test_run_id):
#         """Test listing models for a run."""
#         print(f"\n🤖 Listing models for run: {test_run_id}")

#         models = integration_client.models.list(test_run_id)

#         print(f"✅ Found {len(models.items)} model(s)")

#         for i, model in enumerate(models.items[:3], 1):
#             print(f"   {i}. Model {model.get('model_id', 'N/A')[:20]}...")

#         assert models is not None

#     def test_run_has_models_access(self, integration_client, test_run_id):
#         """Test that run provides access to models."""
#         print("\n🔗 Testing run-models relationship...")

#         # Get run info
#         run = integration_client.organizations.get_run(test_run_id)

#         print("✅ Run retrieved")

#         # Get models for this run
#         models = integration_client.models.list(test_run_id)

#         print(f"✅ Accessed {len(models.items)} model(s) for run")

#         assert models is not None


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestRunConfiguration:
#     """Test run configuration and parameters."""

#     def test_run_configuration(self, integration_client, test_run_id):
#         """Test run configuration structure."""
#         print("\n⚙️  Validating run configuration...")

#         run = integration_client.organizations.get_run(test_run_id)

#         config_fields = ["config", "configuration", "parameters", "settings"]

#         for field in config_fields:
#             if field in run:
#                 print(f"✅ Found {field} field")
#                 config = run[field]
#                 if isinstance(config, dict):
#                     print(f"   Config keys: {list(config.keys())[:5]}")
#                 break
#         else:
#             print("ℹ️  No explicit configuration field found")

#     def test_run_metadata(self, integration_client, test_run_id):
#         """Test run metadata fields."""
#         print("\n📋 Checking run metadata...")

#         run = integration_client.organizations.get_run(test_run_id)

#         metadata_fields = [
#             "dataset_id",
#             "flow_id",
#             "training_time",
#             "epochs",
#             "batch_size",
#         ]

#         found_fields = []
#         for field in metadata_fields:
#             if field in run:
#                 found_fields.append(field)
#                 print(f"   ✓ {field}: {run[field]}")

#         if found_fields:
#             print(f"✅ Found {len(found_fields)} metadata field(s)")
#         else:
#             print("ℹ️  No standard metadata fields found")


# @pytest.mark.integration
# @skip_if_no_credentials
# @pytest.mark.skipif(
#     not os.getenv("ALLOW_RUN_DELETE"),
#     reason="Set ALLOW_RUN_DELETE=1 to test run deletion",
# )
# class TestRunDeleteIntegration:
#     """Integration tests for run delete operations (requires opt-in)."""

#     def test_delete_run_protection(self):
#         """Test that run deletion is properly protected."""
#         print("\n⚠️  Run deletion requires explicit opt-in")
#         print("   Set ALLOW_RUN_DELETE=1 to enable deletion tests")
#         print("✅ Deletion protection verified")

#     def test_delete_run_error_invalid_id(self, integration_client):
#         """Test that deleting non-existent run raises appropriate error."""
#         print("\n❌ Testing delete with invalid run ID...")

#         with pytest.raises(Exception):  # Could be ViError or other error types
#             integration_client.runs.delete(
#                 "definitely_nonexistent_run_12345"
#             )

#         print("✅ Correctly raised error for invalid run")
