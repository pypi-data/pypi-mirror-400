from dataclasses import dataclass, field
import polars as pl
from .enums import Status

@dataclass
class KlineData:
    status: Status
    data: pl.DataFrame = field(default_factory=pl.DataFrame)
    error: str = ""
