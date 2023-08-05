from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    Author_id = db.Column(db.Integer, primary_key=True)
    Author_name = db.Column(db.String)
    Author_birth_date = db.Column(db.String)
    Author_date_of_death = db.Column(db.String)
    books = db.relationship('Book', backref='author', lazy=True)

    def __repr__(self):
        return f"<Author(id={self.Author_id}, name='{self.Author_name}')>"


class Book(db.Model):
    Book_id = db.Column(db.Integer, primary_key=True)
    Book_isbn = db.Column(db.Integer)
    Book_title = db.Column(db.String)
    Book_publication_year = db.Column(db.Integer)
    Book_cover_url = db.Column(db.String)
    Book_rating = db.Column(db.Integer)
    Author_id = db.Column(db.Integer, db.ForeignKey('author.Author_id'), nullable=False)

    def __repr__(self):
        return f"<Book(id={self.Book_id}, title='{self.Book_title}', rating={self.Book_rating})>"
