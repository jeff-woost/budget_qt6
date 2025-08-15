#!/usr/bin/env python3
"""
Budget Tracker Application
Main entry point for the Jeff & Vanessa Budget Tracker
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import BudgetApp

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Budget Tracker")
    app.setOrganizationName("Jeff & Vanessa")
    
    # Create and show main window
    window = BudgetApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()