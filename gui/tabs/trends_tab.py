"""
Trends Tab - Shows spending trends and habits over time
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QPieSeries, QCategoryAxis, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    # Fallback if QtCharts is not available
    print("Warning: PyQt6.QtCharts not available. Charts will be disabled.")
    QChart = QChartView = QLineSeries = QPieSeries = QCategoryAxis = QValueAxis = type(None)
    CHARTS_AVAILABLE = False
    
from datetime import datetime, timedelta
import sqlite3

from database.db_manager import DatabaseManager

class TrendsTab(QWidget):
    """Trends and analytics tab"""
    
    def __init__(self, db=None):
        super().__init__()
        # Handle both DatabaseManager and direct connection
        if isinstance(db, DatabaseManager):
            self.db_manager = db
            self.db = None
        else:
            self.db = db
            self.db_manager = DatabaseManager()
            
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Spending Trends & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Time period selector
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Time Period:"))
        
        self.period_selector = QComboBox()
        self.period_selector.addItems([
            "Last 6 Months",
            "Last 12 Months", 
            "Last 2 Years",
            "All Time"
        ])
        self.period_selector.setCurrentText("Last 12 Months")
        self.period_selector.currentTextChanged.connect(self.refresh_data)
        period_layout.addWidget(self.period_selector)
        
        period_layout.addStretch()
        
        # Export button
        export_btn = QPushButton("Export Trends Report")
        export_btn.clicked.connect(self.export_trends_report)
        period_layout.addWidget(export_btn)
        
        layout.addLayout(period_layout)
        
        # Create main content area with tabs
        self.content_tabs = QTabWidget()
        
        # Monthly trends tab
        self.monthly_tab = self.create_monthly_trends_tab()
        self.content_tabs.addTab(self.monthly_tab, "Monthly Trends")
        
        # Category trends tab
        self.category_tab = self.create_category_trends_tab()
        self.content_tabs.addTab(self.category_tab, "Category Analysis")
        
        # Spending habits tab
        self.habits_tab = self.create_spending_habits_tab()
        self.content_tabs.addTab(self.habits_tab, "Spending Habits")
        
        # Net worth trends tab
        self.networth_tab = self.create_networth_trends_tab()
        self.content_tabs.addTab(self.networth_tab, "Net Worth Growth")
        
        layout.addWidget(self.content_tabs)
        
    def create_monthly_trends_tab(self):
        """Create monthly trends visualization tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Summary metrics
        metrics_layout = QHBoxLayout()
        
        # Income trend metric
        income_frame = QFrame()
        income_frame.setFrameStyle(QFrame.Shape.Box)
        income_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        income_layout = QVBoxLayout(income_frame)
        
        self.avg_income_label = QLabel("$0")
        self.avg_income_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
        self.income_trend_label = QLabel("Avg Monthly Income")
        self.income_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        income_layout.addWidget(self.avg_income_label)
        income_layout.addWidget(self.income_trend_label)
        metrics_layout.addWidget(income_frame)
        
        # Expense trend metric
        expense_frame = QFrame()
        expense_frame.setFrameStyle(QFrame.Shape.Box)
        expense_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        expense_layout = QVBoxLayout(expense_frame)
        
        self.avg_expense_label = QLabel("$0")
        self.avg_expense_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
        self.expense_trend_label = QLabel("Avg Monthly Expenses")
        self.expense_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        expense_layout.addWidget(self.avg_expense_label)
        expense_layout.addWidget(self.expense_trend_label)
        metrics_layout.addWidget(expense_frame)
        
        # Savings trend metric
        savings_frame = QFrame()
        savings_frame.setFrameStyle(QFrame.Shape.Box)
        savings_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        savings_layout = QVBoxLayout(savings_frame)
        
        self.avg_savings_label = QLabel("$0")
        self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3;")
        self.savings_trend_label = QLabel("Avg Monthly Savings")
        self.savings_trend_label.setStyleSheet("color: #666; font-size: 12px;")
        savings_layout.addWidget(self.avg_savings_label)
        savings_layout.addWidget(self.savings_trend_label)
        metrics_layout.addWidget(savings_frame)
        
        layout.addLayout(metrics_layout)
        
        # Monthly trend chart
        if CHARTS_AVAILABLE:
            self.monthly_chart_view = QChartView()
            self.monthly_chart_view.setMinimumHeight(400)
        else:
            self.monthly_chart_view = QLabel("Charts not available - PyQt6.QtCharts not installed")
            self.monthly_chart_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.monthly_chart_view.setMinimumHeight(400)
            self.monthly_chart_view.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        layout.addWidget(self.monthly_chart_view)
        
        return widget
        
    def create_category_trends_tab(self):
        """Create category analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Category comparison controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Compare Categories:"))
        
        self.category_selector = QComboBox()
        self.category_selector.addItem("All Categories")
        self.category_selector.currentTextChanged.connect(self.refresh_category_trends)
        controls_layout.addWidget(self.category_selector)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Split layout for charts
        charts_layout = QHBoxLayout()
        
        # Category trend over time (left)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Category Spending Over Time"))
        if CHARTS_AVAILABLE:
            self.category_trend_chart = QChartView()
            self.category_trend_chart.setMinimumHeight(300)
        else:
            self.category_trend_chart = QLabel("Charts not available")
            self.category_trend_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_trend_chart.setMinimumHeight(300)
            self.category_trend_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        left_layout.addWidget(self.category_trend_chart)
        charts_layout.addWidget(left_widget)
        
        # Category distribution pie chart (right)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("Category Distribution"))
        if CHARTS_AVAILABLE:
            self.category_pie_chart = QChartView()
            self.category_pie_chart.setMinimumHeight(300)
        else:
            self.category_pie_chart = QLabel("Charts not available")
            self.category_pie_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.category_pie_chart.setMinimumHeight(300)
            self.category_pie_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        right_layout.addWidget(self.category_pie_chart)
        charts_layout.addWidget(right_widget)
        
        layout.addLayout(charts_layout)
        
        # Category details table
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(6)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "This Month", "Last Month", "Change", "6-Month Avg", "Trend"
        ])
        self.category_table.horizontalHeader().setStretchLastSection(True)
        self.category_table.setMaximumHeight(200)
        layout.addWidget(self.category_table)
        
        return widget
        
    def create_spending_habits_tab(self):
        """Create spending habits analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Spending patterns section
        patterns_group = QGroupBox("Spending Patterns")
        patterns_layout = QVBoxLayout(patterns_group)
        
        # Day of week spending
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Spending by Day of Week:"))
        if CHARTS_AVAILABLE:
            self.day_chart = QChartView()
            self.day_chart.setMaximumHeight(200)
        else:
            self.day_chart = QLabel("Charts not available")
            self.day_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.day_chart.setMaximumHeight(200)
            self.day_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        day_layout.addWidget(self.day_chart)
        patterns_layout.addLayout(day_layout)
        
        layout.addWidget(patterns_group)
        
        # Person comparison section
        person_group = QGroupBox("Jeff vs Vanessa Spending")
        person_layout = QVBoxLayout(person_group)
        
        # Person comparison chart
        if CHARTS_AVAILABLE:
            self.person_chart = QChartView()
            self.person_chart.setMinimumHeight(300)
        else:
            self.person_chart = QLabel("Charts not available")
            self.person_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.person_chart.setMinimumHeight(300)
            self.person_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        person_layout.addWidget(self.person_chart)
        
        layout.addWidget(person_group)
        
        # Insights section
        insights_group = QGroupBox("Spending Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.insights_text = QTextEdit()
        self.insights_text.setMaximumHeight(150)
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)
        
        layout.addWidget(insights_group)
        
        return widget
        
    def create_networth_trends_tab(self):
        """Create net worth trends tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Net worth summary
        summary_layout = QHBoxLayout()
        
        # Current net worth
        current_frame = QFrame()
        current_frame.setFrameStyle(QFrame.Shape.Box)
        current_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        current_layout = QVBoxLayout(current_frame)
        
        self.current_networth_label = QLabel("$0")
        self.current_networth_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        current_layout.addWidget(QLabel("Current Net Worth"))
        current_layout.addWidget(self.current_networth_label)
        summary_layout.addWidget(current_frame)
        
        # Monthly change
        change_frame = QFrame()
        change_frame.setFrameStyle(QFrame.Shape.Box)
        change_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; padding: 10px; background: white;")
        change_layout = QVBoxLayout(change_frame)
        
        self.networth_change_label = QLabel("$0")
        self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        change_layout.addWidget(QLabel("Monthly Change"))
        change_layout.addWidget(self.networth_change_label)
        summary_layout.addWidget(change_frame)
        
        layout.addLayout(summary_layout)
        
        # Net worth chart
        if CHARTS_AVAILABLE:
            self.networth_chart = QChartView()
            self.networth_chart.setMinimumHeight(400)
        else:
            self.networth_chart = QLabel("Charts not available")
            self.networth_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.networth_chart.setMinimumHeight(400)
            self.networth_chart.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        layout.addWidget(self.networth_chart)
        
        return widget
        
    def refresh_data(self):
        """Refresh all trend data"""
        self.refresh_monthly_trends()
        self.refresh_category_trends()
        self.refresh_spending_habits()
        self.refresh_networth_trends()
        
    def refresh_monthly_trends(self):
        """Refresh monthly trends data"""
        # Get date range based on selection
        end_date = datetime.now()
        
        period = self.period_selector.currentText()
        if period == "Last 6 Months":
            start_date = end_date - timedelta(days=180)
        elif period == "Last 12 Months":
            start_date = end_date - timedelta(days=365)
        elif period == "Last 2 Years":
            start_date = end_date - timedelta(days=730)
        else:  # All Time
            start_date = datetime(2020, 1, 1)
            
        # Get monthly data
        monthly_data = self.get_monthly_summary(start_date, end_date)
        
        # Update metrics
        if monthly_data:
            avg_income = sum(month['income'] for month in monthly_data) / len(monthly_data)
            avg_expense = sum(month['expenses'] for month in monthly_data) / len(monthly_data)
            avg_savings = avg_income - avg_expense
            
            self.avg_income_label.setText(f"${avg_income:,.2f}")
            self.avg_expense_label.setText(f"${avg_expense:,.2f}")
            self.avg_savings_label.setText(f"${avg_savings:,.2f}")
            
            # Update color based on savings trend
            if avg_savings > 0:
                self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
            else:
                self.avg_savings_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
        
        # Create monthly trends chart
        self.create_monthly_trends_chart(monthly_data)
        
    def refresh_category_trends(self):
        """Refresh category trends"""
        # Get categories for selector
        categories = self.get_categories()
        
        # Temporarily disconnect to avoid recursion
        self.category_selector.currentTextChanged.disconnect()
        
        current_text = self.category_selector.currentText()
        self.category_selector.clear()
        self.category_selector.addItem("All Categories")
        self.category_selector.addItems(categories)
        
        # Restore selection if it still exists
        index = self.category_selector.findText(current_text)
        if index >= 0:
            self.category_selector.setCurrentIndex(index)
            
        # Reconnect the signal
        self.category_selector.currentTextChanged.connect(self.refresh_category_trends)
            
        # Update charts and table
        self.create_category_charts()
        self.update_category_table()
        
    def refresh_spending_habits(self):
        """Refresh spending habits analysis"""
        self.create_day_of_week_chart()
        self.create_person_comparison_chart()
        self.update_spending_insights()
        
    def refresh_networth_trends(self):
        """Refresh net worth trends"""
        try:
            # Get current net worth using database manager
            current_networth = self.get_current_networth()
            self.current_networth_label.setText(f"${current_networth:,.2f}")
            
            # Calculate monthly change (placeholder - would need historical data)
            monthly_change = 0  # This would be calculated from historical net worth data
            self.networth_change_label.setText(f"${monthly_change:,.2f}")
            
            if monthly_change >= 0:
                self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #4CAF50;")
            else:
                self.networth_change_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #F44336;")
                
            # Create net worth chart (placeholder)
            self.create_networth_chart()
            
        except Exception as e:
            print(f"Error refreshing net worth trends: {e}")
            
    def get_current_networth(self):
        """Get current net worth total"""
        try:
            if self.db_manager:
                self.db_manager.connect()
                cursor = self.db_manager.cursor
                cursor.execute('''
                    SELECT COALESCE(SUM(value), 0) as total
                    FROM net_worth
                    WHERE date = (SELECT MAX(date) FROM net_worth)
                ''')
                result = cursor.fetchone()
                self.db_manager.disconnect()
                return result[0] if result else 0
            else:
                # Fallback for direct database connection
                cursor = self.db.execute('''
                    SELECT COALESCE(SUM(value), 0) as total
                    FROM net_worth
                    WHERE date = (SELECT MAX(date) FROM net_worth)
                ''')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Error getting current net worth: {e}")
            return 0
            
    def get_monthly_income_expenses(self, month_start, month_end):
        """Get monthly income and expenses totals"""
        try:
            if self.db_manager:
                self.db_manager.connect()
                cursor = self.db_manager.cursor
                
                # Get income
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM income
                    WHERE date >= ? AND date <= ?
                ''', (month_start, month_end))
                income_result = cursor.fetchone()
                income = income_result[0] if income_result else 0
                
                # Get expenses
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM expenses
                    WHERE date >= ? AND date <= ?
                ''', (month_start, month_end))
                expenses_result = cursor.fetchone()
                expenses = expenses_result[0] if expenses_result else 0
                
                self.db_manager.disconnect()
                return income, expenses
            else:
                # Fallback for direct database connection
                income_cursor = self.db.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM income
                    WHERE date >= ? AND date <= ?
                ''', (month_start, month_end))
                income_result = income_cursor.fetchone()
                income = income_result[0] if income_result else 0
                
                expenses_cursor = self.db.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM expenses
                    WHERE date >= ? AND date <= ?
                ''', (month_start, month_end))
                expenses_result = expenses_cursor.fetchone()
                expenses = expenses_result[0] if expenses_result else 0
                
                return income, expenses
                
        except Exception as e:
            print(f"Error getting monthly income/expenses: {e}")
            return 0, 0
            
    def get_monthly_summary(self, start_date, end_date):
        """Get monthly summary data"""
        try:
            monthly_data = []
            current_date = start_date.replace(day=1)
            
            while current_date <= end_date:
                # Calculate month boundaries
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1)
                
                month_start = current_date.strftime("%Y-%m-%d")
                month_end = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")
                
                # Get income and expenses for month
                income, expenses = self.get_monthly_income_expenses(month_start, month_end)
                
                monthly_data.append({
                    'month': current_date.strftime("%b %Y"),
                    'date': current_date,
                    'income': income,
                    'expenses': expenses,
                    'savings': income - expenses
                })
                
                current_date = next_month
                
            return monthly_data
            
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return []
            
    def get_categories(self):
        """Get list of expense categories"""
        try:
            if self.db_manager:
                self.db_manager.connect()
                cursor = self.db_manager.cursor
                cursor.execute('''
                    SELECT DISTINCT category
                    FROM expenses
                    ORDER BY category
                ''')
                result = [row[0] for row in cursor.fetchall()]
                self.db_manager.disconnect()
                return result
            else:
                cursor = self.db.execute('''
                    SELECT DISTINCT category
                    FROM expenses
                    ORDER BY category
                ''')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
            
    def create_monthly_trends_chart(self, monthly_data):
        """Create monthly trends line chart"""
        if not CHARTS_AVAILABLE:
            return
            
        chart = QChart()
        chart.setTitle("Monthly Income, Expenses & Savings Trends")
        
        if not monthly_data:
            self.monthly_chart_view.setChart(chart)
            return
            
        # Create series
        income_series = QLineSeries()
        income_series.setName("Income")
        
        expense_series = QLineSeries()
        expense_series.setName("Expenses")
        
        savings_series = QLineSeries()
        savings_series.setName("Savings")
        
        # Add data points
        for i, data in enumerate(monthly_data):
            income_series.append(i, data['income'])
            expense_series.append(i, data['expenses'])
            savings_series.append(i, data['savings'])
            
        # Add series to chart
        chart.addSeries(income_series)
        chart.addSeries(expense_series)
        chart.addSeries(savings_series)
        
        # Create axes
        axis_x = QCategoryAxis()
        for i, data in enumerate(monthly_data):
            axis_x.append(data['month'], i)
        axis_x.setLabelsAngle(-45)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Amount ($)")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        # Attach axes to series
        income_series.attachAxis(axis_x)
        income_series.attachAxis(axis_y)
        expense_series.attachAxis(axis_x)
        expense_series.attachAxis(axis_y)
        savings_series.attachAxis(axis_x)
        savings_series.attachAxis(axis_y)
        
        # Style the chart
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.monthly_chart_view.setChart(chart)
        
    def create_category_charts(self):
        """Create category analysis charts"""
        if not CHARTS_AVAILABLE:
            return
            
        # Placeholder for category trend chart
        trend_chart = QChart()
        trend_chart.setTitle("Category Spending Trends")
        self.category_trend_chart.setChart(trend_chart)
        
        # Create pie chart for category distribution
        pie_chart = QChart()
        pie_chart.setTitle("Current Month Category Distribution")
        
        try:
            # Get current month data
            current_date = datetime.now()
            month_start = current_date.replace(day=1).strftime("%Y-%m-%d")
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
            month_end = month_end.strftime("%Y-%m-%d")
            
            # Get category data
            if self.db_manager:
                self.db_manager.connect()
                cursor = self.db_manager.cursor
                cursor.execute('''
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE date >= ? AND date <= ?
                    GROUP BY category
                    ORDER BY total DESC
                ''', (month_start, month_end))
                category_data = cursor.fetchall()
                self.db_manager.disconnect()
            else:
                cursor = self.db.execute('''
                    SELECT category, SUM(amount) as total
                    FROM expenses
                    WHERE date >= ? AND date <= ?
                    GROUP BY category
                    ORDER BY total DESC
                ''', (month_start, month_end))
                category_data = cursor.fetchall()
            
            if category_data:
                pie_series = QPieSeries()
                
                for category, amount in category_data:
                    pie_series.append(category, amount)
                    
                pie_chart.addSeries(pie_series)
                pie_series.setLabelsVisible(True)
                
        except Exception as e:
            print(f"Error creating category pie chart: {e}")
            
        self.category_pie_chart.setChart(pie_chart)
        
    def update_category_table(self):
        """Update category comparison table"""
        # Placeholder for category table updates
        self.category_table.setRowCount(0)
        
    def create_day_of_week_chart(self):
        """Create day of week spending chart"""
        if not CHARTS_AVAILABLE:
            return
            
        chart = QChart()
        chart.setTitle("Average Spending by Day of Week")
        
        # Placeholder chart
        self.day_chart.setChart(chart)
        
    def create_person_comparison_chart(self):
        """Create person spending comparison chart"""
        if not CHARTS_AVAILABLE:
            return
            
        chart = QChart()
        chart.setTitle("Jeff vs Vanessa Monthly Spending Comparison")
        
        # Placeholder chart
        self.person_chart.setChart(chart)
        
    def update_spending_insights(self):
        """Update spending insights text"""
        insights = [
            "• Spending patterns analysis will appear here",
            "• Recommendations for budget optimization",
            "• Seasonal spending trends",
            "• Areas for potential savings"
        ]
        
        self.insights_text.setPlainText("\n".join(insights))
        
    def create_networth_chart(self):
        """Create net worth growth chart"""
        if not CHARTS_AVAILABLE:
            return
            
        chart = QChart()
        chart.setTitle("Net Worth Growth Over Time")
        
        # Placeholder chart - would show historical net worth data
        self.networth_chart.setChart(chart)
        
    def export_trends_report(self):
        """Export trends report to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Trends Report",
            f"trends_report_{datetime.now().strftime('%Y%m%d')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("Budget Trends Report\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Period: {self.period_selector.currentText()}\n\n")
                    
                    # Add summary data
                    f.write("Summary:\n")
                    f.write(f"Average Monthly Income: {self.avg_income_label.text()}\n")
                    f.write(f"Average Monthly Expenses: {self.avg_expense_label.text()}\n")
                    f.write(f"Average Monthly Savings: {self.avg_savings_label.text()}\n")
                    
                QMessageBox.information(self, "Export Complete", f"Trends report exported to:\n{file_path}")
                
            except Exception as e:
                QMessageBox.warning(self, "Export Error", f"Failed to export report:\n{str(e)}")
