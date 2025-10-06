"""
Cortellis Patent & Drug Data Analysis System
"""
import pandas as pd
import json
import os
import sys
from datetime import datetime

# Set UTF-8 encoding for console output
sys.stdout.reconfigure(encoding='utf-8')

def analyze_cortellis_data():
    """Analyze and understand Cortellis data structure"""

    # Load patent data
    patents_file = 'cortellis_patents.xlsx'
    drugs_file = 'cortellis_drugs.xlsx'

    print("=" * 80)
    print("CORTELLIS DATA ANALYSIS")
    print("=" * 80)

    # Analyze Patents
    if os.path.exists(patents_file):
        print("\nPATENT DATA ANALYSIS:")
        print("-" * 40)

        # Read all sheets
        xl_file = pd.ExcelFile(patents_file)
        print(f"Total sheets: {len(xl_file.sheet_names)}")
        print(f"Sheet names: {xl_file.sheet_names}")

        for sheet in xl_file.sheet_names:
            df = pd.read_excel(patents_file, sheet_name=sheet)
            print(f"\nSheet: {sheet}")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)[:10]}")  # First 10 columns

            # Show sample data
            if not df.empty:
                print(f"\n  Sample data (first row):")
                for col in df.columns[:5]:  # First 5 columns
                    print(f"    {col}: {df.iloc[0][col] if pd.notna(df.iloc[0][col]) else 'N/A'}")

    # Analyze Drugs
    if os.path.exists(drugs_file):
        print("\nDRUG DATA ANALYSIS:")
        print("-" * 40)

        # Read all sheets
        xl_file = pd.ExcelFile(drugs_file)
        print(f"Total sheets: {len(xl_file.sheet_names)}")
        print(f"Sheet names: {xl_file.sheet_names}")

        for sheet in xl_file.sheet_names:
            df = pd.read_excel(drugs_file, sheet_name=sheet)
            print(f"\nSheet: {sheet}")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print(f"  Column names: {list(df.columns)[:10]}")  # First 10 columns

            # Show sample data
            if not df.empty:
                print(f"\n  Sample data (first row):")
                for col in df.columns[:5]:  # First 5 columns
                    print(f"    {col}: {df.iloc[0][col] if pd.notna(df.iloc[0][col]) else 'N/A'}")

if __name__ == "__main__":
    analyze_cortellis_data()