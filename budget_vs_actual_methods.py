"""
Budget vs Actual methods for the Presentation Tab
This contains the enhanced implementation for category-wise budget analysis
"""

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

    # Create tables for each category
    for category, subcategories in categories_data.items():
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
