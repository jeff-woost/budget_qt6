"""
Budget Overview Tab - Synopsis of spending and income for the month
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
from database.db_manager import DatabaseManager

class OverviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Header with month selector
        header_layout = QHBoxLayout()
        
        title = QLabel("Budget Overview")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Month/Year selector
        self.month_combo = QComboBox()
        self.month_combo.addItems([
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ])
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        self.month_combo.currentIndexChanged.connect(self.refresh_data)
        
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        self.year_combo.addItems([str(year) for year in range(current_year - 2, current_year + 2)])
        self.year_combo.setCurrentText(str(current_year))
        self.year_combo.currentIndexChanged.connect(self.refresh_data)
        
        header_layout.addWidget(QLabel("Month:"))
        header_layout.addWidget(self.month_combo)
        header_layout.addWidget(QLabel("Year:"))
        header_layout.addWidget(self.year_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Main content area with summary cards
        content_layout = QGridLayout()
        
        # Income Summary Card
        self.income_group = self.create_summary_card("💵 Income", [
            ("Jeff's Income:", "$0.00"),
            ("Vanessa's Income:", "$0.00"),
            ("Total Income:", "$0.00")
        ])
        content_layout.addWidget(self.income_group, 0, 0)
        
        # Expense Summary Card
        self.expense_group = self.create_summary_card("💳 Expenses", [
            ("Jeff's Expenses:", "$0.00"),
            ("Vanessa's Expenses:", "$0.00"),
            ("Total Expenses:", "$0.00")
        ])
        content_layout.addWidget(self.expense_group, 0, 1)
        
        # Net Summary Card
        self.net_group = self.create_summary_card("📊 Net Results", [
            ("Net Income:", "$0.00"),
            ("Savings Rate:", "0%"),
            ("Available for Savings:", "$0.00")
        ])
        content_layout.addWidget(self.net_group, 1, 0)
        
        # Top Categories Card
        self.categories_group = self.create_summary_card("🏷️ Top Categories", [
            ("1.", ""),
            ("2.", ""),
            ("3.", ""),
            ("4.", ""),
            ("5.", "")
        ])
        content_layout.addWidget(self.categories_group, 1, 1)
        
        # Budget Health Card
        self.budget_health_group = self.create_summary_card("❤️ Budget Health", [
            ("On Track:", "0"),
            ("Over Budget:", "0"),
            ("Under Budget:", "0"),
            ("Health Score:", "0%")
        ])
        content_layout.addWidget(self.budget_health_group, 2, 0)
        
        # Quick Stats Card
        self.stats_group = self.create_summary_card("📈 Quick Stats", [
            ("Days in Month:", "30"),
            ("Daily Average:", "$0.00"),
            ("Projected Monthly:", "$0.00"),
            ("Days Remaining:", "0")
        ])
        content_layout.addWidget(self.stats_group, 2, 1)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def create_summary_card(self, title, items):
        """Create a summary card widget"""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QGridLayout()
        
        self.labels = {}
        for i, (label_text, value_text) in enumerate(items):
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: normal;")
            value = QLabel(value_text)
            value.setStyleSheet("font-weight: bold; color: #2a82da;")
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            layout.addWidget(label, i, 0)
            layout.addWidget(value, i, 1)
            
            # Store reference to value labels for updating
            key = f"{title}_{label_text}"
            self.labels[key] = value
            
        group.setLayout(layout)
        return group
        
    def refresh_data(self):
        """Refresh the overview data"""
        try:
            month = self.month_combo.currentIndex() + 1
            year = int(self.year_combo.currentText())
            
            # Get monthly summary from database
            summary = self.db.get_monthly_summary(year, month)
            
            # Update Income Card
            jeff_income = summary['income'].get('Jeff', 0)
            vanessa_income = summary['income'].get('Vanessa', 0)
            total_income = jeff_income + vanessa_income
            
            self.labels["💵 Income_Jeff's Income:"].setText(f"${jeff_income:,.2f}")
            self.labels["💵 Income_Vanessa's Income:"].setText(f"${vanessa_income:,.2f}")
            self.labels["💵 Income_Total Income:"].setText(f"${total_income:,.2f}")
            
            # Update Expense Card
            jeff_expenses = summary['expenses'].get('Jeff', 0)
            vanessa_expenses = summary['expenses'].get('Vanessa', 0)
            total_expenses = jeff_expenses + vanessa_expenses
            
            self.labels["💳 Expenses_Jeff's Expenses:"].setText(f"${jeff_expenses:,.2f}")
            self.labels["💳 Expenses_Vanessa's Expenses:"].setText(f"${vanessa_expenses:,.2f}")
            self.labels["💳 Expenses_Total Expenses:"].setText(f"${total_expenses:,.2f}")
            
            # Update Net Results Card
            net_income = total_income - total_expenses
            savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
            
            self.labels["📊 Net Results_Net Income:"].setText(f"${net_income:,.2f}")
            self.labels["📊 Net Results_Savings Rate:"].setText(f"{savings_rate:.1f}%")
            self.labels["📊 Net Results_Available for Savings:"].setText(f"${net_income:,.2f}")
            
            # Update Top Categories
            top_categories = sorted(summary['by_category'], key=lambda x: x['total'], reverse=True)[:5]
            for i in range(5):
                label_key = f"🏷️ Top Categories_{i+1}."
                if i < len(top_categories):
                    cat = top_categories[i]
                    self.labels[label_key].setText(f"{cat['category']}: ${cat['total']:,.2f}")
                else:
                    self.labels[label_key].setText("")
            
            # Update Quick Stats
            from calendar import monthrange
            days_in_month = monthrange(year, month)[1]
            current_day = datetime.now().day if datetime.now().month == month and datetime.now().year == year else days_in_month
            daily_avg = total_expenses / current_day if current_day > 0 else 0
            projected = daily_avg * days_in_month
            days_remaining = max(0, days_in_month - current_day)
            
            self.labels["📈 Quick Stats_Days in Month:"].setText(str(days_in_month))
            self.labels["📈 Quick Stats_Daily Average:"].setText(f"${daily_avg:,.2f}")
            self.labels["📈 Quick Stats_Projected Monthly:"].setText(f"${projected:,.2f}")
            self.labels["📈 Quick Stats_Days Remaining:"].setText(str(days_remaining))
            
        except Exception as e:
            print(f"Error refreshing overview data: {e}")