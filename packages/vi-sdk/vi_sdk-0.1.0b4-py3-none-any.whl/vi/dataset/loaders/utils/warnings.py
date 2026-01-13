#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   warnings.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK datasets warnings module.
"""

NO_ASSETS_WARNING = (
    "[yellow]⚠ Warning: No assets found in {split_name} split. You may have "
    "specified the dataset export format as `ViJsonl`, which only exports annotations. "
    "You may want to re-export the dataset with the ViFull format to include assets.[/yellow]"
)

NO_ANNOTATIONS_WARNING = (
    "[yellow]⚠ Warning: No annotations found in {split_name} split.[/yellow]"
)

ASSET_ANNOTATION_MISMATCH_WARNING = (
    "[yellow]⚠ Warning: Number of assets ({num_assets}) does not match number of annotations "
    "({num_annotations}) in {split_name} split. This will cause issues when iterating over "
    "the dataset using .iter_pairs(), or when visualizing the dataset using .visualize().[/yellow]"
)
