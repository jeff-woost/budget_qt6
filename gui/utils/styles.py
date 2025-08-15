"""
Application styling and themes
"""

def get_app_stylesheet():
    """Get the main application stylesheet"""
    return """
    QMainWindow {
        background-color: #f5f5f5;
        color: #333333;
    }
    
    QTabWidget::pane {
        border: 1px solid #cccccc;
        background-color: white;
        border-radius: 4px;
    }
    
    QTabBar::tab {
        background-color: #e6e6e6;
        color: #333333;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 120px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #2196F3;
        font-weight: bold;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #d9d9d9;
    }
    
    QTableWidget {
        background-color: white;
        alternate-background-color: #f8f9fa;
        selection-background-color: #2196F3;
        border: 1px solid #ddd;
        gridline-color: #e0e0e0;
    }
    
    QHeaderView::section {
        background-color: #f1f3f4;
        color: #333333;
        padding: 8px;
        border: 1px solid #ddd;
        font-weight: bold;
    }
    
    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #1976D2;
    }
    
    QPushButton:pressed {
        background-color: #0D47A1;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
        padding: 6px;
        border: 1px solid #ddd;
        border-radius: 4px;
        background-color: white;
    }
    
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
        border-color: #2196F3;
    }
    
    QLabel {
        color: #333333;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 1ex;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    
    /* Chart container styling */
    .chart-container {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 8px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #2196F3;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666666;
        margin-top: 4px;
    }
    """

def get_chart_colors():
    """Get consistent colors for charts"""
    return [
        '#2196F3',  # Blue
        '#4CAF50',  # Green
        '#FF9800',  # Orange
        '#F44336',  # Red
        '#9C27B0',  # Purple
        '#00BCD4',  # Cyan
        '#795548',  # Brown
        '#607D8B',  # Blue Grey
        '#E91E63',  # Pink
        '#CDDC39',  # Lime
        '#FF5722',  # Deep Orange
        '#3F51B5',  # Indigo
    ]
