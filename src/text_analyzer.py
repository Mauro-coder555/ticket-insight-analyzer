import re
from collections import Counter

import pandas as pd


STOPWORDS = {
    # English common words
    "a",
    "about",
    "after",
    "again",
    "all",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "can",
    "cannot",
    "could",
    "do",
    "does",
    "doesn",
    "during",
    "for",
    "from",
    "has",
    "have",
    "having",
    "how",
    "i",
    "in",
    "into",
    "is",
    "it",
    "its",
    "not",
    "of",
    "on",
    "or",
    "our",
    "out",
    "over",
    "should",
    "that",
    "the",
    "their",
    "there",
    "this",
    "to",
    "too",
    "under",
    "up",
    "was",
    "we",
    "when",
    "where",
    "which",
    "while",
    "with",
    "without",
    "would",

    # Spanish common words
    "al",
    "como",
    "con",
    "de",
    "del",
    "desde",
    "el",
    "en",
    "es",
    "esta",
    "este",
    "la",
    "las",
    "lo",
    "los",
    "más",
    "para",
    "por",
    "que",
    "se",
    "sin",
    "su",
    "sus",
    "un",
    "una",
    "uno",

    # Ticket/support generic words
    "ticket",
    "tickets",
    "case",
    "cases",
    "issue",
    "issues",
    "request",
    "requests",
    "customer",
    "customers",
    "client",
    "clients",
    "user",
    "users",
    "support",
    "agent",
    "agents",
    "status",
    "priority",
    "category",
    "need",
    "needs",
    "new",
    "review",
    "update",
    "updated",
    "change",
    "changes",
    "problem",
    "problems",

    # Generic error words that are too broad alone
    "error",
    "failed",
    "fails",
    "failure",
    "unexpected",
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