"""
Database management module for the budget application
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import json

class DatabaseManager:
    def __init__(self, db_path: str = "budget_tracker.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def initialize_database(self):
        """Create all necessary tables"""
        self.connect()
        
        # Categories table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                UNIQUE(category, subcategory)
            )
        ''')
        
        # Income table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Expenses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                description TEXT,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Net worth assets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS net_worth_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                asset_name TEXT NOT NULL,
                value REAL NOT NULL,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Savings goals table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL UNIQUE,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                target_date DATE,
                priority INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Savings allocations table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (goal_id) REFERENCES savings_goals (id)
            )
        ''')
        
        # Budget targets table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT,
                monthly_target REAL NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                UNIQUE(category, subcategory, year, month)
            )
        ''')
        
        self.conn.commit()
        self.load_default_categories()
        self.disconnect()
        
    def load_default_categories(self):
        """Load categories from CSV file"""
        categories = [
            ("Housing", "Mortgage"),
            ("Housing", "Special Assessment"),
            ("Housing", "Additional Principal"),
            ("Housing", "Lima Apartment Wires"),
            ("Housing", "Lima Apartment Fees"),
            ("Housing", "Escrow"),
            ("Housing", "HOA"),
            ("Housing", "Reserves"),
            ("Housing", "Condo Insurance"),
            ("Housing", "Property Taxes"),
            ("Housing", "Labor"),
            ("Utilities", "Optimum"),
            ("Utilities", "PSEG"),
            ("Utilities", "Cell Phone"),
            ("Utilities", "Car Insurance"),
            ("Utilities", "Gloria"),
            ("Utilities", "Insurance"),
            ("Utilities", "Taxi / Transit"),
            ("Utilities", "Bus Pass"),
            ("Utilities", "Misc Utility"),
            ("Food", "Food (Groceries)"),
            ("Food", "Food (Take Out)"),
            ("Food", "Food (Dining Out)"),
            ("Food", "Food (Other)"),
            ("Food", "Food (Party)"),
            ("Food", "Food (Guests)"),
            ("Food", "Food (Work)"),
            ("Food", "Food (Special Occasion)"),
            ("Healthcare", "Jeff Doctor"),
            ("Healthcare", "Prescriptions"),
            ("Healthcare", "Vitamins"),
            ("Healthcare", "Other Doctor Visits"),
            ("Healthcare", "Haircut"),
            ("Healthcare", "Hygenie"),
            ("Healthcare", "Family"),
            ("Healthcare", "Fertility"),
            ("Healthcare", "Co-Pay"),
            ("Healthcare", "Baker"),
            ("Healthcare", "HC Subscriptions"),
            ("Healthcare", "Joaquin Health Care"),
            ("Healthcare", "Zoe Health Care"),
            ("Healthcare", "Misc Health Care"),
            ("Childcare", "Village Classes"),
            ("Childcare", "Baby Sitting"),
            ("Childcare", "Clothing"),
            ("Childcare", "Diapers"),
            ("Childcare", "Necessities"),
            ("Childcare", "Accessories"),
            ("Childcare", "Toys"),
            ("Childcare", "Food / Snacks"),
            ("Childcare", "Haircut"),
            ("Childcare", "Activities"),
            ("Childcare", "Uber / Lyft"),
            ("Childcare", "Misc."),
            ("Vehicles", "Vehicle Fixes"),
            ("Vehicles", "Vehicle Other"),
            ("Vehicles", "Gas"),
            ("Vehicles", "DMV"),
            ("Vehicles", "Parts"),
            ("Vehicles", "Tires / Wheels"),
            ("Vehicles", "Insurance"),
            ("Vehicles", "Oil Changes"),
            ("Vehicles", "Car Wash"),
            ("Vehicles", "Parking"),
            ("Vehicles", "Tolls"),
            ("Home", "Home Necessities"),
            ("Home", "Home Décor"),
            ("Home", "House Cleaning"),
            ("Home", "Bathroom"),
            ("Home", "Bedrooms"),
            ("Home", "Kitchen"),
            ("Home", "Tools / Hardware"),
            ("Home", "Storage"),
            ("Home", "Homeware"),
            ("Home", "Subscriptions"),
            ("Other", "Gifts"),
            ("Other", "Taxes"),
            ("Other", "Donations"),
            ("Other", "Gatherings"),
            ("Other", "Parties"),
            ("Other", "Clothes"),
            ("Other", "Shoes"),
            ("Other", "Pets"),
            ("Other", "Target AutoPay"),
            ("Other", "Stupid Tax"),
            ("Other", "Amazon Prime"),
            ("Other", "Fees"),
            ("Other", "Reversal"),
            ("Other", "Entertainment"),
            ("Other", "Other"),
            ("Vacation", "Flights/Travel"),
            ("Vacation", "Rental Car"),
            ("Vacation", "Airport"),
            ("Vacation", "Taxi"),
            ("Vacation", "Food"),
            ("Vacation", "Eating Out"),
            ("Vacation", "Gas"),
            ("Vacation", "Activities"),
            ("Vacation", "Bedding"),
            ("Vacation", "Fees"),
            ("Vacation", "Physical Goods"),
            ("Vacation", "Housing"),
            ("Vacation", "Necessities")
        ]
        
        for category, subcategory in categories:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO categories (category, subcategory) VALUES (?, ?)",
                    (category, subcategory)
                )
            except Exception as e:
                print(f"Error inserting category {category}/{subcategory}: {e}")
        
        self.conn.commit()
    
    # Income methods
    def add_income(self, person: str, amount: float, date: str, description: str = None):
        """Add income entry"""
        self.connect()
        self.cursor.execute(
            "INSERT INTO income (person, amount, date, description) VALUES (?, ?, ?, ?)",
            (person, amount, date, description)
        )
        self.conn.commit()
        self.disconnect()
        
    def get_income(self, start_date: str = None, end_date: str = None, person: str = None):
        """Get income entries with optional filters"""
        self.connect()
        query = "SELECT * FROM income WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if person:
            query += " AND person = ?"
            params.append(person)
            
        query += " ORDER BY date DESC"
        
        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    # Expense methods
    def add_expense(self, person: str, amount: float, date: str, category: str, 
                   subcategory: str, description: str = None, payment_method: str = None):
        """Add expense entry"""
        self.connect()
        self.cursor.execute(
            """INSERT INTO expenses (person, amount, date, category, subcategory, 
               description, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (person, amount, date, category, subcategory, description, payment_method)
        )
        self.conn.commit()
        self.disconnect()
        
    def get_expenses(self, start_date: str = None, end_date: str = None, 
                    person: str = None, category: str = None):
        """Get expense entries with optional filters"""
        self.connect()
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if person:
            query += " AND person = ?"
            params.append(person)
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY date DESC"
        
        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    def bulk_add_expenses(self, expenses: List[Dict]):
        """Add multiple expense entries at once"""
        self.connect()
        for expense in expenses:
            self.cursor.execute(
                """INSERT INTO expenses (person, amount, date, category, subcategory, 
                   description, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (expense['person'], expense['amount'], expense['date'], 
                 expense['category'], expense['subcategory'], 
                 expense.get('description'), expense.get('payment_method'))
            )
        self.conn.commit()
        self.disconnect()
    
    # Net worth methods
    def add_asset(self, person: str, asset_type: str, asset_name: str, 
                 value: float, date: str, notes: str = None):
        """Add or update net worth asset"""
        self.connect()
        self.cursor.execute(
            """INSERT INTO net_worth_assets (person, asset_type, asset_name, 
               value, date, notes) VALUES (?, ?, ?, ?, ?, ?)""",
            (person, asset_type, asset_name, value, date, notes)
        )
        self.conn.commit()
        self.disconnect()
        
    def get_assets(self, date: str = None, person: str = None):
        """Get net worth assets"""
        self.connect()
        
        if date:
            # Get most recent values for each asset up to the specified date
            query = """
                SELECT * FROM net_worth_assets 
                WHERE id IN (
                    SELECT MAX(id) FROM net_worth_assets 
                    WHERE date <= ? 
                    GROUP BY person, asset_type, asset_name
                )
            """
            params = [date]
        else:
            # Get most recent values for all assets
            query = """
                SELECT * FROM net_worth_assets 
                WHERE id IN (
                    SELECT MAX(id) FROM net_worth_assets 
                    GROUP BY person, asset_type, asset_name
                )
            """
            params = []
        
        if person:
            query += " AND person = ?"
            params.append(person)
            
        self.cursor.execute(query, params)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    # Savings goals methods
    def add_savings_goal(self, goal_name: str, target_amount: float, 
                        target_date: str = None, priority: int = 1, notes: str = None):
        """Add a new savings goal"""
        self.connect()
        self.cursor.execute(
            """INSERT INTO savings_goals (goal_name, target_amount, target_date, 
               priority, notes) VALUES (?, ?, ?, ?, ?)""",
            (goal_name, target_amount, target_date, priority, notes)
        )
        self.conn.commit()
        self.disconnect()
        
    def get_savings_goals(self):
        """Get all savings goals"""
        self.connect()
        self.cursor.execute(
            "SELECT * FROM savings_goals ORDER BY priority, goal_name"
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    def allocate_to_goal(self, goal_id: int, amount: float, date: str, notes: str = None):
        """Allocate money to a savings goal"""
        self.connect()
        
        # Add allocation record
        self.cursor.execute(
            """INSERT INTO savings_allocations (goal_id, amount, date, notes) 
               VALUES (?, ?, ?, ?)""",
            (goal_id, amount, date, notes)
        )
        
        # Update current amount in goals table
        self.cursor.execute(
            "UPDATE savings_goals SET current_amount = current_amount + ? WHERE id = ?",
            (amount, goal_id)
        )
        
        self.conn.commit()
        self.disconnect()
    
    # Budget targets methods
    def set_budget_target(self, category: str, monthly_target: float, 
                         year: int, month: int, subcategory: str = None):
        """Set or update budget target for a category"""
        self.connect()
        self.cursor.execute(
            """INSERT OR REPLACE INTO budget_targets 
               (category, subcategory, monthly_target, year, month) 
               VALUES (?, ?, ?, ?, ?)""",
            (category, subcategory, monthly_target, year, month)
        )
        self.conn.commit()
        self.disconnect()
        
    def get_budget_targets(self, year: int, month: int):
        """Get budget targets for a specific month"""
        self.connect()
        self.cursor.execute(
            "SELECT * FROM budget_targets WHERE year = ? AND month = ?",
            (year, month)
        )
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    # Analytics methods
    def get_monthly_summary(self, year: int, month: int):
        """Get income and expense summary for a month"""
        self.connect()
        
        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month+1:02d}-01"
        
        # Get total income
        self.cursor.execute(
            """SELECT person, SUM(amount) as total 
               FROM income 
               WHERE date >= ? AND date < ? 
               GROUP BY person""",
            (start_date, end_date)
        )
        income_data = {row['person']: row['total'] for row in self.cursor.fetchall()}
        
        # Get total expenses
        self.cursor.execute(
            """SELECT person, SUM(amount) as total 
               FROM expenses 
               WHERE date >= ? AND date < ? 
               GROUP BY person""",
            (start_date, end_date)
        )
        expense_data = {row['person']: row['total'] for row in self.cursor.fetchall()}
        
        # Get expenses by category
        self.cursor.execute(
            """SELECT category, subcategory, SUM(amount) as total 
               FROM expenses 
               WHERE date >= ? AND date < ? 
               GROUP BY category, subcategory
               ORDER BY category, subcategory""",
            (start_date, end_date)
        )
        category_data = [dict(row) for row in self.cursor.fetchall()]
        
        self.disconnect()
        
        return {
            'income': income_data,
            'expenses': expense_data,
            'by_category': category_data
        }
    
    def get_categories(self):
        """Get all categories and subcategories"""
        self.connect()
        self.cursor.execute("SELECT DISTINCT category, subcategory FROM categories ORDER BY category, subcategory")
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results
    
    def get_trend_data(self, months: int = 12):
        """Get trend data for the last N months"""
        self.connect()
        
        # Get monthly totals for income and expenses
        query = """
            SELECT 
                strftime('%Y-%m', date) as month,
                'income' as type,
                person,
                SUM(amount) as total
            FROM income
            WHERE date >= date('now', '-{} months')
            GROUP BY month, person
            
            UNION ALL
            
            SELECT 
                strftime('%Y-%m', date) as month,
                'expense' as type,
                person,
                SUM(amount) as total
            FROM expenses
            WHERE date >= date('now', '-{} months')
            GROUP BY month, person
            
            ORDER BY month, type, person
        """.format(months)
        
        self.cursor.execute(query)
        results = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return results