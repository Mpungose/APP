from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from extension import db


class User(db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    books = db.relationship('Book', backref='seller', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Book(db.Model):
    """Book model for textbook listings"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(50), nullable=False)  # New, Like New, Used
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Faculty/Subject
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Book {self.title}>'


class Order(db.Model):
    """Order model for purchase tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    # Pending, Completed, Cancelled
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    """Order item model for individual book purchases within an order"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of purchase

    # Relationships
    book = db.relationship('Book', backref='order_items')

    def __repr__(self):
        return f'<OrderItem {self.id}>'
