from pathlib import Path

import pandas as pd


SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin1"]


def load_csv(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("The selected file must be a CSV file.")

    last_error = None

    for encoding in SUPPORTED_ENCODINGS:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError as error:
            last_error = error
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty.")
        except pd.errors.ParserError as error:
            raise ValueError(f"The CSV file could not be parsed: {error}")

    raise ValueError(f"Could not read the CSV file. Last error: {last_error}")


def get_preview_rows(dataframe: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe

    return dataframe.head(limit)