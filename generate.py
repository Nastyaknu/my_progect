import sqlite3

HTML_HEAD = """
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Інтернет-крамниця</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .product { border: 1px solid #ccc; padding: 10px; margin: 10px; width: 300px; display: inline-block; vertical-align: top; }
        .product img { max-width: 100%; height: auto; }
        .product h2 { margin: 5px 0; }
        .product p { margin: 5px 0; }
    </style>
</head>
<body>
<h1>Усі товари</h1>
<div class="products">
"""

HTML_FOOT = """
</div>
</body>
</html>
"""

def generate_index():
    with sqlite3.connect("catalog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, description, features, price, image FROM products
        """)
        products = cursor.fetchall()

    with open("all_product.html", "w", encoding="utf-8") as f:
        f.write(HTML_HEAD)

        for name, description, features, price, image in products:
            f.write(f"""
                <div class="product">
                    <img src="images/{image}" alt="{name}">
                    <h2>{name}</h2>
                    <p><strong>Ціна:</strong> {price} грн</p>
                    <p>{description}</p>
                    <p><em>{features}</em></p>
                </div>
            """)

        f.write(HTML_FOOT)

    print("index.html успішно згенеровано.")

generate_index()