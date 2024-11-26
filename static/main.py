from flask import Flask, render_template, request, redirect, url_for, flash, session

from dbservice import get_data, insert_products, insert_sales, get_sales_per_product, get_profit_per_product, get_sales_per_day, get_profit_per_day, register_user, check_email, update_product_data, get_stock_quantity, update_stock_quantity, get_product_by_name

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
        squantity=request.form["sq"]
        
        product=get_product_by_name(pname)
        if product == None:
            insert_products(pname,bprice, sprice, squantity)
        else:
            flash(" Product exists, update instead?")    
        return redirect(url_for("products_list"))
    
@app.route("/update_product", methods= ["GET", "POST"])
def update_product():
    if request.method == "POST":
        pid = request.form["pi"]
        pname = request.form["pn"]
        bprice = request.form["bp"]
        sprice = request.form["sp"]
        squantity=request.form["sq"]

        update_product_data(pname, bprice, sprice, squantity, pid)
        flash("product updated successfully")
        return redirect(url_for("products_list"))
    else:
        flash("fill in all the inputs")
        return redirect(url_for("products_list"))



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
            flash(f"Insufficient stock for the requested sale.{stockquantity}: is remaining.")
            return redirect(url_for("sales"))
        else:
            insert_sales(pname, quantity)
            stockquantity-=quantity
            update_stock_quantity(stockquantity, pname)
            flash("The sale is successfull. Thank you!")
            return redirect(url_for("sales"))

@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Login to view dashboard")
        return redirect(url_for("login"))

    s_prods = get_sales_per_product()
    products_profit = get_profit_per_product()
    sales_per_day = get_sales_per_day()
    profit_per_day = get_profit_per_day()

    names = []
    sales = []
    profit = []
    date = []
    d_profit = []
    d_sales=[]
    
    for i in s_prods:
        names.append(i[0])
        sales.append(i[1])

    for i in products_profit:
        profit.append(i[1])

    for i in sales_per_day:
        date.append(str(i[0]))
        d_sales.append(i[1])

    for i in profit_per_day:
        d_profit.append(i[1])

    return render_template("dashboard.html", names=names, sales=sales, profit=profit, date=date, d_profit=d_profit, d_sales=d_sales)


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
            register_user(firstname, lastname, email,
                        hashed_password)
            flash("Registration successful! Now login using the email and password")
            return redirect(url_for("login"))
        else:
            flash("Email already exists, login here")
            return redirect(url_for("login"))

    return render_template("registering.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_page = request.args.get("next", "dashboard")

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

if __name__ == "__main__":
    app.run(debug=True)
