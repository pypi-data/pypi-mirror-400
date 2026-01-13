import pandas as pd
from typing import Sequence

from pydantic import BaseModel


def to_pandas(
    models: Sequence[BaseModel],
    index_col: str | list[str] = "id",
    rename_index: str | list[str] | None = None,
    rename_columns: dict[str, str] | None = None,
    drop_columns: str | list[str] | None = None,
) -> pd.DataFrame:
    df = pd.DataFrame([m.model_dump() for m in models])
    df.set_index(index_col, inplace=True)
    if rename_index is not None:
        df.index.set_names(rename_index, inplace=True)
    if rename_columns is not None:
        df.rename(columns=rename_columns, inplace=True)
    if drop_columns is not None:
        df.drop(drop_columns, axis=1, inplace=True)
    return df
