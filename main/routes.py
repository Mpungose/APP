from flask import Blueprint, render_template, request
from models import Book, db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page with featured books"""
    # Get search parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    # Build query
    query = Book.query.filter_by(is_available=True)

    if search:
        query = query.filter(
            (Book.title.contains(search)) |
            (Book.author.contains(search)) |
            (Book.description.contains(search))
        )

    if category:
        query = query.filter_by(category=category)

    books = query.all()

    # Get all categories for filter dropdown
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories]

    return render_template('main/index.html', books=books, categories=categories,
                           current_search=search, current_category=category)


@main_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    """Individual book detail page"""
    book = Book.query.get_or_404(book_id)
    return render_template('main/book_detail.html', book=book)


@main_bp.route('/books')
def books():
    """All books listing page"""
    # Get search and filter parameters
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    condition = request.args.get('condition', '')
    sort_by = request.args.get('sort', 'newest')

    # Build query
    query = Book.query.filter_by(is_available=True)

    if search:
        query = query.filter(
            (Book.title.contains(search)) |
            (Book.author.contains(search))
        )

    if category:
        query = query.filter_by(category=category)

    if condition:
        query = query.filter_by(condition=condition)

    # Apply sorting
    if sort_by == 'price_low':
        query = query.order_by(Book.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Book.price.desc())
    elif sort_by == 'title':
        query = query.order_by(Book.title.asc())
    else:  # newest
        query = query.order_by(Book.created_at.desc())

    books = query.all()

    # Get filter options
    categories = db.session.query(Book.category).distinct().all()
    categories = [cat[0] for cat in categories]

    conditions = db.session.query(Book.condition).distinct().all()
    conditions = [cond[0] for cond in conditions]

    return render_template('main/books.html', books=books, categories=categories,
                           conditions=conditions, current_search=search,
                           current_category=category, current_condition=condition,
                           current_sort=sort_by)
