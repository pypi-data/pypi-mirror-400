# folder-indexer-py
A Python script to index a large folder structure into a parquet file, along with metadata

## Description

This script is useful for searching for files stored on a reasonably slow disk
from backups, especially in where you aren't sure about the files are are searching for.

Use tools like DBeaver and DuckDB to query and explore the generated index.

## Usage

```bash
uv tool install folder_indexer

folder_indexer -i /path/to/input/folder -o /path/to/output/folder
```

## Metadata Indexed and Output

The output parquet file (`file_index.parquet`) has the following columns:

    * file_path
    * folder_path
    * file_name
    * file_size_bytes
    * md5_hash_hex
    * sha256_base64
    * date_created
    * date_modified
    * magic_file_type_1
    * first_100_bytes
    * last_100_bytes
    * timestamp_crawled
    * indexing_start_timestamp
