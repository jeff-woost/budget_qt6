"""
Application styling and themes
"""

def get_app_stylesheet():
    """Get the main application stylesheet with enterprise/professional theme"""
    return """
    /* Main Application Window - Distinct Border & Blue Light Reduction */
    QMainWindow {
        background-color: #faf8f5;  /* Warm off-white to reduce blue light */
        color: #2d3748;  /* Warmer dark gray instead of pure black */
        font-family: "Segoe UI", "Roboto", "Arial", sans-serif;
        border: 4px solid #2c5530;  /* Thick dark green border for main window */
        border-radius: 12px;
    }
    
    /* Tab Widget Styling - Thicker Frames */
    QTabWidget::pane {
        border: 4px solid #1e3a8a;  /* Increased from 2px to 4px */
        background-color: #fffef8;  /* Warm white background */
        border-radius: 8px;
        margin-top: 2px;
    }
    
    QTabBar::tab {
        background-color: #f0ede8;  /* Warmer tab background */
        color: #4a5568;  /* Warmer text color */
        padding: 12px 24px;  /* Increased padding */
        margin-right: 2px;
        margin-bottom: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 140px;
        font-weight: 600;
        border: 3px solid #d4c5b9;  /* Thicker border */
    }
    
    QTabBar::tab:selected {
        background-color: #fffef8;  /* Warm white */
        border: 4px solid #1e3a8a;  /* Thicker selected border */
        border-bottom: none;
        color: #1e3a8a;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #f7f1e8;  /* Warm hover color */
        border-color: #3b82f6;
    }
    
    /* Enhanced Group Box (Section Delimitation) - Much Thicker Frames */
    QGroupBox {
        font-weight: bold;
        font-size: 14px;
        color: #2c5530;  /* Dark green for better contrast */
        border: 5px solid #2c5530;  /* Much thicker border (increased from 2px to 5px) */
        border-radius: 12px;
        margin-top: 1.2ex;
        padding-top: 18px;
        background-color: #fffef8;  /* Warm white background */
        box-shadow: 0 4px 8px rgba(44, 85, 48, 0.15);  /* Enhanced shadow */
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 18px;
        padding: 0 12px;
        background-color: #fffef8;
        color: #2c5530;
        font-weight: bold;
        font-size: 15px;
    }
    
    /* Table Styling - Thicker Frames */
    QTableWidget {
        background-color: #fffef8;  /* Warm white */
        alternate-background-color: #f8f6f0;  /* Warm alternating rows */
        selection-background-color: #e6f3ff;  /* Soft blue selection */
        selection-color: #1e3a8a;
        border: 4px solid #2c5530;  /* Thicker green border */
        border-radius: 8px;
        gridline-color: #e8e2d4;  /* Warm gridlines */
        font-size: 13px;
    }
    
    QHeaderView::section {
        background-color: #2c5530;  /* Dark green headers */
        color: #ffffff;
        padding: 14px 10px;  /* Increased padding */
        border: 2px solid #1e3d24;  /* Thicker header borders */
        font-weight: bold;
        font-size: 13px;
    }
    
    QHeaderView::section:first {
        border-top-left-radius: 6px;
    }
    
    QHeaderView::section:last {
        border-top-right-radius: 6px;
    }
    
    /* Professional Button Styling - Thicker Borders */
    QPushButton {
        background-color: #2c5530;  /* Dark green buttons */
        color: #ffffff;
        border: 3px solid #2c5530;  /* Thicker button border */
        padding: 12px 20px;  /* Increased padding */
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        min-width: 100px;
        min-height: 24px;
    }
    
    QPushButton:hover {
        background-color: #38663d;
        border-color: #38663d;
        box-shadow: 0 3px 6px rgba(44, 85, 48, 0.3);
    }
    
    QPushButton:pressed {
        background-color: #1e3d24;
        border-color: #1e3d24;
    }
    
    QPushButton:disabled {
        background-color: #a0a0a0;
        border-color: #a0a0a0;
        color: #ffffff;
    }
    
    /* Form Elements - Thicker Borders */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
        padding: 10px 14px;  /* Increased padding */
        border: 3px solid #d4c5b9;  /* Thicker warm border */
        border-radius: 8px;
        background-color: #fffef8;
        font-size: 13px;
        min-height: 24px;
        color: #2d3748;
    }
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
        border-color: #2c5530;  /* Green focus border */
        outline: none;
        box-shadow: 0 0 0 3px rgba(44, 85, 48, 0.15);
    }
    
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    
    QComboBox::down-arrow {
        border: 2px solid #2c5530;
        width: 10px;
        height: 10px;
        background-color: #2c5530;
    }
    
    /* Enhanced Labels - Warmer Colors */
    QLabel {
        color: #4a5568;  /* Warmer gray text */
        font-size: 13px;
    }
    
    /* Professional Frames/Separators - Much Thicker */
    QFrame[frameShape="4"] { /* HLine */
        border: none;
        background-color: #2c5530;
        max-height: 4px;  /* Much thicker separator */
        margin: 15px 0;
    }
    
    QFrame[frameShape="5"] { /* VLine */
        border: none;
        background-color: #2c5530;
        max-width: 4px;  /* Much thicker separator */
        margin: 0 15px;
    }
    
    /* Enhanced Chart Container - Thicker Border */
    .chart-container {
        background-color: #fffef8;
        border: 4px solid #2c5530;  /* Much thicker chart borders */
        border-radius: 12px;
        padding: 20px;
        margin: 8px;
        box-shadow: 0 4px 8px rgba(44, 85, 48, 0.15);
    }
    
    /* Professional Metric Cards - Thicker Borders */
    .metric-card {
        background-color: #fffef8;
        border: 4px solid #2c5530;  /* Much thicker card borders */
        border-radius: 12px;
        padding: 24px;
        margin: 12px;
        box-shadow: 0 6px 12px rgba(44, 85, 48, 0.15);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2c5530;  /* Green metric values */
        margin-bottom: 8px;
    }
    
    .metric-label {
        font-size: 14px;
        color: #6b7280;
        font-weight: 500;
        margin-top: 8px;
    }
    
    /* Section Headers - Enhanced */
    .section-header {
        background-color: #2c5530;  /* Dark green headers */
        color: #ffffff;
        padding: 15px 18px;  /* Increased padding */
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px 8px 0 0;
        margin-bottom: 0;
        border: 3px solid #2c5530;
    }
    
    /* Content Areas - Thicker Borders */
    .content-section {
        background-color: #fffef8;
        border: 4px solid #2c5530;  /* Much thicker content borders */
        border-radius: 12px;
        padding: 20px;
        margin: 8px;
        box-shadow: 0 4px 8px rgba(44, 85, 48, 0.1);
    }
    
    /* Enhanced Scrollbars - Thicker */
    QScrollBar:vertical {
        background-color: #f8f6f0;
        width: 16px;  /* Thicker scrollbar */
        border-radius: 8px;
        border: 2px solid #d4c5b9;
    }
    
    QScrollBar::handle:vertical {
        background-color: #2c5530;
        border-radius: 6px;
        min-height: 30px;
        border: 1px solid #1e3d24;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #38663d;
    }
    
    QScrollBar:horizontal {
        background-color: #f8f6f0;
        height: 16px;  /* Thicker scrollbar */
        border-radius: 8px;
        border: 2px solid #d4c5b9;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #2c5530;
        border-radius: 6px;
        min-width: 30px;
        border: 1px solid #1e3d24;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #38663d;
    }
    
    /* Menu Styling - Updated Colors */
    QMenuBar {
        background-color: #2c5530;  /* Dark green menu bar */
        color: #ffffff;
        border-bottom: 3px solid #1e3d24;  /* Thicker border */
        font-weight: 600;
        padding: 4px;
    }
    
    QMenuBar::item {
        padding: 10px 15px;  /* Increased padding */
        background-color: transparent;
        border-radius: 6px;
    }
    
    QMenuBar::item:selected {
        background-color: #38663d;
        border-radius: 6px;
    }
    
    QMenu {
        background-color: #fffef8;
        border: 3px solid #2c5530;  /* Thicker menu border */
        border-radius: 8px;
        padding: 6px;
    }
    
    QMenu::item {
        padding: 10px 15px;
        border-radius: 6px;
        color: #2d3748;
    }
    
    QMenu::item:selected {
        background-color: #f7f1e8;
        color: #2c5530;
    }
    """

def get_chart_colors():
    """Get consistent colors for charts - Eye-friendly warm theme"""
    return [
        '#2c5530',  # Primary Dark Green
        '#38663d',  # Medium Green
        '#4a7c59',  # Forest Green
        '#5c9275',  # Sage Green
        '#6ea891',  # Teal Green
        '#8bb9a3',  # Light Green
        '#7b6143',  # Warm Brown
        '#9d7f5f',  # Light Brown
        '#b8967b',  # Tan
        '#d4c5b9',  # Warm Beige
        '#8a6b47',  # Golden Brown
        '#a68b5b',  # Olive
    ]
