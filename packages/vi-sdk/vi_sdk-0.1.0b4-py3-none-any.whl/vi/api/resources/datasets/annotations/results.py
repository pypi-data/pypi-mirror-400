#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   results.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Result wrapper for simplified annotation upload result handling.
"""

from vi.api.resources.datasets.annotations.responses import AnnotationImportSession
from vi.api.resources.managers.results import UploadResult


class AnnotationUploadResult(UploadResult):
    """Simplified wrapper for annotation upload results.

    Provides simple access to annotation import statistics, hiding complexity
    of the underlying import session structure.

    Attributes:
        session: Underlying annotation import session response

    Examples:
        ```python
        result = client.annotations.upload(dataset_id="id", paths="./annotations.jsonl")
        print(f"Imported: {result.total_annotations}")
        print(result.summary())
        ```

    """

    def __init__(self, session: AnnotationImportSession):
        """Initialize annotation upload result wrapper.

        Args:
            session: Annotation import session from upload operation

        """
        self.session = session
        self.start_time = session.metadata.time_created
        self.end_time = session.metadata.last_updated

    @property
    def total_files(self) -> int:
        """Total number of annotation files processed."""
        return self.session.status.files.page_count

    @property
    def total_size_bytes(self) -> int:
        """Total size of annotation files in bytes."""
        return self.session.status.files.total_size_bytes

    @property
    def total_annotations(self) -> int:
        """Total number of annotations imported."""
        return sum(self.session.status.annotations.status_count.values())

    @property
    def annotations_by_status(self) -> dict[str, int]:
        """Dictionary mapping annotation status to count."""
        return self.session.status.annotations.status_count

    @property
    def files_by_status(self) -> dict[str, int]:
        """Dictionary mapping file status to count."""
        return self.session.status.files.status_count

    @property
    def is_complete(self) -> bool:
        """Check if import session is complete."""
        # Check if any condition indicates completion
        for condition in self.session.status.conditions:
            if (
                condition.condition == "Complete"
                and condition.status.value == "Reached"
            ):
                return True
        return False

    @property
    def session_id(self) -> str:
        """Annotation import session ID."""
        return self.session.annotation_import_session_id

    def summary(self) -> str:
        """Return formatted summary of annotation upload results.

        Returns:
            Multi-line string with import statistics and status

        Example:
            ```python
            print(result.summary())
            # ✓ Annotation Import Complete
            #   Files: 3 processed
            #   Annotations: 450 imported
            #   Total Size: 1.2 MB
            #   Duration: 12.3s
            #
            #   File Status:
            #     • Processed: 3
            #
            #   Annotation Status:
            #     • Created: 450
            ```

        """
        icon = "✓" if self.is_complete else "⏳"
        status = (
            "Annotation Import Complete" if self.is_complete else "Import In Progress"
        )

        size_mb = self.total_size_bytes / (1024 * 1024)

        summary = f"""
{icon} {status}
  Files: {self.total_files} processed
  Annotations: {self.total_annotations} imported
  Total Size: {size_mb:.2f} MB
  Duration: {self.duration_seconds:.1f}s
"""

        if self.files_by_status:
            summary += "\n  File Status:\n"
            for status_name, count in self.files_by_status.items():
                summary += f"    • {status_name}: {count}\n"

        if self.annotations_by_status:
            summary += "\n  Annotation Status:\n"
            for status_name, count in self.annotations_by_status.items():
                summary += f"    • {status_name}: {count}\n"

        if self.session.status.reason:
            summary += f"\n  Note: {self.session.status.reason}\n"

        return summary

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"AnnotationUploadResult(files={self.total_files}, "
            f"annotations={self.total_annotations})"
        )
