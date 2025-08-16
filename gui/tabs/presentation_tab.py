"""
Monthly Presentation Tab
Shows monthly spending breakdown by category and unrealized expenses tracking
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *

from database.models import IncomeModel, ExpenseModel
from database.category_manager import get_category_manager

class PresentationTab(QWidget):
    """Monthly presentation tab with subtabs"""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.category_manager = get_category_manager()
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

        # Budget vs Actual tab (new functionality)
        budget_vs_actual_tab = QWidget()
        self.setup_budget_vs_actual_tab(budget_vs_actual_tab)
        self.tab_widget.addTab(budget_vs_actual_tab, "Budget vs Actual")

        # Unrealized expenses tab (existing functionality)
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

    def setup_budget_vs_actual_tab(self, tab):
        """Set up the budget vs actual tab with category-specific tables"""
        layout = QVBoxLayout(tab)

        # Instructions
        instructions = QLabel(
            "This tab shows detailed budget vs actual analysis for each category. "
            "Each category displays subcategories with estimates vs actual spending by person."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; margin-bottom: 10px; font-size: 12px;")
        layout.addWidget(instructions)

        # Controls section
        controls_layout = QHBoxLayout()

        # Refresh button
        refresh_btn = QPushButton("Refresh Analysis")
        refresh_btn.clicked.connect(self.refresh_budget_vs_actual_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c5530;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #38663d;
            }
        """)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Create scroll area for category tables
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Widget to contain all category tables
        self.categories_widget = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(15)

        scroll_area.setWidget(self.categories_widget)
        layout.addWidget(scroll_area)

        # Store references to category tables for updates
        self.category_tables = {}

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
        self.refresh_budget_vs_actual_data()
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

    def refresh_budget_vs_actual_data(self):
        """Refresh data for the budget vs actual tab with category-specific tables"""
        # Get selected month range
        selected_date = self.month_selector.date()
        month_start = selected_date.toString("yyyy-MM-01")
        month_end = selected_date.addMonths(1).addDays(-1).toString("yyyy-MM-dd")

        # Clear existing tables
        for i in reversed(range(self.categories_layout.count())):
            child = self.categories_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.category_tables.clear()

        # Get all categories and their subcategories
        categories_data = self.category_manager.get_categories()

        # Get actual expenses by category, subcategory, and person
        cursor = self.db.execute('''
            SELECT 
                category,
                subcategory,
                person,
                COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category, subcategory, person
            ORDER BY category, subcategory, person
        ''', (month_start, month_end))

        actual_expenses = {}
        for row in cursor.fetchall():
            key = (row['category'], row['subcategory'])
            if key not in actual_expenses:
                actual_expenses[key] = {'Jeff': 0, 'Vanessa': 0}
            actual_expenses[key][row['person']] = row['total']

        # Get budget targets (if they exist)
        year = selected_date.year()
        month = selected_date.month()
        cursor = self.db.execute('''
            SELECT category, subcategory, monthly_target
            FROM budget_targets
            WHERE year = ? AND month = ?
        ''', (year, month))

        budget_targets = {}
        for row in cursor.fetchall():
            key = (row['category'], row['subcategory'])
            budget_targets[key] = row['monthly_target']

        # Create tables for each category that has either expenses or budget
        all_category_keys = set(actual_expenses.keys()) | set(budget_targets.keys())
        categories_with_data = {}

        for key in all_category_keys:
            category = key[0]
            if category not in categories_with_data:
                categories_with_data[category] = []
            categories_with_data[category].append(key[1])

        # Add categories from category manager that don't have data but should be shown
        for category, subcategories in categories_data.items():
            if category not in categories_with_data:
                categories_with_data[category] = subcategories
            else:
                # Add any missing subcategories
                for subcat in subcategories:
                    if subcat not in categories_with_data[category]:
                        categories_with_data[category].append(subcat)

        # Create tables for each category
        for category, subcategories in categories_with_data.items():
            self.create_category_table(category, subcategories, actual_expenses, budget_targets)

        # Add stretch at the end
        self.categories_layout.addStretch()

    def create_category_table(self, category, subcategories, actual_expenses, budget_targets):
        """Create a table for a specific category"""
        # Create group box for the category
        category_group = QGroupBox(f"{category} - Budget vs Actual")
        category_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c5530;
                border: 3px solid #2c5530;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #fffef8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px;
                background-color: #fffef8;
                color: #2c5530;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        category_layout = QVBoxLayout(category_group)

        # Create table for this category
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Subcategory", "Estimate", "Jeff's Expenses", "Vanessa's Expenses", "Total Actual", "Variance"
        ])

        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Subcategory
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Estimate
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Jeff
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Vanessa
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Total
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Variance

        table.setColumnWidth(1, 100)  # Estimate
        table.setColumnWidth(2, 120)  # Jeff
        table.setColumnWidth(3, 120)  # Vanessa
        table.setColumnWidth(4, 100)  # Total
        table.setColumnWidth(5, 100)  # Variance

        # Style the table
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                background-color: #fffef8;
                alternate-background-color: #f8f6f0;
                selection-background-color: #e6f3ff;
                gridline-color: #e8e2d4;
                border: 2px solid #d4c5b9;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #2c5530;
                color: white;
                padding: 8px;
                border: 1px solid #1e3d24;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
                color: #2d3748;
            }
        """)

        # Populate table with subcategories
        table.setRowCount(len(subcategories))
        category_totals = {'estimate': 0, 'jeff': 0, 'vanessa': 0, 'actual': 0, 'variance': 0}

        for i, subcategory in enumerate(subcategories):
            # Subcategory name
            table.setItem(i, 0, QTableWidgetItem(subcategory))

            # Get budget estimate (default to 0 if no budget set)
            key = (category, subcategory)
            estimate = budget_targets.get(key, 0)
            table.setItem(i, 1, QTableWidgetItem(f"${estimate:,.2f}"))

            # Get actual expenses
            jeff_actual = actual_expenses.get(key, {}).get('Jeff', 0)
            vanessa_actual = actual_expenses.get(key, {}).get('Vanessa', 0)
            total_actual = jeff_actual + vanessa_actual

            # Jeff's expenses
            jeff_item = QTableWidgetItem(f"${jeff_actual:,.2f}")
            if jeff_actual > 0:
                jeff_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            table.setItem(i, 2, jeff_item)

            # Vanessa's expenses
            vanessa_item = QTableWidgetItem(f"${vanessa_actual:,.2f}")
            if vanessa_actual > 0:
                vanessa_item.setForeground(QColor(200, 50, 50))  # Red for expenses
            table.setItem(i, 3, vanessa_item)

            # Total actual
            total_item = QTableWidgetItem(f"${total_actual:,.2f}")
            if total_actual > 0:
                total_item.setForeground(QColor(200, 50, 50))  # Red for expenses
                total_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            table.setItem(i, 4, total_item)

            # Variance (Estimate - Actual)
            variance = estimate - total_actual
            variance_item = QTableWidgetItem(f"${variance:,.2f}")
            if variance < 0:
                variance_item.setForeground(QColor(200, 50, 50))  # Red for over budget
                variance_item.setFont(QFont("Arial", -1, QFont.Weight.Bold))
            else:
                variance_item.setForeground(QColor(50, 150, 50))  # Green for under budget
            table.setItem(i, 5, variance_item)

            # Add to category totals
            category_totals['estimate'] += estimate
            category_totals['jeff'] += jeff_actual
            category_totals['vanessa'] += vanessa_actual
            category_totals['actual'] += total_actual
            category_totals['variance'] += variance

        # Add totals row
        totals_row = table.rowCount()
        table.insertRow(totals_row)

        # Style totals row
        total_font = QFont("Arial", -1, QFont.Weight.Bold)

        total_label = QTableWidgetItem("TOTAL")
        total_label.setFont(total_font)
        total_label.setBackground(QColor(230, 230, 230))
        table.setItem(totals_row, 0, total_label)

        estimate_total = QTableWidgetItem(f"${category_totals['estimate']:,.2f}")
        estimate_total.setFont(total_font)
        estimate_total.setBackground(QColor(230, 230, 230))
        table.setItem(totals_row, 1, estimate_total)

        jeff_total = QTableWidgetItem(f"${category_totals['jeff']:,.2f}")
        jeff_total.setFont(total_font)
        jeff_total.setBackground(QColor(230, 230, 230))
        jeff_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 2, jeff_total)

        vanessa_total = QTableWidgetItem(f"${category_totals['vanessa']:,.2f}")
        vanessa_total.setFont(total_font)
        vanessa_total.setBackground(QColor(230, 230, 230))
        vanessa_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 3, vanessa_total)

        actual_total = QTableWidgetItem(f"${category_totals['actual']:,.2f}")
        actual_total.setFont(total_font)
        actual_total.setBackground(QColor(230, 230, 230))
        actual_total.setForeground(QColor(200, 50, 50))
        table.setItem(totals_row, 4, actual_total)

        variance_total = QTableWidgetItem(f"${category_totals['variance']:,.2f}")
        variance_total.setFont(total_font)
        variance_total.setBackground(QColor(230, 230, 230))
        if category_totals['variance'] < 0:
            variance_total.setForeground(QColor(200, 50, 50))
        else:
            variance_total.setForeground(QColor(50, 150, 50))
        table.setItem(totals_row, 5, variance_total)

        # Set table height based on content
        table.resizeRowsToContents()
        table_height = table.verticalHeader().length() + table.horizontalHeader().height() + 20
        table.setMaximumHeight(min(table_height, 300))  # Cap at 300px
        table.setMinimumHeight(min(table_height, 150))  # Minimum 150px

        category_layout.addWidget(table)

        # Store table reference
        self.category_tables[category] = table

        # Add to main layout
        self.categories_layout.addWidget(category_group)

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
