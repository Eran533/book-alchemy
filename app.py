from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

db_path = os.path.join(os.path.dirname(__file__), "data", "library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
db = SQLAlchemy(app)

class Author(db.Model):
    Author_id = db.Column(db.Integer, primary_key=True)
    Author_name = db.Column(db.String)
    Author_birth_date = db.Column(db.String)
    Author_date_of_death = db.Column(db.String)

    def __repr__(self):
        return f"<Author(id={self.Author_id}, name='{self.Author_name}')>"


class Book(db.Model):
    Book_id = db.Column(db.Integer, primary_key=True)
    Book_isbn = db.Column(db.Integer)
    Book_title = db.Column(db.String)
    Book_publication_year = db.Column(db.Integer)

    def __repr__(self):
        return f"<Book(id={self.Book_id}, title='{self.Book_title}')>"

@app.route('/add_author')
def add_author():
    return render_template('add_author.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
