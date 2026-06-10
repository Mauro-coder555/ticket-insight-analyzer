from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Ticket Insight Analyzer")
        self.resize(1000, 700)

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

        load_button = QPushButton("Load CSV")
        load_button.setMinimumHeight(40)

        placeholder_label = QLabel(
            "Next step: connect this button to a CSV file picker and preview table."
        )
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("color: #777;")

        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(24)
        layout.addWidget(load_button)
        layout.addSpacing(24)
        layout.addWidget(placeholder_label)
        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)