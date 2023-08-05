from flask import Flask, render_template, request, redirect, url_for
import os
import requests
from data_models import Book, Author, db

def get_book_cover(isbn):
    url = "https://book-cover-api2.p.rapidapi.com/api/public/books/v1/cover/url"

    querystring = {"languageCode": "en", "isbn": str(isbn)}

    headers = {
        "X-RapidAPI-Key": "567cd28ad3mshdcbf94d7a737abdp17456djsn79f1ea7523d3",
        "X-RapidAPI-Host": "book-cover-api2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        book_cover_url = data.get('url')
        if book_cover_url:
            return book_cover_url
        else:
            return "default_cover_url.jpg"
    except requests.exceptions.RequestException as e:
        return "default_cover_url.jpg"

def ask_review(data):
    url = "https://chatgpt-api8.p.rapidapi.com/"

    payload = [
        {
            "content": f"What book do you recommend based on this information : {data}",
            "role": "user"
        }
    ]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "567cd28ad3mshdcbf94d7a737abdp17456djsn79f1ea7523d3",
        "X-RapidAPI-Host": "chatgpt-api8.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)
    review_text = response.json()['text']
    return review_text

app = Flask(__name__)
db_path = os.path.join(os.path.dirname(__file__), "data", "library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db.init_app(app)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = ""
    if request.method == 'POST':
        author_name = request.form['name']
        author_birthdate = request.form['birthdate']
        date_of_death = request.form['date_of_death']
        new_author = Author(Author_name=author_name, Author_birth_date=author_birthdate, Author_date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()
        message = "Author added successfully."
    return render_template('add_author.html', message=message)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = ""
    authors = Author.query.all()

    if request.method == 'POST':
        book_isbn = request.form['isbn']
        book_title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = int(request.form['author_id'])
        existing_book = Book.query.filter_by(Book_title=book_title).first()
        if existing_book:
            message = "Book already exists."
        else:
            existing_author = Author.query.get(author_id)
            if not existing_author:
                message = "Author not found. Please add the author first before adding the book."
            else:
                book_cover_url = get_book_cover(book_isbn)
                if book_cover_url:
                    new_book = Book(
                        Book_isbn=book_isbn,
                        Book_title=book_title,
                        Book_publication_year=publication_year,
                        Book_cover_url=book_cover_url,
                        Author_id=author_id
                    )
                    db.session.add(new_book)
                    db.session.commit()
                    message = "Book added successfully."
                else:
                    message = "Failed to fetch the book cover."
    return render_template('add_book.html', message=message, authors=authors)

@app.route('/')
def home():
    books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).order_by(Book.Book_title).all()
    return render_template('home.html', books_data=books_data)


@app.route('/sort_books/<sort_by>')
def sort_books(sort_by):
    if sort_by == 'title':
        books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).order_by(
            Book.Book_title).all()
    elif sort_by == 'author':
        books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).order_by(
            Author.Author_name).all()
    else:
        books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).order_by(
            Book.Book_title).all()

    return render_template('home.html', books_data=books_data)

@app.route('/search_books', methods=['GET'])
def search_books():
    query = request.args.get('query')
    if not query:
        books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).order_by(
            Book.Book_title).all()
        return render_template('home.html', books_data=books_data)
    books_data = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).filter(
        Book.Book_title.like(f"%{query}%")
    ).order_by(Book.Book_title).all()
    if not books_data:
        message = "No books found matching the search criteria."
        return render_template('home.html', message=message)
    return render_template('home.html', books_data=books_data)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        author = book.author
        other_books = Book.query.filter_by(Author_id=author.Author_id).filter(Book.Book_id != book_id).all()
        if other_books:
            db.session.delete(book)
            db.session.commit()
            message = f"Book '{book.Book_title}' has been deleted successfully."
        else:
            db.session.delete(book)
            db.session.delete(author)
            db.session.commit()
            message = f"Book '{book.Book_title}' and its author have been deleted successfully."
    else:
        message = "Book not found."
    return redirect(url_for('home', message=message))

@app.route('/book/<int:book_id>/details', methods=['GET'])
def book_details(book_id):
    book = db.session.query(Book, Author).join(Author, Book.Author_id == Author.Author_id).filter(
        Book.Book_id == book_id).first()
    book_data, author_data = book
    return render_template('book_details.html', book=book_data, author=author_data)

@app.route('/rate_book/<int:book_id>', methods=['POST'])
def rate_book(book_id):
    book = Book.query.get(book_id)
    if book:
        rating = int(request.form['rating'])
        if 1 <= rating <= 10:
            book.Book_rating = rating
            db.session.commit()
            message = f"Rating for '{book.Book_title}' has been added successfully."
        else:
            message = "Invalid rating. Please provide a rating between 1 and 10."
    else:
        message = "Book not found."

    return redirect(url_for('home', message=message))

@app.route('/book_review', methods=['GET'])
def book_review():
    books = Book.query.all()
    Suggest_a_Book = ask_review(books)
    return render_template('book_review.html', Suggest_a_Book=Suggest_a_Book)

@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get(author_id)
    if author:
        if author.books:
            for book in author.books:
                db.session.delete(book)
        db.session.delete(author)
        db.session.commit()
        message = f"Author '{author.Author_name}' and their books have been deleted successfully."
    else:
        message = "Author not found."
    return redirect(url_for('home', message=message))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
