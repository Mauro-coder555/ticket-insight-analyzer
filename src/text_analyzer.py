import re
from collections import Counter

import pandas as pd


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "can",
    "cannot",
    "could",
    "de",
    "el",
    "en",
    "error",
    "for",
    "from",
    "has",
    "have",
    "i",
    "in",
    "is",
    "it",
    "la",
    "las",
    "los",
    "not",
    "of",
    "on",
    "or",
    "para",
    "por",
    "que",
    "the",
    "this",
    "to",
    "un",
    "una",
    "user",
    "with",
}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value).lower()
    text = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_frequent_words(
    dataframe: pd.DataFrame,
    text_column: str | None,
    top_n: int = 15,
) -> dict[str, int]:
    if not text_column or text_column not in dataframe.columns:
        return {}

    words: list[str] = []

    for value in dataframe[text_column].dropna():
        cleaned_text = clean_text(value)

        for word in cleaned_text.split():
            if len(word) < 3:
                continue

            if word in STOPWORDS:
                continue

            words.append(word)

    return dict(Counter(words).most_common(top_n))