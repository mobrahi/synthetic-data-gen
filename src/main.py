"""
synthetic_data_generator.py
Generates messy spreadsheets for testing the AI-Powered Spreadsheet Cleaner
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import openpyxl
from pathlib import Path

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
    'product': ['Product Name', 'item', 'PRODUCT', 'merchandise', 'product_name'],
    'quantity': ['Qty', 'Quantity', 'count', 'QTY', 'amount'],
    'price': ['Price ($)', 'cost', 'PRICE', 'unit price', 'price_usd'],
    'date': ['Date', 'Transaction Date', 'DATE', 'order_date', 'created_at'],
    'status': ['Status', 'Order Status', 'STATE', 'progress', 'stage']
}

TYPO_DICTIONARY = {
    'New York': ['New Yrok', 'New Yory', 'Nw York', 'NewYork', 'NYC'],
    'Los Angeles': ['Los Angelos', 'LA', 'Los Angelse', 'Lost Angeles', 'L.A.'],
    'Chicago': ['Chicage', 'Chigaco', 'Chi-town', 'Chicago', 'Shicago'],
    'Houston': ['Houseton', 'Huston', 'Howston', 'Housten', 'Houson'],
    'Phoenix': ['Pheonix', 'Phonenix', 'Pheonixx', 'Phoenixx', 'Foenix'],
    'Philadelphia': ['Philidelphia', 'Philly', 'Philadephia', 'Filadelfia'],
    'San Antonio': ['San Antonio', 'SanAntonio', 'San Antonia', 'SA'],
    'San Diego': ['San Diego', 'SanDiego', 'San Diago', 'SD'],
    'Dallas': ['Dallas', 'Dalllas', 'Dallaz', 'Big D'],
    'Austin': ['Austin', 'Austen', 'Austiin', 'ATX'],
    
    # Product typos
    'Laptop': ['Lap top', 'Laptopp', 'Lapotp', 'Notebook'],
    'Mouse': ['Mous', 'Mause', 'Moouse', 'Wireless Mouse'],
    'Keyboard': ['Key Board', 'Keybord', 'Keyboad', 'KB'],
    'Monitor': ['Moniter', 'Monotor', 'LCD', 'Screen'],
    'Headphones': ['Head phones', 'Headpones', 'Headset', 'Earphones'],
    
    # Name typos
    'Michael': ['Micheal', 'Michell', 'Michale', 'Mike'],
    'Jennifer': ['Jenifer', 'Jennefer', 'Jenniffer', 'Jenny'],
    'Christopher': ['Christoper', 'Cristopher', 'Chris', 'Topher'],
    'Jessica': ['Jesica', 'Jessicca', 'Jessi', 'Jess'],
    'Daniel': ['Danial', 'Danieal', 'Danny', 'Dan'],
    
    # Email domain typos
    'gmail.com': ['gmail.co', 'gmial.com', 'gmal.com', 'gmail.cm'],
    'yahoo.com': ['yahho.com', 'yaho.com', 'yhoo.com', 'yahoo.co'],
    'hotmail.com': ['hotmail.co', 'hotmai.com', 'hotmal.com', 'hotmail.cm']
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
        duplicate_indices = np.random.choice(len(df), duplicate_count, replace=False)
        duplicates = df.iloc[duplicate_indices].copy()
        # Add slight variations to some columns to make semantic duplicates
        for idx in duplicates.index:
            if 'email' in df.columns:
                duplicates.loc[idx, 'email'] = add_typos(duplicates.loc[idx, 'email'], 0.5)
            if 'address' in df.columns:
                duplicates.loc[idx, 'address'] = add_typos(duplicates.loc[idx, 'address'], 0.3)
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
    
    # Messy headers (will be applied when saving)
    
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
    
    # Inconsistent date formats (will be mixed when saving)
    
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
    
    # Status inconsistencies
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
    
    # Inconsistent date formats
    df['order_date'] = df['order_date'].apply(
        lambda x: x.strftime(random.choice(['%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%Y/%m/%d']))
        if random.random() < 0.3 else x
    )
    
    return df

def generate_product_inventory(rows=500):
    """Generate product inventory dataset"""
    print(f"Generating {rows} rows of inventory data...")
    
    product_prefixes = ['Pro', 'Ultra', 'Basic', 'Premium', 'Eco', 'Smart', 'Max', 'Lite']
    product_suffixes = ['X', 'Plus', 'Pro', 'Air', 'Max', 'Mini', 'Elite', 'Standard']
    
    data = []
    for _ in range(rows):
        prefix = random.choice(product_prefixes)
        suffix = random.choice(product_suffixes)
        product_name = f"{prefix} {fake.word().capitalize()} {suffix}"
        
        data.append({
            'SKU': f"SKU-{fake.random_number(digits=5)}",
            'Product Name': product_name,
            'Description': fake.sentence(),
            'Price': round(random.uniform(10, 1000), 2),
            'Stock Quantity': random.randint(0, 500),
            'Supplier': fake.company(),
            'Last Restocked': fake.date_between(start_date='-90d', end_date='today'),
            'Warehouse Location': random.choice(['A1', 'B2', 'C3', 'D4', 'E5', 'F6'])
        })
    
    df = pd.DataFrame(data)
    
    # Add messiness
    print("  Adding messiness...")
    
    # SKU duplicates
    duplicate_skus = np.random.choice(df['SKU'].tolist(), size=int(rows * 0.03), replace=False)
    for sku in duplicate_skus:
        duplicate_row = df[df['SKU'] == sku].iloc[0].copy()
        duplicate_row['Stock Quantity'] = duplicate_row['Stock Quantity'] + random.randint(-50, 50)
        df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)
    
    # Price with wrong format (strings with $)
    price_mask = np.random.random(len(df)) < 0.1
    df.loc[price_mask, 'Price'] = df.loc[price_mask, 'Price'].apply(
        lambda x: f"${x}" if random.random() < 0.5 else f"{x} USD"
    )
    
    # Missing values
    df = add_missing_values(df, 'Description', 0.06)
    df = add_missing_values(df, 'Supplier', 0.04)
    
    # Typos in product names
    df['Product Name'] = df['Product Name'].apply(lambda x: add_typos(x, 0.1))
    
    return df

# ============================================
# SAVE FUNCTIONS WITH MESSY HEADERS
# ============================================

def apply_messy_headers(df, messiness_level='medium'):
    """Apply messy headers to the dataframe"""
    messy_df = df.copy()
    header_mapping = {}
    
    for clean_col in messy_df.columns:
        if clean_col in MESSY_HEADERS:
            if messiness_level == 'high':
                # Use random messy header
                new_header = random.choice(MESSY_HEADERS[clean_col])
            elif messiness_level == 'medium':
                # Use first messy header
                new_header = MESSY_HEADERS[clean_col][0]
            else:
                new_header = clean_col
            header_mapping[clean_col] = new_header
    
    messy_df.columns = [header_mapping.get(col, col) for col in messy_df.columns]
    return messy_df

def save_with_mixed_formats(df, base_filename, formats=['csv', 'xlsx']):
    """Save dataset in multiple formats with different issues"""
    saved_files = []
    
    for format_type in formats:
        if format_type == 'csv':
            filename = f"{base_filename}_messy.csv"
            # CSV with mixed header styles
            messy_df = apply_messy_headers(df, 'medium')
            messy_df.to_csv(filename, index=False)
            saved_files.append(filename)
            
            # Also save clean version for comparison
            clean_filename = f"{base_filename}_clean.csv"
            df.to_csv(clean_filename, index=False)
            saved_files.append(clean_filename)
            
        elif format_type == 'xlsx':
            filename = f"{base_filename}_messy.xlsx"
            messy_df = apply_messy_headers(df, 'high')
            
            # Create Excel with multiple sheets for extra messiness
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Main data sheet with messy headers
                messy_df.to_excel(writer, sheet_name='Data', index=False)
                
                # Add a "notes" sheet with metadata
                notes_df = pd.DataFrame({
                    'Note': ['This file has intentional issues for testing:',
                            '- Messy headers',
                            '- Typos in text fields',
                            '- Missing values',
                            '- Duplicate rows',
                            '- Mixed date formats']
                })
                notes_df.to_excel(writer, sheet_name='README', index=False)
                
                # Add a summary sheet with wrong name
                summary_df = messy_df.describe()
                summary_df.to_excel(writer, sheet_name='Stats (maybe wrong)', index=True)
            
            saved_files.append(filename)
            
            # Save clean version
            clean_filename = f"{base_filename}_clean.xlsx"
            df.to_excel(clean_filename, index=False)
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
    os.chdir(output_dir)
    
    all_files = []
    
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
    
    # 3. Product Inventory
    print("\n📦 3. PRODUCT INVENTORY")
    df = generate_product_inventory(500)
    files = save_with_mixed_formats(df, "inventory")
    all_files.extend(files)
    print(f"  ✓ Saved {len(files)} files")
    
    # 4. Special edge case datasets
    print("\n🔬 4. EDGE CASE DATASETS")
    
    # Empty rows dataset
    print("  Generating dataset with empty rows...")
    empty_df = generate_customer_data(100)
    empty_indices = np.random.choice(len(empty_df), 10, replace=False)
    empty_df.iloc[empty_indices] = np.nan
    empty_df.to_csv("edge_case_empty_rows.csv", index=False)
    empty_df.to_excel("edge_case_empty_rows.xlsx", index=False)
    all_files.extend(["edge_case_empty_rows.csv", "edge_case_empty_rows.xlsx"])
    
    # All caps headers
    print("  Generating dataset with all caps headers...")
    caps_df = generate_customer_data(50)
    caps_df.columns = [col.upper() for col in caps_df.columns]
    caps_df.to_csv("edge_case_all_caps_headers.csv", index=False)
    caps_df.to_excel("edge_case_all_caps_headers.xlsx", index=False)
    all_files.extend(["edge_case_all_caps_headers.csv", "edge_case_all_caps_headers.xlsx"])
    
    # Special characters in headers
    print("  Generating dataset with special characters...")
    special_df = generate_customer_data(50)
    special_df.columns = [f"{col} #$%" for col in special_df.columns]
    special_df.to_csv("edge_case_special_chars.csv", index=False)
    special_df.to_excel("edge_case_special_chars.xlsx", index=False)
    all_files.extend(["edge_case_special_chars.csv", "edge_case_special_chars.xlsx"])
    
    # Summary
    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE!")
    print(f"   Created {len(all_files)} test files in '{output_dir}/'")
    print("\n📁 Files created:")
    for f in sorted(all_files):
        print(f"   • {f}")
    
    print("\n🚀 Next steps:")
    print("   1. Test the cleaner on small files first:")
    print("      python ../cleaner.py clean customers_small_messy.csv")
    print("\n   2. Compare with clean versions:")
    print("      diff customers_small_clean.csv customers_small_messy.csv")
    print("\n   3. Try different models:")
    print("      python ../cleaner.py clean sales_medium_messy.xlsx --model llama3.2:3b")
    
    print("\n" + "="*60)
    
    return all_files

# ============================================
# RUN GENERATOR
# ============================================

if __name__ == "__main__":
    import os
    
    try:
        generate_all_datasets()
    except Exception as e:
        print(f"\n❌ Error generating datasets: {e}")
        print("\nMake sure you have installed required packages:")
        print("pip install faker pandas numpy openpyxl")
