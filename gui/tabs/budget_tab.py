"""
Budget Tab - Manages income and expenses with two sub-tabs
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QDateEdit, QTabWidget,
    QHeaderView, QMessageBox, QFileDialog, QDialog,
    QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import csv
import os
from database.db_manager import DatabaseManager
from gui.utils.expense_loader import ExpenseLoader

class BudgetTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI with Income and Expenses sub-tabs"""
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Budget Management")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Create sub-tabs for Income and Expenses
        self.sub_tabs = QTabWidget()
        
        # Income Tab
        self.income_tab = IncomeSubTab()
        self.sub_tabs.addTab(self.income_tab, "💵 Income")
        
        # Expenses Tab
        self.expenses_tab = ExpensesSubTab()
        self.sub_tabs.addTab(self.expenses_tab, "💳 Expenses")
        
        layout.addWidget(self.sub_tabs)
        self.setLayout(layout)
        
    def refresh_data(self):
        """Refresh data in both sub-tabs"""
        self.income_tab.refresh_data()
        self.expenses_tab.refresh_data()


class IncomeSubTab(QWidget):
    """Sub-tab for managing income entries"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the Income UI"""
        layout = QVBoxLayout()
        
        # Top section - Add Income Form
        form_group = QGroupBox("Add Income")
        form_layout = QGridLayout()
        
        # Person selector
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa"])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        # Amount
        form_layout.addWidget(QLabel("Amount:"), 0, 2)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter income amount")
        form_layout.addWidget(self.amount_input, 0, 3)
        
        # Date
        form_layout.addWidget(QLabel("Date:"), 1, 0)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 1, 1)
        
        # Description
        form_layout.addWidget(QLabel("Description:"), 1, 2)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("e.g., Monthly Salary, Bonus, etc.")
        form_layout.addWidget(self.description_input, 1, 3)
        
        # Add button
        add_btn = QPushButton("Add Income")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        add_btn.clicked.connect(self.add_income)
        form_layout.addWidget(add_btn, 2, 0, 1, 4)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Monthly Summary Section
        summary_layout = QHBoxLayout()
        
        # Jeff's Income Summary
        self.jeff_summary = self.create_summary_card("Jeff's Monthly Income", "$0.00")
        summary_layout.addWidget(self.jeff_summary)
        
        # Vanessa's Income Summary
        self.vanessa_summary = self.create_summary_card("Vanessa's Monthly Income", "$0.00")
        summary_layout.addWidget(self.vanessa_summary)
        
        # Total Income Summary
        self.total_summary = self.create_summary_card("Total Monthly Income", "$0.00")
        summary_layout.addWidget(self.total_summary)
        
        layout.addLayout(summary_layout)
        
        # Income History Table
        history_group = QGroupBox("Income History")
        history_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_person = QComboBox()
        self.filter_person.addItems(["All", "Jeff", "Vanessa"])
        self.filter_person.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_person)
        
        filter_layout.addWidget(QLabel("Month:"))
        self.filter_month = QComboBox()
        self.filter_month.addItems([
            "All", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.filter_month.setCurrentIndex(datetime.now().month)
        self.filter_month.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_month)
        
        filter_layout.addWidget(QLabel("Year:"))
        self.filter_year = QComboBox()
        current_year = datetime.now().year
        self.filter_year.addItems(["All"] + [str(year) for year in range(current_year - 2, current_year + 2)])
        self.filter_year.setCurrentText(str(current_year))
        self.filter_year.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_year)
        
        filter_layout.addStretch()
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_income)
        filter_layout.addWidget(delete_btn)
        
        history_layout.addLayout(filter_layout)
        
        # Income table
        self.income_table = QTableWidget()
        self.income_table.setColumnCount(5)
        self.income_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Description", "ID"
        ])
        self.income_table.hideColumn(4)  # Hide ID column
        
        # Set column widths
        header = self.income_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        history_layout.addWidget(self.income_table)
        history_group.setLayout(history_layout)
        
        layout.addWidget(history_group)
        self.setLayout(layout)
        
    def create_summary_card(self, title, value):
        """Create a summary card widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2a82da;")
        layout.addWidget(value_label)
        
        group.setLayout(layout)
        group.value_label = value_label  # Store reference for updating
        return group
        
    def add_income(self):
        """Add income entry to database"""
        try:
            person = self.person_combo.currentText()
            amount_text = self.amount_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            description = self.description_input.text().strip()
            
            # Validate amount
            if not amount_text:
                QMessageBox.warning(self, "Warning", "Please enter an amount")
                return
                
            try:
                amount = float(amount_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for amount")
                return
            
            # Add to database
            self.db.add_income(person, amount, date, description)
            
            # Clear form
            self.amount_input.clear()
            self.description_input.clear()
            
            # Refresh display
            self.refresh_data()
            
            QMessageBox.information(self, "Success", "Income added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add income: {str(e)}")
            
    def delete_selected_income(self):
        """Delete selected income entries"""
        selected_rows = []
        for row in range(self.income_table.rowCount()):
            if self.income_table.item(row, 0) and self.income_table.item(row, 0).isSelected():
                selected_rows.append(row)
            elif any(self.income_table.item(row, col) and self.income_table.item(row, col).isSelected()
                    for col in range(self.income_table.columnCount())):
                selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select one or more income entries to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_rows)} income entr{'y' if len(selected_rows) == 1 else 'ies'}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Delete each selected income entry
            deleted_count = 0
            for row in reversed(selected_rows):  # Reverse to maintain row indices
                income_id_item = self.income_table.item(row, 4)  # ID is in column 4
                if income_id_item:
                    income_id = int(income_id_item.text())

                    # Delete from database using the model's delete method
                    from database.models import IncomeModel
                    IncomeModel.delete(self.db, income_id)
                    deleted_count += 1

            # Refresh the table
            self.refresh_data()

            QMessageBox.information(
                self,
                "Success",
                f"Successfully deleted {deleted_count} income entr{'y' if deleted_count == 1 else 'ies'}."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete income entries: {str(e)}")

    def refresh_data(self):
        """Refresh the income data display"""
        try:
            # Build filter parameters
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            
            # Date filters
            start_date = None
            end_date = None
            
            if self.filter_month.currentIndex() > 0 and self.filter_year.currentText() != "All":
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"
            
            # Get income data
            income_data = self.db.get_income(start_date, end_date, person_filter)
            
            # Clear and populate table
            self.income_table.setRowCount(0)
            
            jeff_total = 0
            vanessa_total = 0
            
            for income in income_data:
                row = self.income_table.rowCount()
                self.income_table.insertRow(row)
                
                self.income_table.setItem(row, 0, QTableWidgetItem(income['date']))
                self.income_table.setItem(row, 1, QTableWidgetItem(income['person']))
                
                amount = income['amount']
                self.income_table.setItem(row, 2, QTableWidgetItem(f"${amount:,.2f}"))
                self.income_table.setItem(row, 3, QTableWidgetItem(income.get('description', '')))
                self.income_table.setItem(row, 4, QTableWidgetItem(str(income['id'])))
                
                # Calculate totals for current month
                if income['person'] == 'Jeff':
                    jeff_total += amount
                else:
                    vanessa_total += amount
            
            # Update summary cards
            self.jeff_summary.value_label.setText(f"${jeff_total:,.2f}")
            self.vanessa_summary.value_label.setText(f"${vanessa_total:,.2f}")
            self.total_summary.value_label.setText(f"${jeff_total + vanessa_total:,.2f}")
            
        except Exception as e:
            print(f"Error refreshing income data: {e}")


class ExpensesSubTab(QWidget):
    """Sub-tab for managing expense entries"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.categories_data = {}
        self.init_ui()
        self.load_categories()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the Expenses UI"""
        layout = QVBoxLayout()
        
        # Top section - Add Expense Form
        form_group = QGroupBox("Add Expense")
        form_layout = QGridLayout()
        
        # Row 1
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa"])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        form_layout.addWidget(QLabel("Amount:"), 0, 2)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter expense amount")
        form_layout.addWidget(self.amount_input, 0, 3)
        
        form_layout.addWidget(QLabel("Date:"), 0, 4)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 0, 5)
        
        # Row 2
        form_layout.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        form_layout.addWidget(self.category_combo, 1, 1)
        
        form_layout.addWidget(QLabel("Subcategory:"), 1, 2)
        self.subcategory_combo = QComboBox()
        form_layout.addWidget(self.subcategory_combo, 1, 3)
        
        form_layout.addWidget(QLabel("Payment Method:"), 1, 4)
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["Cash", "Credit Card", "Debit Card", "Check", "Transfer", "Other"])
        form_layout.addWidget(self.payment_combo, 1, 5)
        
        # Row 3
        form_layout.addWidget(QLabel("Description:"), 2, 0)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Optional description")
        form_layout.addWidget(self.description_input, 2, 1, 1, 4)

        # Add realized checkbox
        self.realized_checkbox = QCheckBox("Already taken from joint checking")
        self.realized_checkbox.setToolTip("Check if this expense has already been paid from the joint checking account")
        form_layout.addWidget(self.realized_checkbox, 2, 5)

        # Row 4 - Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Expense")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a82da;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1e5fa8;
            }
        """)
        add_btn.clicked.connect(self.add_expense)
        button_layout.addWidget(add_btn)
        
        import_btn = QPushButton("Import from File")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
        """)
        import_btn.clicked.connect(self.import_expenses)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        form_layout.addLayout(button_layout, 3, 0, 1, 6)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Monthly Summary Section
        summary_layout = QHBoxLayout()
        
        # Jeff's Expenses Summary
        self.jeff_summary = self.create_summary_card("Jeff's Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.jeff_summary)
        
        # Vanessa's Expenses Summary
        self.vanessa_summary = self.create_summary_card("Vanessa's Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.vanessa_summary)
        
        # Total Expenses Summary
        self.total_summary = self.create_summary_card("Total Monthly Expenses", "$0.00")
        summary_layout.addWidget(self.total_summary)
        
        # Top Category Summary
        self.top_category_summary = self.create_summary_card("Top Category", "None")
        summary_layout.addWidget(self.top_category_summary)
        
        layout.addLayout(summary_layout)
        
        # Expense History Table
        history_group = QGroupBox("Expense History")
        history_layout = QVBoxLayout()
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter by:"))
        
        self.filter_person = QComboBox()
        self.filter_person.addItems(["All", "Jeff", "Vanessa"])
        self.filter_person.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_person)
        
        self.filter_category = QComboBox()
        self.filter_category.addItems(["All Categories"])
        self.filter_category.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_category)
        
        filter_layout.addWidget(QLabel("Month:"))
        self.filter_month = QComboBox()
        self.filter_month.addItems([
            "All", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.filter_month.setCurrentIndex(datetime.now().month)
        self.filter_month.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_month)
        
        filter_layout.addWidget(QLabel("Year:"))
        self.filter_year = QComboBox()
        current_year = datetime.now().year
        self.filter_year.addItems(["All"] + [str(year) for year in range(current_year - 2, current_year + 2)])
        self.filter_year.setCurrentText(str(current_year))
        self.filter_year.currentTextChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.filter_year)
        
        filter_layout.addStretch()
        
        # Export and Delete buttons
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_expenses)
        filter_layout.addWidget(export_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_expenses)
        filter_layout.addWidget(delete_btn)
        
        history_layout.addLayout(filter_layout)
        
        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(8)
        self.expense_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Category", "Subcategory", 
            "Description", "Payment", "ID"
        ])
        self.expense_table.hideColumn(7)  # Hide ID column
        
        # Set column widths
        header = self.expense_table.horizontalHeader()
        for i in range(7):
            if i == 5:  # Description column
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        history_layout.addWidget(self.expense_table)
        history_group.setLayout(history_layout)
        
        layout.addWidget(history_group)
        self.setLayout(layout)
        
    def create_summary_card(self, title, value):
        """Create a summary card widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                min-width: 150px;
            }
        """)
        
        layout = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #d9534f;")
        layout.addWidget(value_label)
        
        group.setLayout(layout)
        group.value_label = value_label  # Store reference for updating
        return group
        
    def load_categories(self):
        """Load categories from database"""
        try:
            categories = self.db.get_categories()
            
            # Organize categories
            self.categories_data = {}
            for cat in categories:
                category = cat['category']
                subcategory = cat['subcategory']
                
                if category not in self.categories_data:
                    self.categories_data[category] = []
                self.categories_data[category].append(subcategory)
            
            # Populate category combo
            self.category_combo.clear()
            self.category_combo.addItems(sorted(self.categories_data.keys()))
            
            # Populate filter category combo
            self.filter_category.clear()
            self.filter_category.addItems(["All Categories"] + sorted(self.categories_data.keys()))
            
        except Exception as e:
            print(f"Error loading categories: {e}")
            
    def on_category_changed(self, category):
        """Update subcategories when category changes"""
        self.subcategory_combo.clear()
        if category in self.categories_data:
            self.subcategory_combo.addItems(self.categories_data[category])
            
    def add_expense(self):
        """Add expense entry to database"""
        try:
            person = self.person_combo.currentText()
            amount_text = self.amount_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            category = self.category_combo.currentText()
            subcategory = self.subcategory_combo.currentText()
            description = self.description_input.text().strip()
            payment_method = self.payment_combo.currentText()
            realized = self.realized_checkbox.isChecked()  # Get realized status

            # Validate inputs
            if not amount_text:
                QMessageBox.warning(self, "Warning", "Please enter an amount")
                return
                
            if not category or not subcategory:
                QMessageBox.warning(self, "Warning", "Please select category and subcategory")
                return
                
            try:
                amount = float(amount_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for amount")
                return
            
            # Add to database using the updated ExpenseModel.add method
            from database.models import ExpenseModel
            ExpenseModel.add(self.db, date, person, amount, category, subcategory,
                           description, payment_method, realized)

            # Clear form
            self.amount_input.clear()
            self.description_input.clear()
            self.realized_checkbox.setChecked(False)  # Reset checkbox

            # Refresh display
            self.refresh_data()
            
            QMessageBox.information(self, "Success", "Expense added successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add expense: {str(e)}")
            
    def import_expenses(self):
        """Import expenses from CSV or TXT file using ExpenseLoader"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Import Expenses", 
                "", 
                "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if not file_path:
                return
            
            # Use ExpenseLoader to parse the file
            loader = ExpenseLoader()
            expenses = []
            errors = []

            if file_path.lower().endswith('.csv'):
                expenses, errors = loader.load_csv_file(file_path)
            elif file_path.lower().endswith('.txt'):
                expenses, errors = loader.load_txt_file(file_path)
            else:
                # Try CSV first, then TXT
                expenses, errors = loader.load_csv_file(file_path)
                if not expenses and not errors:
                    expenses, errors = loader.load_txt_file(file_path)

            # Show errors if any
            if errors:
                error_dialog = QMessageBox()
                error_dialog.setWindowTitle("Import Warnings")
                error_dialog.setIcon(QMessageBox.Icon.Warning)
                error_dialog.setText(f"Found {len(errors)} issues while parsing the file:")
                error_dialog.setDetailedText("\n".join(errors))
                error_dialog.exec()

            if not expenses:
                QMessageBox.warning(self, "Warning", "No valid expenses found in the file")
                return

            # Validate expenses
            valid_expenses, validation_errors = loader.validate_expenses(expenses)

            if validation_errors:
                error_dialog = QMessageBox()
                error_dialog.setWindowTitle("Validation Errors")
                error_dialog.setIcon(QMessageBox.Icon.Warning)
                error_dialog.setText(f"Found {len(validation_errors)} validation issues:")
                error_dialog.setDetailedText("\n".join(validation_errors))
                error_dialog.exec()

            if not valid_expenses:
                QMessageBox.warning(self, "Warning", "No valid expenses after validation")
                return

            # Show preview dialog
            preview_dialog = ExpensePreviewDialog(valid_expenses, self.categories_data)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                final_expenses = preview_dialog.get_final_expenses()

                if final_expenses:
                    # Add to database
                    self.db.bulk_add_expenses(final_expenses)
                    self.refresh_data()

                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Successfully imported {len(final_expenses)} expenses!\n\n"
                        f"Parsing errors: {len(errors)}\n"
                        f"Validation errors: {len(validation_errors)}\n"
                        f"Successfully imported: {len(final_expenses)}"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import expenses: {str(e)}")
            
    def export_expenses(self):
        """Export expenses to CSV file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Expenses",
                f"expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
                
            # Get current filter settings
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            category_filter = None if self.filter_category.currentText() == "All Categories" else self.filter_category.currentText()
            
            # Build date filters
            start_date = None
            end_date = None
            
            if self.filter_month.currentIndex() > 0 and self.filter_year.currentText() != "All":
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"
            
            # Get expense data
            expenses = self.db.get_expenses(start_date, end_date, person_filter, category_filter)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['date', 'person', 'amount', 'category', 'subcategory', 
                            'description', 'payment_method']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for expense in expenses:
                    writer.writerow({
                        'date': expense['date'],
                        'person': expense['person'],
                        'amount': expense['amount'],
                        'category': expense['category'],
                        'subcategory': expense['subcategory'],
                        'description': expense.get('description', ''),
                        'payment_method': expense.get('payment_method', '')
                    })
            
            QMessageBox.information(self, "Success", f"Expenses exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export expenses: {str(e)}")
            
    def delete_selected_expenses(self):
        """Delete selected expense entries"""
        selected_rows = []
        for row in range(self.expense_table.rowCount()):
            if self.expense_table.item(row, 0) and self.expense_table.item(row, 0).isSelected():
                selected_rows.append(row)
            elif any(self.expense_table.item(row, col) and self.expense_table.item(row, col).isSelected()
                    for col in range(self.expense_table.columnCount())):
                selected_rows.append(row)

        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select one or more expense entries to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_rows)} expense entr{'y' if len(selected_rows) == 1 else 'ies'}?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Delete each selected expense entry
            deleted_count = 0
            for row in reversed(selected_rows):  # Reverse to maintain row indices
                expense_id_item = self.expense_table.item(row, 7)  # ID is in column 7
                if expense_id_item:
                    expense_id = int(expense_id_item.text())

                    # Delete from database using the model's delete method
                    from database.models import ExpenseModel
                    ExpenseModel.delete(self.db, expense_id)
                    deleted_count += 1

            # Refresh the table
            self.refresh_data()

            QMessageBox.information(
                self,
                "Success",
                f"Successfully deleted {deleted_count} expense entr{'y' if deleted_count == 1 else 'ies'}."
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete expense entries: {str(e)}")

    def refresh_data(self):
        """Refresh the expense data display"""
        try:
            # Build filter parameters
            person_filter = None if self.filter_person.currentText() == "All" else self.filter_person.currentText()
            category_filter = None if self.filter_category.currentText() == "All Categories" else self.filter_category.currentText()
            
            # Date filters
            start_date = None
            end_date = None
            
            if self.filter_month.currentIndex() > 0 and self.filter_year.currentText() != "All":
                year = int(self.filter_year.currentText())
                month = self.filter_month.currentIndex()
                start_date = f"{year:04d}-{month:02d}-01"
                if month == 12:
                    end_date = f"{year+1:04d}-01-01"
                else:
                    end_date = f"{year:04d}-{month+1:02d}-01"
            
            # Get expense data
            expense_data = self.db.get_expenses(start_date, end_date, person_filter, category_filter)
            
            # Clear and populate table
            self.expense_table.setRowCount(0)
            
            jeff_total = 0
            vanessa_total = 0
            category_totals = {}
            
            for expense in expense_data:
                row = self.expense_table.rowCount()
                self.expense_table.insertRow(row)
                
                self.expense_table.setItem(row, 0, QTableWidgetItem(expense['date']))
                self.expense_table.setItem(row, 1, QTableWidgetItem(expense['person']))
                
                amount = expense['amount']
                amount_item = QTableWidgetItem(f"${amount:,.2f}")
                amount_item.setForeground(Qt.GlobalColor.red)
                self.expense_table.setItem(row, 2, amount_item)
                
                self.expense_table.setItem(row, 3, QTableWidgetItem(expense['category']))
                self.expense_table.setItem(row, 4, QTableWidgetItem(expense['subcategory']))
                self.expense_table.setItem(row, 5, QTableWidgetItem(expense.get('description', '')))
                self.expense_table.setItem(row, 6, QTableWidgetItem(expense.get('payment_method', '')))
                self.expense_table.setItem(row, 7, QTableWidgetItem(str(expense['id'])))
                
                # Calculate totals
                if expense['person'] == 'Jeff':
                    jeff_total += amount
                else:
                    vanessa_total += amount
                    
                # Track category totals
                category = expense['category']
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += amount
            
            # Update summary cards
            self.jeff_summary.value_label.setText(f"${jeff_total:,.2f}")
            self.vanessa_summary.value_label.setText(f"${vanessa_total:,.2f}")
            self.total_summary.value_label.setText(f"${jeff_total + vanessa_total:,.2f}")
            
            # Find top category
            if category_totals:
                top_category = max(category_totals, key=category_totals.get)
                self.top_category_summary.value_label.setText(
                    f"{top_category}\n${category_totals[top_category]:,.2f}"
                )
            else:
                self.top_category_summary.value_label.setText("None")
            
        except Exception as e:
            print(f"Error refreshing expense data: {e}")


class ImportDialog(QDialog):
    """Dialog for importing expenses from file"""
    
    def __init__(self, file_path, categories_data):
        super().__init__()
        self.file_path = file_path
        self.categories_data = categories_data
        self.parsed_expenses = []
        
        self.setWindowTitle("Import Expenses")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_file()
        
    def init_ui(self):
        """Initialize the import dialog UI"""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Map the columns from your file to the expense fields. "
            "Select the appropriate column for each field."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Column mapping section
        mapping_group = QGroupBox("Column Mapping")
        mapping_layout = QGridLayout()
        
        self.column_combos = {}
        fields = [
            ("Date", True),
            ("Amount", True),
            ("Description", False),
            ("Category", False),
            ("Subcategory", False),
            ("Payment Method", False)
        ]
        
        for i, (field, required) in enumerate(fields):
            label_text = f"{field}:" if not required else f"{field}*:"
            mapping_layout.addWidget(QLabel(label_text), i, 0)
            
            combo = QComboBox()
            combo.addItem("-- Not Mapped --")
            self.column_combos[field] = combo
            mapping_layout.addWidget(combo, i, 1)
            
        # Person assignment
        mapping_layout.addWidget(QLabel("Assign to:"), len(fields), 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa", "Ask for Each"])
        mapping_layout.addWidget(self.person_combo, len(fields), 1)
        
        # Default category (if not in file)
        mapping_layout.addWidget(QLabel("Default Category:"), len(fields) + 1, 0)
        self.default_category_combo = QComboBox()
        self.default_category_combo.addItems(["-- Select --"] + list(self.categories_data.keys()))
        mapping_layout.addWidget(self.default_category_combo, len(fields) + 1, 1)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.process_import)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_file(self):
        """Load and preview the file"""
        try:
            with open(self.file_path, 'r') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                # Detect delimiter
                if '\t' in sample:
                    delimiter = '\t'
                elif ',' in sample:
                    delimiter = ','
                else:
                    delimiter = ','
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
                
                if not rows:
                    QMessageBox.warning(self, "Warning", "The file appears to be empty")
                    return
                
                # Assume first row is headers
                headers = rows[0] if rows else []
                data_rows = rows[1:6] if len(rows) > 1 else []  # Preview first 5 data rows
                
                # Update column combos
                for combo in self.column_combos.values():
                    combo.clear()
                    combo.addItem("-- Not Mapped --")
                    combo.addItems(headers)
                
                # Try to auto-map columns based on header names
                self.auto_map_columns(headers)
                
                # Update preview table
                self.preview_table.setColumnCount(len(headers))
                self.preview_table.setHorizontalHeaderLabels(headers)
                self.preview_table.setRowCount(len(data_rows))
                
                for i, row in enumerate(data_rows):
                    for j, value in enumerate(row):
                        self.preview_table.setItem(i, j, QTableWidgetItem(value))
                        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            
    def auto_map_columns(self, headers):
        """Try to automatically map columns based on header names"""
        mappings = {
            "Date": ["date", "transaction date", "posted date", "trans date"],
            "Amount": ["amount", "debit", "charge", "payment"],
            "Description": ["description", "memo", "merchant", "details"],
            "Category": ["category", "type"],
            "Subcategory": ["subcategory", "sub category", "sub-category"],
            "Payment Method": ["payment", "method", "card", "account"]
        }
        
        headers_lower = [h.lower() for h in headers]
        
        for field, keywords in mappings.items():
            combo = self.column_combos[field]
            for i, header in enumerate(headers_lower):
                for keyword in keywords:
                    if keyword in header:
                        combo.setCurrentIndex(i + 1)  # +1 because of "-- Not Mapped --"
                        break
                        
    def process_import(self):
        """Process the import with the current mapping"""
        try:
            # Validate required fields are mapped
            date_col = self.column_combos["Date"].currentIndex() - 1
            amount_col = self.column_combos["Amount"].currentIndex() - 1
            
            if date_col < 0 or amount_col < 0:
                QMessageBox.warning(self, "Warning", "Date and Amount columns must be mapped")
                return
            
            # Read the entire file
            with open(self.file_path, 'r') as file:
                delimiter = '\t' if '\t' in file.read(1024) else ','
                file.seek(0)
                
                reader = csv.reader(file, delimiter=delimiter)
                rows = list(reader)
                
                if len(rows) <= 1:
                    QMessageBox.warning(self, "Warning", "No data rows found")
                    return
                
                # Skip header row
                data_rows = rows[1:]
                
                # Process each row
                self.parsed_expenses = []
                person = self.person_combo.currentText()
                
                for row in data_rows:
                    try:
                        expense = {
                            'person': person if person != "Ask for Each" else "Jeff",  # Default to Jeff
                            'date': row[date_col] if date_col >= 0 else "",
                            'amount': abs(float(row[amount_col].replace(",", "").replace("$", ""))),
                        }
                        
                        # Optional fields
                        desc_col = self.column_combos["Description"].currentIndex() - 1
                        if desc_col >= 0 and desc_col < len(row):
                            expense['description'] = row[desc_col]
                        else:
                            expense['description'] = ""
                        
                        cat_col = self.column_combos["Category"].currentIndex() - 1
                        if cat_col >= 0 and cat_col < len(row):
                            expense['category'] = row[cat_col]
                        else:
                            expense['category'] = self.default_category_combo.currentText()
                            
                        subcat_col = self.column_combos["Subcategory"].currentIndex() - 1
                        if subcat_col >= 0 and subcat_col < len(row):
                            expense['subcategory'] = row[subcat_col]
                        else:
                            # Use first subcategory for the category
                            if expense['category'] in self.categories_data:
                                expense['subcategory'] = self.categories_data[expense['category']][0]
                            else:
                                expense['subcategory'] = "Other"
                        
                        payment_col = self.column_combos["Payment Method"].currentIndex() - 1
                        if payment_col >= 0 and payment_col < len(row):
                            expense['payment_method'] = row[payment_col]
                        else:
                            expense['payment_method'] = "Credit Card"
                        
                        # Validate and add
                        if expense['date'] and expense['amount'] > 0:
                            self.parsed_expenses.append(expense)
                            
                    except Exception as e:
                        print(f"Error processing row: {e}")
                        continue
                
                if self.parsed_expenses:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Warning", "No valid expenses could be parsed")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process import: {str(e)}")
            
    def get_parsed_expenses(self):
        """Return the parsed expenses"""
        return self.parsed_expenses


class ExpensePreviewDialog(QDialog):
    """Dialog for previewing expenses before import"""

    def __init__(self, expenses, categories_data):
        super().__init__()
        self.expenses = expenses
        self.categories_data = categories_data
        self.final_expenses = []

        self.setWindowTitle("Preview Expenses")
        self.setModal(True)
        self.setMinimumSize(800, 600)

        self.init_ui()
        self.populate_preview()

    def init_ui(self):
        """Initialize the preview dialog UI"""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Review the expenses below. You can edit the values, select rows and delete them, "
            "or remove any expense that you do not want to import."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(7)
        self.preview_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Category", "Subcategory", "Description", "Payment Method"
        ])

        # Enable row selection
        self.preview_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.preview_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)

        # Set column widths
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.preview_table)

        # Action buttons layout
        action_layout = QHBoxLayout()

        # Delete selected button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_rows)
        action_layout.addWidget(delete_btn)

        action_layout.addStretch()

        # Row count label
        self.row_count_label = QLabel()
        self.update_row_count()
        action_layout.addWidget(self.row_count_label)

        layout.addLayout(action_layout)

        # Buttons
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("Import All")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
        """)
        ok_btn.clicked.connect(self.import_all)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def delete_selected_rows(self):
        """Delete selected rows from the preview table"""
        try:
            # Get selected rows
            selected_rows = set()
            for item in self.preview_table.selectedItems():
                selected_rows.add(item.row())

            if not selected_rows:
                QMessageBox.information(self, "Info", "Please select one or more rows to delete.")
                return

            # Confirm deletion
            count = len(selected_rows)
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete {count} selected expense{'s' if count != 1 else ''}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Delete rows in reverse order to maintain row indices
            for row in sorted(selected_rows, reverse=True):
                self.preview_table.removeRow(row)

            # Update row count display
            self.update_row_count()

            QMessageBox.information(self, "Success", f"Deleted {count} expense{'s' if count != 1 else ''}.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete rows: {str(e)}")

    def update_row_count(self):
        """Update the row count label"""
        count = self.preview_table.rowCount()
        self.row_count_label.setText(f"Total expenses: {count}")

    def populate_preview(self):
        """Populate the preview table with expense data and editable subcategory dropdowns"""
        self.preview_table.setRowCount(len(self.expenses))

        for i, expense in enumerate(self.expenses):
            # Standard text items for non-editable columns
            self.preview_table.setItem(i, 0, QTableWidgetItem(expense['date']))
            self.preview_table.setItem(i, 1, QTableWidgetItem(expense['person']))
            self.preview_table.setItem(i, 2, QTableWidgetItem(f"${expense['amount']:,.2f}"))

            # Category dropdown
            category_combo = QComboBox()
            category_combo.addItems(sorted(self.categories_data.keys()))
            category_combo.setCurrentText(expense['category'])
            category_combo.currentTextChanged.connect(lambda text, row=i: self.on_category_changed_in_table(row, text))
            self.preview_table.setCellWidget(i, 3, category_combo)

            # Subcategory dropdown
            subcategory_combo = QComboBox()
            category = expense['category']
            if category in self.categories_data:
                subcategory_combo.addItems(self.categories_data[category])
                if expense['subcategory'] in self.categories_data[category]:
                    subcategory_combo.setCurrentText(expense['subcategory'])
                else:
                    # If subcategory doesn't exist, show it as blank and add it as an option
                    subcategory_combo.addItem(expense['subcategory'])
                    subcategory_combo.setCurrentText(expense['subcategory'])
            else:
                # If category doesn't exist, add the subcategory as is
                subcategory_combo.addItem(expense['subcategory'])
                subcategory_combo.setCurrentText(expense['subcategory'])

            self.preview_table.setCellWidget(i, 4, subcategory_combo)

            # Regular text items for description and payment method
            self.preview_table.setItem(i, 5, QTableWidgetItem(expense.get('description', '')))
            self.preview_table.setItem(i, 6, QTableWidgetItem(expense.get('payment_method', '')))

        # Update row count display
        self.update_row_count()

    def on_category_changed_in_table(self, row, category):
        """Update subcategory dropdown when category changes in the preview table"""
        subcategory_combo = self.preview_table.cellWidget(row, 4)
        if subcategory_combo:
            subcategory_combo.clear()
            if category in self.categories_data:
                subcategory_combo.addItems(self.categories_data[category])
            else:
                subcategory_combo.addItem("Other")

    def import_all(self):
        """Import all remaining displayed expenses"""
        try:
            # Check if there are any rows left
            if self.preview_table.rowCount() == 0:
                QMessageBox.warning(self, "Warning", "No expenses to import.")
                return

            # Collect final expenses from remaining rows
            for i in range(self.preview_table.rowCount()):
                try:
                    date = self.preview_table.item(i, 0).text()
                    person = self.preview_table.item(i, 1).text()
                    amount_text = self.preview_table.item(i, 2).text().replace("$", "").replace(",", "")

                    # Get values from dropdown widgets
                    category_combo = self.preview_table.cellWidget(i, 3)
                    subcategory_combo = self.preview_table.cellWidget(i, 4)

                    category = category_combo.currentText() if category_combo else "Other"
                    subcategory = subcategory_combo.currentText() if subcategory_combo else "Other"

                    description = self.preview_table.item(i, 5).text()
                    payment_method = self.preview_table.item(i, 6).text()

                    amount = abs(float(amount_text))  # Ensure positive amount

                    expense = {
                        'date': date,
                        'person': person,
                        'amount': amount,
                        'category': category,
                        'subcategory': subcategory,
                        'description': description,
                        'payment_method': payment_method
                    }

                    self.final_expenses.append(expense)

                except Exception as e:
                    print(f"Error processing row {i}: {e}")
                    continue

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import expenses: {str(e)}")

    def get_final_expenses(self):
        """Return the final expenses list"""
        return self.final_expenses
