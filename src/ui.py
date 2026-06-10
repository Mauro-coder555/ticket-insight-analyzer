import os
import platform
import subprocess
from pathlib import Path

import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.analyzer import analyze_tickets
from src.column_mapper import COLUMN_TYPES, detect_column_mapping
from src.csv_loader import get_preview_rows, load_csv
from src.report import save_markdown_report


NOT_AVAILABLE_OPTION = "Not available"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.dataframe: pd.DataFrame | None = None
        self.source_file_path: Path | None = None
        self.analysis_result: dict | None = None
        self.column_combos: dict[str, QComboBox] = {}

        self.setWindowTitle("Ticket Insight Analyzer")
        self.resize(1250, 850)

        self._setup_ui()

    def _setup_ui(self) -> None:
        main_container = QWidget()
        main_layout = QVBoxLayout()
        main_container.setLayout(main_layout)

        title_label = QLabel("Ticket Insight Analyzer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold;")

        subtitle_label = QLabel(
            "Analyze support ticket CSV files locally and generate backlog insights."
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; color: #777;")

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #777;")

        actions_layout = QHBoxLayout()

        load_button = QPushButton("Load CSV")
        load_button.setMinimumHeight(38)
        load_button.clicked.connect(self.load_csv_file)

        analyze_button = QPushButton("Analyze Tickets")
        analyze_button.setMinimumHeight(38)
        analyze_button.clicked.connect(self.run_analysis)

        export_button = QPushButton("Export Markdown Report")
        export_button.setMinimumHeight(38)
        export_button.clicked.connect(self.export_report)

        open_reports_button = QPushButton("Open Reports Folder")
        open_reports_button.setMinimumHeight(38)
        open_reports_button.clicked.connect(self.open_reports_folder)

        actions_layout.addWidget(load_button)
        actions_layout.addWidget(analyze_button)
        actions_layout.addWidget(export_button)
        actions_layout.addWidget(open_reports_button)

        self.kpi_group = QGroupBox("Backlog Overview")
        self.kpi_layout = QGridLayout()
        self.kpi_group.setLayout(self.kpi_layout)

        self.chart_group = QGroupBox("Ticket Statistics")
        self.chart_layout = QGridLayout()
        self.chart_group.setLayout(self.chart_layout)

        self.preview_group = QGroupBox("CSV Preview")
        preview_layout = QVBoxLayout()
        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(180)
        self.preview_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        preview_layout.addWidget(self.preview_table)
        self.preview_group.setLayout(preview_layout)

        self.advanced_button = QPushButton("Show Advanced Column Mapping")
        self.advanced_button.setMinimumHeight(32)
        self.advanced_button.clicked.connect(self.toggle_mapping_visibility)

        self.mapping_group = QGroupBox("Advanced Column Mapping")
        self.mapping_layout = QGridLayout()
        self.mapping_group.setLayout(self.mapping_layout)
        self.mapping_group.setVisible(False)

        self.recommendations_group = QGroupBox("Recommendations")
        recommendations_layout = QVBoxLayout()
        self.recommendations_label = QLabel("Run an analysis to see recommendations.")
        self.recommendations_label.setWordWrap(True)
        self.recommendations_label.setStyleSheet("font-size: 13px;")
        recommendations_layout.addWidget(self.recommendations_label)
        self.recommendations_group.setLayout(recommendations_layout)

        self.status_label = QLabel("Load a CSV file to start.")
        self.status_label.setStyleSheet("color: #777;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        scroll_layout.addWidget(self.kpi_group)
        scroll_layout.addWidget(self.chart_group)
        scroll_layout.addWidget(self.recommendations_group)
        scroll_layout.addWidget(self.preview_group)
        scroll_layout.addWidget(self.advanced_button)
        scroll_layout.addWidget(self.mapping_group)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(self.file_label)
        main_layout.addLayout(actions_layout)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.status_label)

        self.setCentralWidget(main_container)

        self._build_empty_mapping_controls()
        self._render_empty_dashboard()

    def load_csv_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file",
            "",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            dataframe = load_csv(file_path)
        except Exception as error:
            QMessageBox.critical(self, "CSV Load Error", str(error))
            return

        self.dataframe = dataframe
        self.source_file_path = Path(file_path)
        self.analysis_result = None

        self.file_label.setText(f"Loaded file: {self.source_file_path.name}")
        self.status_label.setText("CSV loaded. Click 'Analyze Tickets' to generate insights.")

        self._populate_preview_table(get_preview_rows(dataframe))
        self._populate_mapping_controls(dataframe.columns.tolist())
        self._render_empty_dashboard()

    def run_analysis(self) -> None:
        if self.dataframe is None:
            QMessageBox.warning(self, "Missing CSV", "Please load a CSV file first.")
            return

        column_mapping = self._get_selected_column_mapping()

        try:
            self.analysis_result = analyze_tickets(
                dataframe=self.dataframe,
                column_mapping=column_mapping,
            )
        except Exception as error:
            QMessageBox.critical(self, "Analysis Error", str(error))
            return

        self._render_dashboard(self.analysis_result)
        self.status_label.setText("Analysis completed successfully.")

    def export_report(self) -> None:
        if self.analysis_result is None:
            QMessageBox.warning(
                self,
                "Missing Analysis",
                "Please run the analysis before exporting a report.",
            )
            return

        source_file_name = (
            self.source_file_path.name
            if self.source_file_path is not None
            else "unknown_file.csv"
        )

        try:
            output_path = save_markdown_report(
                analysis_result=self.analysis_result,
                source_file_name=source_file_name,
            )
        except Exception as error:
            QMessageBox.critical(self, "Export Error", str(error))
            return

        self.status_label.setText(f"Report exported: {output_path}")
        QMessageBox.information(
            self,
            "Report Exported",
            f"Markdown report saved at:\n{output_path}",
        )

    def open_reports_folder(self) -> None:
        reports_path = Path("reports")
        reports_path.mkdir(parents=True, exist_ok=True)

        try:
            if platform.system() == "Windows":
                os.startfile(reports_path.resolve())
            elif platform.system() == "Darwin":
                subprocess.run(["open", str(reports_path.resolve())], check=False)
            else:
                subprocess.run(["xdg-open", str(reports_path.resolve())], check=False)
        except Exception as error:
            QMessageBox.critical(
                self,
                "Open Folder Error",
                f"Could not open reports folder:\n{error}",
            )

    def toggle_mapping_visibility(self) -> None:
        is_visible = self.mapping_group.isVisible()
        self.mapping_group.setVisible(not is_visible)

        if is_visible:
            self.advanced_button.setText("Show Advanced Column Mapping")
        else:
            self.advanced_button.setText("Hide Advanced Column Mapping")

    def _render_empty_dashboard(self) -> None:
        self._clear_layout(self.kpi_layout)
        self._clear_layout(self.chart_layout)

        empty_label = QLabel("No analysis available yet.")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("font-size: 16px; color: #777; padding: 24px;")

        self.kpi_layout.addWidget(empty_label, 0, 0)

        chart_empty_label = QLabel("Charts will appear after running the analysis.")
        chart_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_empty_label.setStyleSheet("font-size: 16px; color: #777; padding: 24px;")

        self.chart_layout.addWidget(chart_empty_label, 0, 0)

        self.recommendations_label.setText("Run an analysis to see recommendations.")

    def _render_dashboard(self, analysis_result: dict) -> None:
        self._clear_layout(self.kpi_layout)
        self._clear_layout(self.chart_layout)

        health_score = analysis_result["backlog_health_score"]

        kpis = [
            (
                "Total Tickets",
                analysis_result["total_tickets"],
                "Total records found in the CSV file.",
            ),
            (
                "Open Tickets",
                self._format_optional_value(analysis_result["open_ticket_count"]),
                "Tickets that appear to be unresolved.",
            ),
            (
                "Open %",
                self._format_optional_value(
                    analysis_result["open_ticket_percentage"],
                    suffix="%",
                ),
                "Share of tickets currently open.",
            ),
            (
                "High Priority",
                self._format_optional_value(analysis_result["high_priority_count"]),
                "High or critical priority tickets.",
            ),
            (
                "Older than 30 days",
                self._format_optional_value(
                    analysis_result["aging_summary"].get("older_than_30_days")
                ),
                "Open tickets older than 30 days.",
            ),
            (
                "Health Score",
                f"{health_score['score']}/100",
                health_score["label"],
            ),
        ]

        for index, (title, value, subtitle) in enumerate(kpis):
            row = index // 3
            column = index % 3
            self.kpi_layout.addWidget(
                self._create_kpi_card(title, str(value), subtitle),
                row,
                column,
            )

        self._add_bar_chart(
            title="Tickets by Status",
            values=analysis_result["top_statuses"],
            row=0,
            column=0,
        )

        self._add_bar_chart(
            title="Tickets by Priority",
            values=analysis_result["top_priorities"],
            row=0,
            column=1,
        )

        self._add_bar_chart(
            title="Top Categories",
            values=analysis_result["top_categories"],
            row=1,
            column=0,
        )

        self._add_bar_chart(
            title="Top Agents",
            values=analysis_result["top_agents"],
            row=1,
            column=1,
        )

        self._add_bar_chart(
            title="Top Customers",
            values=analysis_result["top_customers"],
            row=2,
            column=0,
        )

        self._add_bar_chart(
            title="Frequent Words",
            values=analysis_result["frequent_words"],
            row=2,
            column=1,
        )

        recommendations = analysis_result.get("recommendations", [])

        if recommendations:
            recommendations_text = "\n".join(
                f"• {recommendation}" for recommendation in recommendations
            )
        else:
            recommendations_text = "No recommendations available."

        self.recommendations_label.setText(recommendations_text)

    def _create_kpi_card(self, title: str, value: str, subtitle: str) -> QFrame:
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setMinimumHeight(115)
        card.setStyleSheet(
            """
            QFrame {
                border: 1px solid #444;
                border-radius: 8px;
                padding: 12px;
            }
            """
        )

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 13px; color: #999;")

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("font-size: 12px; color: #888;")

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

        card.setLayout(layout)

        return card

    def _add_bar_chart(
        self,
        title: str,
        values: dict[str, int],
        row: int,
        column: int,
    ) -> None:
        chart_widget = self._create_bar_chart(title, values)
        self.chart_layout.addWidget(chart_widget, row, column)

    def _create_bar_chart(self, title: str, values: dict[str, int]) -> QWidget:
        container = QFrame()
        container.setFrameShape(QFrame.Shape.StyledPanel)
        container.setMinimumHeight(300)

        layout = QVBoxLayout()
        container.setLayout(layout)

        if not values:
            label = QLabel(f"{title}\nNot available")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 15px; color: #777;")
            layout.addWidget(label)
            return container

        figure = Figure(figsize=(5, 3), tight_layout=True)
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)

        labels = list(values.keys())
        counts = list(values.values())

        colors = [
            "#4C78A8",
            "#F58518",
            "#54A24B",
            "#E45756",
            "#72B7B2",
            "#B279A2",
            "#FF9DA6",
            "#9D755D",
        ]

        axis.bar(labels, counts, color=colors[: len(labels)])
        axis.set_title(title)
        axis.tick_params(axis="x", rotation=25)
        axis.set_ylabel("Tickets")
        axis.grid(axis="y", alpha=0.25)

        layout.addWidget(canvas)

        return container

    def _populate_preview_table(self, preview_dataframe: pd.DataFrame) -> None:
        self.preview_table.clear()
        self.preview_table.setRowCount(len(preview_dataframe))
        self.preview_table.setColumnCount(len(preview_dataframe.columns))
        self.preview_table.setHorizontalHeaderLabels(
            [str(column) for column in preview_dataframe.columns]
        )

        for row_index, (_, row) in enumerate(preview_dataframe.iterrows()):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if pd.isna(value) else str(value))
                self.preview_table.setItem(row_index, column_index, item)

    def _build_empty_mapping_controls(self) -> None:
        for row_index, (column_type, label) in enumerate(COLUMN_TYPES.items()):
            label_widget = QLabel(label)
            combo = QComboBox()
            combo.addItem(NOT_AVAILABLE_OPTION)

            self.column_combos[column_type] = combo

            self.mapping_layout.addWidget(label_widget, row_index, 0)
            self.mapping_layout.addWidget(combo, row_index, 1)

    def _populate_mapping_controls(self, columns: list[str]) -> None:
        detected_mapping = detect_column_mapping(columns)

        for column_type, combo in self.column_combos.items():
            combo.clear()
            combo.addItem(NOT_AVAILABLE_OPTION)
            combo.addItems(columns)

            detected_column = detected_mapping.get(column_type)

            if detected_column and detected_column in columns:
                combo.setCurrentText(detected_column)
            else:
                combo.setCurrentText(NOT_AVAILABLE_OPTION)

    def _get_selected_column_mapping(self) -> dict[str, str | None]:
        selected_mapping: dict[str, str | None] = {}

        for column_type, combo in self.column_combos.items():
            selected_value = combo.currentText()

            if selected_value == NOT_AVAILABLE_OPTION:
                selected_mapping[column_type] = None
            else:
                selected_mapping[column_type] = selected_value

        return selected_mapping

    def _clear_layout(self, layout: QGridLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _format_optional_value(self, value: object, suffix: str = "") -> str:
        if value is None:
            return "N/A"

        return f"{value}{suffix}"