from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3


app = Flask(__name__)
DB_FILE = "books_list.db"


def execute_query(query, parameters=None, fetchall=False):
    with sqlite3.connect(DB_FILE) as db:
        cursor = db.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        db.commit()
        return cursor.fetchall() if fetchall else None


@app.route('/')
def home():
    # Reading books from db
    sql_query2 = "SELECT * FROM books"
    data = execute_query(sql_query2, fetchall=True)
    return render_template('index.html', data=data)


@app.route("/delete", methods=["GET", "POST"])
def delete():
    # Delete book from db
    if request.method == "POST":
        book_id = request.form["id"]
        sql_query = "DELETE FROM books WHERE id = ?"
        execute_query(sql_query, (book_id,))
        return redirect(url_for('home'))

    book_id = request.args.get('id')
    sql_query2 = "SELECT * FROM books WHERE Id = ?"
    selected_book = execute_query(sql_query2, (book_id,), fetchall=True)
    return render_template("delete.html", book=selected_book)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        # UPDATE RECORD
        new_rating = request.form.get('rating')
        book_id = request.form.get("id")
        # Check if rating is valid number
        try:
            rating_float = float(new_rating)
            if rating_float > 10:
                abort(400, "Error: Rating must be between 0-10")
        except ValueError:
            abort(400, "Error: Rating must be valid number")
            # Update book rating
        sql_query = "UPDATE books SET Rating = ? WHERE Id = ?"
        execute_query(sql_query, parameters=[new_rating, book_id], fetchall=True)
        return redirect(url_for('home'))
    # Shows a book details
    book_id2 = request.args.get('id')
    sql_query2 = "SELECT * FROM books WHERE Id = ?"
    selected_book = execute_query(sql_query2, (book_id2,), fetchall=True)
    return render_template("edit.html", book=selected_book)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_book = {
            "title": request.form["title"],
            "author": request.form["author"],
            "rating": request.form["rating"]}
        try:
            rating = float(request.form["rating"])
        except ValueError:
            error = "Rating must be a valid number"
            return render_template('add.html', error=error)

        if rating > 10 or rating == "":
            error = "Rating must be between 0-10"
            return render_template('add.html', error=error)
        elif request.form["title"] == "":
            error = "Title field is empty"
            return render_template('add.html', error=error)
        elif request.form["author"] == "":
            error = "Author field is empty"
            return render_template('add.html', error=error)
        else:
            sql_query = "INSERT INTO books (title, author, rating) VALUES (?, ?, ?)"
            execute_query(sql_query, parameters=[new_book["title"], new_book["author"], new_book["rating"]])
            return redirect(url_for("home"))
    return render_template('add.html')


if __name__ == "__main__":
    app.run(debug=True)
