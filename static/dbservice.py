import psycopg2

conn = psycopg2.connect(
    dbname='myduka_db',
    password='7663',
    user='postgres',
    host='localhost',
    port=5432
)
cur = conn.cursor()


def get_data(table):
    query = f"SELECT * FROM {table}"
    cur.execute(query)
    data = cur.fetchall()
    return data


def insert_products(name, buying_price, selling_price, stock_quantity):
    query = "INSERT INTO PRODUCTS(name, buying_price, selling_price, stock_quantity) VALUES(%s, %s, %s, %s)"
    values = (name, buying_price, selling_price, stock_quantity)
    cur.execute(query, values)
    conn.commit()


def insert_sales(productid, quantity):
    query = "INSERT INTO SALES (pid, quantity, created_at) VALUES(%s, %s, now())"
    values = (productid, quantity)
    cur.execute(query, values)
    conn.commit()


def get_stock_quantity(id):
    query = "SELECT stock_quantity FROM products WHERE products.id=%s"
    values = (id,)
    cur.execute(query, values)
    stockquantity = cur.fetchone()
    return stockquantity[0]


def get_profit_per_product():
    query = "SELECT name, sum(selling_price - buying_price) AS profit_per_product FROM products JOIN sales ON products.id=sales.pid GROUP BY products.name;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_sales_per_product():
    query = "SELECT name, sum(selling_price * quantity) AS sales_per_product FROM products JOIN sales ON products.id=sales.pid GROUP BY name;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_sales_per_day():
    query = "SELECT date(created_at) AS Day, sum((selling_price )*quantity) AS sales_per_day FROM products JOIN sales ON products.id=sales.pid GROUP BY date(created_at) ORDER BY day;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_profit_per_day():
    query = "SELECT date(created_at) AS Day, sum((selling_price-buying_price )*quantity) AS profit_per_day FROM products JOIN sales ON products.id=sales.pid GROUP BY date(created_at) ORDER BY day;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def register_user(first_name, last_name, email, password):
    query = "INSERT INTO users(first_name, last_name, email, password) VALUES(%s, %s, %s, %s)"
    values = (first_name, last_name, email, password)
    cur.execute(query, values)
    conn.commit()


def check_email(email):
    query = "SELECT * FROM users WHERE email=%s"
    cur.execute(query, (email,))
    data = cur.fetchone()
    if data:
        return data


def check_email_pass(email, password):
    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cur.execute(query, (email, password,))
    res = cur.fetchall()
    return res


def get_product_by_name(name):
    query = "SELECT * FROM products WHERE name=%s"
    cur.execute(query, (name,))
    data = cur.fetchone()
    return data


def update_product_data(name, buyingprice, sellingprice, stockquantity, id,):
    query = "UPDATE products SET name=%s, buying_price=%s, selling_price=%s, stock_quantity=%s WHERE id=%s"
    cur.execute(query, (name, buyingprice, sellingprice, stockquantity, id))
    conn.commit()


def update_stock_quantity(stock_quantity, id):
    query = " UPDATE products SET stock_quantity=%s WHERE id=%s"
    values = (stock_quantity, id)
    cur.execute(query, values)
    conn.commit()
