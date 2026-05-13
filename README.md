# 🎲 Synthetic Data Generator for Spreadsheet Testing

Generate realistic, intentionally-messy spreadsheets to test data cleaning tools, ETL pipelines, and LLM-based data processors.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Overview

This tool creates synthetic datasets with **real-world data quality issues** including:
- Messy/inconsistent headers
- Typos and misspellings
- Missing values (nulls)
- Exact and semantic duplicates
- Mixed data formats (dates, prices, etc.)
- Special characters and edge cases

Perfect for testing:
- AI-powered data cleaners
- ETL pipelines
- Data validation rules
- LLM-based data normalization

## ✨ Features

- **Multiple Dataset Types**: Customers, Sales, Inventory
- **Configurable Messiness**: Control the level of data corruption
- **Multiple Formats**: CSV and Excel (.xlsx) output
- **Clean Reference Files**: Includes clean versions for comparison
- **Reproducible**: Fixed random seed for consistent results
- **Edge Cases**: Special characters, all-caps headers, empty rows

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/synthetic-data-generator.git
cd synthetic-data-generator

# Install dependencies
pip install -r requirements.txt
```

### Generate Your First Dataset

```bash
# Run the generator
python synthetic_data_generator.py

# Output will be in the 'test_datasets/' directory
ls test_datasets/
```

## 📊 Generated Datasets

The generator creates the following datasets:

### 1. Customer Data (`customers_*.csv/xlsx`)

| Size | Rows | Use Case |
|------|------|----------|
| Small | 100 | Quick testing |
| Medium | 500 | Development |
| Large | 2,000 | Performance testing |

**Fields**: customer_id, name, email, phone, address, city, state, zipcode, signup_date, status

### 2. Sales Data (`sales_*.csv/xlsx`)

| Size | Rows | Use Case |
|------|------|----------|
| Small | 200 | Feature validation |
| Medium | 1,000 | Integration testing |
| Large | 3,000 | Stress testing |

**Fields**: order_id, product_name, category, quantity, unit_price, total, customer_name, order_date, status, shipping_address

### 3. Inventory Data (`inventory_*.csv/xlsx`)

| Version | Description |
|---------|-------------|
| Base | Standard inventory data |
| Mixed Prices | Prices formatted with $ and USD suffixes |

**Fields**: sku, product_name, description, price, stock_quantity, supplier, last_restocked, warehouse_location

### 4. Edge Case Datasets

| File | Issues |
|------|--------|
| `edge_case_empty_rows.csv` | 10% null rows |
| `edge_case_all_caps_headers.csv` | UPPERCASE column names |
| `edge_case_special_chars.csv` | Headers with `#$%` characters |
| `edge_case_many_duplicates.csv` | 25% duplicate rows |

## 🎯 Types of Messiness

### Headers
```python
# Before
['Cust ID', 'First Name', 'Email Address', 'Phone #']

# After (clean version)
['customer_id', 'first_name', 'email', 'phone']
```

### Typos and Misspellings
| Correct | Messy Versions |
|---------|----------------|
| New York | New Yrok, New Yory, Nw York |
| Laptop | Lap top, Laptopp, Lapotp |
| Michael | Micheal, Michell, Michale |

### Data Quality Issues
- **Missing Values**: 3-6% nulls in critical fields
- **Duplicates**: 5-8% exact duplicates + semantic variations
- **Mixed Formats**: Dates in 4 different formats, prices with/without currency symbols

## 📁 Output Structure

```
test_datasets/
├── customers_small_messy.csv      # Messy version
├── customers_small_clean.csv      # Clean reference
├── customers_small_messy.xlsx     # Excel format
├── customers_small_clean.xlsx
├── sales_medium_messy.csv
├── sales_medium_clean.csv
├── inventory_base_messy.csv
├── inventory_mixed_prices_messy.csv
└── edge_case_*.csv/xlsx
```

## 🛠️ Configuration

### Modify Messiness Levels

Edit the generator to adjust intensity:

```python
# Change typo probability (default: 0.15 = 15%)
df['column'] = df['column'].apply(lambda x: add_typos(x, 0.25))

# Change missing value rate (default: 0.03 = 3%)
df = add_missing_values(df, 'column', 0.10)

# Change duplicate count (default: 5% of rows)
df = add_duplicates(df, duplicate_count=int(rows * 0.15))
```

### Add Custom Dataset Types

```python
def generate_custom_dataset(rows=1000):
    data = []
    for _ in range(rows):
        data.append({
            'field1': fake.word(),
            'field2': fake.random_number(),
            # Add your fields
        })
    
    df = pd.DataFrame(data)
    
    # Add messiness
    df['field1'] = df['field1'].apply(lambda x: add_typos(x, 0.1))
    
    return df
```

## 💻 Usage Examples

### Basic Generation
```bash
# Generate all default datasets
python synthetic_data_generator.py
```

### In Python Scripts
```python
from synthetic_data_generator import generate_customer_data

# Generate 500 rows of messy customer data
df = generate_customer_data(rows=500)

# Save with custom filename
df.to_csv('my_test_data.csv', index=False)
```

### Integration with Testing

```python
import pytest
from synthetic_data_generator import generate_sales_data

def test_data_cleaner():
    # Generate test data
    messy_df = generate_sales_data(rows=100)
    
    # Run your cleaner
    cleaned_df = your_cleaner(messy_df)
    
    # Assertions
    assert cleaned_df.isnull().sum().sum() < 10
    assert cleaned_df.duplicated().sum() == 0
```

## 📦 Requirements

```
pandas>=2.0.0
numpy>=1.24.0
Faker>=18.0.0
openpyxl>=3.1.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

## 🔧 Troubleshooting

### "No module named 'faker'"
```bash
pip install faker
```

### "Excel file format error"
```bash
pip install openpyxl --upgrade
```

### Memory issues with large datasets
```python
# Reduce dataset size
generate_customer_data(rows=100)  # Instead of 2000
```

## 🧪 Testing Your Cleaner

### Compare Clean vs Messy
```bash
# Generate test data
python synthetic_data_generator.py

# Run your cleaner
python cleaner.py test_datasets/customers_small_messy.csv

# Compare results
diff test_datasets/customers_small_clean.csv cleaned_output.csv
```

### Benchmark Performance
```python
import time
from synthetic_data_generator import generate_sales_data

# Generate large dataset
df = generate_sales_data(rows=10000)

# Time your cleaning process
start = time.time()
cleaned = your_cleaner(df)
print(f"Cleaned 10k rows in {time.time()-start:.2f} seconds")
```

## 📈 Use Cases

### 1. Unit Testing
```python
def test_email_normalization():
    df = generate_customer_data(50)
    # Emails have intentional typos (gmail.co, gmial.com)
    cleaned = normalize_emails(df)
    assert all('@' in email for email in cleaned['email'])
```

### 2. Performance Testing
Test how your tool handles:
- Large files (2000+ rows)
- Mixed data types
- High duplicate rates

### 3. Edge Case Validation
Verify your tool handles:
- Empty files
- All-caps headers
- Special characters
- Missing critical fields

## 🤝 Contributing

Contributions welcome! Ideas for improvement:

- [ ] Add more dataset types (Healthcare, Financial, Log data)
- [ ] Support JSON and Parquet formats
- [ ] Add configurable messiness profiles (mild, medium, extreme)
- [ ] Generate schema validation rules
- [ ] Add data drift simulation over time
- [ ] Create web UI for custom dataset generation

## 📝 License

MIT License - Use freely for personal and commercial projects.

## 🙏 Acknowledgments

- [Faker](https://github.com/joke2k/faker) - Realistic fake data
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Excel file handling

---