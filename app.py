from __future__ import annotations
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column, String, Integer, select, DateTime, Float
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from typing import List
import os

app = Flask(__name__)

# Secure connection to DB without hardcoding credentials
db_user = os.getenv("DB_USER", "root")
db_password = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "3306")
db_name = os.getenv("DB_NAME", "ecommerce_api")

if db_password:
    default_db_uri = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
else:
    default_db_uri = f"mysql+mysqlconnector://{db_user}@{db_host}:{db_port}/{db_name}"

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", default_db_uri)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Creating Base Model
class Base(DeclarativeBase):
    pass

# Initializing SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

#============= Models/Tables ================

#Relationship Table for Orders and Products
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    address: Mapped[str] = mapped_column(String(200), nullable=False)

    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(
        secondary=order_product,
        back_populates="orders",
    )

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String(200))
    price: Mapped[float] = mapped_column(Float)

    orders: Mapped[List["Order"]] = relationship(
        secondary=order_product,
        back_populates="products",
    )

#=========== Schemas ============

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class OrderSchema(ma.SQLAlchemyAutoSchema):
    products = ma.Nested("ProductSchema", many=True)

    class Meta:
        model = Order
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Commit current transaction; rollback and return a 409 response on DB integrity conflicts.
def commit_or_rollback():
    try:
        db.session.commit()
        return None
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error. Check duplicate/required values and foreign keys."}), 409

#=========== Routes ============

# USER ROUTES

# Create User with POST
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_user = User(name=user_data['name'], email=user_data['email'], address=user_data['address'])
    db.session.add(new_user)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result

    return user_schema.jsonify(new_user), 201  # 201 is a successful creation status

# Retrieve all users with GET
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200

# Retrieve a single user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user ID"}), 400

    return user_schema.jsonify(user), 200

# Update User
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user ID"}), 400
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user.name = user_data['name']
    user.email = user_data['email']

    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result
    return user_schema.jsonify(user), 200

# Delete User
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user ID"}), 400
    
    db.session.delete(user)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result
    return jsonify({"message": f"successfully deleted user {id}"}), 200

# PRODUCT ROUTES

# Create Product with POST
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result

    return product_schema.jsonify(new_product), 201  # 201 is a successful creation status

# Retrieve all products with GET
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200

# Retrieve a single product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product ID"}), 400

    return product_schema.jsonify(product), 200

# Update Product
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product ID"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data['product_name']
    product.price = product_data['price']

    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result
    return product_schema.jsonify(product), 200

# Delete Product
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product ID"}), 400
    
    db.session.delete(product)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result
    return jsonify({"message": f"successfully deleted product {id}"}), 200


# ORDER ROUTES

# Create Order with POST
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Validate that the user exists
    user = db.session.get(User, order_data['user_id'])
    if not user:
        return jsonify({"message": "Invalid user ID"}), 400

    new_order_data = {"user_id": order_data['user_id']}
    if 'order_date' in order_data:
        new_order_data['order_date'] = order_data['order_date']

    new_order = Order(**new_order_data)
    db.session.add(new_order)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result

    return order_schema.jsonify(new_order), 201  # 201 is a successful creation status

# Add Product to Order
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    # Validate that the order exists
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Invalid order ID"}), 400

    # Validate that the product exists
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Invalid product ID"}), 400

    # Check if product is already in the order (prevent duplicates)
    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400

    # Add product to order
    order.products.append(product)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result

    return order_schema.jsonify(order), 200

# Delete a Product from Order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def delete_product_from_order(order_id, product_id):
    # Validate that the order exists
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"message": "Invalid order ID"}), 400

    # Validate that the product exists
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message": "Invalid product ID"}), 400

    # Ensure product is currently associated with the order
    if product not in order.products:
        return jsonify({"message": "Product not in order"}), 400

    # Remove product from order
    order.products.remove(product)
    commit_result = commit_or_rollback()
    if commit_result:
        return commit_result

    return order_schema.jsonify(order), 200

# Get all orders for a User
@app.route('/orders/users/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "Invalid user ID"}), 400

    query = select(Order).where(Order.user_id == user_id)
    orders = db.session.execute(query).scalars().all()

    return orders_schema.jsonify(orders), 200

# Get all products for an Order
@app.route('/orders/<int:order_id>/products', methods=["GET"])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Invalid order ID"}), 400

    return products_schema.jsonify(order.products), 200

if __name__ == "__main__":
    with app.app_context():
        Base.metadata.create_all(db.engine)
    app.run(debug=True)