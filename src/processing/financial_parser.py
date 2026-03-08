"""
Parse financial data from extracted tables
"""
import pandas as pd
from typing import Dict, List, Optional
import re

class FinancialParser:
    def __init__(self):
        # Key line items to extract from balance sheet
        self.balance_sheet_items = [
            'total assets',
            'total liabilities',
            'loss adjustment expenses',
            'unearned premiums',
            'total equity'
        ]
        
        # Key metrics to extract from income statement
        self.income_items = [
            'net premiums earned',
            'losses and loss adjustment expenses',
            'underwriting income',
            'net income'
        ]
    
    def parse_balance_sheet(self, table_data: List[Dict]) -> Dict:
        """
        Parse balance sheet table into structured metrics
        
        Args:
            table_data: Table data from TableExtractor
        
        Returns:
            Dict of financial metrics
        """
        df = pd.DataFrame(table_data)
        
        if df.empty:
            return {}
        
        # Assume first column is line item names
        line_item_col = df.columns[0]
        
        metrics = {}
        
        for item in self.balance_sheet_items:
            # Find row matching this item
            matching_rows = df[
                df[line_item_col].str.lower().str.contains(item, na=False)
            ]
            
            if not matching_rows.empty:
                row = matching_rows.iloc[0]
                # Get value from most recent period (usually second column)
                if len(row) > 1:
                    value = self._parse_financial_value(row[df.columns[1]])
                    metrics[item.replace(' ', '_')] = value
        
        return metrics
    
    def parse_reserves(self, table_data: List[Dict], text: str) -> Dict:
        """
        Parse reserve-related information
        
        Args:
            table_data: Table with reserve amounts
            text: Surrounding narrative text
        
        Returns:
            Dict with reserve metrics
        """
        reserves = {
            'total_reserves': None,
            'prior_year_development': None,
            'by_line_of_business': []
        }
        
        # Extract total reserves from table
        df = pd.DataFrame(table_data)
        if not df.empty:
            # Look for total reserves row
            total_row = df[
                df[df.columns[0]].str.lower().str.contains('unpaid loss', na=False)
            ]
            if not total_row.empty:
                reserves['total_reserves'] = self._parse_financial_value(
                    total_row.iloc[0][df.columns[1]]
                )
        
        # Extract development from text
        dev_pattern = r'(?i)(favorable|adverse).*development.*\$?([\d,]+)\s*million'
        match = re.search(dev_pattern, text)
        if match:
            direction = match.group(1).lower()
            amount = float(match.group(2).replace(',', ''))
            reserves['prior_year_development'] = {
                'direction': direction,
                'amount': amount
            }
        
        return reserves
    
    def _parse_financial_value(self, value: str) -> Optional[float]:
        """
        Parse financial value from string
        
        Examples:
            '$123,456' -> 123456.0
            '(1,234)' -> -1234.0 (parentheses indicate negative)
        """
        if pd.isna(value) or value == '':
            return None
        
        # Convert to string
        value = str(value).strip()
        
        # Check for negative (parentheses)
        is_negative = value.startswith('(') and value.endswith(')')
        
        # Remove all non-numeric except decimal point
        numeric_str = re.sub(r'[^\d.]', '', value)
        
        if not numeric_str:
            return None
        
        try:
            result = float(numeric_str)
            return -result if is_negative else result
        except ValueError:
            return None