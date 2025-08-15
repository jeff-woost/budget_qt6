"""
Monthly Presentation Tab
Shows monthly spending breakdown by category and unrealized expenses tracking
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *

from database.models import IncomeModel, ExpenseModel

class PresentationTab(QWidget):
    """Monthly presentation tab with subtabs"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Set up the UI with tab widget"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Monthly Presentation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Month selector (shared across all tabs)
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Select Month:"))
        self.month_selector = QDateEdit()
        self.month_selector.setDisplayFormat("MMMM yyyy")
        self.month_selector.setDate(QDate.currentDate())
        self.month_selector.setCalendarPopup(True)
        self.month_selector.dateChanged.connect(self.refresh_data)
        month_layout.addWidget(self.month_selector)
        month_layout.addStretch()
        layout.addLayout(month_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()

        # Overview tab (existing functionality)
        overview_tab = QWidget()
        self.setup_overview_tab(overview_tab)
        self.tab_widget.addTab(overview_tab, "Overview")

        # Unrealized expenses tab (new functionality)
        unrealized_tab = QWidget()
        self.setup_unrealized_tab(unrealized_tab)
        self.tab_widget.addTab(unrealized_tab, "Unrealized Expenses")

        layout.addWidget(self.tab_widget)

    def setup_overview_tab(self, tab):
        """Set up the overview tab with existing functionality"""
        layout = QVBoxLayout(tab)

        # Summary section
        summary_layout = QHBoxLayout()
        
        # Income summary
        income_group = QGroupBox("Income Summary")
        income_layout = QVBoxLayout()
        self.jeff_income_label = QLabel("Jeff: $0.00")
        self.vanessa_income_label = QLabel("Vanessa: $0.00")
        self.total_income_label = QLabel("Total: $0.00")
        self.total_income_label.setStyleSheet("font-weight: bold;")
        income_layout.addWidget(self.jeff_income_label)
        income_layout.addWidget(self.vanessa_income_label)
        income_layout.addWidget(self.total_income_label)
        income_group.setLayout(income_layout)
        summary_layout.addWidget(income_group)
        
        # Expense summary
        expense_group = QGroupBox("Expense Summary")
        expense_layout = QVBoxLayout()
        self.jeff_expense_label = QLabel("Jeff: $0.00")
        self.vanessa_expense_label = QLabel("Vanessa: $0.00")
        self.total_expense_label = QLabel("Total: $0.00")
        self.total_expense_label.setStyleSheet("font-weight: bold;")
        expense_layout.addWidget(self.jeff_expense_label)
        expense_layout.addWidget(self.vanessa_expense_label)
        expense_layout.addWidget(self.total_expense_label)
        expense_group.setLayout(expense_layout)
        summary_layout.addWidget(expense_group)
        
        layout.addLayout(summary_layout)
        
        # Category breakdown table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "Subcategory", "Budgeted", "Actual", "Variance"
        ])
        self.category_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.category_table)
        
        # Spending chart
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        layout.addWidget(self.chart_view)
        
    def setup_unrealized_tab(self, tab):
        """Set up the unrealized expenses tab"""
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel("This shows expenses that haven't been taken out of the joint checking account yet.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Summary section for unrealized expenses
        summary_layout = QHBoxLayout()

        # Unrealized expenses summary
        unrealized_group = QGroupBox("Unrealized Expenses to Withdraw")
        unrealized_layout = QVBoxLayout()
        self.jeff_unrealized_label = QLabel("Jeff: $0.00")
        self.vanessa_unrealized_label = QLabel("Vanessa: $0.00")
        self.total_unrealized_label = QLabel("Total to Withdraw: $0.00")
        self.total_unrealized_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #d32f2f;")
        unrealized_layout.addWidget(self.jeff_unrealized_label)
        unrealized_layout.addWidget(self.vanessa_unrealized_label)
        unrealized_layout.addWidget(QLabel(""))  # Spacer
        unrealized_layout.addWidget(self.total_unrealized_label)
        unrealized_group.setLayout(unrealized_layout)
        summary_layout.addWidget(unrealized_group)
        summary_layout.addStretch()

        layout.addLayout(summary_layout)

        # Unrealized expenses table
        self.unrealized_table = QTableWidget()
        self.unrealized_table.setColumnCount(7)
        self.unrealized_table.setHorizontalHeaderLabels([
            "Date", "Person", "Amount", "Category", "Subcategory", "Description", "Actions"
        ])
        self.unrealized_table.horizontalHeader().setStretchLastSection(True)
        self.unrealized_table.setAlternatingRowColors(True)
        layout.addWidget(self.unrealized_table)

    def refresh_data(self):
        """Refresh presentation data for all tabs"""
        self.refresh_overview_data()
        self.refresh_unrealized_data()

    def refresh_overview_data(self):
        """Refresh data for the overview tab"""
        # Get selected month range
        selected_date = self.month_selector.date()
        month_start = selected_date.toString("yyyy-MM-01")
        month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")
        
        # Get income by person
        cursor = self.db.execute('''
            SELECT person, COALESCE(SUM(amount), 0) as total
            FROM income
            WHERE date >= ? AND date <= ?
            GROUP BY person
        ''', (month_start, month_end))
        
        income_by_person = {row['person']: row['total'] for row in cursor.fetchall()}
        jeff_income = income_by_person.get('Jeff', 0)
        vanessa_income = income_by_person.get('Vanessa', 0)
        total_income = jeff_income + vanessa_income
        
        self.jeff_income_label.setText(f"Jeff: ${jeff_income:,.2f}")
        self.vanessa_income_label.setText(f"Vanessa: ${vanessa_income:,.2f}")
        self.total_income_label.setText(f"Total: ${total_income:,.2f}")
        
        # Get expenses by person
        cursor = self.db.execute('''
            SELECT person, COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY person
        ''', (month_start, month_end))
        
        expenses_by_person = {row['person']: row['total'] for row in cursor.fetchall()}
        jeff_expenses = expenses_by_person.get('Jeff', 0)
        vanessa_expenses = expenses_by_person.get('Vanessa', 0)
        total_expenses = jeff_expenses + vanessa_expenses
        
        self.jeff_expense_label.setText(f"Jeff: ${jeff_expenses:,.2f}")
        self.vanessa_expense_label.setText(f"Vanessa: ${vanessa_expenses:,.2f}")
        self.total_expense_label.setText(f"Total: ${total_expenses:,.2f}")
        
        # Update category table
        categories = ExpenseModel.get_by_category(self.db, month_start, month_end)
        
        self.category_table.setRowCount(len(categories))
        for i, cat in enumerate(categories):
            self.category_table.setItem(i, 0, QTableWidgetItem(cat['category']))
            self.category_table.setItem(i, 1, QTableWidgetItem(cat['subcategory'] or ""))
            self.category_table.setItem(i, 2, QTableWidgetItem("$0.00"))  # Budgeted placeholder
            self.category_table.setItem(i, 3, QTableWidgetItem(f"${cat['total']:.2f}"))
            
            variance = 0 - cat['total']  # Since no budget set
            variance_item = QTableWidgetItem(f"${variance:.2f}")
            if variance < 0:
                variance_item.setForeground(QColor(244, 67, 54))
            else:
                variance_item.setForeground(QColor(76, 175, 80))
            self.category_table.setItem(i, 4, variance_item)
        
        # Update chart
        self.update_spending_chart(month_start, month_end)
        
    def refresh_unrealized_data(self):
        """Refresh data for the unrealized expenses tab"""
        # Get selected month range
        selected_date = self.month_selector.date()
        month_start = selected_date.toString("yyyy-MM-01")
        month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Get unrealized expenses by person
        unrealized_by_person = ExpenseModel.get_unrealized_by_person(self.db, month_start, month_end)
        unrealized_dict = {row['person']: row['total'] for row in unrealized_by_person}

        jeff_unrealized = unrealized_dict.get('Jeff', 0)
        vanessa_unrealized = unrealized_dict.get('Vanessa', 0)
        total_unrealized = jeff_unrealized + vanessa_unrealized

        self.jeff_unrealized_label.setText(f"Jeff: ${jeff_unrealized:,.2f}")
        self.vanessa_unrealized_label.setText(f"Vanessa: ${vanessa_unrealized:,.2f}")
        self.total_unrealized_label.setText(f"Total to Withdraw: ${total_unrealized:,.2f}")

        # Get all unrealized expenses
        unrealized_expenses = ExpenseModel.get_unrealized_expenses(self.db, month_start, month_end)

        self.unrealized_table.setRowCount(len(unrealized_expenses))
        for i, expense in enumerate(unrealized_expenses):
            self.unrealized_table.setItem(i, 0, QTableWidgetItem(expense['date']))
            self.unrealized_table.setItem(i, 1, QTableWidgetItem(expense['person']))
            self.unrealized_table.setItem(i, 2, QTableWidgetItem(f"${expense['amount']:.2f}"))
            self.unrealized_table.setItem(i, 3, QTableWidgetItem(expense['category']))
            self.unrealized_table.setItem(i, 4, QTableWidgetItem(expense['subcategory'] or ""))
            self.unrealized_table.setItem(i, 5, QTableWidgetItem(expense['description'] or ""))

            # Add "Mark as Realized" button
            mark_button = QPushButton("Mark as Realized")
            mark_button.clicked.connect(lambda checked, exp_id=expense['id']: self.mark_expense_realized(exp_id))
            mark_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; border: none; padding: 5px; }")
            self.unrealized_table.setCellWidget(i, 6, mark_button)

    def mark_expense_realized(self, expense_id):
        """Mark an expense as realized and refresh the data"""
        ExpenseModel.mark_as_realized(self.db, expense_id)
        self.refresh_unrealized_data()

        # Show confirmation message
        QMessageBox.information(self, "Success", "Expense marked as realized!")

    def update_spending_chart(self, month_start, month_end):
        """Update spending pie chart for overview tab"""
        # Get category data
        categories = ExpenseModel.get_by_category(self.db, month_start, month_end)

        if not categories:
            # Clear chart if no data
            self.chart_view.setChart(QChart())
            return

        # Create pie series
        series = QPieSeries()

        for cat in categories:
            slice_label = f"{cat['category']}"
            if cat['subcategory']:
                slice_label += f" - {cat['subcategory']}"
            series.append(slice_label, cat['total'])

        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly Spending by Category")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)

        self.chart_view.setChart(chart)
