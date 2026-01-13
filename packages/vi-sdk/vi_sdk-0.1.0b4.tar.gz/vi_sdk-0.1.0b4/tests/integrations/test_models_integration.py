#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   test_models_integration.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Integration tests for Model API.
"""

# import pytest

# from .conftest import skip_if_no_credentials


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelsList:
#     """Test model listing functionality."""

#     def test_list_models_for_run(self, integration_client, test_run_id):
#         """Test listing all models for a run."""
#         print(f"\n🤖 Listing models for run: {test_run_id}")

#         models = integration_client.models.list(test_run_id)

#         print(f"✅ Found {len(models.items)} model(s)")

#         for i, model in enumerate(models.items[:3], 1):
#             model_id = model.get("model_id", "N/A")
#             checkpoint = model.get("checkpoint", "N/A")
#             print(f"   {i}. Model {model_id[:20]}... (checkpoint: {checkpoint})")

#         assert models is not None
#         assert hasattr(models, "items")

#     def test_list_models_pagination(self, integration_client, test_run_id):
#         """Test model listing with pagination."""
#         print("\n📄 Testing model pagination...")

#         page1 = integration_client.models.list(test_run_id, page_size=5)

#         print(f"✅ Retrieved page with {len(page1.items)} model(s)")

#         assert page1 is not None

#     def test_list_models_iteration(self, integration_client, test_run_id):
#         """Test iterating over all models."""
#         print("\n🔄 Iterating over models...")

#         models = integration_client.models.list(test_run_id)
#         count = 0

#         for model in models:
#             count += 1
#             if count <= 3:
#                 print(f"   Model {count}: {model.get('model_id', 'N/A')[:20]}...")

#         print(f"✅ Iterated over {count} model(s)")

#         assert count >= 0


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelGet:
#     """Test getting individual model information."""

#     def test_get_model_by_id(self, integration_client, test_run_id, test_model_id):
#         """Test getting a model by ID."""
#         print(f"\n🤖 Fetching model: {test_model_id}")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         print("✅ Model retrieved")
#         print(f"   ID: {model.get('model_id', 'N/A')[:20]}...")
#         print(f"   Run ID: {model.get('run_id', 'N/A')[:20]}...")
#         print(f"   Checkpoint: {model.get('checkpoint', 'N/A')}")

#         assert model is not None
#         assert model.get("model_id") == test_model_id

#     def test_model_has_required_fields(
#         self, integration_client, test_run_id, test_model_id
#     ):
#         """Test that model has all required fields."""
#         print("\n📋 Validating model fields...")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         required_fields = ["model_id", "run_id", "organization_id", "created_at"]

#         for field in required_fields:
#             assert field in model, f"Missing required field: {field}"
#             print(f"   ✓ {field}")

#         print("✅ All required fields present")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelCheckpoints:
#     """Test model checkpoint functionality."""

#     def test_list_model_checkpoints(self, integration_client, test_run_id):
#         """Test listing models with different checkpoints."""
#         print(f"\n🔖 Listing model checkpoints for run: {test_run_id}")

#         models = integration_client.models.list(test_run_id)

#         checkpoints = set()
#         for model in models.items:
#             if "checkpoint" in model:
#                 checkpoints.add(model["checkpoint"])

#         print(f"✅ Found {len(checkpoints)} unique checkpoint(s)")

#         for checkpoint in list(checkpoints)[:5]:
#             print(f"   - Checkpoint: {checkpoint}")

#         assert models is not None

#     def test_get_specific_checkpoint(self, integration_client, test_run_id):
#         """Test getting a model with specific checkpoint."""
#         print("\n🔖 Testing checkpoint-specific model retrieval...")

#         # First get list of models to find a checkpoint
#         models = integration_client.models.list(test_run_id)

#         if len(models.items) == 0:
#             pytest.skip("No models available for checkpoint test")

#         first_model = models.items[0]
#         model_id = first_model.get("model_id")
#         checkpoint = first_model.get("checkpoint", "latest")

#         print(f"   Testing model: {model_id[:20]}...")
#         print(f"   Checkpoint: {checkpoint}")

#         # Get the specific model
#         model = integration_client.models.get(test_run_id, model_id)

#         print("✅ Retrieved model with checkpoint")

#         assert model is not None


# @pytest.mark.integration
# @skip_if_no_credentials
# @pytest.mark.slow
# class TestModelDownload:
#     """Test model download functionality."""

#     def test_download_model_metadata(
#         self, integration_client, test_run_id, test_model_id, tmp_path
#     ):
#         """Test initiating model download."""
#         print(f"\n⬇️  Initiating model download...")

#         download_path = tmp_path / "model_download"

#         try:
#             result = integration_client.models.download(
#                 test_run_id, test_model_id, str(download_path), wait_until_done=False
#             )

#             print("✅ Download initiated")
#             print(f"   Download path: {download_path}")

#             assert result is not None

#         except Exception as e:
#             print(f"ℹ️  Model download test skipped: {e}")
#             pytest.skip("Model download not available")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelMetadata:
#     """Test model metadata and metrics."""

#     def test_model_metrics(self, integration_client, test_run_id, test_model_id):
#         """Test model metrics and performance data."""
#         print("\n📊 Checking model metrics...")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         metrics_fields = [
#             "accuracy",
#             "loss",
#             "precision",
#             "recall",
#             "f1_score",
#             "map",
#             "metrics",
#         ]

#         found_metrics = []
#         for field in metrics_fields:
#             if field in model:
#                 found_metrics.append(field)
#                 print(f"   ✓ {field}: {model[field]}")

#         if found_metrics:
#             print(f"✅ Found {len(found_metrics)} metric field(s)")
#         else:
#             print("ℹ️  No explicit metrics found")

#     def test_model_file_info(self, integration_client, test_run_id, test_model_id):
#         """Test model file information."""
#         print("\n📦 Checking model file info...")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         file_fields = ["size", "format", "file_name", "download_url"]

#         for field in file_fields:
#             if field in model:
#                 print(f"   ✓ {field}: {model[field]}")

#         print("✅ File info check complete")

#     def test_model_architecture_info(
#         self, integration_client, test_run_id, test_model_id
#     ):
#         """Test model architecture information."""
#         print("\n🏗️  Checking model architecture info...")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         arch_fields = [
#             "architecture",
#             "model_type",
#             "framework",
#             "backbone",
#             "input_shape",
#         ]

#         found_fields = []
#         for field in arch_fields:
#             if field in model:
#                 found_fields.append(field)
#                 print(f"   ✓ {field}: {model[field]}")

#         if found_fields:
#             print(f"✅ Found {len(found_fields)} architecture field(s)")
#         else:
#             print("ℹ️  No explicit architecture fields found")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelFiltering:
#     """Test model filtering and search."""

#     def test_list_models_by_checkpoint(self, integration_client, test_run_id):
#         """Test filtering models by checkpoint."""
#         print(f"\n🔍 Testing checkpoint filtering...")

#         # Get all models first
#         all_models = integration_client.models.list(test_run_id)

#         if len(all_models.items) == 0:
#             pytest.skip("No models available for filtering test")

#         # Try to filter by checkpoint if supported
#         print(f"✅ Retrieved {len(all_models.items)} model(s)")

#         # Group by checkpoint
#         by_checkpoint = {}
#         for model in all_models.items:
#             checkpoint = model.get("checkpoint", "unknown")
#             by_checkpoint.setdefault(checkpoint, []).append(model)

#         print(f"   Models grouped by {len(by_checkpoint)} checkpoint(s)")

#         for checkpoint, models in list(by_checkpoint.items())[:3]:
#             print(f"   - {checkpoint}: {len(models)} model(s)")


# @pytest.mark.integration
# @skip_if_no_credentials
# class TestModelVersioning:
#     """Test model versioning."""

#     def test_model_version_info(self, integration_client, test_run_id, test_model_id):
#         """Test model version information."""
#         print("\n🔢 Checking model version info...")

#         model = integration_client.models.get(test_run_id, test_model_id)

#         version_fields = ["version", "checkpoint", "epoch", "iteration", "step"]

#         for field in version_fields:
#             if field in model:
#                 print(f"   ✓ {field}: {model[field]}")

#         print("✅ Version info check complete")
