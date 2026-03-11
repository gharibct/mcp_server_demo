import sqlite3
import os

DB_NAME = "inventory.db"

def init_db():
    """Initializes the sample database with product data."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        category TEXT NOT NULL
    )
    ''')
    
    # Sample data
    products = [
        (1, 'Laptop', 1200.0, 10, 'Electronics'),
        (2, 'Mouse', 25.0, 50, 'Accessories'),
        (3, 'Keyboard', 75.0, 30, 'Accessories'),
        (4, 'Monitor', 300.0, 15, 'Electronics'),
        (5, 'Desk Lamp', 45.0, 20, 'Office')
    ]
    
    cursor.executemany('INSERT INTO products (id, name, price, stock, category) VALUES (?, ?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()

def query_product(name: str):
    """Queries product information by name."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price, stock, category FROM products WHERE name LIKE ?", (f'%{name}%',))
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return f"No product found with name '{name}'."
    
    output = "Products found:\n"
    for r in results:
        output += f"- {r[0]}: ${r[1]}, Stock: {r[2]}, Category: {r[3]}\n"
    return output

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
