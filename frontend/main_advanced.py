import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QComboBox, QLabel, QMessageBox,
    QDialog, QFormLayout, QListWidgetItem, QSplitter, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

BACKEND_URL = "http://127.0.0.1:5000"

class AddMediaWindow(QDialog):
    """Dialog window for adding new media items."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Media")
        self.resize(400, 300)

        layout = QFormLayout()

        # Input fields
        self.input_name = QLineEdit()
        self.input_author = QLineEdit()
        self.input_date = QLineEdit()
        self.input_category = QComboBox()
        self.input_category.addItems(["Book", "Film", "Magazine"])
        
        # Image path input with browse button
        image_layout = QHBoxLayout()
        self.input_image = QLineEdit()
        self.input_image.setPlaceholderText("Optional: path to image")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_image)
        image_layout.addWidget(self.input_image)
        image_layout.addWidget(self.btn_browse)

        # Add fields to form
        layout.addRow("Name:", self.input_name)
        layout.addRow("Author:", self.input_author)
        layout.addRow("Publication Date:", self.input_date)
        layout.addRow("Category:", self.input_category)
        layout.addRow("Image:", image_layout)

        # Save button
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        layout.addRow(self.btn_save)

        self.setLayout(layout)

    def browse_image(self):
        """Open file dialog to select an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.input_image.setText(file_path)

    def save(self):
        """Save the new media item to the backend."""
        data = {
            "name": self.input_name.text(),
            "author": self.input_author.text(),
            "publication_date": self.input_date.text(),
            "category": self.input_category.currentText(),
            "image": self.input_image.text(),
            "status": "available"
        }

        # Validation
        if not data["name"] or not data["author"] or not data["publication_date"]:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return

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
    """Main application window with advanced features."""
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Online Library - Advanced System")
        self.resize(1100, 650)
        
        # Track current theme
        self.is_dark_mode = False

        # Main horizontal layout
        main_layout = QHBoxLayout()

        # Left side: controls and list
        left_layout = QVBoxLayout()

        # --- Theme toggle ---
        theme_layout = QHBoxLayout()
        self.btn_theme = QPushButton("🌙 Dark Mode")
        self.btn_theme.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.btn_theme)
        theme_layout.addStretch()

        # --- Control buttons row 1 ---
        controls_layout1 = QHBoxLayout()
        self.btn_all = QPushButton("Show All Media")
        self.btn_all.clicked.connect(self.load_all_media)
        self.category_box = QComboBox()
        self.category_box.addItems(["Book", "Film", "Magazine"])
        self.btn_category = QPushButton("Show by Category")
        self.btn_category.clicked.connect(self.load_by_category)
        controls_layout1.addWidget(self.btn_all)
        controls_layout1.addWidget(QLabel("Category:"))
        controls_layout1.addWidget(self.category_box)
        controls_layout1.addWidget(self.btn_category)

        # --- Search and sorting row ---
        controls_layout2 = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search (partial match)")
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.search_by_name)
        self.sort_box = QComboBox()
        self.sort_box.addItems(["Sort: Name A-Z", "Sort: Name Z-A", "Sort: Category", 
                                "Sort: Year (Old-New)", "Sort: Year (New-Old)"])
        self.sort_box.currentIndexChanged.connect(self.apply_sort)
        controls_layout2.addWidget(self.search_input)
        controls_layout2.addWidget(self.btn_search)
        controls_layout2.addWidget(self.sort_box)

        # --- Media list ---
        self.media_list = QListWidget()
        self.media_list.itemClicked.connect(self.show_media_details)

        # --- Bottom action buttons ---
        action_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add New")
        self.btn_add.clicked.connect(self.open_add_window)
        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.clicked.connect(self.delete_media)
        self.btn_borrow = QPushButton("📖 Borrow")
        self.btn_borrow.clicked.connect(self.borrow_media)
        self.btn_return = QPushButton("↩️ Return")
        self.btn_return.clicked.connect(self.return_media)
        action_layout.addWidget(self.btn_add)
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_borrow)
        action_layout.addWidget(self.btn_return)

        # Add to left layout
        left_layout.addLayout(theme_layout)
        left_layout.addLayout(controls_layout1)
        left_layout.addLayout(controls_layout2)
        left_layout.addWidget(self.media_list)
        left_layout.addLayout(action_layout)

        # Right side: media details and image
        right_layout = QVBoxLayout()
        self.detail_label = QLabel("Select a media item to view details")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignTop)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 400)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.image_label.setText("No image")
        right_layout.addWidget(QLabel("<b>Media Details:</b>"))
        right_layout.addWidget(self.detail_label)
        right_layout.addWidget(QLabel("<b>Cover Image:</b>"))
        right_layout.addWidget(self.image_label)
        right_layout.addStretch()

        # Create widgets and splitter
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
        self.setLayout(main_layout)

        # Store media data for sorting
        self.current_media_data = {}
        self.load_all_media()

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QPushButton { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; padding: 5px; border-radius: 3px; }
                QPushButton:hover { background-color: #4d4d4d; }
                QLineEdit, QComboBox { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; padding: 3px; }
                QListWidget { background-color: #3d3d3d; color: #ffffff; border: 1px solid #555; }
                QLabel { color: #ffffff; }
            """)
            self.btn_theme.setText("☀️ Light Mode")
            self.image_label.setStyleSheet("border: 1px solid #555; background-color: #3d3d3d;")
        else:
            self.setStyleSheet("")
            self.btn_theme.setText("🌙 Dark Mode")
            self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")

    def load_all_media(self):
        """Load all media from backend."""
        try:
            response = requests.get(f"{BACKEND_URL}/media")
            if response.status_code == 200:
                self.current_media_data = response.json()
                self.display_media_list(self.current_media_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def display_media_list(self, media_data):
        """Display media items in list (grey out borrowed items)."""
        self.media_list.clear()
        for name, item in media_data.items():
            list_item = QListWidgetItem(name)
            if item.get("status") == "borrowed":
                list_item.setForeground(Qt.gray)
                list_item.setText(f"{name} [BORROWED]")
            self.media_list.addItem(list_item)

    def load_by_category(self):
        """Load media by category."""
        category = self.category_box.currentText()
        try:
            response = requests.get(f"{BACKEND_URL}/media/category/{category}")
            if response.status_code == 200:
                self.current_media_data = response.json()
                self.display_media_list(self.current_media_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def search_by_name(self):
        """Search with partial match."""
        query = self.search_input.text()
        if not query:
            QMessageBox.information(self, "Info", "Please enter a search term.")
            return
        try:
            response = requests.get(f"{BACKEND_URL}/media/search/{query}")
            if response.status_code == 200:
                self.current_media_data = response.json()
                if not self.current_media_data:
                    QMessageBox.information(self, "No Results", "No media found.")
                self.display_media_list(self.current_media_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def apply_sort(self):
        """Apply sorting to media list."""
        sort_option = self.sort_box.currentText()
        if not self.current_media_data:
            return
        
        items = list(self.current_media_data.items())
        if sort_option == "Sort: Name A-Z":
            items.sort(key=lambda x: x[0].lower())
        elif sort_option == "Sort: Name Z-A":
            items.sort(key=lambda x: x[0].lower(), reverse=True)
        elif sort_option == "Sort: Category":
            items.sort(key=lambda x: x[1].get("category", ""))
        elif sort_option == "Sort: Year (Old-New)":
            items.sort(key=lambda x: x[1].get("publication_date", "0"))
        elif sort_option == "Sort: Year (New-Old)":
            items.sort(key=lambda x: x[1].get("publication_date", "0"), reverse=True)
        
        sorted_data = {name: item for name, item in items}
        self.current_media_data = sorted_data
        self.display_media_list(sorted_data)

    def show_media_details(self, item):
        """Display details and image of selected media."""
        name = item.text().replace(" [BORROWED]", "")
        media = self.current_media_data.get(name)
        if not media:
            return
        
        status_text = "📗 Available" if media.get("status") == "available" else "📕 Borrowed"
        details = (
            f"<b>Name:</b> {media.get('name')}<br>"
            f"<b>Author:</b> {media.get('author')}<br>"
            f"<b>Publication Date:</b> {media.get('publication_date')}<br>"
            f"<b>Category:</b> {media.get('category')}<br>"
            f"<b>Status:</b> {status_text}"
        )
        self.detail_label.setText(details)
        
        image_path = media.get("image", "")
        if image_path and image_path.strip():
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(280, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    self.image_label.setText("Image not found")
                    self.image_label.setPixmap(QPixmap())
            except:
                self.image_label.setText("Error loading image")
                self.image_label.setPixmap(QPixmap())
        else:
            self.image_label.setText("No image available")
            self.image_label.setPixmap(QPixmap())

    def open_add_window(self):
        """Open add media dialog."""
        dialog = AddMediaWindow()
        dialog.exec_()
        self.load_all_media()

    def delete_media(self):
        """Delete selected media."""
        selected_item = self.media_list.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Info", "Select an item to delete.")
            return
        
        name = selected_item.text().replace(" [BORROWED]", "")
        reply = QMessageBox.question(self, "Confirm", f"Delete '{name}'?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                response = requests.delete(f"{BACKEND_URL}/media/{name}")
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Deleted!")
                    self.load_all_media()
                    self.detail_label.setText("Select a media item")
                    self.image_label.setText("No image")
                    self.image_label.setPixmap(QPixmap())
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def borrow_media(self):
        """Borrow selected media."""
        selected_item = self.media_list.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Info", "Select an item to borrow.")
            return
        
        name = selected_item.text().replace(" [BORROWED]", "")
        try:
            response = requests.put(f"{BACKEND_URL}/media/{name}/borrow")
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"Borrowed '{name}'!")
                self.load_all_media()
                self.show_media_details(self.media_list.currentItem())
            elif response.status_code == 400:
                QMessageBox.warning(self, "Error", "Already borrowed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def return_media(self):
        """Return borrowed media."""
        selected_item = self.media_list.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Info", "Select an item to return.")
            return
        
        name = selected_item.text().replace(" [BORROWED]", "")
        try:
            response = requests.put(f"{BACKEND_URL}/media/{name}/return")
            if response.status_code == 200:
                QMessageBox.information(self, "Success", f"Returned '{name}'!")
                self.load_all_media()
                self.show_media_details(self.media_list.currentItem())
            elif response.status_code == 400:
                QMessageBox.warning(self, "Error", "Not borrowed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
