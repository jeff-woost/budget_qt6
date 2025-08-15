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
        # Default category mappings for common merchants/descriptions
        self.category_mappings = {
            'WALGREENS': ('Health & Wellness', 'Prescriptions'),
            'CVS': ('Health & Wellness', 'Prescriptions'),
            'APPLE.COM': ('Other', 'Entertainment'),
            'AMAZON': ('Other', 'Other'),
            'EBAY': ('Other', 'Other'),
            'WHOLEFDS': ('Food', 'Food (Groceries)'),
            'WHOLE FOODS': ('Food', 'Food (Groceries)'),
            'ACME': ('Food', 'Food (Groceries)'),
            'ALDI': ('Food', 'Food (Groceries)'),
            'TRADER JOE': ('Food', 'Food (Groceries)'),
            'TARGET': ('Other', 'Other'),
            'MCDONALDS': ('Food', 'Food (Take Out)'),
            'UBER': ('Utilities', 'Taxi / Transit'),
            'LYFT': ('Utilities', 'Taxi / Transit'),
            '7-ELEVEN': ('Vehicles', 'Gas'),
            'GOOGLE': ('Other', 'Entertainment'),
            'NETFLIX': ('Other', 'Entertainment'),
            'HULU': ('Other', 'Entertainment'),
            'HBO': ('Other', 'Entertainment'),
            'PRIME VIDEO': ('Other', 'Entertainment'),
            'GITHUB': ('Other', 'Other'),
        }

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
                        date_obj = datetime.strptime(transaction_date, '%m/%d/%Y')
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

        # Check our mapping dictionary
        for key, (category, subcategory) in self.category_mappings.items():
            if key in description_upper:
                return category, subcategory

        # Fallback mappings based on keywords
        if any(keyword in description_upper for keyword in ['GROCERY', 'SUPERMARKET', 'MARKET']):
            return 'Food', 'Food (Groceries)'
        elif any(keyword in description_upper for keyword in ['RESTAURANT', 'CAFE', 'PIZZA', 'DELI']):
            return 'Food', 'Food (Dining Out)'
        elif any(keyword in description_upper for keyword in ['GAS', 'FUEL', 'EXXON', 'SHELL', 'BP']):
            return 'Vehicles', 'Gas'
        elif any(keyword in description_upper for keyword in ['PHARMACY', 'DRUG', 'MEDICAL', 'DOCTOR']):
            return 'Healthcare', 'Other Doctor Visits'
        elif any(keyword in description_upper for keyword in ['PARKING', 'TOLL']):
            return 'Vehicles', 'Parking'

        # Use original category if available and mappable
        if original_category:
            category_mapping = {
                'Shopping': ('Other', 'Other'),
                'Health & Wellness': ('Healthcare', 'Other Doctor Visits'),
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
                return category_mapping[original_category]

        # Default fallback
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
