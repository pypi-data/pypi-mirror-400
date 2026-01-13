#!/usr/bin/env python
# -*-coding:utf-8 -*-

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   03_dataset_loader_training.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Dataset loader and training data preparation example.

Dataset Loader and Training Data Preparation Example.

This example demonstrates:
- Loading datasets with the ViDataset loader
- Accessing different splits (training, validation, dump)
- Iterating through asset-annotation pairs
- Dataset protocol features (indexing, length, iteration)
- Batch processing and training loops
- Visualizing annotations
- Preparing data for model training

Requirements:
    - Vi SDK installed: pip install vi-sdk
    - Downloaded dataset from previous examples

Usage:
    python3 03_dataset_loader_training.py
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from vi.dataset import ViDataset


def main():
    """Demonstrate dataset loader functionality."""
    # Check if we have a downloaded dataset
    data_dir = Path("./data")
    if not data_dir.exists() or not list(data_dir.iterdir()):
        print("❌ No datasets found in ./data/")
        print("💡 Run 01_basic_dataset_operations.py first to download a dataset")
        return

    # Find first dataset directory
    dataset_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
    if not dataset_dirs:
        print("❌ No dataset directories found")
        return

    dataset_dir = dataset_dirs[0]
    print(f"📁 Loading dataset from: {dataset_dir}")

    # Load dataset with memory management
    print("\n📊 Loading dataset...")
    dataset = ViDataset(
        dataset_dir,
        memory_limit=100,  # Cache up to 100 samples
        prefetch_size=5,  # Prefetch 5 samples ahead
        enable_memory_mapping=True,
    )

    # Get dataset info
    info = dataset.info()
    print("\n📋 Dataset Information:")
    print(f"   Name: {info.name}")
    print(f"   Organization: {info.organization_id}")
    print(f"   Export Directory: {info.export_dir}")
    print(f"   Created: {info.created_at}")
    print(f"   Total Assets: {info.total_assets}")
    print(f"   Total Annotations: {info.total_annotations}")

    # Display split information
    print("\n📊 Split Information:")
    for split_name, split_info in info.splits.items():
        print(f"\n   {split_name.upper()}:")
        print(f"      Assets: {split_info.assets}")
        print(f"      Annotations: {split_info.annotations}")

    # Demonstrate Dataset Protocol Features
    print("\n🎯 Dataset Protocol Features:")
    print("=" * 40)

    # 1. Length protocol
    print(f"1. Length Protocol: len(dataset) = {len(dataset)}")

    # 2. Indexing protocol
    if len(dataset) > 0:
        print("2. Indexing Protocol:")
        asset, annotations = dataset[0]
        print(f"   First sample: {asset.filename} with {len(annotations)} annotations")

        if len(dataset) > 1:
            asset, annotations = dataset[-1]
            print(
                f"   Last sample: {asset.filename} with {len(annotations)} annotations"
            )

    # 3. Iteration protocol
    print("3. Iteration Protocol:")
    sample_count = 0
    for asset, annotations in dataset:
        sample_count += 1
        if sample_count >= 3:  # Show first 3 samples
            break
        print(f"   Sample {sample_count}: {asset.filename}")

    print(f"   ... and {len(dataset) - 3} more samples")

    # Demonstrate advanced features
    print("\n🚀 Advanced Dataset Features:")
    print("=" * 40)

    # Split-based indexing
    print("4. Split-based Indexing:")
    for split_name in ["training", "validation", "dump"]:
        indices = dataset.get_split_indices(split_name)
        if indices:
            print(f"   {split_name.capitalize()} split: {len(indices)} samples")
            print(f"   First {split_name} sample index: {indices[0]}")

    # Sample metadata
    print("\n5. Sample Metadata:")
    if len(dataset) > 0:
        info_sample = dataset.get_sample_info(0)
        print(f"   Sample 0 info: {info_sample}")

    # Demonstrate batch processing
    print("\n🔧 Batch Processing Features:")
    print("=" * 40)

    # Simulate batch processing behavior
    print("6. Batch Processing Simulation:")
    batch_size = 4
    batch_count = 0

    for i, (asset, annotations) in enumerate(dataset):
        if i % batch_size == 0:
            batch_count += 1
            print(
                f"   Batch {batch_count}: samples {i}-{min(i + batch_size - 1, len(dataset) - 1)}"
            )

            if batch_count >= 3:  # Show first 3 batches
                break

    # Demonstrate custom collate function
    print("\n7. Custom Collate Function Example:")

    def custom_collate_fn(batch: List[Tuple[Any, List[Any]]]) -> Dict[str, Any]:
        """Collate dataset batches."""
        assets, annotations_list = zip(*batch)

        return {
            "assets": list(assets),
            "annotations": list(annotations_list),
            "batch_size": len(batch),
            "filenames": [asset.filename for asset in assets],
            "image_sizes": [(asset.width, asset.height) for asset in assets],
        }

    # Simulate batch processing with custom collate
    batch = []
    for i, (asset, annotations) in enumerate(dataset):
        batch.append((asset, annotations))
        if len(batch) == batch_size:
            collated = custom_collate_fn(batch)
            print(f"   Collated batch: {collated['batch_size']} samples")
            print(f"   Filenames: {collated['filenames'][:2]}...")
            print(f"   Image sizes: {collated['image_sizes'][:2]}...")
            batch = []
            break

    # Performance optimization examples
    print("\n⚡ Performance Optimization Examples:")
    print("=" * 40)

    # Random access performance
    print("8. Random Access Performance:")
    if len(dataset) > 10:
        # Test random access speed
        start_time = time.time()
        for i in range(min(100, len(dataset))):
            _ = dataset[i % len(dataset)]
        end_time = time.time()

        print(f"   Random access: {100} samples in {end_time - start_time:.4f}s")
        print(f"   Average: {(end_time - start_time) / 100 * 1000:.2f}ms per sample")

    # Memory efficiency
    print("\n9. Memory Efficiency:")
    print("   - Lazy loading: Assets loaded on-demand")
    print("   - Index caching: Built once, reused for random access")
    print("   - Split-based organization: Efficient memory usage")

    # Training loop simulation
    print("\n🎓 Training Loop Simulation:")
    print("=" * 30)

    print("10. Simulated Training Loop:")
    epochs = 2
    batch_size = 8

    for epoch in range(epochs):
        print(f"   Epoch {epoch + 1}/{epochs}:")

        batch_count = 0
        for i, (asset, annotations) in enumerate(dataset):
            if i % batch_size == 0:
                batch_count += 1
                print(
                    f"     Batch {batch_count}: Processing samples {i}-{min(i + batch_size - 1, len(dataset) - 1)}"
                )

                # Simulate training step
                # model_output = model(asset, annotations)
                # loss = compute_loss(model_output, annotations)
                # optimizer.step()

                if batch_count >= 3:  # Limit for demo
                    break

        print(f"     Epoch {epoch + 1} completed with {batch_count} batches")

    # Demonstrate Memory Management Features
    print("\n🧠 Memory Management Features:")
    print("=" * 40)

    print("11. Memory Statistics:")
    stats = dataset.get_memory_stats()
    print(f"   Cached samples: {stats['cached_samples']}")
    print(f"   Memory limit: {stats['memory_limit']}")
    print(f"   Prefetch size: {stats['prefetch_size']}")
    print(f"   Cache hit ratio: {stats['cache_hit_ratio']:.2%}")

    print("\n12. Batch Processing with get_batch():")
    # Demonstrate get_batch method
    batch_indices = list(range(min(8, len(dataset))))
    batch = dataset.get_batch(batch_indices)
    print(f"   Retrieved batch of {len(batch)} samples")
    print(f"   Batch indices: {batch_indices}")

    # Show memory stats after batch loading
    stats_after = dataset.get_memory_stats()
    print(f"   Cached samples after batch: {stats_after['cached_samples']}")
    print(f"   Cache hit ratio: {stats_after['cache_hit_ratio']:.2%}")

    print("\n13. Memory Management Operations:")
    # Demonstrate cache management
    stats_before = dataset.get_memory_stats()
    print("   Original cache size:", stats_before["cached_samples"])

    # Clear cache
    dataset.clear_cache()
    stats_after_clear = dataset.get_memory_stats()
    print("   After clearing cache:", stats_after_clear["cached_samples"])

    # Set new memory limit
    dataset.set_memory_limit(50)
    stats_after_limit = dataset.get_memory_stats()
    print("   New memory limit:", stats_after_limit["memory_limit"])

    # Load some samples to fill cache
    for i in range(min(10, len(dataset))):
        _ = dataset[i]

    final_stats = dataset.get_memory_stats()
    print("   Final cached samples:", final_stats["cached_samples"])

    # Explore training split
    if info.splits["training"].assets > 0:
        print("\n🎓 Exploring TRAINING split:")
        print(f"   Total assets: {len(dataset.training.assets)}")
        print(f"   Total annotations: {len(dataset.training.annotations)}")

        # Iterate through first 3 pairs
        print("\n   First 3 training examples:")
        for i, (asset, annotations) in enumerate(dataset.training.iter_pairs()):
            if i >= 3:
                break

            print(f"\n   Example {i + 1}:")
            print(f"      Asset: {asset.filename}")
            print(f"         Dimensions: {asset.width}x{asset.height}")
            if asset.filepath:
                print(f"         Path: {asset.filepath}")

            print(f"      Annotations: {len(annotations)}")
            for j, ann in enumerate(annotations, 1):
                print(f"         {j}. ID: {ann.id}")
                print(f"            Category: {ann.category or 'N/A'}")

                # Display annotation type-specific information
                if hasattr(ann.contents, "caption"):
                    # Phrase grounding
                    print("            Type: Phrase Grounding")
                    print(f"            Caption: {ann.contents.caption[:100]}...")
                    print(
                        f"            Grounded Phrases: {len(ann.contents.grounded_phrases)}"
                    )

                    # Show first phrase
                    if ann.contents.grounded_phrases:
                        phrase = ann.contents.grounded_phrases[0]
                        print(f"               - '{phrase.phrase}'")
                        print(
                            f"                 Tokens: [{phrase.start_token_index}, {phrase.end_token_index}]"
                        )
                        print(f"                 Bounds: {len(phrase.bounds)} boxes")

                elif hasattr(ann.contents, "interactions"):
                    # VQA
                    print("            Type: Visual Question Answering")
                    print(f"            Q&A Pairs: {len(ann.contents.interactions)}")

                    # Show first interaction
                    if ann.contents.interactions:
                        qa = ann.contents.interactions[0]
                        print(f"               Q: {qa.question[:100]}...")
                        print(f"               A: {qa.answer[:100]}...")

    # Explore validation split
    if info.splits["validation"].assets > 0:
        print("\n✅ Exploring VALIDATION split:")
        print(f"   Total assets: {len(dataset.validation.assets)}")
        print(f"   Total annotations: {len(dataset.validation.annotations)}")

        # Count annotation types
        pg_count = 0
        vqa_count = 0

        for asset, annotations in dataset.validation.iter_pairs():
            for ann in annotations:
                if hasattr(ann.contents, "caption"):
                    pg_count += 1
                elif hasattr(ann.contents, "interactions"):
                    vqa_count += 1

        print(f"   Phrase Grounding annotations: {pg_count}")
        print(f"   VQA annotations: {vqa_count}")

    # Demonstrate data preparation for training
    print("\n🔧 Preparing data for training...")
    print("\n   Example: Converting to training format")

    training_data = []
    for i, (asset, annotations) in enumerate(dataset.training.iter_pairs()):
        if i >= 5:  # Just show first 5
            break

        for ann in annotations:
            if hasattr(ann.contents, "caption"):
                # Phrase grounding format
                training_example = {
                    "image_path": asset.filepath or asset.filename,
                    "image_size": (asset.width, asset.height),
                    "caption": ann.contents.caption,
                    "phrases": [
                        {
                            "text": p.phrase,
                            "bbox": p.bounds[0] if p.bounds else None,
                            "tokens": (p.start_token_index, p.end_token_index),
                        }
                        for p in ann.contents.grounded_phrases
                    ],
                }
                training_data.append(training_example)

            elif hasattr(ann.contents, "interactions"):
                # VQA format
                training_example = {
                    "image_path": asset.filepath or asset.filename,
                    "image_size": (asset.width, asset.height),
                    "conversations": [
                        {"question": qa.question, "answer": qa.answer}
                        for qa in ann.contents.interactions
                    ],
                }
                training_data.append(training_example)

    print(f"   ✓ Prepared {len(training_data)} training examples")
    if training_data:
        print("\n   Sample training example:")
        print(json.dumps(training_data[0], indent=2)[:500] + "...")

    # Visualize annotations (if PIL is available)
    try:
        print("\n🎨 Visualizing annotations...")
        visualization_dir = Path("./visualizations")
        visualization_dir.mkdir(exist_ok=True)

        viz_count = 0
        for i, image in enumerate(dataset.training.visualize()):
            if i >= 3:  # Save first 3
                break

            output_path = visualization_dir / f"training_viz_{i + 1}.png"
            image.save(output_path)
            viz_count += 1

        print(f"   ✓ Saved {viz_count} visualizations to {visualization_dir}")

    except ImportError:
        print("   ⚠️  PIL not available - skipping visualization")
    except Exception as e:
        print(f"   ⚠️  Visualization error: {e}")

    # Direct access to assets and annotations
    print("\n📦 Direct access to splits:")

    # Access just assets
    print("\n   Training assets:")
    for i, asset in enumerate(dataset.training.assets.items):
        if i >= 3:
            break
        print(f"      {i + 1}. {asset.filename} ({asset.width}x{asset.height})")

    # Access just annotations
    print("\n   Training annotations:")
    for i, annotations in enumerate(dataset.training.annotations.items):
        if i >= 3:
            break
        print(f"      Batch {i + 1}: {len(annotations)} annotations")

    # Performance tips
    print("\n⚡ Performance Tips:")
    print("   - Use iter_pairs() for efficient streaming")
    print("   - Assets are loaded lazily (not all at once)")
    print("   - Visualizations are generated on-demand")
    print("   - Iterate once, process as you go")

    # Example: Efficient batch processing
    print("\n🚀 Example: Efficient batch processing")

    batch_size = 8
    batch = []

    for i, (asset, annotations) in enumerate(dataset.training.iter_pairs()):
        batch.append((asset, annotations))

        if len(batch) == batch_size or i == len(dataset.training.assets) - 1:
            # Process batch
            print(f"   Processing batch of {len(batch)} items...")
            # Your training code here
            batch = []

        if i >= 15:  # Demo only
            break

    # Summary
    print("\n" + "=" * 60)
    print("✅ Dataset loader demonstration completed!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   - Dataset: {info.name}")
    print(f"   - Total assets: {info.total_assets}")
    print(f"   - Training examples: {info.splits['training'].assets}")
    print(f"   - Validation examples: {info.splits['validation'].assets}")
    print("   - Dataset protocol: ✅ __len__, __getitem__, __iter__")
    print("   - Index caching: ✅ Efficient random access")
    print("   - Split support: ✅ Training/validation/dump splits")
    print("   - Memory efficient: ✅ Lazy loading")
    print("   - Memory management: ✅ LRU cache, prefetching, batch processing")
    print("   - Performance: ✅ Intelligent caching and memory optimization")
    print("\n💡 Next steps:")
    print("   - Integrate with your training pipeline")
    print("   - Use with ML frameworks (PyTorch, TensorFlow, etc.)")
    print("   - Explore model inference: 05_model_inference.py")
    print("   - Check advanced examples for more patterns")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
