from ...models import Column, Table


class DeltaLoaderMetadataTable(Table):
    """A Table Model for the Delta CDF Reader Metadata Table."""

    data_source_format: str = "DELTA"
    partition_by: list[str] = ["source_table_identifier"]
    liquid_clustering: bool = True
    columns: list[Column] = [
        Column(
            name="BK",
            data_type="STRING",
        ),
        Column(
            name="delta_load_identifier",
            data_type="STRING",
        ),
        Column(
            name="source_table_identifier",
            data_type="STRING",
        ),
        Column(
            name="is_processed",
            data_type="BOOLEAN",
        ),
        Column(
            name="is_stale",
            data_type="BOOLEAN",
        ),
        Column(
            name="last_read_timestamp",
            data_type="TIMESTAMP",
            nullable=True,
        ),
        Column(
            name="rows",
            data_type="BIGINT",
        ),
        Column(
            name="start_commit_version",
            data_type="INT",
            nullable=True,
        ),
        Column(
            name="end_commit_version",
            data_type="INT",
            nullable=True,
        ),
        Column(
            name="start_commit_timestamp_utc",
            data_type="TIMESTAMP",
            nullable=True,
        ),
        Column(
            name="end_commit_timestamp_utc",
            data_type="TIMESTAMP",
            nullable=True,
        ),
        Column(
            name="__DCR",
            data_type="TIMESTAMP",
        ),
        Column(
            name="__DMR",
            data_type="TIMESTAMP",
        ),
    ]
