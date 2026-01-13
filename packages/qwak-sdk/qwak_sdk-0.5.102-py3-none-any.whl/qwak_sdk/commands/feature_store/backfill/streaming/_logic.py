from pathlib import Path
from typing import List, Tuple

from qwak.feature_store.execution.streaming_backfill import StreamingAggregationBackfill
from qwak.feature_store.feature_sets.streaming_backfill import StreamingBackfill

from qwak_sdk.inner.file_registry import extract_class_objects
from qwak_sdk.tools.utils import qwak_spinner

DELIMITER = "----------------------------------------"


def _trigger_streaming_backfills(backfill_definition_files: List[Tuple[str, str]]):
    """
    Trigger streaming aggregation backfills from Python files.

    Args:
        backfill_definition_files: List of tuples (module_name, file_path) containing qwak imports
    """
    with qwak_spinner(
        begin_text="Finding streaming backfill definitions", print_callback=print
    ):
        streaming_backfills: List[
            Tuple[StreamingBackfill, str]
        ] = extract_class_objects(backfill_definition_files, StreamingBackfill)

    print(f"👀 Found {len(streaming_backfills)} streaming backfill definition(s)")

    print(DELIMITER)

    # Trigger each backfill
    for backfill_spec, source_file_path in streaming_backfills:
        print(
            f"Triggering backfill for featureset '{backfill_spec.featureset_name}' from '{source_file_path}'"
        )

        try:
            # Create executor and trigger
            executor = StreamingAggregationBackfill(
                backfill_spec, Path(source_file_path)
            )
            execution_id = executor.trigger()

            print(f"✅ Execution ID: {execution_id}")

        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            exit(1)

        print(DELIMITER)
