from datetime import datetime

import pandas as pd

from src.text_analyzer import get_frequent_words


OPEN_STATUS_KEYWORDS = {
    "open",
    "opened",
    "new",
    "in progress",
    "pending",
    "pending customer",
    "waiting",
    "assigned",
    "reopened",
}

CLOSED_STATUS_KEYWORDS = {
    "closed",
    "resolved",
    "done",
    "completed",
    "cancelled",
    "canceled",
}

HIGH_PRIORITY_KEYWORDS = {
    "high",
    "critical",
    "urgent",
    "blocker",
    "p0",
    "p1",
}


def analyze_tickets(
    dataframe: pd.DataFrame,
    column_mapping: dict[str, str | None],
) -> dict:
    total_tickets = len(dataframe)

    status_column = column_mapping.get("status")
    priority_column = column_mapping.get("priority")
    category_column = column_mapping.get("category")
    agent_column = column_mapping.get("agent")
    customer_column = column_mapping.get("customer")
    created_date_column = column_mapping.get("created_date")
    text_column = column_mapping.get("text")

    open_mask = build_open_ticket_mask(dataframe, status_column)
    open_ticket_count = int(open_mask.sum()) if open_mask is not None else None
    open_ticket_percentage = (
        round((open_ticket_count / total_tickets) * 100, 2)
        if open_ticket_count is not None and total_tickets > 0
        else None
    )

    high_priority_count = count_high_priority_tickets(dataframe, priority_column)

    aging_summary = calculate_aging_summary(
        dataframe=dataframe,
        created_date_column=created_date_column,
        open_mask=open_mask,
    )

    top_categories = get_top_values(dataframe, category_column)
    top_statuses = get_top_values(dataframe, status_column)
    top_priorities = get_top_values(dataframe, priority_column)
    top_agents = get_top_values(dataframe, agent_column)
    top_customers = get_top_values(dataframe, customer_column)
    frequent_words = get_frequent_words(dataframe, text_column)

    backlog_health_score = calculate_backlog_health_score(
        total_tickets=total_tickets,
        open_ticket_percentage=open_ticket_percentage,
        high_priority_count=high_priority_count,
        aging_summary=aging_summary,
        top_categories=top_categories,
        top_agents=top_agents,
    )

    recommendations = generate_recommendations(
        total_tickets=total_tickets,
        open_ticket_percentage=open_ticket_percentage,
        high_priority_count=high_priority_count,
        aging_summary=aging_summary,
        top_categories=top_categories,
        top_agents=top_agents,
        top_customers=top_customers,
    )

    executive_summary = build_executive_summary(
        total_tickets=total_tickets,
        open_ticket_percentage=open_ticket_percentage,
        high_priority_count=high_priority_count,
        backlog_health_score=backlog_health_score,
        top_categories=top_categories,
        top_customers=top_customers,
        aging_summary=aging_summary,
    )

    return {
        "total_tickets": total_tickets,
        "open_ticket_count": open_ticket_count,
        "open_ticket_percentage": open_ticket_percentage,
        "high_priority_count": high_priority_count,
        "aging_summary": aging_summary,
        "top_categories": top_categories,
        "top_statuses": top_statuses,
        "top_priorities": top_priorities,
        "top_agents": top_agents,
        "top_customers": top_customers,
        "frequent_words": frequent_words,
        "backlog_health_score": backlog_health_score,
        "recommendations": recommendations,
        "executive_summary": executive_summary,
        "column_mapping": column_mapping,
    }


def build_open_ticket_mask(
    dataframe: pd.DataFrame,
    status_column: str | None,
) -> pd.Series | None:
    if not status_column or status_column not in dataframe.columns:
        return None

    normalized_status = dataframe[status_column].fillna("").astype(str).str.strip().str.lower()

    closed_mask = normalized_status.isin(CLOSED_STATUS_KEYWORDS)
    open_mask = normalized_status.isin(OPEN_STATUS_KEYWORDS)

    unknown_mask = ~(closed_mask | open_mask)

    return open_mask | unknown_mask


def count_high_priority_tickets(
    dataframe: pd.DataFrame,
    priority_column: str | None,
) -> int | None:
    if not priority_column or priority_column not in dataframe.columns:
        return None

    normalized_priority = dataframe[priority_column].fillna("").astype(str).str.strip().str.lower()

    return int(normalized_priority.isin(HIGH_PRIORITY_KEYWORDS).sum())


def calculate_aging_summary(
    dataframe: pd.DataFrame,
    created_date_column: str | None,
    open_mask: pd.Series | None,
) -> dict:
    unavailable_summary = {
        "older_than_7_days": None,
        "older_than_14_days": None,
        "older_than_30_days": None,
        "oldest_open_ticket_age": None,
    }

    if not created_date_column or created_date_column not in dataframe.columns:
        return unavailable_summary

    if open_mask is None:
        return unavailable_summary

    created_dates = pd.to_datetime(dataframe[created_date_column], errors="coerce")
    today = pd.Timestamp(datetime.now().date())

    ages = (today - created_dates).dt.days
    open_ticket_ages = ages[open_mask & ages.notna()]

    if open_ticket_ages.empty:
        return {
            "older_than_7_days": 0,
            "older_than_14_days": 0,
            "older_than_30_days": 0,
            "oldest_open_ticket_age": 0,
        }

    return {
        "older_than_7_days": int((open_ticket_ages > 7).sum()),
        "older_than_14_days": int((open_ticket_ages > 14).sum()),
        "older_than_30_days": int((open_ticket_ages > 30).sum()),
        "oldest_open_ticket_age": int(open_ticket_ages.max()),
    }


def get_top_values(
    dataframe: pd.DataFrame,
    column_name: str | None,
    limit: int = 5,
) -> dict[str, int]:
    if not column_name or column_name not in dataframe.columns:
        return {}

    counts = (
        dataframe[column_name]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
        .head(limit)
    )

    return {str(key): int(value) for key, value in counts.items()}


def calculate_backlog_health_score(
    total_tickets: int,
    open_ticket_percentage: float | None,
    high_priority_count: int | None,
    aging_summary: dict,
    top_categories: dict[str, int],
    top_agents: dict[str, int],
) -> dict:
    score = 100
    reasons: list[str] = []

    if open_ticket_percentage is not None:
        if open_ticket_percentage > 70:
            score -= 25
            reasons.append("High percentage of open tickets.")
        elif open_ticket_percentage > 50:
            score -= 15
            reasons.append("Moderate percentage of open tickets.")
        elif open_ticket_percentage > 30:
            score -= 8
            reasons.append("Some backlog accumulation detected.")

    older_than_30 = aging_summary.get("older_than_30_days")

    if older_than_30 is not None and total_tickets > 0:
        old_ticket_percentage = (older_than_30 / total_tickets) * 100

        if old_ticket_percentage > 20:
            score -= 25
            reasons.append("Many open tickets are older than 30 days.")
        elif old_ticket_percentage > 10:
            score -= 15
            reasons.append("Some open tickets are older than 30 days.")
        elif older_than_30 > 0:
            score -= 7
            reasons.append("There are a few old open tickets.")

    if high_priority_count is not None and total_tickets > 0:
        high_priority_percentage = (high_priority_count / total_tickets) * 100

        if high_priority_percentage > 30:
            score -= 20
            reasons.append("High or critical tickets represent a large share.")
        elif high_priority_percentage > 15:
            score -= 10
            reasons.append("High or critical tickets need attention.")

    if top_categories and total_tickets > 0:
        top_category_count = max(top_categories.values())
        category_concentration = (top_category_count / total_tickets) * 100

        if category_concentration > 40:
            score -= 15
            reasons.append("One category concentrates too many tickets.")
        elif category_concentration > 25:
            score -= 8
            reasons.append("One category is noticeably dominant.")

    if top_agents and len(top_agents) > 1:
        top_agent_count = max(top_agents.values())
        average_agent_load = sum(top_agents.values()) / len(top_agents)

        if average_agent_load > 0 and top_agent_count > average_agent_load * 1.8:
            score -= 10
            reasons.append("Ticket workload may be uneven across agents.")

    score = max(0, min(100, score))

    if score >= 80:
        label = "Healthy"
    elif score >= 60:
        label = "Moderate risk"
    elif score >= 40:
        label = "High risk"
    else:
        label = "Critical"

    return {
        "score": score,
        "label": label,
        "reasons": reasons,
    }


def generate_recommendations(
    total_tickets: int,
    open_ticket_percentage: float | None,
    high_priority_count: int | None,
    aging_summary: dict,
    top_categories: dict[str, int],
    top_agents: dict[str, int],
    top_customers: dict[str, int],
) -> list[str]:
    recommendations: list[str] = []

    if open_ticket_percentage is not None and open_ticket_percentage > 50:
        recommendations.append(
            "Review the current backlog process because more than half of the tickets are still open."
        )

    older_than_30 = aging_summary.get("older_than_30_days")

    if older_than_30 is not None and older_than_30 > 0:
        recommendations.append(
            "Prioritize open tickets older than 30 days to reduce backlog aging."
        )

    if high_priority_count is not None and total_tickets > 0:
        high_priority_percentage = (high_priority_count / total_tickets) * 100

        if high_priority_percentage > 20:
            recommendations.append(
                "Validate priority criteria because high or critical tickets represent a large share."
            )

    if top_categories and total_tickets > 0:
        top_category, top_category_count = next(iter(top_categories.items()))

        if (top_category_count / total_tickets) * 100 > 30:
            recommendations.append(
                f"Review the '{top_category}' category because it concentrates a significant number of tickets."
            )

    if top_agents and len(top_agents) > 1:
        top_agent, top_agent_count = next(iter(top_agents.items()))
        average_agent_load = sum(top_agents.values()) / len(top_agents)

        if average_agent_load > 0 and top_agent_count > average_agent_load * 1.5:
            recommendations.append(
                f"Review workload distribution because {top_agent} has the highest ticket load."
            )

    if top_customers and total_tickets > 0:
        top_customer, top_customer_count = next(iter(top_customers.items()))

        if (top_customer_count / total_tickets) * 100 > 25:
            recommendations.append(
                f"Investigate recurring issues for {top_customer}, the customer with the most tickets."
            )

    if not recommendations:
        recommendations.append(
            "No major risks detected. Continue monitoring backlog volume, aging and priority distribution."
        )

    return recommendations


def build_executive_summary(
    total_tickets: int,
    open_ticket_percentage: float | None,
    high_priority_count: int | None,
    backlog_health_score: dict,
    top_categories: dict[str, int],
    top_customers: dict[str, int],
    aging_summary: dict,
) -> str:
    summary_parts = [
        f"The dataset contains {total_tickets} tickets.",
        f"The Backlog Health Score is {backlog_health_score['score']}/100 ({backlog_health_score['label']}).",
    ]

    if open_ticket_percentage is not None:
        summary_parts.append(f"{open_ticket_percentage}% of tickets are currently open.")

    if high_priority_count is not None:
        summary_parts.append(f"There are {high_priority_count} high or critical priority tickets.")

    if top_categories:
        top_category, top_category_count = next(iter(top_categories.items()))
        summary_parts.append(f"The most frequent category is '{top_category}' with {top_category_count} tickets.")

    if top_customers:
        top_customer, top_customer_count = next(iter(top_customers.items()))
        summary_parts.append(f"The customer with the most tickets is '{top_customer}' with {top_customer_count} tickets.")

    older_than_30 = aging_summary.get("older_than_30_days")

    if older_than_30 is not None:
        summary_parts.append(f"There are {older_than_30} open tickets older than 30 days.")

    return " ".join(summary_parts)