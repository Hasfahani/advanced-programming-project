import sys
import os
import requests
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLabel, QPushButton, QComboBox,
    QLineEdit, QMessageBox, QDialog, QFormLayout,
    QListWidgetItem, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

BACKEND_URL = "http://127.0.0.1:5000"
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "picss")


# ---------------------------------------------------------
# BORROW DIALOG
# ---------------------------------------------------------
class BorrowDialog(QDialog):
    def __init__(self, media_name):
        super().__init__()
        self.setWindowTitle("Borrow Media")
        self.media_name = media_name
        self.resize(300, 150)

        layout = QFormLayout()

        self.input_name = QLineEdit()
        self.input_days = QLineEdit()
        self.input_days.setPlaceholderText("Number of days")

        layout.addRow("Borrower Name:", self.input_name)
        layout.addRow("Days:", self.input_days)

        btn = QPushButton("Confirm Borrow")
        btn.clicked.connect(self.accept)
        layout.addRow(btn)

        self.setLayout(layout)

    def get_data(self):
        return self.input_name.text(), self.input_days.text()


# ---------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Media Library")
        self.resize(1100, 650)

        self.current_data = {}

        main_layout = QHBoxLayout(self)

        # LEFT SIDE
        left_layout = QVBoxLayout()

        title = QLabel("📚 Media Library")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        left_layout.addWidget(title)

        controls = QHBoxLayout()
        self.category_box = QComboBox()
        self.category_box.addItems(["All", "Book", "Film", "Magazine"])
        self.category_box.currentTextChanged.connect(self.load_media)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.search_media)

        controls.addWidget(self.category_box)
        controls.addWidget(self.search_input)
        left_layout.addLayout(controls)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.show_details)
        left_layout.addWidget(self.list_widget)

        action_layout = QHBoxLayout()
        self.btn_borrow = QPushButton("Borrow")
        self.btn_return = QPushButton("Return")
        self.btn_borrow.clicked.connect(self.borrow_media)
        self.btn_return.clicked.connect(self.return_media)
        action_layout.addWidget(self.btn_borrow)
        action_layout.addWidget(self.btn_return)
        left_layout.addLayout(action_layout)

        # RIGHT SIDE
        right_layout = QVBoxLayout()

        self.details = QLabel("Select an item to view details")
        self.details.setWordWrap(True)
        self.details.setAlignment(Qt.AlignTop)
        self.details.setFont(QFont("Arial", 11))

        self.image = QLabel("No Image")
        self.image.setAlignment(Qt.AlignCenter)
        self.image.setFixedSize(300, 420)
        self.image.setStyleSheet("border: 1px solid #ccc; background:#f5f5f5;")

        right_layout.addWidget(QLabel("Details", font=QFont("Arial", 12, QFont.Bold)))
        right_layout.addWidget(self.details)
        right_layout.addWidget(QLabel("Cover", font=QFont("Arial", 12, QFont.Bold)))
        right_layout.addWidget(self.image)
        right_layout.addStretch()

        # SPLITTER
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        self.load_media()

    # -----------------------------------------------------
    def load_media(self):
        try:
            if self.category_box.currentText() == "All":
                r = requests.get(f"{BACKEND_URL}/media")
            else:
                cat = self.category_box.currentText()
                r = requests.get(f"{BACKEND_URL}/media/category/{cat}")

            self.current_data = r.json()
            self.update_list(self.current_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_list(self, data):
        self.list_widget.clear()
        for name, item in data.items():
            text = name
            if item["status"] == "borrowed":
                if self.is_overdue(item):
                    text += " 🔴 OVERDUE"
                else:
                    text += " 🔒 Borrowed"

            lw = QListWidgetItem(text)
            self.list_widget.addItem(lw)

    def search_media(self):
        query = self.search_input.text().lower()
        filtered = {
            k: v for k, v in self.current_data.items()
            if query in k.lower()
        }
        self.update_list(filtered)

    # -----------------------------------------------------
    def show_details(self, item):
        name = item.text().replace(" 🔒 Borrowed", "").replace(" 🔴 OVERDUE", "")
        media = self.current_data.get(name)
        if not media:
            return

        status = media["status"].upper()
        if status == "BORROWED" and self.is_overdue(media):
            status = "OVERDUE"

        text = (
            f"<b>Title:</b> {media['name']}<br>"
            f"<b>Author:</b> {media['author']}<br>"
            f"<b>Year:</b> {media['publication_date']}<br>"
            f"<b>Category:</b> {media['category']}<br>"
            f"<b>Status:</b> {status}<br>"
        )

        if media["status"] == "borrowed":
            text += (
                f"<b>Borrowed By:</b> {media['borrowed_by']}<br>"
                f"<b>Due Date:</b> {media['due_date']}<br>"
            )

        self.details.setText(text)
        self.load_image(media.get("image"))

    def load_image(self, filename):
        self.image.clear()
        if not filename:
            self.image.setText("No Image")
            return

        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            pix = QPixmap(path).scaled(
                self.image.width(),
                self.image.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image.setPixmap(pix)
        else:
            self.image.setText("Image not found")

    # -----------------------------------------------------
    def borrow_media(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        name = item.text().split(" 🔒")[0].split(" 🔴")[0]
        dialog = BorrowDialog(name)
        if dialog.exec_():
            borrower, days = dialog.get_data()
            try:
                days = int(days)
                requests.post(
                    f"{BACKEND_URL}/media/{name}/borrow",
                    json={"borrowed_by": borrower, "days": days}
                )
                self.load_media()
            except:
                QMessageBox.warning(self, "Error", "Invalid borrow data")

    def return_media(self):
        item = self.list_widget.currentItem()
        if not item:
            return

        name = item.text().split(" 🔒")[0].split(" 🔴")[0]
        requests.post(f"{BACKEND_URL}/media/{name}/return")
        self.load_media()

    # -----------------------------------------------------
    def is_overdue(self, media):
        if not media.get("due_date"):
            return False
        return datetime.now().date() > datetime.strptime(media["due_date"], "%Y-%m-%d").date()


# ---------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
