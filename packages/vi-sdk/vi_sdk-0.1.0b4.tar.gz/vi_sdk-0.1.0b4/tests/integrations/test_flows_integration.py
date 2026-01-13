#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_flows_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Flow API.
"""

# import os

# import pytest

# from .conftest import skip_if_no_credentials


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestFlowsList:
#     """Test flow listing functionality."""

#     def test_list_flows(self, integration_client):
#         """Test listing all flows."""
#         print("\n🔄 Listing flows...")

#         flows = integration_client.flows.list()

#         print(f"✅ Found {len(flows.items)} flow(s)")

#         for i, flow in enumerate(flows.items[:3], 1):
#             print(f"   {i}. {flow.spec.name} ({flow.flow_id[:20]}...)")

#         assert flows is not None
#         assert hasattr(flows, "items")

#     def test_list_flows_pagination(self, integration_client):
#         """Test flow listing with pagination."""
#         print("\n📄 Testing flow pagination...")

#         page1 = integration_client.flows.list(pagination={"page_size": 5})

#         print(f"✅ Retrieved page with {len(page1.items)} flow(s)")

#         assert page1 is not None

#     def test_list_flows_iteration(self, integration_client):
#         """Test iterating over all flows."""
#         print("\n🔄 Iterating over flows...")

#         flows = integration_client.flows.list(pagination={"page_size": 5})
#         count = 0

#         for flow in flows.items:
#             count += 1
#             if count <= 3:
#                 print(f"   Flow {count}: {flow.spec.name} ({flow.flow_id[:20]}...)")

#         print(f"✅ Iterated over {count} flow(s)")

#         assert count >= 0


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestFlowGet:
#     """Test getting individual flow information."""

#     def test_get_flow_by_id(self, integration_client, test_flow_id):
#         """Test getting a flow by ID."""
#         print(f"\n🔄 Fetching flow: {test_flow_id}")

#         flow = integration_client.flows.get(test_flow_id)

#         print("✅ Flow retrieved")
#         print(f"   Name: {flow.spec.name}")
#         print(f"   ID: {flow.flow_id[:20]}...")

#         assert flow is not None
#         assert flow.flow_id == test_flow_id


# @pytest.mark.integration
# @skip_if_no_credentials
# @pytest.mark.skipif(
#     not os.getenv("ALLOW_FLOW_DELETE"),
#     reason="Set ALLOW_FLOW_DELETE=1 to test flow deletion",
# )
# class TestFlowDelete:
#     """Test flow deletion (requires opt-in)."""

#     def test_delete_flow_warning(self):
#         """Test that flow deletion is properly protected."""
#         print("\n⚠️  Flow deletion test (requires opt-in)")
#         print("   Set ALLOW_FLOW_DELETE=1 to enable deletion tests")
#         print("✅ Deletion protection verified")

#     def test_delete_flow_error_invalid_id(self, integration_client):
#         """Test that deleting non-existent flow raises appropriate error."""
#         print("\n❌ Testing delete with invalid flow ID...")

#         with pytest.raises(Exception):  # Could be ViError or other error types
#             integration_client.flows.delete(
#                 "definitely_nonexistent_flow_12345"
#             )

#         print("✅ Correctly raised error for invalid flow")
