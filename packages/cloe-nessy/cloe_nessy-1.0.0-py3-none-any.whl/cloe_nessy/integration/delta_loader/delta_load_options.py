from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel


class DeltaLoadOptions(BaseModel):
    """Options to configure the DeltaLoader.

    Args:
        strategy: Delta load strategy to use.
        delta_load_identifier: Unique delta load identifier used to track the delta load metadata.
        strategy_options: Options used to configure the chosen delta load strategy.
            See the config class of the particular strategy for more info.
        metadata_table_identifier: Identifier of the metadata table used to keep
            track of the delta load metadata. The table will be created if it does
            not exist. If none, it will default to `<source_catalog>.<source_schema>.metadata_delta_load`.
    """

    strategy: str
    delta_load_identifier: str
    strategy_options: dict
    metadata_table_identifier: str | None = None

    @classmethod
    def from_yaml_str(cls, yaml_str: str) -> Self:
        """Creates an instance of DeltaLoadOptions from a YAML string."""
        options = yaml.safe_load(yaml_str)
        return cls(**options)

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        """Creates an instance of DeltaLoadOptions from a YAML file."""
        with Path(path).open() as f:
            yaml_str = f.read()
        return cls.from_yaml_str(yaml_str)
