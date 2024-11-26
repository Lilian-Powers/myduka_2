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
    query = f"select * from {table}"
    cur.execute(query)
    data = cur.fetchall()
    return data


def insert_products(name, buying_price, selling_price, stock_quantity):
    query = "insert into products(name, buying_price, selling_price, stock_quantity) values(%s, %s, %s, %s)"
    values = (name, buying_price, selling_price, stock_quantity)
    cur.execute(query, values)
    conn.commit()


def insert_sales(productid, quantity):
    query = "insert into sales(pid, quantity, created_at) values(%s, %s, now())"
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
    query = "select name, sum(selling_price - buying_price) as profit_per_product from products join sales on products.id=sales.pid group by products.name;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_sales_per_product():
    query = "select name, sum(selling_price * quantity) as sales_per_product from products join sales on products.id=sales.pid group by name;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_sales_per_day():
    query = "select date(created_at) as Day, sum((selling_price )*quantity) as sales_per_day from products join sales on products.id=sales.pid group by date(created_at) order by day;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def get_profit_per_day():
    query = "select date(created_at) as Day, sum((selling_price-buying_price )*quantity) as profit_per_day from products join sales on products.id=sales.pid group by date(created_at) order by day;"
    cur.execute(query)
    res = cur.fetchall()
    return res


def register_user(first_name, last_name, email, password):
    query = "insert into users(first_name, last_name, email, password) values(%s, %s, %s, %s)"
    values = (first_name, last_name, email, password)
    cur.execute(query, values)
    conn.commit()


def check_email(email):
    query = "select * from users where email=%s"
    cur.execute(query, (email,))
    data = cur.fetchone()
    if data:
        return data


def check_email_pass(email, password):
    query = "select * from users where email=%s and password=%s"
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
