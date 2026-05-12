"""
synthetic_data_generator.py
Fixed version - Generates messy spreadsheets for testing the AI-Powered Spreadsheet Cleaner
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import openpyxl
from pathlib import Path
import os

# Initialize Faker for realistic data
fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================
# DATA QUALITY ISSUES TO INJECT
# ============================================

MESSY_HEADERS = {
    'customer_id': ['Cust ID', 'Customer #', 'client-id', 'CUST_ID', 'customer id'],
    'first_name': ['First Name', 'fname', 'given-name', 'FIRST', 'firstName'],
    'last_name': ['Last Name', 'lname', 'surname', 'LAST', 'lastName'],
    'email': ['Email Address', 'e-mail', 'email id', 'EMAIL', 'mail'],
    'phone': ['Phone #', 'Telephone', 'contact no', 'PHONE', 'mobile'],
    'address': ['Address', 'Addr', 'street', 'location', 'ADDRESS'],
    'city': ['City', 'Town', 'CITY', 'municipality', 'city_name'],
    'state': ['State', 'Province', 'STATE', 'region', 'st'],
    'zipcode': ['Zip', 'Postal Code', 'ZIPCODE', 'pin code', 'zip_code'],
    'product_name': ['Product Name', 'item', 'PRODUCT', 'merchandise', 'product_name'],
    'quantity': ['Qty', 'Quantity', 'count', 'QTY', 'amount'],
    'price': ['Price ($)', 'cost', 'PRICE', 'unit price', 'price_usd'],
    'order_date': ['Date', 'Transaction Date', 'DATE', 'order_date', 'created_at'],
    'status': ['Status', 'Order Status', 'STATE', 'progress', 'stage'],
    'sku': ['SKU', 'Item #', 'Product Code', 'SKU #', 'sku_number'],
    'stock_quantity': ['Stock', 'Inventory', 'Qty on Hand', 'STOCK', 'available']
}

TYPO_DICTIONARY = {
    'New York': ['New Yrok', 'New Yory', 'Nw York', 'NewYork', 'NYC'],
    'Los Angeles': ['Los Angelos', 'LA', 'Los Angelse', 'Lost Angeles', 'L.A.'],
    'Chicago': ['Chicage', 'Chigaco', 'Chi-town', 'Chicago', 'Shicago'],
    'Houston': ['Houseton', 'Huston', 'Howston', 'Housten', 'Houson'],
    'Phoenix': ['Pheonix', 'Phonenix', 'Pheonixx', 'Phoenixx', 'Foenix'],
    'Laptop': ['Lap top', 'Laptopp', 'Lapotp', 'Notebook'],
    'Mouse': ['Mous', 'Mause', 'Moouse', 'Wireless Mouse'],
    'Keyboard': ['Key Board', 'Keybord', 'Keyboad', 'KB'],
    'Monitor': ['Moniter', 'Monotor', 'LCD', 'Screen'],
    'Headphones': ['Head phones', 'Headpones', 'Headset', 'Earphones'],
    'Michael': ['Micheal', 'Michell', 'Michale', 'Mike'],
    'Jennifer': ['Jenifer', 'Jennefer', 'Jenniffer', 'Jenny'],
}

STATUS_VALUES = ['Pending', 'Shipped', 'Delivered', 'Cancelled', 'Returned']

# ============================================
# GENERATOR FUNCTIONS
# ============================================

def add_typos(text, typo_probability=0.3):
    """Add random typos to text"""
    if not isinstance(text, str) or random.random() > typo_probability:
        return text
    
    # Check if text matches any known typo patterns
    for correct, typos in TYPO_DICTIONARY.items():
        if correct.lower() in text.lower() or text.lower() == correct.lower():
            return random.choice(typos)
    
    # Random character typos
    if len(text) > 3 and random.random() < 0.5:
        text_list = list(text)
        pos = random.randint(0, len(text_list)-1)
        # Swap adjacent characters
        if pos < len(text_list)-1:
            text_list[pos], text_list[pos+1] = text_list[pos+1], text_list[pos]
            text = ''.join(text_list)
    
    return text

def add_missing_values(df, column, missing_probability=0.05):
    """Add random missing values to a column"""
    mask = np.random.random(len(df)) < missing_probability
    df.loc[mask, column] = np.nan
    return df

def add_duplicates(df, duplicate_count=5):
    """Add duplicate rows"""
    if duplicate_count > 0 and len(df) > duplicate_count:
        duplicate_indices = np.random.choice(len(df), min(duplicate_count, len(df)), replace=False)
        duplicates = df.iloc[duplicate_indices].copy()
        # Add slight variations to some columns to make semantic duplicates
        for idx in duplicates.index:
            if 'email' in df.columns:
                duplicates.loc[idx, 'email'] = add_typos(str(duplicates.loc[idx, 'email']), 0.5)
            if 'address' in df.columns:
                duplicates.loc[idx, 'address'] = add_typos(str(duplicates.loc[idx, 'address']), 0.3)
        df = pd.concat([df, duplicates], ignore_index=True)
    return df

def generate_customer_data(rows=1000):
    """Generate customer dataset with intentional messiness"""
    print(f"Generating {rows} rows of customer data...")
    
    data = []
    for _ in range(rows):
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        data.append({
            'customer_id': fake.uuid4()[:8],
            'first_name': first_name,
            'last_name': last_name,
            'email': f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}",
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zipcode': fake.zipcode(),
            'signup_date': fake.date_between(start_date='-2y', end_date='today'),
            'status': random.choice(['Active', 'Inactive', 'Suspended', 'Pending'])
        })
    
    df = pd.DataFrame(data)
    
    # Add messiness
    print("  Adding messiness...")
    
    # Typos in text columns
    for col in ['first_name', 'last_name', 'city', 'state', 'address']:
        df[col] = df[col].apply(lambda x: add_typos(x, 0.15))
    
    # Email typos
    df['email'] = df['email'].apply(lambda x: add_typos(x, 0.1))
    
    # Missing values
    for col in ['phone', 'address', 'zipcode']:
        df = add_missing_values(df, col, 0.03)
    
    # Duplicates
    df = add_duplicates(df, duplicate_count=int(rows * 0.05))
    
    return df

def generate_sales_data(rows=2000):
    """Generate sales/order dataset"""
    print(f"Generating {rows} rows of sales data...")
    
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones', 'USB Cable', 'Desk Chair', 'Webcam']
    categories = ['Electronics', 'Accessories', 'Furniture']
    
    data = []
    for _ in range(rows):
        product = random.choice(products)
        quantity = random.randint(1, 10)
        price = {
            'Laptop': 999.99,
            'Mouse': 29.99,
            'Keyboard': 79.99,
            'Monitor': 299.99,
            'Headphones': 89.99,
            'USB Cable': 9.99,
            'Desk Chair': 199.99,
            'Webcam': 69.99
        }[product]
        
        data.append({
            'order_id': f"ORD-{fake.random_number(digits=6)}",
            'product_name': product,
            'category': random.choice(categories),
            'quantity': quantity,
            'unit_price': price,
            'total': quantity * price,
            'customer_name': fake.name(),
            'order_date': fake.date_between(start_date='-1y', end_date='today'),
            'status': random.choice(STATUS_VALUES),
            'shipping_address': fake.address().replace('\n', ', ')
        })
    
    df = pd.DataFrame(data)
    
    # Add messiness
    print("  Adding messiness...")
    
    # Typos in product names
    df['product_name'] = df['product_name'].apply(lambda x: add_typos(x, 0.2))
    
    # Typos in customer names
    df['customer_name'] = df['customer_name'].apply(lambda x: add_typos(x, 0.1))
    
    # Status inconsistencies (keep as strings)
    status_typos = {
        'Pending': ['Pendig', 'Pendng', 'PENDING', 'pendin'],
        'Shipped': ['Shiped', 'Shippd', 'SHIPPED', 'shipd'],
        'Delivered': ['Delivered', 'Deliverd', 'DELIVERED', 'delivrd'],
        'Cancelled': ['Canceled', 'Canceld', 'CANCELLED', 'cancel'],
        'Returned': ['Returnd', 'RETURNED', 'return', 'ret']
    }
    for status, typos in status_typos.items():
        mask = df['status'] == status
        df.loc[mask, 'status'] = df.loc[mask, 'status'].apply(
            lambda x: random.choice([x] + typos) if random.random() < 0.2 else x
        )
    
    # Missing values
    df = add_missing_values(df, 'shipping_address', 0.04)
    df = add_missing_values(df, 'category', 0.02)
    
    # Duplicates
    df = add_duplicates(df, duplicate_count=int(rows * 0.08))
    
    # Mixed date formats (keep as strings for variety)
    df['order_date'] = df['order_date'].apply(
        lambda x: x.strftime(random.choice(['%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%Y/%m/%d']))
        if random.random() < 0.3 else x
    )
    
    return df

def generate_product_inventory(rows=500):
    """Generate product inventory dataset - FIXED VERSION"""
    print(f"Generating {rows} rows of inventory data...")
    
    product_prefixes = ['Pro', 'Ultra', 'Basic', 'Premium', 'Eco', 'Smart', 'Max', 'Lite']
    product_suffixes = ['X', 'Plus', 'Pro', 'Air', 'Max', 'Mini', 'Elite', 'Standard']
    
    data = []
    for _ in range(rows):
        prefix = random.choice(product_prefixes)
        suffix = random.choice(product_suffixes)
        product_name = f"{prefix} {fake.word().capitalize()} {suffix}"
        
        # Keep price as float initially
        price = round(random.uniform(10, 1000), 2)
        
        data.append({
            'sku': f"SKU-{fake.random_number(digits=5)}",
            'product_name': product_name,
            'description': fake.sentence(),
            'price': price,  # Store as float
            'stock_quantity': random.randint(0, 500),
            'supplier': fake.company(),
            'last_restocked': fake.date_between(start_date='-90d', end_date='today'),
            'warehouse_location': random.choice(['A1', 'B2', 'C3', 'D4', 'E5', 'F6'])
        })
    
    df = pd.DataFrame(data)
    
    # Add messiness
    print("  Adding messiness...")
    
    # SKU duplicates
    duplicate_skus = np.random.choice(df['sku'].tolist(), size=int(rows * 0.03), replace=False)
    for sku in duplicate_skus:
        duplicate_row = df[df['sku'] == sku].iloc[0].copy()
        duplicate_row['stock_quantity'] = duplicate_row['stock_quantity'] + random.randint(-50, 50)
        df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)
    
    # Missing values
    df = add_missing_values(df, 'description', 0.06)
    df = add_missing_values(df, 'supplier', 0.04)
    
    # Typos in product names
    df['product_name'] = df['product_name'].apply(lambda x: add_typos(x, 0.1))
    
    # For string columns, ensure they're strings
    df['supplier'] = df['supplier'].astype(str)
    df['description'] = df['description'].astype(str)
    
    return df

def generate_mixed_price_column(df):
    """Convert price column to mixed strings/numbers for testing - SEPARATE FUNCTION"""
    # Create a copy to avoid modifying original
    df_with_mixed_prices = df.copy()
    
    # Convert price to string for some rows
    price_mask = np.random.random(len(df_with_mixed_prices)) < 0.15
    for idx in df_with_mixed_prices[price_mask].index:
        price_val = df_with_mixed_prices.loc[idx, 'price']
        if random.random() < 0.5:
            df_with_mixed_prices.loc[idx, 'price'] = f"${price_val}"
        else:
            df_with_mixed_prices.loc[idx, 'price'] = f"{price_val} USD"
    
    return df_with_mixed_prices

# ============================================
# SAVE FUNCTIONS WITH MESSY HEADERS
# ============================================

def apply_messy_headers(df, messiness_level='medium'):
    """Apply messy headers to the dataframe"""
    messy_df = df.copy()
    header_mapping = {}
    
    for clean_col in messy_df.columns:
        # Find matching messy header
        matched = False
        for key, messy_options in MESSY_HEADERS.items():
            if key in clean_col or clean_col in key:
                if messiness_level == 'high':
                    new_header = random.choice(messy_options)
                elif messiness_level == 'medium':
                    new_header = messy_options[0]
                else:
                    new_header = clean_col
                header_mapping[clean_col] = new_header
                matched = True
                break
        
        if not matched:
            header_mapping[clean_col] = clean_col
    
    messy_df.columns = [header_mapping.get(col, col) for col in messy_df.columns]
    return messy_df

def safe_save_csv(df, filename):
    """Safely save CSV handling mixed types"""
    try:
        df.to_csv(filename, index=False)
        return True
    except Exception as e:
        print(f"    Warning: CSV save issue: {e}")
        # Try converting all to string
        df_str = df.astype(str)
        df_str.to_csv(filename, index=False)
        return False

def safe_save_excel(df, filename):
    """Safely save Excel handling mixed types"""
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"    Warning: Excel save issue: {e}")
        # Try converting to string and saving
        df_str = df.astype(str)
        df_str.to_excel(filename, index=False, engine='openpyxl')
        return False

def save_with_mixed_formats(df, base_filename, formats=['csv', 'xlsx']):
    """Save dataset in multiple formats with different issues"""
    saved_files = []
    
    for format_type in formats:
        if format_type == 'csv':
            # CSV with messy headers
            filename = f"{base_filename}_messy.csv"
            messy_df = apply_messy_headers(df, 'medium')
            safe_save_csv(messy_df, filename)
            saved_files.append(filename)
            
            # Clean version for comparison
            clean_filename = f"{base_filename}_clean.csv"
            safe_save_csv(df, clean_filename)
            saved_files.append(clean_filename)
            
        elif format_type == 'xlsx':
            filename = f"{base_filename}_messy.xlsx"
            messy_df = apply_messy_headers(df, 'high')
            
            try:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Main data sheet with messy headers
                    messy_df.to_excel(writer, sheet_name='Data', index=False)
                    
                    # Add notes sheet (always strings)
                    notes_df = pd.DataFrame({
                        'Note': ['This file has intentional issues for testing:',
                                '- Messy headers',
                                '- Typos in text fields',
                                '- Missing values',
                                '- Duplicate rows',
                                '- Mixed data types']
                    })
                    notes_df.to_excel(writer, sheet_name='README', index=False)
                    
                saved_files.append(filename)
            except Exception as e:
                print(f"    Error saving Excel: {e}")
                # Fallback to simple save
                safe_save_excel(messy_df, filename)
                saved_files.append(filename)
            
            # Save clean version
            clean_filename = f"{base_filename}_clean.xlsx"
            safe_save_excel(df, clean_filename)
            saved_files.append(clean_filename)
    
    return saved_files

# ============================================
# MAIN GENERATION FUNCTION
# ============================================

def generate_all_datasets():
    """Generate all synthetic datasets for testing"""
    
    print("\n" + "="*60)
    print("🧪 SYNTHETIC DATA GENERATOR FOR SPREADSHEET CLEANER")
    print("="*60 + "\n")
    
    # Create output directory
    output_dir = Path("test_datasets")
    output_dir.mkdir(exist_ok=True)
    
    # Save current directory and change to output dir
    original_dir = os.getcwd()
    os.chdir(output_dir)
    
    all_files = []
    
    try:
        # 1. Customer Dataset (small, medium, large)
        print("\n📊 1. CUSTOMER DATASETS")
        for size, rows in [('small', 100), ('medium', 500), ('large', 2000)]:
            print(f"\n  Generating {size} customer dataset ({rows} rows)...")
            df = generate_customer_data(rows)
            files = save_with_mixed_formats(df, f"customers_{size}")
            all_files.extend(files)
            print(f"    ✓ Saved {len(files)} files")
        
        # 2. Sales Dataset
        print("\n💰 2. SALES DATASETS")
        for size, rows in [('small', 200), ('medium', 1000), ('large', 3000)]:
            print(f"\n  Generating {size} sales dataset ({rows} rows)...")
            df = generate_sales_data(rows)
            files = save_with_mixed_formats(df, f"sales_{size}")
            all_files.extend(files)
            print(f"    ✓ Saved {len(files)} files")
        
        # 3. Product Inventory (with mixed price column as separate version)
        print("\n📦 3. PRODUCT INVENTORY")
        print("  Generating base inventory...")
        df = generate_product_inventory(500)
        
        # Save base version
        files = save_with_mixed_formats(df, "inventory_base")
        all_files.extend(files)
        print(f"    ✓ Saved base version ({len(files)} files)")
        
        # Create version with mixed price formats
        print("  Generating inventory with mixed price formats...")
        df_mixed_price = generate_mixed_price_column(df)
        files = save_with_mixed_formats(df_mixed_price, "inventory_mixed_prices")
        all_files.extend(files)
        print(f"    ✓ Saved mixed price version ({len(files)} files)")
        
        # 4. Special edge case datasets
        print("\n🔬 4. EDGE CASE DATASETS")
        
        # Empty rows dataset
        print("  Generating dataset with empty rows...")
        empty_df = generate_customer_data(100)
        empty_indices = np.random.choice(len(empty_df), 10, replace=False)
        for idx in empty_indices:
            empty_df.iloc[idx] = np.nan
        safe_save_csv(empty_df, "edge_case_empty_rows.csv")
        safe_save_excel(empty_df, "edge_case_empty_rows.xlsx")
        all_files.extend(["edge_case_empty_rows.csv", "edge_case_empty_rows.xlsx"])
        print("    ✓ Saved empty rows datasets")
        
        # All caps headers
        print("  Generating dataset with all caps headers...")
        caps_df = generate_customer_data(50)
        caps_df.columns = [col.upper() for col in caps_df.columns]
        safe_save_csv(caps_df, "edge_case_all_caps_headers.csv")
        safe_save_excel(caps_df, "edge_case_all_caps_headers.xlsx")
        all_files.extend(["edge_case_all_caps_headers.csv", "edge_case_all_caps_headers.xlsx"])
        print("    ✓ Saved all caps headers datasets")
        
        # Special characters in headers
        print("  Generating dataset with special characters...")
        special_df = generate_customer_data(50)
        special_df.columns = [f"{col}#$%" for col in special_df.columns]
        safe_save_csv(special_df, "edge_case_special_chars.csv")
        safe_save_excel(special_df, "edge_case_special_chars.xlsx")
        all_files.extend(["edge_case_special_chars.csv", "edge_case_special_chars.xlsx"])
        print("    ✓ Saved special characters datasets")
        
        # Duplicate heavy dataset
        print("  Generating dataset with many duplicates...")
        dup_df = generate_customer_data(200)
        dup_df = add_duplicates(dup_df, duplicate_count=50)
        safe_save_csv(dup_df, "edge_case_many_duplicates.csv")
        safe_save_excel(dup_df, "edge_case_many_duplicates.xlsx")
        all_files.extend(["edge_case_many_duplicates.csv", "edge_case_many_duplicates.xlsx"])
        print("    ✓ Saved many duplicates datasets")
        
        # Summary
        print("\n" + "="*60)
        print("✅ GENERATION COMPLETE!")
        print(f"   Created {len(all_files)} test files in 'test_datasets/'")
        print("\n📁 Files created:")
        for f in sorted(all_files)[:20]:  # Show first 20
            file_size = Path(f).stat().st_size if Path(f).exists() else 0
            print(f"   • {f} ({file_size:,} bytes)")
        if len(all_files) > 20:
            print(f"   ... and {len(all_files) - 20} more files")
        
        print("\n🚀 Next steps:")
        print("   1. Test the cleaner on small files first:")
        print("      python ../cleaner.py clean customers_small_messy.csv")
        print("\n   2. Compare with clean versions:")
        print("      diff customers_small_clean.csv customers_small_messy.csv")
        print("\n   3. Test mixed price formats:")
        print("      python ../cleaner.py clean inventory_mixed_prices_messy.xlsx")
        print("\n   4. Try edge cases:")
        print("      python ../cleaner.py clean edge_case_all_caps_headers.csv --fix-typos True")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Change back to original directory
        os.chdir(original_dir)
    
    return all_files

# ============================================
# RUN GENERATOR
# ============================================

if __name__ == "__main__":
    try:
        # Check if required packages are installed
        import faker
        import openpyxl
        generate_all_datasets()
    except ImportError as e:
        print(f"\n❌ Missing required package: {e}")
        print("\nPlease install required packages:")
        print("pip install faker pandas numpy openpyxl")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()