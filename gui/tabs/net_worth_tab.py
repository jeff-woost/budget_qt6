"""
Net Worth Tab - Track assets and calculate net worth over time
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QComboBox, QLineEdit, QDateEdit, QTextEdit, QSplitter,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
from database.db_manager import DatabaseManager

class NetWorthTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Net Worth Tracker")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Create splitter for left and right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Add/Edit Assets
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Asset entry form
        form_group = QGroupBox("Add/Update Asset")
        form_layout = QGridLayout()
        
        # Person selector
        form_layout.addWidget(QLabel("Person:"), 0, 0)
        self.person_combo = QComboBox()
        self.person_combo.addItems(["Jeff", "Vanessa", "Joint"])
        form_layout.addWidget(self.person_combo, 0, 1)
        
        # Asset type
        form_layout.addWidget(QLabel("Asset Type:"), 1, 0)
        self.asset_type_combo = QComboBox()
        self.asset_type_combo.addItems([
            "Real Estate", "Checking Account", "Savings Account",
            "Brokerage Account", "401(k)", "Roth IRA", "Traditional IRA",
            "HSA", "529 Plan", "Cryptocurrency", "Precious Metals",
            "Vehicle", "Other Asset", "Debt/Liability"
        ])
        form_layout.addWidget(self.asset_type_combo, 1, 1)
        
        # Asset name
        form_layout.addWidget(QLabel("Asset Name:"), 2, 0)
        self.asset_name_input = QLineEdit()
        self.asset_name_input.setPlaceholderText("e.g., Chase Checking, Fidelity 401k")
        form_layout.addWidget(self.asset_name_input, 2, 1)
        
        # Value
        form_layout.addWidget(QLabel("Value:"), 3, 0)
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter amount (negative for liabilities)")
        form_layout.addWidget(self.value_input, 3, 1)
        
        # Date
        form_layout.addWidget(QLabel("Date:"), 4, 0)
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        form_layout.addWidget(self.date_input, 4, 1)
        
        # Notes
        form_layout.addWidget(QLabel("Notes:"), 5, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form_layout.addWidget(self.notes_input, 5, 1)
        
        # Add button
        add_btn = QPushButton("Add/Update Asset")
        add_btn.clicked.connect(self.add_asset)
        form_layout.addWidget(add_btn, 6, 0, 1, 2)
        
        form_group.setLayout(form_layout)
        left_layout.addWidget(form_group)
        
        # Summary cards
        summary_layout = QGridLayout()
        
        self.jeff_total_label = self.create_summary_label("Jeff's Net Worth:", "$0.00")
        summary_layout.addWidget(self.jeff_total_label, 0, 0)
        
        self.vanessa_total_label = self.create_summary_label("Vanessa's Net Worth:", "$0.00")
        summary_layout.addWidget(self.vanessa_total_label, 0, 1)
        
        self.joint_total_label = self.create_summary_label("Joint Net Worth:", "$0.00")
        summary_layout.addWidget(self.joint_total_label, 1, 0)
        
        self.total_net_worth_label = self.create_summary_label("Total Net Worth:", "$0.00")
        self.total_net_worth_label.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 3px solid #2a82da;
            }
        """)
        summary_layout.addWidget(self.total_net_worth_label, 1, 1)
        
        left_layout.addLayout(summary_layout)
        left_layout.addStretch()
        
        # Right panel - Assets table
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Assets table
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(6)
        self.assets_table.setHorizontalHeaderLabels([
            "Person", "Type", "Name", "Value", "Date", "Notes"
        ])
        
        # Set column widths
        header = self.assets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        right_layout.addWidget(QLabel("Current Assets"))
        right_layout.addWidget(self.assets_table)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
    def create_summary_label(self, title, value):
        """Create a summary label widget"""
        group = QGroupBox()
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #2a82da;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        group.setLayout(layout)
        group.value_label = value_label  # Store reference for updating
        
        return group
        
    def add_asset(self):
        """Add or update an asset"""
        try:
            person = self.person_combo.currentText()
            asset_type = self.asset_type_combo.currentText()
            asset_name = self.asset_name_input.text().strip()
            value_text = self.value_input.text().strip()
            date = self.date_input.date().toString("yyyy-MM-dd")
            notes = self.notes_input.toPlainText().strip()
            
            # Validate inputs
            if not asset_name:
                QMessageBox.warning(self, "Warning", "Please enter an asset name")
                return
                
            if not value_text:
                QMessageBox.warning(self, "Warning", "Please enter a value")
                return
                
            try:
                value = float(value_text.replace(",", "").replace("$", ""))
            except ValueError:
                QMessageBox.warning(self, "Warning", "Please enter a valid number for value")
                return
            
            # Add to database
            self.db.add_asset(person, asset_type, asset_name, value, date, notes)
            
            # Clear form
            self.asset_name_input.clear()
            self.value_input.clear()
            self.notes_input.clear()
            
            # Refresh display
            self.refresh_data()
            
            QMessageBox.information(self, "Success", "Asset added/updated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add asset: {str(e)}")
            
    def refresh_data(self):
        """Refresh the net worth data"""
        try:
            # Get current assets
            assets = self.db.get_assets()
            
            # Clear and populate table
            self.assets_table.setRowCount(0)
            
            # Calculate totals
            jeff_total = 0
            vanessa_total = 0
            joint_total = 0
            
            for asset in assets:
                row = self.assets_table.rowCount()
                self.assets_table.insertRow(row)
                
                self.assets_table.setItem(row, 0, QTableWidgetItem(asset['person']))
                self.assets_table.setItem(row, 1, QTableWidgetItem(asset['asset_type']))
                self.assets_table.setItem(row, 2, QTableWidgetItem(asset['asset_name']))
                
                value = asset['value']
                value_item = QTableWidgetItem(f"${value:,.2f}")
                if value < 0:
                    value_item.setForeground(Qt.GlobalColor.red)
                self.assets_table.setItem(row, 3, value_item)
                
                self.assets_table.setItem(row, 4, QTableWidgetItem(asset['date']))
                self.assets_table.setItem(row, 5, QTableWidgetItem(asset.get('notes', '')))
                
                # Add to totals
                if asset['person'] == 'Jeff':
                    jeff_total += value
                elif asset['person'] == 'Vanessa':
                    vanessa_total += value
                elif asset['person'] == 'Joint':
                    joint_total += value
            
            # Update summary labels
            self.jeff_total_label.value_label.setText(f"${jeff_total:,.2f}")
            self.vanessa_total_label.value_label.setText(f"${vanessa_total:,.2f}")
            self.joint_total_label.value_label.setText(f"${joint_total:,.2f}")
            
            total_net_worth = jeff_total + vanessa_total + joint_total
            self.total_net_worth_label.value_label.setText(f"${total_net_worth:,.2f}")
            
            # Color code total based on positive/negative
            if total_net_worth >= 0:
                self.total_net_worth_label.value_label.setStyleSheet("color: #2a82da;")
            else:
                self.total_net_worth_label.value_label.setStyleSheet("color: red;")
                
        except Exception as e:
            print(f"Error refreshing net worth data: {e}")