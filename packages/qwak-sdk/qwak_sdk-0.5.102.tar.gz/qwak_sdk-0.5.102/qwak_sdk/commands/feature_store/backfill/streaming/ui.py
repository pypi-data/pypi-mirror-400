from pathlib import Path
from typing import List, Tuple

import click

from qwak_sdk.commands.feature_store.backfill.streaming._logic import (
    _trigger_streaming_backfills,
)
from qwak_sdk.inner.file_registry import list_qwak_python_files
from qwak_sdk.inner.tools.cli_tools import QwakCommand
from qwak_sdk.tools.utils import qwak_spinner


@click.command(
    "streaming",
    cls=QwakCommand,
    help="Trigger backfills for all streaming aggregation backfill definitions under the given path",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Directory or file path containing backfill definitions (decorated with @streaming.backfill)",
)
def backfill_streaming(path: Path, **kwargs):
    """
    Trigger streaming aggregation backfills from a definition file.

    The file should contain functions decorated with @streaming.backfill
    that defines the backfill transformation and configuration.

    Examples:
        An example file can look like this:
            from qwak.feature_store.feature_sets import streaming
            from qwak.feature_store.feature_sets.streaming_backfill import BackfillDataSource
            from datetime import datetime

            @streaming.backfill(
                feature_set_name="my_streaming_fs",
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 12, 1),
                data_sources=[BackfillDataSource(data_source_name="batch_source")]
            )

            def my_backfill():
                return SparkSqlTransformation("SELECT * FROM batch_source")

        Usage:
            qwak features backfill streaming --path backfill_definition.py
    """
    backfill_definition_files: List[Tuple[str, str]]

    if Path.is_dir(path):
        backfill_definition_files = _handle_directory(path)
    else:
        backfill_definition_files = [(str(path), str(path.absolute()))]

    _trigger_streaming_backfills(backfill_definition_files)


def _handle_directory(path: Path) -> list[tuple[str, str]]:
    with qwak_spinner(
        begin_text="Recursively looking for python files in input dir",
        print_callback=print,
    ) as sp:
        return list_qwak_python_files(path, sp)
