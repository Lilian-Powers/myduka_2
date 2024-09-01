from flask import Flask, render_template, request, redirect, url_for, flash, session

from dbservice import get_data, insert_products, insert_sales, get_sales_per_product, get_profit_per_product, get_sales_per_day, get_profit_per_day, register_user, check_email

from flask_bcrypt import Bcrypt

app = Flask(__name__)

bcrypt=Bcrypt(app)

app.secret_key = "12345"


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/products")
def products():
    prods = get_data("products")
    return render_template("products.html", prods=prods)


@app.route("/sales")
def sales():
    sale = get_data("sales")
    products = get_data("products")
    return render_template("sales.html", sale=sale, products=products)


@app.route("/add_products", methods=["POST", "GET"])
def add_product():
    if "email1" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        pname = request.form["pn"]
        sprice = request.form["sp"]
        bprice = request.form["bp"]
        squantity = request.form["sq"]

        new_prods = (pname, sprice, bprice, squantity)
        insert_products(new_prods)
        return redirect(url_for("products"))


@app.route("/make_sales", methods=["POST", "GET"])
def make_sale():
    if "email1" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        pname = request.form["productid"]
        quantity = request.form["quant"]

        new_sale = (pname, quantity)
        insert_sales(new_sale)
        return redirect(url_for("sales"))


@app.route("/dashboard")
def dashboard():
    s_prods = get_sales_per_product()
    products_profit = get_profit_per_product()
    sales_per_day = get_sales_per_day()
    profit_per_day = get_profit_per_day()

    names = []
    sales = []
    profit = []
    date = []
    d_profit = []

    for i in s_prods:
        names.append(i[0])
        sales.append(i[1])

    for i in products_profit:
        profit.append(i[1])

    for i in sales_per_day:
        date.append(str(i[0]))
        sales.append(i[1])

    for i in profit_per_day:
        d_profit.append(i[1])

    return render_template("dashboard.html", names=names, sales=sales, profit=profit, date=date, d_profit=d_profit)


@app.route("/registering", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form["fname"]
        lastname = request.form["lname"]
        email = request.form["mail"]
        gender1 = request.form["g"]
        ip_address = request.form["ip"]
        password1 = request.form["password"]
        
        hashed_password=bcrypt.generate_password_hash(password1).decode("utf-8")

        x = check_email(email)
        if x == None:
            new_user = (firstname, lastname, email,
                        gender1, ip_address, hashed_password)
            register_user(new_user)
            return redirect(url_for("login"))
        else:
            flash("Email already exists")
            return redirect(url_for("login"))

    return render_template("registering.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    

    if request.method == "POST":
        email1 = request.form["mail"]
        password1 = request.form["password"]
        
        c_email = check_email(email1)
        if c_email == None:
            flash("Email does not exist. Please register here.", "danger")
            return redirect(url_for("register"))
        else:
            if bcrypt.check_password_hash(c_email[-1], password1):
                flash("login successfull", "success")
                session["email"]=email1
                return redirect(url_for("dashboard"))
            
            else:
                flash("password is incorrect", "danger")
                return redirect(url_for("login"))

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("email1", None)
    return redirect(url_for("login"))

@app.route("/calc")
def net_pay_calc():
    return render_template("netpaycalc.html")


if __name__ == "__main__":
    app.run(debug=True)
