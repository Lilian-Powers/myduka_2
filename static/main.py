from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, Column, Integer, Numeric,String, ForeignKey, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from flask_bcrypt import Bcrypt
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "12345"
bcrypt = Bcrypt(app)

# SQLAlchemy Setup
Base = declarative_base()
engine = create_engine("postgresql://postgres:7663@localhost:5432/myduka_db")
Session = sessionmaker(bind=engine)
db_session = Session()

# Database Models
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    buying_price = Column(Numeric(14, 2))
    selling_price = Column(Numeric(14, 2))
    stock_quantity = Column(Integer)
    sales = relationship("Sale", backref="product", lazy=True)

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))

# Create Database Tables
Base.metadata.create_all(engine)

# Helper Functions
def insert_product(name, buying_price, selling_price, stock_quantity):
    product = Product(name=name, buying_price=buying_price, selling_price=selling_price, stock_quantity=stock_quantity)
    db_session.add(product)
    db_session.commit()

def get_product_by_name(name):
    return db_session.query(Product).filter_by(name=name).first()

def update_product(product_id, name, buying_price, selling_price, stock_quantity):
    product = db_session.query(Product).filter_by(id=product_id).first()
    if product:
        product.name = name
        product.buying_price = buying_price
        product.selling_price = selling_price
        product.stock_quantity = stock_quantity
        db_session.commit()

def insert_sale(product_id, quantity):
    sale = Sale(product_id=product_id, quantity=quantity, created_at=datetime.utcnow())
    db_session.add(sale)
    db_session.commit()

def get_sales_per_product():
    return db_session.query(Product.name, func.sum(Sale.quantity))\
        .join(Sale, Product.id == Sale.product_id)\
        .group_by(Product.name).all()

def get_profit_per_product():
    return db_session.query(
        Product.name,
        (func.sum(Sale.quantity) * (Product.selling_price - Product.buying_price)).label("profit")
    ).join(Sale, Product.id == Sale.product_id).group_by(
        Product.name, Product.selling_price, Product.buying_price
    ).all()


def get_sales_per_day():
    return db_session.query(
        func.date(Sale.created_at).label("date"),
        func.sum(Sale.quantity).label("total_sales")
    ).group_by(func.date(Sale.created_at)).all()

def get_profit_per_day():
    return db_session.query(
        func.date(Sale.created_at).label("date"),
        func.sum(Sale.quantity * (Product.selling_price - Product.buying_price)).label("profit")
    ).join(Product, Sale.product_id == Product.id).group_by(func.date(Sale.created_at)).all()

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/products_list")
def products_list():
    if "email" not in session:
        flash("Login to view products")
        return redirect(url_for("login"))
    
    products = db_session.query(Product).all()
    return render_template("products.html", products=products)

@app.route("/sales", methods=['GET', 'POST'])
def sales():
    if "email" not in session:
        flash("Login to view sales")
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        quantity = request.form['quant']
        payment_method = request.form['check']
        
        new_sale = Sale(product_id=product_id, quantity=quantity, payment_method=payment_method)
        db_session.add(new_sale)
        db_session.commit()

    sales = db_session.query(Sale).all()
    products = db_session.query(Product).all()
    
    product_name = {product.id: product.name for product in products}
    
    return render_template("sales.html", sales=sales, product_name=product_name, products=products)

@app.route("/add_products", methods=["POST", "GET"])
def add_product():
    if "email" not in session:
        flash("Login to add products")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        name = request.form["pn"]
        buying_price = int(request.form["bp"])
        selling_price = int(request.form["sp"])
        stock_quantity = int(request.form["sq"])

        if not get_product_by_name(name):
            insert_product(name, buying_price, selling_price, stock_quantity)
            flash("Product added successfully")
        else:
            flash("Product already exists")
        return redirect(url_for("products_list"))

@app.route("/update_product", methods=["POST"])
def update_product():
    if "email" not in session:
        flash("Login to update products")
        return redirect(url_for("login"))
    
    product_id = int(request.form["pi"])
    name = request.form["pn"]
    buying_price = int(request.form["bp"])
    selling_price = int(request.form["sp"])
    stock_quantity = int(request.form["sq"])

    update_product(product_id, name, buying_price, selling_price, stock_quantity)
    flash("Product updated successfully")
    return redirect(url_for("products_list"))

@app.route("/make_sales", methods=["POST", "GET"])
def make_sale():
    if "email" not in session:
        flash("Login to make sales")
        return redirect(url_for("login"))

    if request.method == "POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quant"])
        product = db_session.query(Product).filter_by(id=product_id).first()

        if not product or product.stock_quantity < quantity:
            flash("Insufficient stock or product not found")
            return redirect(url_for("sales"))
        
        product.stock_quantity -= quantity
        insert_sale(product_id, quantity)
        db_session.commit()
        flash("Sale recorded successfully")
        return redirect(url_for("sales"))

@app.route("/dashboard")
def dashboard():
    if "email" not in session:
        flash("Login to view dashboard")
        return redirect(url_for("login"))

    sales_per_product = get_sales_per_product()
    profit_per_product = get_profit_per_product()
    sales_per_day = get_sales_per_day()
    profit_per_day = get_profit_per_day()

    names, sales, profits, dates, daily_sales, daily_profits = [], [], [], [], [], []

    for product in sales_per_product:
        names.append(product[0])
        sales.append(product[1])

    for product in profit_per_product:
        profits.append(product[1])

    for day in sales_per_day:
        dates.append(str(day[0]))
        daily_sales.append(day[1])

    for day in profit_per_day:
        daily_profits.append(day[1])

    return render_template(
        "dashboard.html",
        names=names,
        sales=sales,
        profits=profits,
        dates=dates,
        daily_sales=daily_sales,
        daily_profits=daily_profits,
    )

@app.route("/registering", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        first_name = request.form["fname"]
        last_name = request.form["lname"]
        email = request.form["mail"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if not db_session.query(User).filter_by(email=email).first():
            user = User(first_name=first_name, last_name=last_name, email=email, password=password)
            db_session.add(user)
            db_session.commit()
            flash("Registration successful! Please log in.")
        else:
            flash("Email already exists. Please log in.")
        return redirect(url_for("login"))

    return render_template("registering.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["mail"]
        password = request.form["password"]

        user = db_session.query(User).filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session["email"] = user.email
            flash("Login successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    flash("Logged out successfully!")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
