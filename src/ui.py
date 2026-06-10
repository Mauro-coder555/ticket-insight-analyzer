from pathlib import Path

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.analyzer import analyze_tickets
from src.column_mapper import COLUMN_TYPES, detect_column_mapping
from src.csv_loader import get_preview_rows, load_csv
from src.report import build_markdown_report, save_markdown_report


NOT_AVAILABLE_OPTION = "Not available"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.dataframe: pd.DataFrame | None = None
        self.source_file_path: Path | None = None
        self.analysis_result: dict | None = None
        self.column_combos: dict[str, QComboBox] = {}

        self.setWindowTitle("Ticket Insight Analyzer")
        self.resize(1200, 800)

        self._setup_ui()

    def _setup_ui(self) -> None:
        title_label = QLabel("Ticket Insight Analyzer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        subtitle_label = QLabel(
            "Load a CSV file with support tickets and generate backlog insights."
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; color: #555;")

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("color: #555;")

        load_button = QPushButton("Load CSV")
        load_button.setMinimumHeight(36)
        load_button.clicked.connect(self.load_csv_file)

        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(220)
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.mapping_group = QGroupBox("Column Mapping")
        self.mapping_layout = QGridLayout()
        self.mapping_group.setLayout(self.mapping_layout)

        analyze_button = QPushButton("Analyze")
        analyze_button.setMinimumHeight(36)
        analyze_button.clicked.connect(self.run_analysis)

        export_button = QPushButton("Export Markdown Report")
        export_button.setMinimumHeight(36)
        export_button.clicked.connect(self.export_report)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Analysis results will appear here.")
        self.results_text.setMinimumHeight(260)

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(self.file_label)
        layout.addWidget(load_button)
        layout.addWidget(QLabel("CSV Preview"))
        layout.addWidget(self.preview_table)
        layout.addWidget(self.mapping_group)
        layout.addWidget(analyze_button)
        layout.addWidget(export_button)
        layout.addWidget(QLabel("Results"))
        layout.addWidget(self.results_text)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        self._build_empty_mapping_controls()

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
        self.results_text.clear()

        self._populate_preview_table(get_preview_rows(dataframe))
        self._populate_mapping_controls(dataframe.columns.tolist())

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

        source_file_name = (
            self.source_file_path.name
            if self.source_file_path is not None
            else "unknown_file.csv"
        )

        markdown_preview = build_markdown_report(
            analysis_result=self.analysis_result,
            source_file_name=source_file_name,
        )

        self.results_text.setPlainText(markdown_preview)

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

        QMessageBox.information(
            self,
            "Report Exported",
            f"Markdown report saved at:\n{output_path}",
        )

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