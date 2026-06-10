from datetime import datetime
from pathlib import Path


def build_markdown_report(
    analysis_result: dict,
    source_file_name: str,
) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# Ticket Insight Analyzer Report",
        "",
        f"Generated at: {generated_at}",
        f"Source file: `{source_file_name}`",
        "",
        "## Executive Summary",
        "",
        analysis_result["executive_summary"],
        "",
        "## Main Metrics",
        "",
        f"- Total tickets: {analysis_result['total_tickets']}",
        f"- Open tickets: {format_optional_value(analysis_result['open_ticket_count'])}",
        f"- Open tickets percentage: {format_optional_value(analysis_result['open_ticket_percentage'], suffix='%')}",
        f"- High or critical priority tickets: {format_optional_value(analysis_result['high_priority_count'])}",
        "",
        "## Backlog Health Score",
        "",
        f"**{analysis_result['backlog_health_score']['score']}/100 - {analysis_result['backlog_health_score']['label']}**",
        "",
    ]

    score_reasons = analysis_result["backlog_health_score"].get("reasons", [])

    if score_reasons:
        lines.append("Main score factors:")
        lines.append("")

        for reason in score_reasons:
            lines.append(f"- {reason}")

        lines.append("")

    lines.extend([
        "## Aging Summary",
        "",
    ])

    aging_summary = analysis_result["aging_summary"]

    lines.extend([
        f"- Open tickets older than 7 days: {format_optional_value(aging_summary.get('older_than_7_days'))}",
        f"- Open tickets older than 14 days: {format_optional_value(aging_summary.get('older_than_14_days'))}",
        f"- Open tickets older than 30 days: {format_optional_value(aging_summary.get('older_than_30_days'))}",
        f"- Oldest open ticket age: {format_optional_value(aging_summary.get('oldest_open_ticket_age'), suffix=' days')}",
        "",
    ])

    add_ranking_section(lines, "Top Statuses", analysis_result["top_statuses"])
    add_ranking_section(lines, "Top Priorities", analysis_result["top_priorities"])
    add_ranking_section(lines, "Top Categories", analysis_result["top_categories"])
    add_ranking_section(lines, "Top Agents", analysis_result["top_agents"])
    add_ranking_section(lines, "Top Customers", analysis_result["top_customers"])
    add_ranking_section(lines, "Frequent Words", analysis_result["frequent_words"])

    lines.extend([
        "## Recommendations",
        "",
    ])

    for recommendation in analysis_result["recommendations"]:
        lines.append(f"- {recommendation}")

    lines.extend([
        "",
        "## Column Mapping Used",
        "",
    ])

    for column_type, column_name in analysis_result["column_mapping"].items():
        lines.append(f"- {column_type}: {column_name or 'Not available'}")

    lines.append("")

    return "\n".join(lines)


def save_markdown_report(
    analysis_result: dict,
    source_file_name: str,
    reports_dir: str = "reports",
) -> Path:
    output_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_stem = Path(source_file_name).stem
    output_path = output_dir / f"{source_stem}_ticket_report_{timestamp}.md"

    markdown_content = build_markdown_report(
        analysis_result=analysis_result,
        source_file_name=source_file_name,
    )

    output_path.write_text(markdown_content, encoding="utf-8")

    return output_path


def add_ranking_section(
    lines: list[str],
    title: str,
    values: dict[str, int],
) -> None:
    lines.extend([
        f"## {title}",
        "",
    ])

    if not values:
        lines.extend([
            "Not available.",
            "",
        ])
        return

    for key, value in values.items():
        lines.append(f"- {key}: {value}")

    lines.append("")


def format_optional_value(value: object, suffix: str = "") -> str:
    if value is None:
        return "Not available"

    return f"{value}{suffix}"