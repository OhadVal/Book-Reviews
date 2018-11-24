# Book-Reviews

This is a book reviews website.
Users are able to:
*Sign in/up
*Logout
*Search for books.
*Leave review for a book.
*See reviews made by other people.




### Prerequisites & Installing

After you clone this repository, there are several steps to do in order to use it.

1. PostgreSQL - if you don't have it yet, get it.

2. If you don't have Flask or SQLAlchemy installed, run the following from the terminal(in the project's folder):
```
pip3 install -r requirements.txt
```

3. Configure Flask and env:
```
export FLASK_ENV=development
export FLASK_APP=application.py
export DATABASE_URL=postgres://czxselkgpvbikt:bd37405781c1311f29d31d25700cfd0ab4de7d938846a88624ed328711468cd8@ec2-54-235-193-0.compute-1.amazonaws.com:5432/d6ieop4g81flub
```
4. Run ``` flask run ``` and you're good to go.




## Built With

* [Python's Flask](https://github.com/pallets/flask/) - The web framework used.
* [PostgreSQL](https://www.postgresql.org/) connected with [Heroku](http://heroku.com/) - Database.
* HTML5, CSS3(SCSS) - Frontend.
*[Goodreads API](https://www.goodreads.com/api/) - Get review statistics.




##API
There's a built in API you can use to fetch information.
How to use it:
Make a GET request to /api/<isbn> where isbn is the ISBN of the book and you will get a JSON.
Example for the JSON file:
```
{
  "Author":	"Harlan Coben",
  "Goodreads Rating":	"4.04",
  "ISBN":	"0752849190",
  "Reviews": [],
  "Title": "Darkest Fear",
  "Votes":	16355,
  "Year":	"1999"
 }
```
