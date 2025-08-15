"""
Monthly Presentation Tab
Shows monthly spending breakdown by category
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *

from database.models import IncomeModel, ExpenseModel

class PresentationTab(QWidget):
    """Monthly presentation tab"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Monthly Presentation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Month selector
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
        
    def refresh_data(self):
        """Refresh presentation data"""
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
        
    def update_spending_chart(self, month_start, month_end):
        """Update spending pie chart"""
        cursor = self.db.execute('''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category
            ORDER BY total DESC
            LIMIT 10
        ''', (month_start, month_end))
        
        categories = cursor.fetchall()
        
        if categories:
            series = QPieSeries()
            
            for cat in categories:
                slice = series.append(cat['category'], cat['total'])
                slice.setLabelVisible(True)
                slice.setLabel(f"{cat['category']}: ${cat['total']:.0f}")
            
            chart = QChart()
            chart.addSeries(series)
            chart.setTitle("Spending by Category")
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
            
            self.chart_view.setChart(chart)