# Sample Data Format

This folder contains example sales data files to help you understand the required format.

## File Naming Convention

```
BusinessName_YYYYMMDD.xlsx
```

**Examples:**
- `SalesData_20241215.xlsx`
- `DailySales_20241216.xlsx`
- `Transactions_20241217.xlsx`

## Required Columns

Your Excel files must contain these columns:

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `Date` or `TransactionDate` | Date | ✅ Yes | Date of sale | 2024-12-15 |
| `Description` | Text | ✅ Yes | Product name | House Sourdough Bread |
| `Quantity` | Number | ✅ Yes | Number of units sold | 5 |
| `ExtendedNetAmount` | Number | ✅ Yes | Total revenue for line | 45.50 |
| `SequenceNumber` | Text/Number | ✅ Yes | Unique transaction ID | TXN12345 |
| `Hour_ID` | Number (0-23) | ⚠️ Optional | Hour of day | 14 |
| `CustomerCount` | Number | ⚠️ Optional | Number of customers | 1 |
| `ItemCount` | Number | ⚠️ Optional | Items in transaction | 3 |

## Sample Data Structure

### Example 1: Simple Format

| Date | Description | Quantity | ExtendedNetAmount | SequenceNumber |
|------|-------------|----------|-------------------|----------------|
| 2024-12-15 | House Sourdough | 2 | 16.00 | TXN001 |
| 2024-12-15 | Croissant | 3 | 12.00 | TXN001 |
| 2024-12-15 | Coffee | 2 | 9.00 | TXN002 |

### Example 2: Full Format (with optional columns)

| Date | Description | Quantity | ExtendedNetAmount | SequenceNumber | Hour_ID | CustomerCount | ItemCount |
|------|-------------|----------|-------------------|----------------|---------|---------------|-----------|
| 2024-12-15 | House Sourdough | 2 | 16.00 | TXN001 | 9 | 1 | 2 |
| 2024-12-15 | Croissant | 3 | 12.00 | TXN001 | 9 | 1 | 2 |
| 2024-12-15 | Coffee | 2 | 9.00 | TXN002 | 14 | 1 | 1 |

## Data Considerations

### Date Format
- **Accepted formats**: `YYYY-MM-DD`, `MM/DD/YYYY`, `DD/MM/YYYY`
- **Recommended**: `YYYY-MM-DD` (ISO format)
- **Excel format**: Date cells (not text)

### Product Names
- Can include spaces and special characters
- Will be automatically categorized by the app
- Clean names automatically (removes "TMB" prefix if present)

### Revenue
- Should be **net amount** (after discounts/taxes if applicable)
- Positive numbers only
- Currency: Any (displayed with $ symbol)

### Transaction ID
- Must be unique per transaction
- Can be text or number
- Used to count number of transactions

### Hour_ID
- **Optional** but enables hourly analysis
- Format: 0-23 (24-hour clock)
- 0 = midnight, 12 = noon, 23 = 11 PM

## Creating Sample Data

### Option 1: Manual Entry

1. Open Excel
2. Create columns as shown above
3. Add your sales data
4. Save as `.xlsx` format
5. Name file with date: `Sales_20241215.xlsx`

### Option 2: From Your POS System

Most Point of Sale systems can export to Excel:
1. Export daily transactions
2. Map columns to required format
3. Save as Excel file with date

### Option 3: Generate Test Data

You can use this Python script to generate test data:

```python
import pandas as pd
from datetime import datetime, timedelta
import random

# Generate sample sales data
dates = [datetime(2024, 12, 15) + timedelta(days=i) for i in range(30)]
products = ["House Sourdough", "Croissant", "Baguette", "Coffee", "Muffin"]
data = []

for date in dates:
    for hour in range(8, 20):  # 8 AM to 8 PM
        for txn in range(random.randint(5, 15)):  # 5-15 transactions per hour
            num_items = random.randint(1, 5)
            for item in range(num_items):
                product = random.choice(products)
                qty = random.randint(1, 3)
                price = random.uniform(3, 15)
                revenue = qty * price
                
                data.append({
                    'Date': date,
                    'Description': product,
                    'Quantity': qty,
                    'ExtendedNetAmount': round(revenue, 2),
                    'SequenceNumber': f"TXN{len(data)}",
                    'Hour_ID': hour
                })

df = pd.DataFrame(data)
df.to_excel(f"SalesData_{date.strftime('%Y%m%d')}.xlsx", index=False)
print(f"Created sample data: {len(data)} records")
```

## Common Issues

### "No data found"
- Check date range includes your file dates
- Verify filename has date in YYYYMMDD format
- Ensure files are in shared Google Drive folder

### "Column not found"
- Ensure Excel has required columns
- Check spelling (case-insensitive)
- Column names can vary slightly (Date vs TransactionDate)

### "Invalid data"
- Check numbers are not stored as text
- Verify dates are proper date format
- Remove any header rows (data should start at row 1)

## Best Practices

✅ **Do:**
- Use consistent file naming
- Keep one file per day
- Store in dedicated Google Drive folder
- Use proper Excel date format
- Include all required columns

❌ **Don't:**
- Mix multiple days in one file
- Use CSV format (use Excel .xlsx)
- Include summary rows or totals
- Leave required columns empty
- Use special characters in column names

## Example Files

This folder contains:
- `sample_sales_20241215.xlsx` - Simple example
- `sample_sales_full_20241216.xlsx` - Full format with all columns
- `README.md` - This file

## Need Help?

If your data format is different, you can modify the `process_gdrive_files()` function in `sales_dashboard.py` to match your format.

See [SETUP_GUIDE.md](../SETUP_GUIDE.md) for full setup instructions.
