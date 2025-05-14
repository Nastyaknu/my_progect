import urllib.parse
from base import get_products, get_categories
from wsgiref.util import FileWrapper
from urllib.parse import parse_qs
import sqlite3
import os
from http.cookies import SimpleCookie


def handle_register(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            size = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(size)
            params = parse_qs(post_data.decode())

            username = params.get('username', [''])[0]
            password = params.get('password', [''])[0]

            with sqlite3.connect("catalog.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    message = "<p style='color:red;'>Користувач із таким логіном уже існує!</p>"
                else:
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    message = "<p style='color:green;'>Реєстрація успішна!</p>"

            html = f"""
                <h2>Реєстрація</h2>
                {message}
                <a href="/">На головну</a>
            """
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [html.encode('utf-8')]
        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
            return [f"<h2>Помилка: {str(e)}</h2>".encode('utf-8')]

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return ["""
        <h2>Реєстрація</h2>
        <form method="post" action="/register">
            <label>Ім'я користувача: <input type="text" name="username" required></label><br>
            <label>Пароль: <input type="password" name="password" required></label><br>
            <input type="submit" value="Зареєструватися">
        </form>
    """.encode('utf-8')]
def parse_cookies(environ):
    cookie = SimpleCookie()
    if 'HTTP_COOKIE' in environ:
        cookie.load(environ['HTTP_COOKIE'])
    return {key: morsel.value for key, morsel in cookie.items()}

def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    cookies = parse_cookies(environ)
    if path.startswith('/images/'):
        file_path = '.' + path
        if os.path.exists(file_path):
            start_response('200 OK', [('Content-Type', 'image/jpeg')])
            return FileWrapper(open(file_path, 'rb'))
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['File not found'.encode('utf-8')]

    if path == '/register':
        return handle_register(environ, start_response)

    if path == '/product':
        query = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query)
        product_id = params.get('id', [None])[0]

        if product_id:
            with sqlite3.connect("catalog.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, description, features, price, image FROM products WHERE id = ?", (product_id,))
                row = cursor.fetchone()

            if row:
                name, description, features, price, image = row

                html = f"""
                <h1>{name}</h1>
                <img src="/images/{image}" alt="{name}" width="300"><br>
                <p><strong>Ціна:</strong> {price} грн</p>
                <p><strong>Опис:</strong> {description}</p>
                <p><em>{features}</em></p>

                <form method="post" action="/add-to-cart">
                    <input type="hidden" name="product_id" value="{product_id}">
                    <input type="submit" value="Додати в кошик">
                </form>

                <p><a href="/">На головну</a></p>
                """
                start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
                return [html.encode('utf-8')]

        start_response('404 Not Found', [('Content-Type', 'text/plain; charset=utf-8')])
        return ["Товар не знайдено".encode('utf-8')]
    if path == '/cart':
        cart_ids=cookies.get('cart','').split(',' )if cookies.get('cart') else[]
        cart_ids=[int(cid)for cid in cart_ids if cid.isdigit()]
        with sqlite3.connect("catalog.db") as conn:
            cursor = conn.cursor()
            if cart_ids:
                plase_holders=','.join(['?']*len(cart_ids))
                cursor.execute(f"select name, price from products where id in ({plase_holders})", cart_ids)
                items = cursor.fetchall()
            else:
                items = []
            html = """<h1>Ваш кошик</h1><ul> """
            total=0
            for name, price in items:
                html += f"<li>{name}: {price}грн</li>"
                total += price
            html += f"</ul><p><strong>Загальна сума:</strong> {total} грн</p>"
            html += '<p><a href="/">⬅️ Назад до каталогу</a></p>'
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html.encode("utf-8")]


    # Головна сторінка
    query_string = environ.get('QUERY_STRING', '')
    search_query = ""
    category_id = None

    if query_string:
        params = urllib.parse.parse_qs(query_string)
        search_query = params.get('query', [''])[0]
        category_id = params.get('category', [''])[0]
        if not category_id.isdigit():
            category_id = None

    categories = get_categories()
    category_options = '<option value="">Всі категорії</option>\n'
    for cid, cname in categories:
        selected = ' selected' if str(cid) == str(category_id) else ''
        category_options += f'<option value="{cid}"{selected}>{cname}</option>\n'

    products = get_products(search_query, category_id)

    HTML_HEAD = """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Інтернет-крамниця</title>
        <style>
            .product {{
                border: 1px solid black;
                margin: 10px;
                padding: 10px;
                display: inline-block;
                width: 300px;
                vertical-align: top;
            }}
            .product img {{
                width: 100%;
                max-height: 200px;
                object-fit: contain;
            }}
        </style>
    </head>
    <body>
        <h1>Усі товари</h1>
        <form method="get" style="display: flex; gap: 10px; align-items: center;">
            <label for="query">Пошук за назвою:</label>
            <input type="text" name="query" id="query" value="{search_query}">
            <label for="category">Категорія:</label>
            <select name="category" id="category">
                {category_options}
            </select>
            <input type="submit" value="Знайти">
            <button onclick="window.location.href='/register'" type="button">Реєстрація</button>
            <form method="post" action="/cart">
                    <input type="hidden" name="product_id" value="{product_id}">
                    <input type="submit" value="Показати кошик">
                </form>
        </form>
    """

    HTML_FOOT = """
        </div>
    </body>
    </html>
    """

    html_content = HTML_HEAD.format(
        search_query=search_query,
        category_options=category_options
    )

    for product_id, name, description, features, price, image in products:
        html_content += f"""
        <a href="/product?id={product_id}" class="product">
            <img src="/images/{image}" alt="{name}">
            <h2>{name}</h2>
            <p><strong>Ціна:</strong> {price} грн</p>
        </a>
        """

    html_content += HTML_FOOT

    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html_content.encode('utf-8')]
