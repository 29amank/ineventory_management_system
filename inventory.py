import sys
import sqlite3
import csv
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QFileDialog, QInputDialog
from PyQt5.QtGui import QIcon
import logging
from functools import wraps
import hashlib
import locale
from pyzbar.pyzbar import decode
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import openpyxl

# Set up logging
logging.basicConfig(filename='inventory.log', level=logging.INFO)

# Connect to SQLite database
conn = sqlite3.connect('inventory.db')
c = conn.cursor()

# Create table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS products
             (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER, barcode TEXT UNIQUE)''')
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')

# Function to log errors
def log_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
            QMessageBox.critical(args[0], "Error", f"An error occurred: {e}")
    return wrapper

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to generate barcode image
def generate_barcode_image(barcode_data):
    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(barcode_data, writer=ImageWriter())
        barcode_path = f'barcode_images/{barcode_data}.png'
        barcode_instance.save(barcode_path)
        return barcode_path
    except Exception as e:
        logging.error(f"Error generating barcode image: {e}", exc_info=True)
        return None

# Function to export data to Excel file
def export_to_excel():
    options = QFileDialog.Options()
    file_name, _ = QFileDialog.getSaveFileName(None, "Save Excel File", "", "Excel Files (*.xlsx)", options=options)
    if file_name:
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["ID", "Name", "Quantity", "Barcode"])
            c.execute("SELECT * FROM products")
            products = c.fetchall()
            for product in products:
                ws.append(product)
            wb.save(file_name)
            QMessageBox.information(None, "Export Successful", f"Inventory exported to {file_name}")
        except Exception as e:
            logging.error(f"Error exporting to Excel: {e}", exc_info=True)
            QMessageBox.critical(None, "Export Failed", f"An error occurred while exporting: {e}")

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    @log_errors
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Fetch user credentials from database and validate
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        if user_data and user_data[2] == hash_password(password):
            self.close()
            main_window.show()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 800, 600)

        # Company name label
        self.company_label = QLabel("DMV PROJECTS AND ENGINEERING PVT. LTD.")
        self.company_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # Buttons
        self.add_product_button = QPushButton(QIcon("icons/add.png"), "Add Product")
        self.add_product_button.setToolTip("Add a new product")
        self.add_product_button.clicked.connect(self.show_add_product_dialog)

        self.scan_barcode_button = QPushButton(QIcon("icons/scan.png"), "Scan Barcode")
        self.scan_barcode_button.setToolTip("Scan product barcode")
        self.scan_barcode_button.clicked.connect(self.scan_barcode)

        self.display_products_button = QPushButton(QIcon("icons/display.png"), "Display Products")
        self.display_products_button.setToolTip("Display products in inventory")
        self.display_products_button.clicked.connect(self.display_products)

        self.export_csv_button = QPushButton(QIcon("icons/export.png"), "Export Inventory to CSV")
        self.export_csv_button.setToolTip("Export inventory data to CSV file")
        self.export_csv_button.clicked.connect(self.export_to_csv)

        self.generate_barcode_button = QPushButton(QIcon("icons/generate.png"), "Generate Barcode")
        self.generate_barcode_button.setToolTip("Generate barcode image")
        self.generate_barcode_button.clicked.connect(self.generate_barcode)

        self.export_excel_button = QPushButton(QIcon("icons/excel.png"), "Export Inventory to Excel")
        self.export_excel_button.setToolTip("Export inventory data to Excel file")
        self.export_excel_button.clicked.connect(export_to_excel)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Barcode"])

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.company_label)
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.add_product_button)
        layout_buttons.addWidget(self.scan_barcode_button)
        layout_buttons.addWidget(self.display_products_button)
        layout_buttons.addWidget(self.export_csv_button)
        layout_buttons.addWidget(self.generate_barcode_button)
        layout_buttons.addWidget(self.export_excel_button)
        layout.addLayout(layout_buttons)
        layout.addWidget(self.table_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @log_errors
    def show_add_product_dialog(self):
        add_product_dialog = AddProductDialog()
        add_product_dialog.exec_()

    @log_errors
    def scan_barcode(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Scan Barcode", "", "Image Files (*.png *.jpg *.bmp)", options=options)
            if file_name:
                with open(file_name, 'rb') as f:
                    pil = Image.open(f)
                    decoded_objects = decode(pil)
                    if decoded_objects:
                        barcode_data = decoded_objects[0].data.decode('utf-8')
                        self.track_purchase(barcode_data)
                        QMessageBox.information(self, "Barcode Scanned", f"Scanned barcode: {barcode_data}")
                    else:
                        QMessageBox.warning(self, "No Barcode", "No barcode detected in the image")
        except Exception as e:
            logging.error(f"Error scanning barcode: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while scanning barcode: {e}")

    @log_errors
    def track_purchase(self, barcode_data):
        c.execute("SELECT * FROM products WHERE barcode = ?", (barcode_data,))
        product = c.fetchone()
        if product:
            product_id, name, quantity, barcode = product
            print(f"Product purchased: {name}, Quantity: {quantity}")
        else:
            QMessageBox.warning(self, "Product Not Found", "No product found for the scanned barcode")

    @log_errors
    def display_products(self):
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        self.table_widget.setRowCount(0)
        for row_num, product in enumerate(products):
            self.table_widget.insertRow(row_num)
            for col_num, data in enumerate(product):
                self.table_widget.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    @log_errors
    def export_to_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)", options=options)
        if file_name:
            try:
                with open(file_name, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["ID", "Name", "Quantity", "Barcode"])
                    c.execute("SELECT * FROM products")
                    products = c.fetchall()
                    for product in products:
                        writer.writerow(product)
                QMessageBox.information(self, "Export Successful", f"Inventory exported to {file_name}")
            except Exception as e:
                logging.error(f"Error exporting to CSV: {e}", exc_info=True)
                QMessageBox.critical(self, "Export Failed", f"An error occurred while exporting: {e}")

    @log_errors
    def generate_barcode(self):
        barcode_data, ok_pressed = QInputDialog.getText(self, "Generate Barcode", "Enter Barcode Data:")
        if ok_pressed and barcode_data.strip():
            barcode_image_path = generate_barcode_image(barcode_data)
            if barcode_image_path:
                QMessageBox.information(self, "Barcode Generated", f"Barcode image generated successfully: {barcode_image_path}")
            else:
                QMessageBox.warning(self, "Barcode Generation Failed", "Failed to generate barcode image")

class AddProductDialog(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Product")
        self.setGeometry(200, 200, 300, 200)

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.quantity_label = QLabel("Quantity:")
        self.quantity_input = QLineEdit()
        self.barcode_label = QLabel("Barcode:")
        self.barcode_input = QLineEdit()

        self.add_product_button = QPushButton("Add Product")
        self.add_product_button.clicked.connect(self.add_product)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.barcode_label)
        layout.addWidget(self.barcode_input)
        layout.addWidget(self.add_product_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @log_errors
    def add_product(self):
        try:
            name = self.name_input.text()
            quantity = int(self.quantity_input.text())
            barcode = self.barcode_input.text()
            c.execute("INSERT INTO products (name, quantity, barcode) VALUES (?, ?, ?)", (name, quantity, barcode))
            conn.commit()
            QMessageBox.information(self, "Success", "Product added successfully.")
            self.close()
        except Exception as e:
            logging.error(f"Error adding product: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"An error occurred while adding product: {e}")

if __name__ == "__main__":
    # Initialize locale for localization
    locale.setlocale(locale.LC_ALL, '')  

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    main_window = MainWindow()
    login_window.show()
    sys.exit(app.exec_())

# Close the connection
conn.close()
