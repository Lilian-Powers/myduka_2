import psycopg2

conn = psycopg2.connect(
    dbname='myduka',
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


def insert_products(values):
    query = "insert into products(name, buyingprice, sellingprice, stockquantity) values(%s, %s, %s, %s)"
    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()


def insert_sales(values):
    query = "insert into sales(productid, quantity, createdat) values(%s, %s, now())"
    cur.execute(query, values)
    conn.commit()

def get_profit_per_product():
    query = "select name, sum((sellingprice - buyingprice)*stockquantity) as profit_per_product from products join sales on products.productid=sales.productid group by products.name;"
    cur.execute(query)
    res = cur.fetchall()
    return res

def get_sales_per_product():
    query = "select name, sum(sellingprice * quantity) as sales_per_product from products join sales on products.productid=sales.productid group by name;"
    cur.execute(query)
    res = cur.fetchall()
    return res

def get_sales_per_day():
    query = "select date(createdat) as Day, sum((sellingprice )*quantity) as sales_per_day from products join sales on products.productid=sales.productid group by date(createdat) order by day;"
    cur.execute(query)
    res = cur.fetchall()
    return res

def get_profit_per_day():
    query = "select date(createdat) as Day, sum((sellingprice-buyingprice )*quantity) as profit_per_day from products join sales on products.productid=sales.productid group by date(createdat) order by day;"
    cur.execute(query)
    res = cur.fetchall()
    return res

def register_user(values):
    query = "insert into users(first_name, last_name, email, gender, ip_address, password) values(%s, %s, %s, %s, %s, %s)"
    cur.execute(query, values)
    conn.commit()

def check_email(email):
    query = "select * from users where email=%s"
    cur.execute(query, (email,))
    data = cur.fetchone()
    if data:
        return data

def check_email_pass(email1, password1):
    query = "select * from users where email=%s and password=%s"
    cur.execute(query, (email1, password1,))
    res = cur.fetchall()
    return res