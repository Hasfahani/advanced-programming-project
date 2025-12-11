import sys
import os
import requests
from datetime import datetime
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLineEdit, QComboBox, QLabel, QMessageBox, QDialog, QFormLayout, QInputDialog,
    QListWidgetItem
)

BACKEND_URL = "http://127.0.0.1:5000"


# ---------------------------------------------------------
# ADD NEW MEDIA WINDOW
# ---------------------------------------------------------
class AddMediaWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Media")
        self.resize(300, 250)

        layout = QFormLayout()

        self.input_name = QLineEdit()
        self.input_author = QLineEdit()
        self.input_date = QLineEdit()
        self.input_category = QComboBox()
        self.input_category.addItems(["Book", "Film", "Magazine"])
        self.input_image = QLineEdit()
        self.input_image.setPlaceholderText("Optional: images/example.jpg")

        layout.addRow("Name:", self.input_name)
        layout.addRow("Author:", self.input_author)
        layout.addRow("Publication Date:", self.input_date)
        layout.addRow("Category:", self.input_category)
        layout.addRow("Image Path:", self.input_image)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def save(self):
        data = {
            "name": self.input_name.text(),
            "author": self.input_author.text(),
            "publication_date": self.input_date.text(),
            "category": self.input_category.currentText(),
            "image": self.input_image.text(),
            "status": "available",
            "borrowed_by": None,
            "borrow_date": None,
            "due_date": None
        }

        try:
            r = requests.post(f"{BACKEND_URL}/media", json=data)
            if r.status_code == 201:
                QMessageBox.information(self, "Success", "Media added successfully!")
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Error creating media item.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ---------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Library – Advanced System")
        self.resize(900, 550)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # ----------------- CONTROLS BAR --------------------
        top_controls = QHBoxLayout()

        self.btn_dark = QPushButton("Dark Mode")
        self.btn_dark.clicked.connect(self.toggle_dark_mode)

        self.btn_all = QPushButton("Show All Media")
        self.btn_all.clicked.connect(self.load_all_media)

        self.category_box = QComboBox()
        self.category_box.addItems(["Book", "Film", "Magazine"])

        self.btn_category = QPushButton("Show by Category")
        self.btn_category.clicked.connect(self.load_by_category)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search (partial match)...")

        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.search_media)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Name A-Z", "Name Z-A"])

        self.btn_sort = QPushButton("Sort")
        self.btn_sort.clicked.connect(self.apply_sort)

        top_controls.addWidget(self.btn_dark)
        top_controls.addWidget(self.btn_all)
        top_controls.addWidget(QLabel("Category:"))
        top_controls.addWidget(self.category_box)
        top_controls.addWidget(self.btn_category)
        top_controls.addWidget(self.search_input)
        top_controls.addWidget(self.btn_search)
        top_controls.addWidget(self.sort_box)
        top_controls.addWidget(self.btn_sort)

        left_layout.addLayout(top_controls)

        # ----------------- MEDIA LIST ----------------------
        self.media_list = QListWidget()
        self.media_list.itemSelectionChanged.connect(self.update_details)
        left_layout.addWidget(self.media_list)

        # ----------------- ACTION BUTTONS -------------------
        action_btns = QHBoxLayout()

        self.btn_add = QPushButton("Add New")
        self.btn_add.clicked.connect(self.open_add_window)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_media)

        self.btn_borrow = QPushButton("Borrow")
        self.btn_borrow.clicked.connect(self.borrow_media)

        self.btn_return = QPushButton("Return")
        self.btn_return.clicked.connect(self.return_media)

        action_btns.addWidget(self.btn_add)
        action_btns.addWidget(self.btn_delete)
        action_btns.addWidget(self.btn_borrow)
        action_btns.addWidget(self.btn_return)

        left_layout.addLayout(action_btns)

        # ----------------- DETAILS PANEL -------------------
        self.details_label = QLabel("Select a media item to view details")
        self.image_label = QLabel("No image")
        self.image_label.setFixedSize(250, 350)
        self.image_label.setStyleSheet("border: 1px solid gray; text-align:center;")

        right_layout.addWidget(QLabel("Media Details:"))
        right_layout.addWidget(self.details_label)
        right_layout.addWidget(QLabel("Cover Image:"))
        right_layout.addWidget(self.image_label)

        main_layout.addLayout(left_layout, 70)
        main_layout.addLayout(right_layout, 30)

        self.setLayout(main_layout)

        self.dark_mode = False
        self.apply_light_mode()

        self.load_all_media()

    # -----------------------------------------------------
    # UI THEMES
    # -----------------------------------------------------
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QPushButton { background-color: #333; color: white; padding: 6px; }
            QListWidget { background-color: #2c2c2c; color: white; }
        """)

    def apply_light_mode(self):
        self.setStyleSheet("""
            QWidget { background-color: white; color: black; }
            QPushButton { background-color: #f0f0f0; padding: 6px; }
            QListWidget { background-color: white; }
        """)

    # -----------------------------------------------------
    # LOAD & DISPLAY MEDIA
    # -----------------------------------------------------
    def load_all_media(self):
        try:
            r = requests.get(f"{BACKEND_URL}/media")
            if r.status_code != 200:
                QMessageBox.warning(self, "Error", "Could not load media.")
                return

            data = r.json()
            self.media_list.clear()

            for name, item in data.items():
                self.add_media_list_item(name, item)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_media_list_item(self, name, item):
        status = item.get("status")
        due_date = item.get("due_date")

        display_name = name
        list_item = QListWidgetItem(display_name)

        # Overdue detection
        if status == "borrowed" and due_date:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            if datetime.now() > due:
                list_item.setForeground(QColor("red"))
                list_item.setText(f"{name} (OVERDUE)")
            else:
                list_item.setForeground(QColor("orange"))
                list_item.setText(f"{name} (Borrowed)")

        self.media_list.addItem(list_item)

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------
    def search_media(self):
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.information(self, "Info", "Enter search text.")
            return

        r = requests.get(f"{BACKEND_URL}/media/search/{query}")
        data = r.json()

        self.media_list.clear()

        for name, item in data.items():
            self.add_media_list_item(name, item)

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------
    def apply_sort(self):
        items = []
        for i in range(self.media_list.count()):
            items.append(self.media_list.item(i).text())

        reverse = (self.sort_box.currentText() == "Name Z-A")
        items.sort(reverse=reverse)

        self.media_list.clear()
        for item in items:
            self.media_list.addItem(item)

    # -----------------------------------------------------
    # CATEGORY FILTER
    # -----------------------------------------------------
    def load_by_category(self):
        category = self.category_box.currentText()
        r = requests.get(f"{BACKEND_URL}/media/category/{category}")
        data = r.json()

        self.media_list.clear()
        for name, item in data.items():
            self.add_media_list_item(name, item)

    # -----------------------------------------------------
    # DETAILS PANEL
    # -----------------------------------------------------
    def update_details(self):
        selected = self.media_list.currentItem()
        if not selected:
            return

        name = selected.text().replace(" (Borrowed)", "").replace(" (OVERDUE)", "")
        r = requests.get(f"{BACKEND_URL}/media/{name}")

        if r.status_code != 200:
            return

        item = r.json()

        details = (
            f"<b>Name:</b> {item['name']}<br>"
            f"<b>Author:</b> {item['author']}<br>"
            f"<b>Date:</b> {item['publication_date']}<br>"
            f"<b>Category:</b> {item['category']}<br>"
            f"<b>Status:</b> {item['status']}<br>"
            f"<b>Borrowed By:</b> {item.get('borrowed_by')}<br>"
            f"<b>Borrow Date:</b> {item.get('borrow_date')}<br>"
            f"<b>Due Date:</b> {item.get('due_date')}<br>"
        )

        self.details_label.setText(details)

        image_path = item.get("image")
        if image_path and os.path.exists(image_path):
            pix = QPixmap(image_path).scaled(250, 350)
            self.image_label.setPixmap(pix)
        else:
            self.image_label.setText("No image")

    # -----------------------------------------------------
    # ADD / DELETE
    # -----------------------------------------------------
    def open_add_window(self):
        window = AddMediaWindow()
        window.exec_()
        self.load_all_media()

    def delete_media(self):
        selected = self.media_list.currentItem()
        if not selected:
            return QMessageBox.warning(self, "Error", "Select an item")

        name = selected.text().split(" (")[0]
        r = requests.delete(f"{BACKEND_URL}/media/{name}")

        if r.status_code == 200:
            QMessageBox.information(self, "Success", "Media deleted.")
            self.load_all_media()
        else:
            QMessageBox.warning(self, "Error", "Could not delete media.")

    # -----------------------------------------------------
    # BORROW / RETURN
    # -----------------------------------------------------
    def borrow_media(self):
        selected = self.media_list.currentItem()
        if not selected:
            return QMessageBox.warning(self, "Error", "Select item")

        name = selected.text().split(" (")[0]

        borrower, ok = QInputDialog.getText(self, "Borrow", "Name of borrower:")
        if not ok or borrower.strip() == "":
            return

        days, ok = QInputDialog.getInt(self, "Borrow Duration", "Days:", min=1, max=365)
        if not ok:
            return

        payload = {
            "borrowed_by": borrower,
            "days": days
        }

        r = requests.post(f"{BACKEND_URL}/media/{name}/borrow", json=payload)

        if r.status_code == 200:
            QMessageBox.information(self, "Success", "Item borrowed.")
            self.load_all_media()
        else:
            QMessageBox.warning(self, "Error", r.json().get("error", ""))

    def return_media(self):
        selected = self.media_list.currentItem()
        if not selected:
            return QMessageBox.warning(self, "Error", "Select item")

        name = selected.text().split(" (")[0]

        r = requests.post(f"{BACKEND_URL}/media/{name}/return")

        if r.status_code == 200:
            QMessageBox.information(self, "Success", "Item returned.")
            self.load_all_media()
        else:
            QMessageBox.warning(self, "Error", r.json().get("error", ""))


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
