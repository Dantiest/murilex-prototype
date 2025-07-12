import sqlite3
from flask import Blueprint, render_template, redirect, request, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        with sqlite3.connect("murilex.db") as connection:
            cursor = connection.cursor()
            try:

                if not username:
                    return ("must provide username", 403)

                if not password or not confirmation:
                    return ("must provide password and confirmation", 403)
                elif len(password) < 8:
                    return ("Password must be at least 8 characters long", 403)
                elif password != confirmation:
                    return ("Password does not match confirmation", 403)
                elif not any(char.isdigit() for char in password):
                    return ("Password must contain at least one digit", 403)
                elif not any(char.isalpha() for char in password):
                    return ("Password must contain at least one letter", 403)
                elif password.isalnum():
                    return ("Password must contain at least one special character", 403)

                rows = cursor.execute("SELECT * FROM user WHERE username = ?", (username,))

                if rows.fetchone() is not None:
                    return ("username already in use", 403)
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute("INSERT INTO user (username, hash) VALUES(?, ?)", (username, hashed_password))
                    connection.commit()

                    return redirect("/login")
            except Exception as error:
                connection.rollback()  # Rollback the transaction if there's an error
                raise error
    else:
        return render_template("register.html")

def login_required(view):
    @wraps(view)
    def protected_view(*args, **kwargs):
        if 'user_id' in session:
            return view(*args, **kwargs)
        else:
            # Print for debugging
            print("protected_view called")
            print("request.url:", request.url)

            # Store the requested URL in the session gimme your number
            session['next_url'] = request.url 
            return redirect("/login")
    return protected_view

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        connection = sqlite3.connect("murilex.db")
        cursor = connection.cursor()

        if not username:
            return ("must provide username", 403)
        if not password:
            return ("must provide password", 403)

        # Query database for username
        rows = cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user = rows.fetchone()
        connection.commit()

        # Ensure username exists and password is correct
        if user is None or not check_password_hash(user[3], password):
            return ("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user[0]
        session['username'] = user[1]
        session["profile_image"] = user[5]

        # Print for debugging
        print("next_url:", session.get('next_url', '/'))

        # Redirect user to the stored URL or home page if not stored
        next_url = session.get('next_url', '/')
        return redirect(next_url)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@auth_bp.route("/users")
def get_users():
    user_id = session.get('user_id')

    conn = sqlite3.connect("murilex.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,))
    users = cursor.fetchall()
    conn.close()

    # Convert the data to JSON and return it to the client
    user_data = [{"id": row[0], "username": row[1]} for row in users]
    print("User data:", user_data)  # Debugging print
    return jsonify(user_data)