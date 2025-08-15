"""
Database models and operations
"""

from datetime import datetime, date

class IncomeModel:
    """Model for income operations"""
    
    @staticmethod
    def add(db, date_str, person, amount, source, notes):
        """Add income entry"""
        db.execute('''
            INSERT INTO income (date, person, amount, source, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (date_str, person, amount, source, notes))
        db.commit()
        
    @staticmethod
    def get_all(db, limit=50):
        """Get all income entries"""
        return db.execute('''
            SELECT * FROM income
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
    @staticmethod
    def get_by_month(db, month_start, month_end):
        """Get income for a specific month"""
        return db.execute('''
            SELECT * FROM income
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (month_start, month_end)).fetchall()
        
    @staticmethod
    def get_total_by_month(db, month_start, month_end):
        """Get total income for a month"""
        result = db.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM income
            WHERE date >= ? AND date <= ?
        ''', (month_start, month_end)).fetchone()
        return result['total'] if result else 0
        
    @staticmethod
    def delete(db, income_id):
        """Delete income entry"""
        db.execute('DELETE FROM income WHERE id = ?', (income_id,))
        db.commit()

class ExpenseModel:
    """Model for expense operations"""
    
    @staticmethod
    def add(db, date_str, person, amount, category, subcategory, description, payment_method):
        """Add expense entry"""
        db.execute('''
            INSERT INTO expenses (date, person, amount, category, subcategory, description, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_str, person, amount, category, subcategory, description, payment_method))
        db.commit()
        
    @staticmethod
    def get_all(db, limit=50):
        """Get all expense entries"""
        return db.execute('''
            SELECT * FROM expenses
            ORDER BY date DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
    @staticmethod
    def get_by_month(db, month_start, month_end):
        """Get expenses for a specific month"""
        return db.execute('''
            SELECT * FROM expenses
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (month_start, month_end)).fetchall()
        
    @staticmethod
    def get_total_by_month(db, month_start, month_end):
        """Get total expenses for a month"""
        result = db.execute('''
            SELECT COALESCE(SUM(amount), 0) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
        ''', (month_start, month_end)).fetchone()
        return result['total'] if result else 0
        
    @staticmethod
    def get_by_category(db, month_start, month_end):
        """Get expenses grouped by category"""
        return db.execute('''
            SELECT category, subcategory, SUM(amount) as total
            FROM expenses
            WHERE date >= ? AND date <= ?
            GROUP BY category, subcategory
            ORDER BY category, subcategory
        ''', (month_start, month_end)).fetchall()
        
    @staticmethod
    def delete(db, expense_id):
        """Delete expense entry"""
        db.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        db.commit()

class NetWorthModel:
    """Model for net worth operations"""
    
    @staticmethod
    def add_or_update(db, asset_type, asset_name, value, person):
        """Add or update asset"""
        # Check if asset exists
        existing = db.execute('''
            SELECT id FROM net_worth
            WHERE asset_name = ? AND date = date('now')
        ''', (asset_name,)).fetchone()
        
        if existing:
            db.execute('''
                UPDATE net_worth
                SET value = ?, asset_type = ?, person = ?
                WHERE id = ?
            ''', (value, asset_type, person, existing['id']))
        else:
            db.execute('''
                INSERT INTO net_worth (date, asset_type, asset_name, value, person)
                VALUES (date('now'), ?, ?, ?, ?)
            ''', (asset_type, asset_name, value, person))
        db.commit()
        
    @staticmethod
    def get_current(db):
        """Get current assets"""
        return db.execute('''
            SELECT * FROM net_worth
            WHERE date = (SELECT MAX(date) FROM net_worth)
            ORDER BY value DESC
        ''').fetchall()
        
    @staticmethod
    def get_total(db):
        """Get total net worth"""
        result = db.execute('''
            SELECT COALESCE(SUM(value), 0) as total
            FROM net_worth
            WHERE date = (SELECT MAX(date) FROM net_worth)
        ''').fetchone()
        return result['total'] if result else 0
        
    @staticmethod
    def delete(db, asset_name):
        """Delete asset"""
        db.execute('DELETE FROM net_worth WHERE asset_name = ?', (asset_name,))
        db.commit()

class SavingsGoalModel:
    """Model for savings goal operations"""
    
    @staticmethod
    def add(db, goal_name, target_amount, target_date, priority):
        """Add savings goal"""
        db.execute('''
            INSERT INTO savings_goals (goal_name, target_amount, target_date, priority)
            VALUES (?, ?, ?, ?)
        ''', (goal_name, target_amount, target_date, priority))
        db.commit()
        
    @staticmethod
    def get_all(db):
        """Get all savings goals"""
        return db.execute('''
            SELECT * FROM savings_goals
            ORDER BY priority
        ''').fetchall()
        
    @staticmethod
    def update_amount(db, goal_id, amount):
        """Update goal current amount"""
        db.execute('''
            UPDATE savings_goals
            SET current_amount = current_amount + ?
            WHERE id = ?
        ''', (amount, goal_id))
        db.commit()
        
    @staticmethod
    def delete(db, goal_id):
        """Delete savings goal"""
        db.execute('DELETE FROM savings_goals WHERE id = ?', (goal_id,))
        db.commit()