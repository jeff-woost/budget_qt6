"""
Category Manager for Budget Tracker
Handles loading, managing, and updating categories and subcategories
"""

import csv
import os
import sqlite3
from typing import Dict, List, Optional, Set
from database.db_manager import DatabaseManager

class CategoryManager:
    """Centralized manager for categories and subcategories"""

    def __init__(self):
        self._categories_data = {}
        self._load_categories()
        self._ensure_categories_table()
        self._sync_with_database()

    def _load_categories(self) -> None:
        """Load categories from the categories.csv file with proper encoding handling"""
        # Try to find categories.csv in the current directory first
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'categories.csv'),
            'categories.csv',
            '/Users/jeffreywooster/Documents/Development/6_Budget_Master/categories.csv',
            os.path.join(os.path.dirname(__file__), '..', '..', 'categories.csv')
        ]

        categories_file = None
        for path in possible_paths:
            if os.path.exists(path):
                categories_file = path
                break

        if categories_file:
            try:
                # Try different encodings to handle potential encoding issues
                encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']

                for encoding in encodings:
                    try:
                        with open(categories_file, 'r', encoding=encoding) as file:
                            reader = csv.DictReader(file)

                            # Clear existing data
                            self._categories_data = {}

                            for row in reader:
                                category = row.get('Category', '').strip()
                                subcategory = row.get('Sub Category', '').strip()

                                if category and subcategory:
                                    if category not in self._categories_data:
                                        self._categories_data[category] = []
                                    if subcategory not in self._categories_data[category]:
                                        self._categories_data[category].append(subcategory)

                        print(f"Loaded {len(self._categories_data)} categories from {categories_file} using {encoding} encoding")
                        return  # Success, exit the function

                    except UnicodeDecodeError:
                        continue  # Try next encoding

                # If we get here, all encodings failed
                raise Exception("Could not decode file with any supported encoding")

            except Exception as e:
                print(f"Error loading categories from CSV: {e}")
                self._load_default_categories()
        else:
            print("Categories.csv not found, using default categories")
            self._load_default_categories()

    def _load_default_categories(self) -> None:
        """Load default categories as fallback"""
        self._categories_data = {
            'Housing': ['Mortgage', 'HOA', 'Property Taxes', 'Reserves'],
            'Utilities': ['Electric', 'Gas', 'Internet', 'Phone', 'Insurance'],
            'Food': ['Food (Groceries)', 'Food (Take Out)', 'Food (Dining Out)'],
            'Healthcare': ['Prescriptions', 'Doctor Visits', 'Co-Pay'],
            'Vehicles': ['Gas', 'Insurance', 'Repairs', 'Parking'],
            'Other': ['Entertainment', 'Clothes', 'Other'],
            'Income': ["Jeff's Income", "Vanessa's Income", "Bonus", "Other Income"]
        }

    def _ensure_categories_table(self) -> None:
        """Ensure the categories table exists in the database"""
        try:
            with DatabaseManager() as db:
                db.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        subcategory TEXT NOT NULL,
                        created_date DATE DEFAULT CURRENT_DATE,
                        UNIQUE(category, subcategory)
                    )
                ''')
        except Exception as e:
            print(f"Error creating categories table: {e}")

    def _sync_with_database(self) -> None:
        """Sync categories with database and load any custom categories"""
        try:
            with DatabaseManager() as db:
                # First, insert all CSV categories into database if they don't exist
                for category, subcategories in self._categories_data.items():
                    for subcategory in subcategories:
                        try:
                            db.execute('''
                                INSERT OR IGNORE INTO categories (category, subcategory)
                                VALUES (?, ?)
                            ''', (category, subcategory))
                        except Exception as e:
                            print(f"Error inserting category {category}/{subcategory}: {e}")

                # Then load any additional categories from database
                db_categories = db.execute('''
                    SELECT category, subcategory FROM categories
                    ORDER BY category, subcategory
                ''').fetchall()

                for row in db_categories:
                    category = row['category']
                    subcategory = row['subcategory']

                    if category not in self._categories_data:
                        self._categories_data[category] = []
                    if subcategory not in self._categories_data[category]:
                        self._categories_data[category].append(subcategory)

        except Exception as e:
            print(f"Error syncing with database: {e}")

    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories and subcategories"""
        return self._categories_data.copy()

    def get_category_names(self) -> List[str]:
        """Get list of all category names"""
        return sorted(self._categories_data.keys())

    def get_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a specific category"""
        return self._categories_data.get(category, []).copy()

    def add_category(self, category: str) -> bool:
        """Add a new category"""
        if not category or category in self._categories_data:
            return False

        try:
            with DatabaseManager() as db:
                # Add category with a default subcategory
                default_subcategory = f"{category} (General)"
                db.execute('''
                    INSERT INTO categories (category, subcategory)
                    VALUES (?, ?)
                ''', (category, default_subcategory))

                self._categories_data[category] = [default_subcategory]
                return True

        except Exception as e:
            print(f"Error adding category {category}: {e}")
            return False

    def add_subcategory(self, category: str, subcategory: str) -> bool:
        """Add a new subcategory to an existing category"""
        if not category or not subcategory:
            return False

        # Create category if it doesn't exist
        if category not in self._categories_data:
            self._categories_data[category] = []

        # Check if subcategory already exists
        if subcategory in self._categories_data[category]:
            return False

        try:
            with DatabaseManager() as db:
                db.execute('''
                    INSERT INTO categories (category, subcategory)
                    VALUES (?, ?)
                ''', (category, subcategory))

                self._categories_data[category].append(subcategory)
                return True

        except Exception as e:
            print(f"Error adding subcategory {category}/{subcategory}: {e}")
            return False

    def remove_subcategory(self, category: str, subcategory: str) -> bool:
        """Remove a subcategory (only if not used in expenses)"""
        if category not in self._categories_data or subcategory not in self._categories_data[category]:
            return False

        try:
            with DatabaseManager() as db:
                # Check if subcategory is used in expenses
                usage_count = db.execute('''
                    SELECT COUNT(*) as count FROM expenses
                    WHERE category = ? AND subcategory = ?
                ''', (category, subcategory)).fetchone()

                if usage_count and usage_count['count'] > 0:
                    print(f"Cannot remove subcategory {category}/{subcategory}: still in use")
                    return False

                # Remove from database
                db.execute('''
                    DELETE FROM categories 
                    WHERE category = ? AND subcategory = ?
                ''', (category, subcategory))

                # Remove from local data
                self._categories_data[category].remove(subcategory)

                # Remove category if it has no subcategories
                if not self._categories_data[category]:
                    del self._categories_data[category]

                return True

        except Exception as e:
            print(f"Error removing subcategory {category}/{subcategory}: {e}")
            return False

    def refresh_from_database(self) -> None:
        """Refresh categories from database"""
        self._categories_data = {}
        self._sync_with_database()

    def refresh(self) -> None:
        """Refresh categories from database (alias for refresh_from_database)"""
        self.refresh_from_database()

    def is_valid_category(self, category: str, subcategory: str) -> bool:
        """Check if a category/subcategory combination is valid"""
        return (category in self._categories_data and
                subcategory in self._categories_data[category])

    def category_exists(self, category: str) -> bool:
        """Check if a category exists"""
        return category in self._categories_data

    def subcategory_exists(self, category: str, subcategory: str) -> bool:
        """Check if a subcategory exists within a category"""
        return (category in self._categories_data and
                subcategory in self._categories_data[category])

# Global instance
_category_manager = CategoryManager()

def get_category_manager() -> CategoryManager:
    """Get the global category manager instance"""
    return _category_manager
