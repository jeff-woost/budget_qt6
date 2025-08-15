"""
Expense Loader Utility for Budget Tracker
Handles CSV files from credit card statements and TXT files with manual entries
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import re

class ExpenseLoader:
    """Utility class for loading expenses from various file formats"""

    def __init__(self):
        # Load categories from CSV file
        self.categories_data = self._load_categories_from_csv()

        # Updated category mappings using correct categories from CSV
        self.category_mappings = {
            'WALGREENS': ('Healthcare', 'Prescriptions'),
            'CVS': ('Healthcare', 'Prescriptions'),
            'RITE AID': ('Healthcare', 'Prescriptions'),
            'PHARMACY': ('Healthcare', 'Prescriptions'),
            'APPLE.COM': ('Other', 'Entertainment'),
            'AMAZON': ('Other', 'Other'),
            'EBAY': ('Other', 'Other'),
            'WHOLEFDS': ('Food', 'Food (Groceries)'),
            'WHOLE FOODS': ('Food', 'Food (Groceries)'),
            'ACME': ('Food', 'Food (Groceries)'),
            'ALDI': ('Food', 'Food (Groceries)'),
            'TRADER JOE': ('Food', 'Food (Groceries)'),
            'SHOPRITE': ('Food', 'Food (Groceries)'),
            'STOP & SHOP': ('Food', 'Food (Groceries)'),
            'TARGET': ('Other', 'Other'),
            'WALMART': ('Other', 'Other'),
            'COSTCO': ('Food', 'Food (Groceries)'),
            'MCDONALDS': ('Food', 'Food (Take Out)'),
            'BURGER KING': ('Food', 'Food (Take Out)'),
            'SUBWAY': ('Food', 'Food (Take Out)'),
            'STARBUCKS': ('Food', 'Food (Take Out)'),
            'DUNKIN': ('Food', 'Food (Take Out)'),
            'UBER': ('Utilities', 'Taxi / Transit'),
            'LYFT': ('Utilities', 'Taxi / Transit'),
            'UBER EATS': ('Food', 'Food (Take Out)'),
            'DOORDASH': ('Food', 'Food (Take Out)'),
            'GRUBHUB': ('Food', 'Food (Take Out)'),
            '7-ELEVEN': ('Vehicles', 'Gas'),
            'SHELL': ('Vehicles', 'Gas'),
            'EXXON': ('Vehicles', 'Gas'),
            'BP': ('Vehicles', 'Gas'),
            'MOBIL': ('Vehicles', 'Gas'),
            'GOOGLE': ('Home', 'Subscriptions'),
            'NETFLIX': ('Home', 'Subscriptions'),
            'HULU': ('Home', 'Subscriptions'),
            'HBO': ('Home', 'Subscriptions'),
            'PRIME VIDEO': ('Home', 'Subscriptions'),
            'SPOTIFY': ('Home', 'Subscriptions'),
            'GITHUB': ('Other', 'Other'),
            'HOME DEPOT': ('Home', 'Tools / Hardware'),
            'LOWES': ('Home', 'Tools / Hardware'),
            'BED BATH': ('Home', 'Homeware'),
            'IKEA': ('Home', 'Home D�cor'),
            'MARSHALLS': ('Other', 'Clothes'),
            'TJ MAXX': ('Other', 'Clothes'),
            'KOHLS': ('Other', 'Clothes'),
            'MACYS': ('Other', 'Clothes'),
        }

    def _load_categories_from_csv(self) -> Dict[str, List[str]]:
        """Load categories from the categories.csv file"""
        categories_data = {}

        # Try to find categories.csv in common locations
        possible_paths = [
            '/Users/jeffreywooster/Documents/Development/6_Budget_Master/categories.csv',
            os.path.join(os.path.dirname(__file__), '..', '..', 'categories.csv'),
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'categories.csv'),
            'categories.csv'
        ]

        categories_file = None
        for path in possible_paths:
            if os.path.exists(path):
                categories_file = path
                break

        if categories_file:
            try:
                with open(categories_file, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        category = row.get('Category', '').strip()
                        subcategory = row.get('Sub Category', '').strip()

                        if category and subcategory:
                            if category not in categories_data:
                                categories_data[category] = []
                            if subcategory not in categories_data[category]:
                                categories_data[category].append(subcategory)
            except Exception as e:
                print(f"Error loading categories from CSV: {e}")

        # If no categories loaded, use default fallback
        if not categories_data:
            categories_data = {
                'Housing': ['Mortgage', 'HOA', 'Property Taxes', 'Reserves'],
                'Utilities': ['Electric', 'Gas', 'Internet', 'Phone', 'Insurance'],
                'Food': ['Food (Groceries)', 'Food (Take Out)', 'Food (Dining Out)'],
                'Healthcare': ['Prescriptions', 'Doctor Visits', 'Co-Pay'],
                'Vehicles': ['Gas', 'Insurance', 'Repairs', 'Parking'],
                'Other': ['Entertainment', 'Clothes', 'Other']
            }

        return categories_data

    def load_csv_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Load expenses from a CSV file (credit card format)
        Returns: (expenses_list, errors_list)
        """
        expenses = []
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect the CSV format
                sample = file.read(1024)
                file.seek(0)

                # Check if this looks like a Chase credit card statement
                if 'Transaction Date' in sample and 'Post Date' in sample:
                    return self._load_chase_csv(file, errors)
                else:
                    # Generic CSV format
                    return self._load_generic_csv(file, errors)

        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")
            return [], errors

    def _load_chase_csv(self, file, errors: List[str]) -> Tuple[List[Dict], List[str]]:
        """Load Chase credit card CSV format"""
        expenses = []

        try:
            reader = csv.DictReader(file)

            for row_num, row in enumerate(reader, start=2):
                try:
                    # Only process "Sale" transactions (skip returns/payments)
                    if row.get('Type', '').strip().lower() != 'sale':
                        continue

                    # Parse the data
                    transaction_date = row.get('Transaction Date', '').strip()
                    description = row.get('Description', '').strip()
                    category = row.get('Category', '').strip()
                    amount_str = row.get('Amount', '').strip()

                    if not all([transaction_date, description, amount_str]):
                        errors.append(f"Row {row_num}: Missing required fields")
                        continue

                    # Parse amount (should be negative for expenses, make positive)
                    try:
                        amount = float(amount_str.replace(',', ''))
                        if amount < 0:
                            amount = abs(amount)  # Make positive for expense
                        else:
                            # Skip if amount is positive (likely a return/credit)
                            continue
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")
                        continue

                    # Parse date
                    try:
                        # Try different date formats
                        date_obj = self._parse_date(transaction_date)
                        date_str = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date format '{transaction_date}'")
                        continue

                    # Map to categories
                    budget_category, subcategory = self._map_category(description, category)

                    expense = {
                        'date': date_str,
                        'person': 'Jeff',  # Default person, can be changed in UI
                        'amount': amount,
                        'category': budget_category,
                        'subcategory': subcategory,
                        'description': description,
                        'payment_method': 'Credit Card'
                    }

                    expenses.append(expense)

                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    continue

        except Exception as e:
            errors.append(f"Error processing CSV: {str(e)}")

        return expenses, errors

    def _load_generic_csv(self, file, errors: List[str]) -> Tuple[List[Dict], List[str]]:
        """Load generic CSV format"""
        expenses = []
        # This can be extended for other CSV formats
        errors.append("Generic CSV format not yet implemented")
        return expenses, errors

    def load_txt_file(self, file_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Load expenses from a TXT file (manual format)
        Expected format: MM/DD description amount
        Returns: (expenses_list, errors_list)
        """
        expenses = []
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # Parse line format: MM/DD description amount
                        # Example: "06/23 uber 32.91"
                        parts = line.split()
                        if len(parts) < 3:
                            errors.append(f"Line {line_num}: Invalid format - expected 'MM/DD description amount'")
                            continue

                        date_part = parts[0]
                        amount_part = parts[-1]
                        description_parts = parts[1:-1]
                        description = ' '.join(description_parts)

                        # Parse date (assume current year)
                        try:
                            current_year = datetime.now().year
                            date_obj = datetime.strptime(f"{current_year}/{date_part}", '%Y/%m/%d')
                            date_str = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            errors.append(f"Line {line_num}: Invalid date format '{date_part}'")
                            continue

                        # Parse amount
                        try:
                            amount = float(amount_part.replace(',', ''))
                        except ValueError:
                            errors.append(f"Line {line_num}: Invalid amount '{amount_part}'")
                            continue

                        # Map to categories
                        budget_category, subcategory = self._map_category(description)

                        expense = {
                            'date': date_str,
                            'person': 'Vanessa',  # Default for TXT files, can be changed
                            'amount': amount,
                            'category': budget_category,
                            'subcategory': subcategory,
                            'description': description,
                            'payment_method': 'Cash/Debit'
                        }

                        expenses.append(expense)

                    except Exception as e:
                        errors.append(f"Line {line_num}: {str(e)}")
                        continue

        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")

        return expenses, errors

    def _map_category(self, description: str, original_category: str = '') -> Tuple[str, str]:
        """
        Map merchant/description to budget categories
        Returns: (category, subcategory)
        """
        description_upper = description.upper()

        # Check our mapping dictionary first
        for key, (category, subcategory) in self.category_mappings.items():
            if key in description_upper:
                # Validate that the category exists in our loaded categories
                if category in self.categories_data and subcategory in self.categories_data[category]:
                    return category, subcategory

        # Enhanced fallback mappings based on keywords using actual categories from CSV
        if any(keyword in description_upper for keyword in ['GROCERY', 'SUPERMARKET', 'MARKET', 'FOODS']):
            if 'Food' in self.categories_data and 'Food (Groceries)' in self.categories_data['Food']:
                return 'Food', 'Food (Groceries)'

        elif any(keyword in description_upper for keyword in ['RESTAURANT', 'CAFE', 'PIZZA', 'DELI', 'DINING']):
            if 'Food' in self.categories_data and 'Food (Dining Out)' in self.categories_data['Food']:
                return 'Food', 'Food (Dining Out)'

        elif any(keyword in description_upper for keyword in ['TAKEOUT', 'TAKE OUT', 'DELIVERY', 'UBER EATS', 'DOORDASH']):
            if 'Food' in self.categories_data and 'Food (Take Out)' in self.categories_data['Food']:
                return 'Food', 'Food (Take Out)'

        elif any(keyword in description_upper for keyword in ['GAS', 'FUEL', 'EXXON', 'SHELL', 'BP', 'MOBIL', 'CHEVRON']):
            if 'Vehicles' in self.categories_data and 'Gas' in self.categories_data['Vehicles']:
                return 'Vehicles', 'Gas'

        elif any(keyword in description_upper for keyword in ['PHARMACY', 'DRUG', 'WALGREENS', 'CVS', 'RITE AID']):
            if 'Healthcare' in self.categories_data and 'Prescriptions' in self.categories_data['Healthcare']:
                return 'Healthcare', 'Prescriptions'

        elif any(keyword in description_upper for keyword in ['MEDICAL', 'DOCTOR', 'HOSPITAL', 'CLINIC']):
            if 'Healthcare' in self.categories_data and 'Other Doctor Visits' in self.categories_data['Healthcare']:
                return 'Healthcare', 'Other Doctor Visits'

        elif any(keyword in description_upper for keyword in ['PARKING', 'TOLL']):
            if 'Vehicles' in self.categories_data and 'Parking' in self.categories_data['Vehicles']:
                return 'Vehicles', 'Parking'

        elif any(keyword in description_upper for keyword in ['INSURANCE']):
            if 'Utilities' in self.categories_data and 'Insurance' in self.categories_data['Utilities']:
                return 'Utilities', 'Insurance'

        elif any(keyword in description_upper for keyword in ['UBER', 'LYFT', 'TAXI', 'TRANSIT']):
            if 'Utilities' in self.categories_data and 'Taxi / Transit' in self.categories_data['Utilities']:
                return 'Utilities', 'Taxi / Transit'

        # Use original category if available and mappable to our categories
        if original_category:
            category_mapping = {
                'Shopping': ('Other', 'Other'),
                'Health & Wellness': ('Healthcare', 'Prescriptions'),
                'Groceries': ('Food', 'Food (Groceries)'),
                'Food & Drink': ('Food', 'Food (Dining Out)'),
                'Gas': ('Vehicles', 'Gas'),
                'Entertainment': ('Other', 'Entertainment'),
                'Professional Services': ('Other', 'Other'),
                'Personal': ('Other', 'Other'),
                'Automotive': ('Vehicles', 'Vehicle Other'),
                'Bills & Utilities': ('Utilities', 'Misc Utility')
            }

            if original_category in category_mapping:
                category, subcategory = category_mapping[original_category]
                # Validate that the mapped category exists in our loaded categories
                if category in self.categories_data and subcategory in self.categories_data[category]:
                    return category, subcategory

        # Default fallback - ensure 'Other' category exists
        if 'Other' in self.categories_data:
            if 'Other' in self.categories_data['Other']:
                return 'Other', 'Other'
            elif self.categories_data['Other']:  # If Other category exists but not 'Other' subcategory
                return 'Other', self.categories_data['Other'][0]

        # Ultimate fallback - use first available category and subcategory
        if self.categories_data:
            first_category = list(self.categories_data.keys())[0]
            first_subcategory = self.categories_data[first_category][0] if self.categories_data[first_category] else 'Other'
            return first_category, first_subcategory

        # If no categories loaded at all, return basic fallback
        return 'Other', 'Other'

    def validate_expenses(self, expenses: List[Dict]) -> Tuple[List[Dict], List[str]]:
        """
        Validate expense data before import
        Returns: (valid_expenses, validation_errors)
        """
        valid_expenses = []
        errors = []

        for i, expense in enumerate(expenses):
            try:
                # Check required fields
                required_fields = ['date', 'person', 'amount', 'category', 'subcategory', 'description']
                missing_fields = [field for field in required_fields if not expense.get(field)]

                if missing_fields:
                    errors.append(f"Expense {i+1}: Missing fields: {', '.join(missing_fields)}")
                    continue

                # Validate amount
                if not isinstance(expense['amount'], (int, float)) or expense['amount'] <= 0:
                    errors.append(f"Expense {i+1}: Invalid amount")
                    continue

                # Validate date format
                try:
                    datetime.strptime(expense['date'], '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Expense {i+1}: Invalid date format")
                    continue

                valid_expenses.append(expense)

            except Exception as e:
                errors.append(f"Expense {i+1}: Validation error - {str(e)}")

        return valid_expenses, errors

    def get_available_categories(self) -> Dict[str, List[str]]:
        """Get the loaded categories data for use by other components"""
        return self.categories_data.copy()

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse a date string into a datetime object
        Tries multiple formats including 2-digit and 4-digit years
        """
        # List of date formats to try
        date_formats = [
            '%m/%d/%Y',    # MM/DD/YYYY
            '%m/%d/%y',    # MM/DD/YY (2-digit year)
            '%m-%d-%Y',    # MM-DD-YYYY
            '%m-%d-%y',    # MM-DD-YY
            '%Y/%m/%d',    # YYYY/MM/DD
            '%Y-%m-%d',    # YYYY-MM-DD
            '%d/%m/%Y',    # DD/MM/YYYY
            '%d/%m/%y',    # DD/MM/YY
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)

                # Handle 2-digit years - if year is less than 50, assume 20xx, otherwise 19xx
                if parsed_date.year < 100:
                    if parsed_date.year < 50:
                        parsed_date = parsed_date.replace(year=parsed_date.year + 2000)
                    else:
                        parsed_date = parsed_date.replace(year=parsed_date.year + 1900)

                return parsed_date
            except ValueError:
                continue

        raise ValueError(f"Date '{date_str}' does not match any known format")
