import os
import requests, json

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

os.environ['DATABASE_URL']='postgres://vwzakfsxqwyeor:1918223b661965c1a6b1967f93bf879dee2f458d249c6c9ccb9ec6d179c7f31a@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d7l23edpbnjkl3'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Home page for login or register
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["POST"])
def login():
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    userCheck = db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username":username, "password":password}).fetchone()
    if userCheck == None:
        return render_template("error.html", message ="such user does not exist or invalid username and/or password")
    else:
        user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username":username})
        result = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]
        return render_template("search.html")

@app.route("/register", methods = ["POST"])
def register():
    session.clear()
    username = request.form.get("username")
    password = request.form.get("password")
    userCheck = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if userCheck:
        return render_template("error.html", message ="Such username is already taken")
    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username":username, "password":password})
        db.commit()
    return render_template("success.html", message="Now you are registered and you can log in")

# Search a book
@app.route("/search", methods = ["POST", "GET"])
def search():
    return render_template("search.html")

# Found books
@app.route("/books", methods = ["POST"])
def books():
    quest = request.form.get("quest")
    # Search all required books
    quest = "%" + quest + "%"
    books = db.execute("SELECT * FROM books WHERE author LIKE :quest OR title LIKE :quest OR isbn LIKE :quest LIMIT 20", {"quest": quest}).fetchall()
    if books is None:
       return render_template("error.html", message="No such book.")
    return render_template("books.html", books=books)

# Info about book and review, grade
@app.route("/books/<int:book_id>")
def book(book_id):
    """Lists details about a single book."""
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
    # Get all reviews.
    reviews = db.execute("SELECT review, grade FROM reviews WHERE books_id = :book_id", {"book_id": book_id}).fetchall()
    return render_template("book.html", book=book, reviews=reviews)

# Insert review and grade in database
@app.route("/reviews", methods = ["POST"])
def reviews():
    review = request.form.get("bookReview")
    bookRange = request.form.get("bookRange")
    book_id = request.form.get("book_id")
# If no review
    if review is "":
        return render_template("error.html", message="You have not submited a review about this book.")

# Users should not be able to submit multiple reviews for the same book.
    reviewCheck = db.execute("SELECT * FROM reviews WHERE books_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id": session["user_id"]}).fetchone()
    if reviewCheck:
        return render_template("error.html", message="You have already submited a review about this book.")
    db.execute("INSERT INTO reviews (review, grade, books_id, user_id) VALUES (:review, :grade, :books_id, :user_id)", {"review": review, "grade": bookRange, "books_id": book_id, "user_id": session["user_id"]})
    db.commit()
    return render_template("success.html", message="Your review has been saved")

@app.route("/goodread", methods = ["GET"])
def goodread():
    isbn = input("ISBN of book: ")
    res = requests.get("https://www.goodreads.com/book/isbn/ISBN?format=json", params={"isbn": isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    return jsonify(data)

@app.route("/logout")
def logout():
    # Forget any user ID
    session.clear()
    # Redirect user to login form
    return render_template("index.html")



