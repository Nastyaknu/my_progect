import sqlite3
name_base="Catalog.db"

def create_table():
    conn = sqlite3.connect('catalog.db')
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT not null)
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT not null,
    description TEXT,
    features TEXT,
    price REAL,
    image TEXT,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    conn.commit()
    conn.close()
def get_products(search_query=""):
    with sqlite3.connect("catalog.db") as conn:
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT name, description, features, price, image FROM products WHERE name LIKE ?", (f"%{search_query}%",))
        else:
            cursor.execute("SELECT name, description, features, price, image FROM products")
        return cursor.fetchall()

def add_data_to_table():
    conn = sqlite3.connect('catalog.db')
    c = conn.cursor()
    c.execute("DELETE FROM products")
    c.execute("DELETE FROM categories")
    categories = ["Ноутбуки", "Смартфони", "Планшети"]
    category_ids = {}
    for name in categories:
        c.execute("""
        INSERT INTO categories (name) VALUES (?)
        """, (name,))
        category_ids[name] = c.lastrowid
    products = [(
        "Lenovo IdeaPad 5", "Потужний ноутбук для роботи та навчання",
        "16GB RAM, 512GB SSD, Intel Core i5", 23999,
        "laptop.jpg", category_ids["Ноутбуки"]
    ), (
        "ASUS Vivobook 15", "Тонкий і легкий ноутбук",
        "8GB RAM, 256GB SSD, AMD Ryzen 5", 19999,
        "asus.jpg", category_ids["Ноутбуки"]
    ), (
        "Samsung Galaxy S21", "Флагманський смартфон із відмінною камерою",
        "8GB RAM, 128GB, 64MP камера", 18999,
        "s21.jpg", category_ids["Смартфони"]
    ), (
        "iPhone 13", "Популярний смартфон від Apple",
        "4GB RAM, 128GB, A15 Bionic", 29999,
        "iphone13.jpg", category_ids["Смартфони"]
    ), (
        "Xiaomi Pad 5", "Бюджетний планшет з великим екраном",
        "6GB RAM, 128GB, Snapdragon 860", 13999,
        "xiaomi_pad.jpg", category_ids["Планшети"]
    )]
    # Додавання товарів
    c.executemany("""        INSERT INTO products (name, description, features, price, image, category_id)
                                  VALUES (?, ?, ?, ?, ?, ?)    """, products)

    conn.commit()
    conn.close()


