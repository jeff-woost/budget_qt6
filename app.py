"""
Main application window
"""

from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from database.db_manager import DatabaseManager
from gui.tabs.overview_tab import OverviewTab
from gui.tabs.net_worth_tab import NetWorthTab
from gui.tabs.budget_tab import BudgetTab
from gui.tabs.presentation_tab import PresentationTab
from gui.tabs.savings_tab import SavingsTab
from gui.tabs.trends_tab import TrendsTab
from gui.utils.styles import get_app_stylesheet

class BudgetApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jeff & Vanessa Budget Tracker")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize database
        self.db = DatabaseManager()
        self.db.initialize_database()
        
        # Set up UI
        self.setup_ui()
        
        # Apply styling
        self.setStyleSheet(get_app_stylesheet())
        
    def setup_ui(self):
        """Set up the main UI with all tabs"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tab instances with database connection
        self.overview_tab = OverviewTab()
        self.net_worth_tab = NetWorthTab()
        self.budget_tab = BudgetTab()
        self.presentation_tab = PresentationTab(self.db)
        self.savings_tab = SavingsTab(self.db)
        self.trends_tab = TrendsTab(self.db)
        
        # Add tabs
        self.tabs.addTab(self.overview_tab, "Budget Overview")
        self.tabs.addTab(self.net_worth_tab, "Net Worth")
        self.tabs.addTab(self.budget_tab, "Budget")
        self.tabs.addTab(self.presentation_tab, "Monthly Presentation")
        self.tabs.addTab(self.savings_tab, "Savings Goals")
        self.tabs.addTab(self.trends_tab, "Trends")
        
        # Connect tab change signal to refresh data
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
    def on_tab_changed(self, index):
        """Handle tab change events"""
        # Refresh the current tab's data
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, 'refresh_data'):
            current_widget.refresh_data()