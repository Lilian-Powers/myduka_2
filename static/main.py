from flask import Flask, render_template, request, redirect, url_for, flash, session

from dbservice import get_data, insert_products, insert_sales, get_sales_per_product, get_profit_per_product, get_sales_per_day, get_profit_per_day, register_user, check_email, insert_stock, update_product_data, edit_product_data, get_remaining_stock_per_product, get_stock_quantity

from pgfunc import get_remaining_stock_per_single_product

from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.secret_key = "12345"


@app.context_processor
def inject_remaining_stock_per_single_product():
    return {}


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/products/<int:productid>")
def products(productid):
    if "email" not in session:
        flash("Login to view products")
        return redirect(url_for("login"))

    prods = get_data("products")
    remaining_stock = get_remaining_stock_per_single_product(productid)
    # making sure the remaining_stock is a dictionary
    if not isinstance(remaining_stock, dict):
        remaining_stock = {}

    return render_template("products.html", prods=prods, remaining_stock=remaining_stock)


@app.route("/products_list")
def products_list():
    if "email" not in session:
        flash("Login to view products")
        return redirect(url_for("login"))
    prods = get_data("products")
    productid = prods[0][0] if prods else None
    remaining_stock = get_remaining_stock_per_single_product(productid)
    # making sure the remaining_stock is a dictionary
    if not isinstance(remaining_stock, dict):
        remaining_stock = {}
    return render_template("products.html", prods=prods, remaining_stock=remaining_stock)


@app.route("/sales")
def sales():
    if "email" not in session:
        flash("Login to view sales")
        return redirect(url_for("login"))
    sale = get_data("sales")
    products = get_data("products")
    product_name = {product[0]: product[1] for product in products}

    return render_template("sales.html", sale=sale, products=products, product_name=product_name)


@app.route("/add_products", methods=["POST", "GET"])
def add_product():
    if "email" not in session:
        flash("Login to add products")
        return redirect(url_for("login"))
    if request.method == "POST":
        pname = request.form["pn"]
        sprice = request.form["sp"]
        bprice = request.form["bp"]

        insert_products(pname, sprice, bprice)

        productid = insert_products(pname, sprice, bprice)
        return redirect(url_for("products_list", productid=productid))


@app.route("/make_sales", methods=["POST", "GET"])
def make_sale():
    if "email" not in session:
        flash("Login to make sales")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        pname = request.form["productid"]
        quantity = int(request.form["quant"])
        stockquantity=get_stock_quantity(pname)
        
    if quantity > stockquantity:
        flash(f"Insufficient stock for the requested sale. {stockquantity}: only remaining.")
        return redirect(url_for("sales"))
    else:
        insert_sales(pname, quantity)
        flash("The sale is successfull. Thank you!")
        return redirect(url_for("sales"))


@app.route("/stock", methods=["POST", "GET"])
def stock():
    if "email" not in session:
        flash("Login to view stocks")
        return redirect(url_for("login", next=request.url))

    stocks = get_data("stock")
    sale = get_data("sales")
    products = get_data("products")
    product_name = {product[0]: product[1] for product in products}

    return render_template("stock.html", stocks=stocks, sale=sale, products=products, product_name=product_name)


@app.route("/add_stock", methods=["POST", "GET"])
def add_stock():
    if "email" not in session:
        flash("Login to add stocks")
        return redirect(url_for("login", next=request.url))

    if request.method == "POST":
        salesid = request.form["si"]
        productid = request.form["pi"]
        # pname = request.form["pn"]
        quantity = int(request.form["quant"])

        # new_stock = (salesid, productid, quantity, pname)
        insert_stock(salesid, productid, quantity)
        flash("Stock added successfully")
        return redirect(url_for("stock"))
    else:
        flash("Error adding stock. Try again.")
        return render_template("stock.html")


@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Login to view dashboard")
        return redirect(url_for("login"))

    s_prods = get_sales_per_product()
    products_profit = get_profit_per_product()
    sales_per_day = get_sales_per_day()
    profit_per_day = get_profit_per_day()
    r_stock = get_remaining_stock_per_product()

    names = []
    sales = []
    profit = []
    date = []
    d_profit = []
    stock = []

    for i in s_prods:
        names.append(i[0])
        sales.append(i[1])

    for i in products_profit:
        profit.append(i[1])

    for i in sales_per_day:
        date.append(str(i[0]))
        # sales.append(i[1])

    for i in profit_per_day:
        d_profit.append(i[1])

    for i in r_stock:
        stock.append(i[1])

    return render_template("dashboard.html", names=names, sales=sales, profit=profit, date=date, d_profit=d_profit, stock=stock)


@app.route("/registering", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form["fname"]
        lastname = request.form["lname"]
        email = request.form["mail"]
        password1 = request.form["password"]

        hashed_password = bcrypt.generate_password_hash(
            password1).decode("utf-8")

        x = check_email(email)
        if x == None:
            new_user = (firstname, lastname, email,
                        hashed_password)
            register_user(new_user)
            flash("Registration successful! Now login using the email and password")
            return redirect(url_for("login"))
        else:
            flash("Email already exists, login here")
            return redirect(url_for("login"))

    return render_template("registering.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", "stock")

    if request.method == "POST":
        email = request.form["mail"]
        password1 = request.form["password"]

        c_email = check_email(email)
        if c_email == None:
            flash("Email does not exist. First, register here", "danger")
            return redirect(url_for("register"))
        else:
            if bcrypt.check_password_hash(c_email[-1], password1):
                flash("login successfull")
                session["email"] = email
                return redirect(url_for(next_page))
            else:
                flash("password is incorrect")
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))

# prefills


@app.route("/edit_product", methods=["GET", "POST"])
def edit_product():
    if "email" not in session:
        flash("Login to edit products")
        return redirect(url_for("login"))
    if request.method == "POST":
        pid = request.form["pi"]
        pname = request.form["pn"]
        sprice = request.form["sp"]
        bprice = request.form["bp"]

        return redirect(url_for("update_product", pi=pid, pn=pname, sp=sprice, bp=bprice))
    else:
        product_data = edit_product_data()
        return render_template("products.html", product_data=product_data)


@app.route("/update_product", methods= ["GET", "POST"])
def update_product():
    if request.method == "POST":
        pid = request.form["pi"]
        pname = request.form["pn"]
        sprice = request.form["sp"]
        bprice = request.form["bp"]

        update_product_data(pid, pname, sprice, bprice)
        flash("product updated successfully")
        return redirect(url_for("products_list"))
    else:
        flash("fill in all the inputs")
        return redirect(url_for("products_list"))


if __name__ == "__main__":
    app.run(debug=True)
