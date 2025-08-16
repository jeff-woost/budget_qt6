"""
Bulk Import Preview Dialog
Allows users to review and edit expense categories before importing
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QDialogButtonBox, QMessageBox, QCheckBox, QGroupBox,
    QInputDialog, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import List, Dict
from database.category_manager import get_category_manager

class CustomComboBox(QComboBox):
    """Custom ComboBox that allows adding new items"""

    def __init__(self, parent=None, category_manager=None, is_subcategory=False, category_combo=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.is_subcategory = is_subcategory
        self.category_combo = category_combo
        self.setEditable(True)
        self.lineEdit().returnPressed.connect(self.add_new_item)

    def add_new_item(self):
        """Add a new item when user presses Enter"""
        new_text = self.lineEdit().text().strip()
        if not new_text:
            return

        if self.is_subcategory and self.category_combo:
            # Adding new subcategory
            category = self.category_combo.currentText()
            if category and self.category_manager:
                if self.category_manager.add_subcategory(category, new_text):
                    self.addItem(new_text)
                    self.setCurrentText(new_text)
                    QMessageBox.information(self, "Success", f"Added new subcategory '{new_text}' to '{category}'")
                else:
                    QMessageBox.warning(self, "Error", f"Could not add subcategory '{new_text}' (may already exist)")
        else:
            # Adding new category
            if self.category_manager and self.category_manager.add_category(new_text):
                self.addItem(new_text)
                self.setCurrentText(new_text)
                QMessageBox.information(self, "Success", f"Added new category '{new_text}'")
            else:
                QMessageBox.warning(self, "Error", f"Could not add category '{new_text}' (may already exist)")

class BulkImportPreviewDialog(QDialog):
    """Dialog for previewing and editing bulk import data"""

    def __init__(self, expenses: List[Dict], categories_data: Dict[str, List[str]], parent=None):
        super().__init__(parent)
        self.expenses = expenses
        self.category_manager = get_category_manager()
        # Refresh categories to get latest data
        self.categories_data = self.category_manager.get_categories()
        self.init_ui()
        self.populate_table()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Import Preview - Review Categories")
        self.setModal(True)
        self.resize(1200, 600)

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("Review and Edit Categories Before Import")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Instructions
        instructions = QLabel(
            "Review the automatically assigned categories below. "
            "Click on category or subcategory cells to change them. "
            "Type new categories/subcategories and press Enter to add them. "
            "Uncheck items you don't want to import."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(instructions)

        # Summary
        summary_group = QGroupBox("Import Summary")
        summary_layout = QHBoxLayout()

        self.total_label = QLabel(f"Total Items: {len(self.expenses)}")
        self.selected_label = QLabel(f"Selected: {len(self.expenses)}")
        self.amount_label = QLabel(f"Total Amount: ${sum(exp['amount'] for exp in self.expenses):,.2f}")

        summary_layout.addWidget(self.total_label)
        summary_layout.addWidget(self.selected_label)
        summary_layout.addWidget(self.amount_label)
        summary_layout.addStretch()

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Import", "Date", "Person", "Amount", "Description",
            "Category", "Subcategory", "Payment Method"
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Import checkbox
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Person
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Amount
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # Category
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)  # Subcategory
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Payment Method

        self.table.setColumnWidth(0, 60)   # Import
        self.table.setColumnWidth(1, 100)  # Date
        self.table.setColumnWidth(2, 80)   # Person
        self.table.setColumnWidth(3, 100)  # Amount
        self.table.setColumnWidth(5, 120)  # Category
        self.table.setColumnWidth(6, 150)  # Subcategory
        self.table.setColumnWidth(7, 120)  # Payment Method

        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_none)
        button_layout.addWidget(select_none_btn)

        # Add refresh categories button
        refresh_btn = QPushButton("Refresh Categories")
        refresh_btn.clicked.connect(self.refresh_categories)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_table(self):
        """Populate the table with expense data"""
        self.table.setRowCount(len(self.expenses))

        for row, expense in enumerate(self.expenses):
            # Import checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_summary)
            self.table.setCellWidget(row, 0, checkbox)

            # Date
            self.table.setItem(row, 1, QTableWidgetItem(expense['date']))

            # Person
            person_combo = QComboBox()
            person_combo.addItems(["Jeff", "Vanessa"])
            person_combo.setCurrentText(expense['person'])
            self.table.setCellWidget(row, 2, person_combo)

            # Amount
            amount_item = QTableWidgetItem(f"${expense['amount']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, amount_item)

            # Description
            self.table.setItem(row, 4, QTableWidgetItem(expense['description']))

            # Category (with ability to add new ones)
            category_combo = CustomComboBox(self, self.category_manager, False)
            category_combo.addItems(sorted(self.categories_data.keys()))
            category_combo.setCurrentText(expense['category'])
            category_combo.currentTextChanged.connect(lambda cat, r=row: self.on_category_changed(r, cat))
            self.table.setCellWidget(row, 5, category_combo)

            # Subcategory (with ability to add new ones)
            subcategory_combo = CustomComboBox(self, self.category_manager, True, category_combo)
            if expense['category'] in self.categories_data:
                subcategory_combo.addItems(self.categories_data[expense['category']])
                if expense['subcategory'] in self.categories_data[expense['category']]:
                    subcategory_combo.setCurrentText(expense['subcategory'])
            self.table.setCellWidget(row, 6, subcategory_combo)

            # Payment Method
            payment_combo = QComboBox()
            payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Check", "Transfer", "Other"])
            payment_combo.setCurrentText(expense.get('payment_method', 'Credit Card'))
            self.table.setCellWidget(row, 7, payment_combo)

    def on_category_changed(self, row: int, category: str):
        """Update subcategory options when category changes"""
        subcategory_combo = self.table.cellWidget(row, 6)
        category_combo = self.table.cellWidget(row, 5)

        if subcategory_combo and category in self.categories_data:
            subcategory_combo.clear()
            subcategory_combo.addItems(self.categories_data[category])
            # Update the category combo reference for the subcategory combo
            subcategory_combo.category_combo = category_combo

    def select_all(self):
        """Select all items for import"""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def select_none(self):
        """Deselect all items"""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def update_summary(self):
        """Update the summary labels"""
        selected_count = 0
        selected_amount = 0.0

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
                selected_amount += self.expenses[row]['amount']

        self.selected_label.setText(f"Selected: {selected_count}")
        self.amount_label.setText(f"Total Amount: ${selected_amount:,.2f}")

    def get_selected_expenses(self) -> List[Dict]:
        """Get the list of selected and edited expenses"""
        selected_expenses = []

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                # Get updated values from the UI
                person_combo = self.table.cellWidget(row, 2)
                category_combo = self.table.cellWidget(row, 5)
                subcategory_combo = self.table.cellWidget(row, 6)
                payment_combo = self.table.cellWidget(row, 7)

                expense = self.expenses[row].copy()
                expense['person'] = person_combo.currentText()
                expense['category'] = category_combo.currentText()
                expense['subcategory'] = subcategory_combo.currentText()
                expense['payment_method'] = payment_combo.currentText()

                selected_expenses.append(expense)

        return selected_expenses

    def refresh_categories(self):
        """Refresh categories from the category manager"""
        self.category_manager.refresh()
        self.categories_data = self.category_manager.get_categories()

        # Update all category combos
        for row in range(self.table.rowCount()):
            category_combo = self.table.cellWidget(row, 5)
            subcategory_combo = self.table.cellWidget(row, 6)

            if category_combo:
                current_category = category_combo.currentText()
                category_combo.clear()
                category_combo.addItems(sorted(self.categories_data.keys()))
                if current_category in self.categories_data:
                    category_combo.setCurrentText(current_category)

            if subcategory_combo and current_category in self.categories_data:
                current_subcategory = subcategory_combo.currentText()
                subcategory_combo.clear()
                subcategory_combo.addItems(self.categories_data[current_category])
                if current_subcategory in self.categories_data[current_category]:
                    subcategory_combo.setCurrentText(current_subcategory)

        QMessageBox.information(self, "Success", "Categories refreshed successfully!")
