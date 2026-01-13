from pathlib import Path

import polars as pl

from folder_indexer.indexer import run_file_indexer_and_merge


def test_with_single_file(tmp_path: Path) -> None:
    input_folder = tmp_path / "input"
    input_folder.mkdir()
    (input_folder / "sample.txt").write_bytes(b"This is a sample file.")

    run_file_indexer_and_merge(
        input_folder=input_folder,
        output_folder=tmp_path,
        strip_prefix=True,
    )

    assert (tmp_path / "file_index.parquet").is_file()

    df = pl.read_parquet(tmp_path / "file_index.parquet")
    assert df.shape == (1, 14)

    assert df.columns == [
        "file_path",
        "folder_path",
        "file_name",
        "file_size_bytes",
        "entry_kind",
        "md5_hex",
        "sha256_base64",
        "date_created",
        "date_modified",
        "magic_file_type_1",
        "first_100_bytes",
        "last_100_bytes",
        "timestamp_crawled",
        "indexing_start_timestamp",
    ]

    assert df.drop(
        [
            "timestamp_crawled",
            "indexing_start_timestamp",
            "date_created",
            "date_modified",
        ]
    ).to_dicts()[0] == {
        "entry_kind": "file",
        "file_name": "sample.txt",
        "file_path": "sample.txt",
        "file_size_bytes": 22,
        "first_100_bytes": b"This is a sample file.",
        "folder_path": ".",
        "last_100_bytes": None,
        "magic_file_type_1": "ASCII text, with no line terminators",
        "md5_hex": "fa5b771787d8687c9d9860ea98367122",
        "sha256_base64": "dGlt6dbjB/9bwtfsBAsqwbRFk7w0YasWgXQ+J8It3fA=",
    }
