import pandas as pd


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove columns that contain only NA values.

    Args:
        df (pd.DataFrame): DataFrame to be processed.

    Returns:
        pd.DataFrame: DataFrame with empty columns removed.
    """
    return df.dropna(axis='columns', how='all')


def merge_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge duplicate columns in a DataFrame by taking the first non-NA value.

    Args:
        df (pd.DataFrame): DataFrame to be processed.

    Returns:
        pd.DataFrame: DataFrame with duplicate columns merged.
    """
    return (df
            .T
            .groupby(df.columns, sort=False)
            .apply(lambda x: x.infer_objects(copy=False).bfill().iloc[0])
            .T
            )


def replace_strings(series: pd.Series, replacements: dict) -> pd.Series:
    for old, new in replacements.items():
        series = series.str.replace(old, new, regex=False)
    return series
