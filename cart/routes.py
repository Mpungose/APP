from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Book, Order, OrderItem, User

cart_bp = Blueprint('cart', __name__)

def get_cart():
    """Get cart items from session"""
    return session.get('cart', {})

def add_to_cart(book_id, quantity=1):
    """Add item to cart"""
    cart = get_cart()
    book_id = str(book_id)
    
    if book_id in cart:
        cart[book_id] += quantity
    else:
        cart[book_id] = quantity
    
    session['cart'] = cart
    session.permanent = True

def remove_from_cart(book_id):
    """Remove item from cart"""
    cart = get_cart()
    book_id = str(book_id)
    
    if book_id in cart:
        del cart[book_id]
        session['cart'] = cart

def get_cart_total():
    """Calculate cart total"""
    cart = get_cart()
    total = 0
    
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            total += book.price * quantity
    
    return total

@cart_bp.route('/add/<int:book_id>')
def add(book_id):
    """Add book to cart"""
    if 'user_id' not in session:
        flash('Please log in to add items to cart', 'error')
        return redirect(url_for('auth.login'))
    
    book = Book.query.get_or_404(book_id)
    
    if not book.is_available:
        flash('This book is no longer available', 'error')
        return redirect(url_for('main.book_detail', book_id=book_id))
    
    add_to_cart(book_id)
    flash(f'"{book.title}" added to cart!', 'success')
    
    return redirect(request.referrer or url_for('main.index'))

@cart_bp.route('/remove/<int:book_id>')
def remove(book_id):
    """Remove book from cart"""
    remove_from_cart(book_id)
    flash('Item removed from cart', 'info')
    return redirect(url_for('cart.view'))

@cart_bp.route('/view')
def view():
    """View cart contents"""
    if 'user_id' not in session:
        flash('Please log in to view your cart', 'error')
        return redirect(url_for('auth.login'))
    
    cart = get_cart()
    cart_items = []
    total = 0
    
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book and book.is_available:
            subtotal = book.price * quantity
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        else:
            # Remove unavailable books from cart
            remove_from_cart(book_id)
    
    return render_template('cart/view.html', cart_items=cart_items, total=total)

@cart_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout process"""
    if 'user_id' not in session:
        flash('Please log in to checkout', 'error')
        return redirect(url_for('auth.login'))
    
    cart = get_cart()
    
    if not cart:
        flash('Your cart is empty', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Process payment (dummy implementation)
        user_id = session['user_id']
        total = get_cart_total()
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total,
            status='Completed'
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order items and mark books as unavailable
        for book_id, quantity in cart.items():
            book = Book.query.get(int(book_id))
            if book:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=book.id,
                    quantity=quantity,
                    price=book.price
                )
                db.session.add(order_item)
                
                # Mark book as sold
                book.is_available = False
        
        db.session.commit()
        
        # Clear cart
        session['cart'] = {}
        
        flash(f'Order #{order.id} placed successfully! Total: ${total:.2f}', 'success')
        return redirect(url_for('cart.order_confirmation', order_id=order.id))
    
    # GET request - show checkout form
    cart_items = []
    total = 0
    
    for book_id, quantity in cart.items():
        book = Book.query.get(int(book_id))
        if book:
            subtotal = book.price * quantity
            cart_items.append({
                'book': book,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
    
    return render_template('cart/checkout.html', cart_items=cart_items, total=total)

@cart_bp.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    if 'user_id' not in session:
        flash('Please log in to view orders', 'error')
        return redirect(url_for('auth.login'))
    
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only view their own orders
    if order.user_id != session['user_id']:
        flash('Access denied', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('cart/order_confirmation.html', order=order)