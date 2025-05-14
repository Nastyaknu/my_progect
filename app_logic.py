import urllib.parse
from base import get_products, get_categories
from wsgiref.util import FileWrapper
from urllib.parse import parse_qs
import sqlite3
import os
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
                    #  Користувач існує — показати повідомлення
                    message = "<p style='color:red;'>Користувач із таким логіном уже існує!</p>"
                else:
                    #  Користувача нема — додати
                    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    conn.commit()
                    message = "<p style='color:green;'>Реєстрація успішна!</p>"

            html = f"""
                            <h2>Реєстрація</h2>
                            {message}
                            <a href="/">На головну</a>
                            """
            start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
            return [html.encode('utf-8')]        except Exception as e:
            start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
            return [f"<h2>Помилка: {str(e)}</h2>".encode('utf-8')]

        # GET-запит – форма реєстрації
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return ["""
        <h2>Реєстрація</h2>
        <form method="post" action="/register">
            <label>Ім'я користувача: <input type="text" name="username" required></label><br>
            <label>Пароль: <input type="password" name="password" required></label><br>
            <input type="submit" value="Зареєструватися">
        </form>
        """.encode('utf-8')]


def application(environ, start_response):
    path = environ.get('PATH_INFO', '')

    # Обробка зображень
    if path.startswith('/images/'):
        file_path = '.' + path
        if os.path.exists(file_path):
            start_response('200 OK', [('Content-Type', 'image/jpeg')])
            return FileWrapper(open(file_path, 'rb'))
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'File not found']

    # Обробка GET-параметрів
    query_string = environ.get('QUERY_STRING', '')
    search_query = ""
    category_id = None

    if query_string:
        params = urllib.parse.parse_qs(query_string)
        search_query = params.get('query', [''])[0]
        category_id = params.get('category', [''])[0]
        if not category_id.isdigit():
            category_id = None

    # Отримання категорій
    categories = get_categories()

    # Генерація <option> для списку категорій
    category_options = '<option value="">Всі категорії</option>\n'
    for cid, cname in categories:
        selected = ' selected' if str(cid) == str(category_id) else ''
        category_options += f'<option value="{cid}"{selected}>{cname}</option>\n'

    # Отримання товарів
    products = get_products(search_query, category_id)

    # HTML-шаблон
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

  <!-- друга кнопка — як посилання -->
  <button onclick="window.location.href='/register'" type="button">Реєстрація</button>
</form>

    """

    HTML_FOOT = """
        </div>
    </body>
    </html>
    """

    if path == '/register':
        return handle_register(environ, start_response)


    # Формування сторінки
    html_content = HTML_HEAD.format(
        search_query=search_query,
        category_options=category_options
    )

    for name, description, features, price, image in products:
        html_content += f"""
        <div class="product">
            <img src="/images/{image}" alt="{name}">
            <h2>{name}</h2>
            <p><strong>Ціна:</strong> {price} грн</p>
            <p>{description}</p>
            <p><em>{features}</em></p>
        </div>
        """

    html_content += HTML_FOOT

    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html_content.encode('utf-8')]
