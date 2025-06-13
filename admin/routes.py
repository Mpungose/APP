from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Book, Order
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    total_users = User.query.count()
    total_books = Book.query.count()
    available_books = Book.query.filter_by(is_available=True).count()
    total_orders = Order.query.count()
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_books': total_books,
        'available_books': available_books,
        'total_orders': total_orders
    }
    
    return render_template('admin/dashboard.html', stats=stats, 
                         recent_orders=recent_orders, recent_books=recent_books)

@admin_bp.route('/books')
@admin_required
def books():
    """Manage books"""
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    """Add new book"""
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            condition=request.form['condition'],
            price=float(request.form['price']),
            category=request.form['category'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            seller_id=session['user_id']  # Admin as seller
        )
        
        db.session.add(book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/add_book.html')

@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    """Edit existing book"""
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.condition = request.form['condition']
        book.price = float(request.form['price'])
        book.category = request.form['category']
        book.description = request.form['description']
        book.image_url = request.form['image_url']
        book.is_available = 'is_available' in request.form
        
        db.session.commit()
        
        flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.books'))
    
    return render_template('admin/edit_book.html', book=book)

@admin_bp.route('/books/delete/<int:book_id>')
@admin_required
def delete_book(book_id):
    """Delete book"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin.books'))

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/orders')
@admin_required
def orders():
    """Manage orders"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)