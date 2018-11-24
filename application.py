import os
import requests
import json

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["POST"])
def login():
    # check the user in the database
    user_name = request.form.get("username")
    password = request.form.get("password")
    user = db.execute("SELECT FROM users WHERE username = :this_user AND password = :this_password",
                      {"this_user": user_name, "this_password": password}).fetchone()

    if 'myUser' in session:
        if user_name in session['myUser']:
            message = "Already logged in"
    else:
        if user is None:
            message = "Invalid username or password"
        else:
            session['myUser'] = user_name
            message = "Successfully logged in"
    return render_template("home.html", login_message=message)


@app.route("/registration", methods=["POST"])
def registration():
    # Get values from the form
    gender = request.form.get("gender")
    age = request.form.get("age")
    username = request.form.get("username")
    password = request.form.get("password")
    verifypassword = request.form.get("verifypassword")

    # Check form values:
    if(password == '' or username == ''):
        return render_template("home.html", reg_message="One or more values are missing")

    if(password != verifypassword):
        return render_template("home.html", reg_message="Passwords don't match")

    # Check if user exist
    is_okay = db.execute(
        "SELECT * FROM users where username= :username", {"username": username}).rowcount == 0
    if(is_okay):

        db.execute("INSERT INTO users (username,password,gender,age) VALUES (:username, :password, :gender, :age)", {
            "username": username, "password": password, "gender": gender, "age": age})
        db.commit()
    else:
        return render_template("home.html", reg_message="Username already exists")
    # Message if succeeded or failed.
    return render_template("home.html", reg_message="You have successfully registered. Welcome, you can now log in!")


@app.route("/logout")
def logout():
    if 'myUser' in session:
        session.clear()
        return render_template("home.html", message="You have disconnected")
    return render_template("home.html", message="It's highly recommended to login before you logout")


@app.route("/search", methods=["GET", "POST"])
def search():
    if 'myUser' in session:  # make user is logged in
        if request.method == "POST":
            session["books"] = []
            search = request.form.get('search')
            results = db.execute("SELECT * FROM books where isbn iLIKE'%"+search+"%' OR title iLIKE'%" +
                                 search+"%' OR author iLIKE'%"+search+"%' OR year iLIKE'%"+search+"%'")
            for result in results:
                session['books'].append(result)
            message = "There are %s  books matching your search:" % len(
                session['books'])
            return render_template("search.html", message=message, results=session['books'])
        else:
            return render_template("search.html")
    return render_template("home.html", message="Please sign in to continue.")


@app.route("/isbn/<string:isbn>", methods=["GET", "POST"])
def book_page(isbn):
    # make user is logged in
    if 'myUser' in session:
        # get books details from DB and goodreads
        book = db.execute(
            "SELECT * FROM books WHERE isbn= :isbn", {"isbn": isbn}).fetchone()
        username = session['myUser']
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "zXR2kKmTJ0tV9D3LG8ekug", "isbns": isbn})
        goodreads_rating = res.json()['books'][0]['average_rating']
        goodreads_num_of_ratings = res.json()['books'][0]['work_ratings_count']
        user_review = db.execute("SELECT * FROM reviews WHERE isbn= :isbn  AND username= :username", {
                                 "isbn": isbn, "username": username}).fetchone()
        review_message = ""
        if request.method == "POST":  # the user is trying to add a review
            if user_review == None:  # the user did not write a review about this book before
                # get the review and add it to DB
                review_text = request.form.get('review_text')
                review_rating = request.form.get('rating')
                db.execute("INSERT INTO reviews (isbn, review, rating, username) VALUES (:isbn, :review, :rating, :username)",
                           {"isbn": isbn, "review": review_text, "rating": review_rating, "username": username})
                db.commit()
                review_message = "Your review has been added!"

            else:
                review_message = "You can write one review per book."
        reviews_data = db.execute(
            "SELECT * FROM reviews WHERE isbn= :isbn", {"isbn": isbn}).fetchall()
        session['reviews'] = []
        for review in reviews_data:
            session['reviews'].append(review)
        return render_template("book_page.html", book=book, reviews=session['reviews'], goodreads_rating=goodreads_rating, goodreads_num_of_ratings=goodreads_num_of_ratings, review_message=review_message)

    else:
        return render_template("home.html", message="Please sign in to continue.")


@app.route("/api/isbn/<string:isbn>")
def book_api(isbn):
    """Return details about a book."""

    # make sure book exists
    book = db.execute("SELECT * FROM books WHERE isbn= :isbn",
                      {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"error": "Invalid flight_id"}), 422

    # get book details
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "zXR2kKmTJ0tV9D3LG8ekug", "isbns": isbn})
    goodreads_rating = res.json()['books'][0]['average_rating']
    goodreads_num_of_ratings = res.json()['books'][0]['work_ratings_count']
    reviews_data = db.execute(
            "SELECT * FROM reviews WHERE isbn= :isbn", {"isbn": isbn}).fetchall()
    reviews=[]
    for review in reviews_data:
        reviews.append(review.review)

    return jsonify({
        "ISBN": book.isbn,
        "Title": book.title,
        "Author": book.author,
        "Year": book.year,
        "Goodreads Rating": goodreads_rating,
        "Votes": goodreads_num_of_ratings,
        "Reviews": reviews
    })
