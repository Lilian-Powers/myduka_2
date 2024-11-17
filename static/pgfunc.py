import psycopg2

def get_remaining_stock_per_single_product(productid):
    conn = psycopg2.connect(
        dbname='myduka',
        password='7663',
        user='postgres',
        host='localhost',
        port=5432
    )
    cur = conn.cursor()

    query = "SELECT productid, SUM(quantity) AS remaining_stock FROM stock WHERE productid = %s GROUP BY productid;"
    cur.execute(query, (productid,))
    res = cur.fetchone()
    # convering the results to a dictionary
    if res is None:
        return {} # empty dictionary
    return {res[0]: res[1]}
    