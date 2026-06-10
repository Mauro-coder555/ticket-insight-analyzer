from typing import Optional


COLUMN_TYPES = {
    "ticket_id": "Ticket ID",
    "created_date": "Created Date",
    "status": "Status",
    "priority": "Priority",
    "category": "Category",
    "agent": "Agent",
    "customer": "Customer",
    "text": "Title or Description",
}


COLUMN_ALIASES = {
    "ticket_id": [
        "id",
        "ticket_id",
        "ticket id",
        "ticket",
        "case_id",
        "case id",
        "issue_id",
        "issue id",
    ],
    "created_date": [
        "created_at",
        "created at",
        "created",
        "creation_date",
        "creation date",
        "date",
        "opened_at",
        "opened at",
        "submitted_at",
        "submitted at",
    ],
    "status": [
        "status",
        "state",
        "ticket_status",
        "ticket status",
        "stage",
    ],
    "priority": [
        "priority",
        "severity",
        "urgency",
        "impact",
        "level",
    ],
    "category": [
        "category",
        "type",
        "topic",
        "reason",
        "issue_type",
        "issue type",
        "tag",
        "tags",
    ],
    "agent": [
        "agent",
        "assignee",
        "owner",
        "responsible",
        "assigned_to",
        "assigned to",
        "support_agent",
        "support agent",
    ],
    "customer": [
        "customer",
        "client",
        "company",
        "account",
        "organization",
        "org",
        "business",
    ],
    "text": [
        "title",
        "subject",
        "description",
        "summary",
        "message",
        "body",
        "details",
    ],
}


def normalize_column_name(column_name: str) -> str:
    return (
        column_name.strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace(".", " ")
    )


def detect_column_mapping(columns: list[str]) -> dict[str, Optional[str]]:
    normalized_columns = {
        normalize_column_name(column): column
        for column in columns
    }

    mapping: dict[str, Optional[str]] = {}

    for column_type, aliases in COLUMN_ALIASES.items():
        detected_column = None

        for alias in aliases:
            normalized_alias = normalize_column_name(alias)

            if normalized_alias in normalized_columns:
                detected_column = normalized_columns[normalized_alias]
                break

        if detected_column is None:
            for normalized_column, original_column in normalized_columns.items():
                if any(normalize_column_name(alias) in normalized_column for alias in aliases):
                    detected_column = original_column
                    break

        mapping[column_type] = detected_column

    return mapping