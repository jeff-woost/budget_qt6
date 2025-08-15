"""
Savings Goals Tab
Manage and allocate funds to savings goals
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from database.models import SavingsGoalModel, IncomeModel, ExpenseModel

class SavingsTab(QWidget):
    """Savings goals tab"""
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Savings Goals")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        # Available to save display
        available_layout = QHBoxLayout()
        available_layout.addWidget(QLabel("Available to Allocate:"))
        self.available_label = QLabel("$0.00")
        self.available_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        available_layout.addWidget(self.available_label)
        available_layout.addStretch()
        layout.addLayout(available_layout)
        
        # Withdrawal amounts
        withdrawal_group = QGroupBox("Monthly Withdrawals for Bills")
        withdrawal_layout = QGridLayout()
        
        withdrawal_layout.addWidget(QLabel("Jeff's Total Expenses:"), 0, 0)
        self.jeff_withdrawal_label = QLabel("$0.00")
        withdrawal_layout.addWidget(self.jeff_withdrawal_label, 0, 1)
        
        withdrawal_layout.addWidget(QLabel("Vanessa's Total Expenses:"), 1, 0)
        self.vanessa_withdrawal_label = QLabel("$0.00")
        withdrawal_layout.addWidget(self.vanessa_withdrawal_label, 1, 1)
        
        withdrawal_group.setLayout(withdrawal_layout)
        layout.addWidget(withdrawal_group)
        
        # Goals form
        goals_group = QGroupBox("Add/Edit Savings Goal")
        goals_layout = QGridLayout()
        
        goals_layout.addWidget(QLabel("Goal Name:"), 0, 0)
        self.goal_name = QLineEdit()
        self.goal_name.setPlaceholderText("e.g., Emergency Fund")
        goals_layout.addWidget(self.goal_name, 0, 1)
        
        goals_layout.addWidget(QLabel("Target Amount:"), 1, 0)
        self.goal_target = QLineEdit()
        self.goal_target.setPlaceholderText("0.00")
        goals_layout.addWidget(self.goal_target, 1, 1)
        
        goals_layout.addWidget(QLabel("Target Date:"), 2, 0)
        self.goal_date = QDateEdit()
        self.goal_date.setDate(QDate.currentDate().addMonths(12))
        self.goal_date.setCalendarPopup(True)
        goals_layout.addWidget(self.goal_date, 2, 1)
        
        goals_layout.addWidget(QLabel("Priority (1-10):"), 3, 0)
        self.goal_priority = QSpinBox()
        self.goal_priority.setRange(1, 10)
        self.goal_priority.setValue(5)
        goals_layout.addWidget(self.goal_priority, 3, 1)
        
        add_goal_btn = QPushButton("Add Goal")
        add_goal_btn.clicked.connect(self.add_goal)
        goals_layout.addWidget(add_goal_btn, 4, 0, 1, 2)
        
        goals_group.setLayout(goals_layout)
        layout.addWidget(goals_group)
        
        # Goals table
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(7)
        self.goals_table.setHorizontalHeaderLabels([
            "Goal", "Target", "Current", "Progress", "Target Date", 
            "Monthly Needed", "Actions"
        ])
        self.goals_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.goals_table)
        
        # Allocate button
        allocate_btn = QPushButton("Allocate Available Funds")
        allocate_btn.clicked.connect(self.allocate_savings)
        layout.addWidget(allocate_btn)
        
    def add_goal(self):
        """Add savings goal"""
        try:
            name = self.goal_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter a goal name.")
                return
                
            target = float(self.goal_target.text() or 0)
            if target <= 0:
                QMessageBox.warning(self, "Warning", "Please enter a valid target amount.")
                return
                
            SavingsGoalModel.add(
                self.db,
                name,
                target,
                self.goal_date.date().toString("yyyy-MM-dd"),
                self.goal_priority.value()
            )
            
            # Clear form
            self.goal_name.clear()
            self.goal_target.clear()
            self.goal_priority.setValue(5)
            
            self.refresh_data()
            QMessageBox.information(self, "Success", "Savings goal added successfully!")
            
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter a valid amount.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add goal: {str(e)}")
            
    def delete_goal(self, goal_id):
        """Delete savings goal"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this goal?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            SavingsGoalModel.delete(self.db, goal_id)
            self.refresh_data()
            
    def allocate_savings(self):
        """Allocate available funds to goals"""
        try:
            # Get available amount
            month_start = QDate.currentDate().toString("yyyy-MM-01")
            month_end = QDate.currentDate().addMonths(1).addDays(-1).toString("yyyy-MM-dd")
            
            total_income = IncomeModel.get_total_by_month(self.db, month_start, month_end)
            total_expenses = ExpenseModel.get_total_by_month(self.db, month_start, month_end)
            
            available = total_income - total_expenses
            
            if available <= 0:
                QMessageBox.warning(self, "No Funds", "No funds available to allocate.")
                return
                
            # Get goals ordered by priority
            goals = SavingsGoalModel.get_all(self.db)
            
            # Allocate funds
            remaining = available
            allocations = []
            
            for goal in goals:
                if remaining <= 0:
                    break
                    
                needed = goal['target_amount'] - goal['current_amount']
                if needed <= 0:
                    continue
                    
                allocation = min(remaining, needed)
                
                # Update goal
                SavingsGoalModel.update_amount(self.db, goal['id'], allocation)
                
                # Record allocation
                self.db.execute('''
                    INSERT INTO savings_allocations (date, goal_id, amount)
                    VALUES (date('now'), ?, ?)
                ''', (goal['id'], allocation))
                
                allocations.append((goal['goal_name'], allocation))
                remaining -= allocation
                
            self.db.commit()
            
            # Show summary
            if allocations:
                summary = "Funds Allocated:\n\n"
                for name, amount in allocations:
                    summary += f"{name}: ${amount:.2f}\n"
                if remaining > 0:
                    summary += f"\nRemaining unallocated: ${remaining:.2f}"
                    
                QMessageBox.information(self, "Allocation Complete", summary)
            else:
                QMessageBox.information(self, "No Allocation", "No funds were allocated.")
                
            self.refresh_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to allocate savings: {str(e)}")
            
    def refresh_data(self):
        """Refresh savings goals display"""
        # Calculate available to save
        month_start = QDate.currentDate().toString("yyyy-MM-01")
        month_end = QDate.currentDate().addMonths(1).addDays(-1).toString("yyyy-MM-dd")
        
        total_income = IncomeModel.get_total_by_month(self.db, month_start, month_end)
        
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
        
        available = total_income - total_expenses
        
        self.available_label.setText(f"${available:,.2f}")
        self.jeff_withdrawal_label.setText(f"${jeff_expenses:,.2f}")
        self.vanessa_withdrawal_label.setText(f"${vanessa_expenses:,.2f}")
        
        # Update goals table
        goals = SavingsGoalModel.get_all(self.db)
        
        self.goals_table.setRowCount(len(goals))
        for i, goal in enumerate(goals):
            progress = (goal['current_amount'] / goal['target_amount'] * 100) if goal['target_amount'] > 0 else 0
            
            self.goals_table.setItem(i, 0, QTableWidgetItem(goal['goal_name']))
            self.goals_table.setItem(i, 1, QTableWidgetItem(f"${goal['target_amount']:,.2f}"))
            self.goals_table.setItem(i, 2, QTableWidgetItem(f"${goal['current_amount']:,.2f}"))
            self.goals_table.setItem(i, 3, QTableWidgetItem(goal['target_date']))
            self.goals_table.setItem(i, 4, QTableWidgetItem(f"{progress:.1f}%"))
            self.goals_table.setItem(i, 5, QTableWidgetItem(str(goal['priority'])))