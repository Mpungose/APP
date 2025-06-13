from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from datetime import datetime
import os

from extension import db
from models import User, Book, Order, OrderItem

# Blueprints
from auth.routes import auth_bp
from main.routes import main_bp
from cart.routes import cart_bp
from admin.routes import admin_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fundahub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(admin_bp, url_prefix='/admin')


def create_dummy_data():
    if User.query.first():
        return

    admin = User(
        username='admin',
        email='admin@fundahub.com',
        password_hash=generate_password_hash('admin123'),
        is_admin=True
    )

    student1 = User(
        username='john_doe',
        email='john@university.edu',
        password_hash=generate_password_hash('password123')
    )

    student2 = User(
        username='jane_smith',
        email='jane@university.edu',
        password_hash=generate_password_hash('password123')
    )

    db.session.add_all([admin, student1, student2])
    db.session.commit()

    books = [
        Book(
            title='Introduction to Computer Science',
            author='John Smith',
            condition='Like New',
            price=89.99,
            category='Computer Science',
            description='Comprehensive introduction to programming and computer science concepts.',
            image_url='https://images.pexels.com/photos/159711/books-bookstore-book-reading-159711.jpeg',
            seller_id=student1.id
        ),
        Book(
            title='Calculus: Early Transcendentals',
            author='James Stewart',
            condition='Used',
            price=120.00,
            category='Mathematics',
            description='Essential calculus textbook for engineering and science students.',
            image_url='https://images.pexels.com/photos/159866/books-book-pages-read-159866.jpeg',
            seller_id=student2.id
        ),
        Book(
            title='Principles of Economics',
            author='N. Gregory Mankiw',
            condition='New',
            price=250.00,
            category='Economics',
            description='Comprehensive economics textbook covering micro and macroeconomics.',
            image_url='https://images.pexels.com/photos/1370295/pexels-photo-1370295.jpeg',
            seller_id=student1.id
        ),
        Book(
            title='Organic Chemistry',
            author='Paula Bruice',
            condition='Like New',
            price=180.50,
            category='Chemistry',
            description='Complete guide to organic chemistry with practice problems.',
            image_url='https://images.pexels.com/photos/256541/pexels-photo-256541.jpeg',
            seller_id=student2.id
        ),
        Book(
            title='Data Structures and Algorithms',
            author='Robert Sedgewick',
            condition='Used',
            price=95.00,
            category='Computer Science',
            description='Essential algorithms and data structures for computer science students.',
            image_url='https://images.pexels.com/photos/1370295/pexels-photo-1370295.jpeg',
            seller_id=student1.id
        )
    ]

    db.session.add_all(books)
    db.session.commit()

    order = Order(
        user_id=student2.id,
        total_amount=89.99,
        status='Completed'
    )
    db.session.add(order)
    db.session.commit()

    order_item = OrderItem(
        order_id=order.id,
        book_id=books[0].id,
        quantity=1,
        price=89.99
    )
    db.session.add(order_item)
    db.session.commit()


def create_tables():
    db.create_all()
    create_dummy_data()


with app.app_context():
    db.create_all()
    create_dummy_data()


if __name__ == '__main__':

    app.run(debug=True)
