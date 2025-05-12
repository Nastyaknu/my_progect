import urllib.parse
from base import get_products

# Блок 1
def application(environ, start_response):
    # Обробка запиту
    query_string = environ.get('QUERY_STRING', '')
    search_query = ""
    if query_string:
        params = dict(param.split('=') for param in query_string.split('&'))
        search_query = params.get('query', "")

    # Отримуємо список товарів з бази даних
    products = get_products(search_query)

    # HTML-шаблон
    HTML_HEAD = """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Інтернет-крамниця</title>
        
    </head>
    <body>
    <h1>Усі товари</h1>
    <form method="get">
        <label for="query">Пошук за назвою: </label>
        <input type="text" name="query" id="query" value="{search_query}">
        <input type="submit" value="Знайти">
    </form>
    <div class="products">
    """

    HTML_FOOT = """
    </div>
    </body>
    </html>
    """

    # Генерація HTML контенту
    html_content = HTML_HEAD.format(search_query=search_query)
    for name, description, features, price, image in products:
        html_content += f"""
            <div class="product">
                <img src="images/{image}" alt="{name}">
                <h2>{name}</h2>
                <p><strong>Ціна:</strong> {price} грн</p>
                <p>{description}</p>
                <p><em>{features}</em></p>
            </div>
        """

    html_content += HTML_FOOT

    # Відправка відповіді
    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    return [html_content.encode('utf-8')]