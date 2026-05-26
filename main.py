import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap
from src.uiitems.close_button import CloseButton
from src.assets.create_folders_from_csv import create_folders_from_csv


class CSVFolderGeneratorApp(QWidget):
    # ============================================
    # APPLICATION DIMENSIONS
    # ============================================
    APP_WIDTH = 640
    APP_HEIGHT = 880

    def __init__(self):
        super().__init__()
        self.csv_path = ""
        self.output_folder = ""
        self.setMouseTracking(True)
        self.oldPos = self.pos()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("App")
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)

        self.setStyleSheet("""
            QWidget {
                font-family: 'Arial';
                background-color: transparent;
                border: 2px solid #CDEBF0;
                border-radius: 20px;
            }
            QPushButton {
                background-color: #CDEBF0;
                color: black;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #BEE0E8;
            }
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                margin: 10px;
            }
        """)

        label_style = """
            font-size: 14px; color: black;
            background-color: #CDEBF0;
            border-radius: 20px;
            text-decoration: underline;
            padding: 20px;
        """
        start_style = """
            font-size: 14px; color: #CDEBF0;
            background-color: black;
            border-radius: 20px;
            text-decoration: underline;
            padding: 20px;
        """

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addLayout(self._create_title_bar())
        layout.addWidget(self._create_logo_label())

        # ── Header 1 (required) ──────────────────────────────────────────
        self.header1_input = self._create_line_edit(
            "Header 1 — column name (required)", label_style
        )

        # ── Header 2 (optional) ─────────────────────────────────────────
        self.header2_input = self._create_line_edit(
            "Header 2 — column name (optional)", label_style
        )

        # ── File / folder pickers ────────────────────────────────────────
        self.csv_label = self._create_path_label("No CSV file selected")
        self.out_label = self._create_path_label("No output folder selected (defaults to CSV directory)")

        csv_btn = self._create_button("Select CSV File",      self._select_csv_file)
        out_btn = self._create_button("Select Output Folder", self._select_output_folder)

        # ── Start ────────────────────────────────────────────────────────
        start_btn = self._create_button("Start Creating Folders", self._start, start_style)

        # ── Assemble ─────────────────────────────────────────────────────
        for w in (
            self.header1_input,
            self.header2_input,
            csv_btn,
            self.csv_label,
            out_btn,
            self.out_label,
            start_btn,
        ):
            layout.addWidget(w)

        self.setLayout(layout)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _create_line_edit(self, placeholder, style):
        le = QLineEdit(self)
        le.setPlaceholderText(placeholder)
        le.setStyleSheet(style)
        return le

    def _create_path_label(self, text):
        lbl = QLabel(text, self)
        lbl.setStyleSheet(
            "font-size: 11px; color: #555; background: transparent; "
            "border: none; margin-left: 14px; margin-bottom: 2px;"
        )
        lbl.setWordWrap(True)
        return lbl

    def _create_button(self, text, slot, style=None):
        btn = QPushButton(text, self)
        btn.clicked.connect(slot)
        if style:
            btn.setStyleSheet(style)
        return btn

    def _separator(self):
        """Default separator character."""
        return "_"

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _select_csv_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if path:
            self.csv_path = path
            self.csv_label.setText(f"CSV: {path}")

    def _select_output_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_folder = path
            self.out_label.setText(f"Output: {path}")

    def _start(self):
        h1 = self.header1_input.text().strip()
        h2 = self.header2_input.text().strip()

        if not h1:
            QMessageBox.warning(self, "Input Error", "Please enter at least Header 1.")
            return
        if not self.csv_path:
            QMessageBox.warning(self, "Input Error", "Please select a CSV file.")
            return

        headers = [h1] + ([h2] if h2 else [])

        output_dir = self.output_folder or os.path.join(
            os.path.dirname(self.csv_path), "generated_folders"
        )

        try:
            created = create_folders_from_csv(
                csv_file=self.csv_path,
                headers=headers,
                base_path=output_dir,
                separator=self._separator(),
            )
            self._show_message(
                "Success",
                f"Created {len(created)} folder(s) in:\n{output_dir}"
            )
        except ValueError as e:
            QMessageBox.warning(self, "Header Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

    def _show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.CustomizeWindowHint)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #BEE0E8;
                font-size: 16px;
            }
            QPushButton {
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                background-color: #BEE0E8;
                padding: 6px;
                font-size: 24px;
                min-width: 70px;
                min-height: 30px;
            }
            QPushButton:hover { background-color: #BEE0E8; }
        """)
        msg.exec_()

    # ── Title bar / logo ──────────────────────────────────────────────────────

    def _create_title_bar(self):
        bar = QHBoxLayout()
        bar.addWidget(CloseButton(self), alignment=Qt.AlignRight)
        return bar

    def _create_logo_label(self):
        logo = QLabel(self)
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        cover_path = os.path.join(base_path, "static", "cover.png")
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(600, 800)
        else:
            pixmap = QPixmap(600, 800)
            pixmap.fill(Qt.lightGray)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        return logo

    # ── Window drag ───────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVFolderGeneratorApp()
    window.show()
    sys.exit(app.exec_())
