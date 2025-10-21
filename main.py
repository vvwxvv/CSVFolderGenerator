import sys
import os
import csv
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
from src.assets.create_folders_from_csv import create_folders_from_csv_language_en, create_folders_from_csv_auto_en


class CSVFolderGeneratorApp(QWidget):
    # ============================================
    # APPLICATION DIMENSIONS
    # ============================================
    APP_WIDTH = 640   # Application window width in pixels
    APP_HEIGHT = 880  # Application window height in pixels
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.csv_path = ""
        self.output_folder = ""  # Store selected output folder
        self.use_auto_en_mode = False  # False = language filter, True = auto _en
        self.setMouseTracking(True)
        self.oldPos = self.pos()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("App")

        self.setStyleSheet(
            """
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
        """
        )
        
        label_style = """
        font-size: 14px; 
        color:black; 
        background-color: #CDEBF0;
        border-radius: 20px;
        text-decoration:underline;
        padding:20px;
        """

        cooking_style = """
        font-size: 14px; 
        color: #CDEBF0; 
        background-color:black;
        border-radius: 20px;
        text-decoration:underline;
        padding:20px;
        """

        toggle_style = """
        font-size: 13px; 
        color: white; 
        background-color: #4CAF50;
        border-radius: 8px;
        padding: 12px;
        margin: 10px;
        font-weight: bold;
        """

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(self.create_title_bar())
        layout.addWidget(self.create_logo_label())

        # Set application window dimensions
        self.resize(self.APP_WIDTH, self.APP_HEIGHT)

        # Toggle button for mode switching
        self.toggle_button = self.create_button(
            "Mode: Language Filter (EN)",
            self.toggle_mode,
            toggle_style
        )
        layout.addWidget(self.toggle_button)

        # CSV Header input
        self.header_input = self.create_line_edit(
            "Enter CSV Headers (comma separated, e.g., year,title,size)", 
            label_style
        )
        
        # Select CSV button
        self.csv_button = self.create_button(
            "Select CSV File", 
            self.select_csv_file
        )
        
        # Select Output Folder button
        self.output_folder_button = self.create_button(
            "Select Output Folder", 
            self.select_output_folder
        )

        layout.addWidget(self.header_input)
        layout.addWidget(self.csv_button)
        layout.addWidget(self.output_folder_button)

        # Start button
        layout.addWidget(
            self.create_button(
                "Start Creating Folders",
                self.start_folder_creation,
                cooking_style,
            )
        )

        self.setLayout(layout)

    def toggle_mode(self):
        """Toggle between language filter mode and auto _en mode"""
        self.use_auto_en_mode = not self.use_auto_en_mode
        
        if self.use_auto_en_mode:
            self.toggle_button.setText("Mode: Auto _EN Suffix")
            self.toggle_button.setStyleSheet("""
                font-size: 13px; 
                color: white; 
                background-color: #FF9800;
                border-radius: 8px;
                padding: 12px;
                margin: 10px;
                font-weight: bold;
            """)
        else:
            self.toggle_button.setText("Mode: Language Filter (EN)")
            self.toggle_button.setStyleSheet("""
                font-size: 13px; 
                color: white; 
                background-color: #4CAF50;
                border-radius: 8px;
                padding: 12px;
                margin: 10px;
                font-weight: bold;
            """)

    def show_custom_message(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.CustomizeWindowHint)
        msg.setStyleSheet(
            """
        QMessageBox {
            background-color: #BEE0E8;
            color: white;
            font-size: 16px;
        }
        QPushButton {
            color: white;
            border: 2px solid white;
            border-radius: 8px;
            color: white;
            background-color: #BEE0E8;
            padding: 6px;
            font-size: 24px;
            min-width: 70px;
            min-height: 30px;
        }
        QPushButton:hover {
            background-color:  #BEE0E8;
        }
    """
        )
        msg.exec_()

    def create_line_edit(self, placeholder, style):
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet(style)
        return line_edit

    def create_button(self, text, slot, style=None):
        button = QPushButton(text, self)
        button.clicked.connect(slot)
        button.setStyleSheet(
            style
            if style
            else """
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
        """
        )
        return button

    def select_csv_file(self):
        csv_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select CSV File", 
            "", 
            "CSV Files (*.csv)"
        )
        if csv_path:
            self.csv_path = csv_path
    
    def select_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Folder"
        )
        if output_folder:
            self.output_folder = output_folder

    def create_title_bar(self):
        title_bar = QHBoxLayout()
        close_button = CloseButton(self)
        title_bar.addWidget(close_button, alignment=Qt.AlignRight)
        return title_bar

    def create_logo_label(self):
        logo = QLabel(self)
        if getattr(sys, "frozen", False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        cover_path = os.path.join(base_path, "static", "logo_imgs", "cover.png")
        # Scale cover image to match application width (100px wider than original)
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(600, 800)
        else:
            print(f"Warning: Cover image not found at {cover_path}")
            pixmap = QPixmap(600, 800)
            pixmap.fill(Qt.lightGray)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        return logo

    def start_folder_creation(self):
        if not self.header_input.text() or not self.csv_path:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter CSV headers and select a CSV file.",
            )
            return
        
        headers_text = self.header_input.text()
        header_list = [h.strip() for h in headers_text.split(',') if h.strip()]
        
        if not header_list:
            QMessageBox.warning(
                self,
                "Input Error",
                "Please enter at least one header name.",
            )
            return
        
        try:
            # Use selected output folder or default to CSV directory
            if self.output_folder:
                output_dir = self.output_folder
            else:
                csv_dir = os.path.dirname(self.csv_path)
                output_dir = os.path.join(csv_dir, "generated_folders")
            
            # Call the appropriate function based on mode
            if self.use_auto_en_mode:
                created_folders = create_folders_from_csv_auto_en(
                    self.csv_path,
                    header_list,
                    output_dir
                )
                mode_text = "Auto _EN Suffix"
            else:
                created_folders = create_folders_from_csv_language_en(
                    self.csv_path,
                    header_list,
                    output_dir
                )
                mode_text = "Language Filter (EN)"
            
            self.show_custom_message(
                "Success",
                f"Mode: {mode_text}\n\nSuccessfully created {len(created_folders)} folders in:\n{output_dir}"
            )
            
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Header Error",
                str(e)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred:\n{str(e)}"
            )

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