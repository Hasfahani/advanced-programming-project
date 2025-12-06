import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QComboBox, QLabel, QMessageBox,
    QDialog, QFormLayout
)

BACKEND_URL = "http://127.0.0.1:5000"

class AddMediaWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Media")
        self.resize(300, 200)

        layout = QFormLayout()

        self.input_name = QLineEdit()
        self.input_author = QLineEdit()
        self.input_date = QLineEdit()
        self.input_category = QComboBox()
        self.input_category.addItems(["Book", "Film", "Magazine"])

        layout.addRow("Name:", self.input_name)
        layout.addRow("Author:", self.input_author)
        layout.addRow("Publication Date:", self.input_date)
        layout.addRow("Category:", self.input_category)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)

        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def save(self):
        data = {
            "name": self.input_name.text(),
            "author": self.input_author.text(),
            "publication_date": self.input_date.text(),
            "category": self.input_category.currentText()
        }

        try:
            r = requests.post(f"{BACKEND_URL}/media", json=data)
            if r.status_code == 201:
                QMessageBox.information(self, "Success", "Media added successfully!")
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Could not add media.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Online Library")
        self.resize(700, 500)

        main_layout = QVBoxLayout()

        # --- Top controls: buttons, category, search ---
        top_layout = QHBoxLayout()

        self.btn_all = QPushButton("Show All Media")
        self.btn_all.clicked.connect(self.load_all_media)

        self.category_box = QComboBox()
        self.category_box.addItems(["Book", "Film", "Magazine"])

        self.btn_category = QPushButton("Show by Category")
        self.btn_category.clicked.connect(self.load_by_category)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter exact media name")

        self.btn_search = QPushButton("Search by Name")
        self.btn_search.clicked.connect(self.search_by_name)

        top_layout.addWidget(self.btn_all)
        top_layout.addWidget(QLabel("Category:"))
        top_layout.addWidget(self.category_box)
        top_layout.addWidget(self.btn_category)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.btn_search)

        # --- Add New Media Button ---
        bottom_layout = QHBoxLayout()
        
        self.btn_add_media = QPushButton("Add New Media")
        self.btn_add_media.clicked.connect(self.open_add_window)
        bottom_layout.addWidget(self.btn_add_media)

        self.btn_delete_media = QPushButton("Delete Selected Media")
        self.btn_delete_media.clicked.connect(self.delete_media)
        bottom_layout.addWidget(self.btn_delete_media)

        # --- List of media ---
        self.media_list = QListWidget()

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.media_list)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def load_all_media(self):
        """Load all media from backend and show in the list."""
        try:
            response = requests.get(f"{BACKEND_URL}/media")
            if response.status_code == 200:
                data = response.json()
                self.media_list.clear()
                for name in data.keys():
                    self.media_list.addItem(name)
            else:
                QMessageBox.warning(self, "Error", "Could not load media.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_by_category(self):
        """Load media of the selected category."""
        category = self.category_box.currentText()
        try:
            response = requests.get(f"{BACKEND_URL}/media/category/{category}")
            if response.status_code == 200:
                data = response.json()
                self.media_list.clear()
                for name in data.keys():
                    self.media_list.addItem(name)
            else:
                QMessageBox.warning(self, "Error", "Could not load by category.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def search_by_name(self):
        """Search a media item by its exact name and show details in a message box."""
        name = self.search_input.text()
        if not name:
            QMessageBox.information(self, "Info", "Please enter a media name.")
            return
        try:
            response = requests.get(f"{BACKEND_URL}/media/search/{name}")
            if response.status_code == 200:
                item = response.json()
                # Show the metadata in a simple way
                text = (
                    f"Name: {item.get('name')}\n"
                    f"Author: {item.get('author')}\n"
                    f"Publication Date: {item.get('publication_date')}\n"
                    f"Category: {item.get('category')}"
                )
                QMessageBox.information(self, "Media Found", text)
            else:
                QMessageBox.warning(self, "Not found", "Media not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_new_media(self):
        """Open the Add Media dialog window."""
        dialog = AddMediaWindow()
        dialog.exec_()

    def open_add_window(self):
        window = AddMediaWindow()
        window.exec_()
        self.load_all_media()

    def delete_media(self):
        """Delete the selected media item."""
        selected_item = self.media_list.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Info", "Please select a media item to delete.")
            return
        
        name = selected_item.text()
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(f"{BACKEND_URL}/media/{name}")
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Media deleted successfully!")
                    self.load_all_media()
                else:
                    QMessageBox.warning(self, "Error", "Could not delete media.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
