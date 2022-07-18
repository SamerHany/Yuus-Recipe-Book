import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Query database for user and get balance
    rows = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

    # Query database for user and shares
    recipes = db.execute("SELECT * FROM users_recipes WHERE user_id = ?;", session['user_id'])

    for recipe in recipes:
        recipe['calories'] = int(recipe['calories'])

    # render user's portfolio
    return render_template("index.html", recipes=recipes)


@app.route("/recipe", methods=["GET", "POST"])
@login_required
def recipe():
    """Show recipe details or record a new recipe"""

    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("recipe_name"):
            return apology("must provide recipe name", 400)

        # check new recipe
        recipe_id = request.form.get('recipe_id')
        if not recipe_id:
            # insert a new recipe
            recipe_id = db.execute("INSERT INTO users_recipes (user_id, name, calories) VALUES(?, ?, ?);", session['user_id'], request.form.get('recipe_name'), request.form.get('calories'))

        else:
            # update recipe
            db.execute("UPDATE users_recipes SET name = ?, calories = ? WHERE recipe_id = ?;", request.form.get('recipe_name'), request.form.get('calories'), recipe_id)

            # delete old ingredients
            db.execute("DELETE FROM recipes WHERE recipe_id = ?;", recipe_id)

        # insert ingredients
        for i in range(1, int(request.form.get('ingredients_count')) + 1):
            db.execute('INSERT INTO recipes (recipe_id, ingredient_id, qty) VALUES (?, ?, ?);', recipe_id, request.form.get(f'ingredient_id_{i}'), request.form.get(f'ingredient_qty_{i}'))

        # redirect user to home page
        return redirect("/")

    else:
        # get recipe
        recipe_id = request.args.get('id')

        # get ingredients
        ingredients = db.execute("SELECT * FROM ingredients;")

        # Get recipe details
        if recipe_id != None:
            recipes = db.execute("SELECT * FROM users_recipes WHERE recipe_id = ?;", recipe_id)
            recipe = recipes[0]
            recipe['ingredients'] = db.execute("SELECT ingredients.id, ingredients.name, recipes.qty, ingredients.calories FROM recipes JOIN ingredients ON ingredients.id = recipes.ingredient_id WHERE recipes.recipe_id = ?", recipe_id)

            for ingredient in recipe['ingredients']:
                ingredient['calories'] = int(ingredient['calories'] * ingredient['qty'])
                ingredient['qty'] = int(ingredient['qty'])

        else:
            recipe = {
                'id': '',
                'name': '',
                'ingredients': '',
            }

        print(recipe)

        return render_template("recipe.html", recipe=recipe, ingredients=ingredients)


@app.route("/delete", methods=["GET"])
@login_required
def delete():
    """Delete recipe details or record a new recipe"""

    # Ensure symbol was submitted
    if not request.args.get("id"):
        return apology("must provide recipe ID", 400)

    # check new recipe
    recipe_id = request.args.get('id')

    # delete recipe
    db.execute("DELETE FROM users_recipes WHERE recipe_id = ?;", recipe_id)

    # delete recipe ingredients
    db.execute("DELETE FROM recipes WHERE recipe_id = ?;", recipe_id)

    # redirect user to home page
    return redirect("/")


@app.route("/ingredient", methods=["GET"])
def ingredient():
    """Get ingredient details from database"""

    # Ensure username was submitted
    if not request.args.get("id"):
        return apology("must provide ingredient ID", 403)


    # Query database for username
    rows = db.execute("SELECT * FROM ingredients WHERE id = ?", request.args.get("id"))

    # get ingredient details
    ing = rows[0]

    # Redirect user to home page
    return ing


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password was submitted
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            return apology("username already exists", 400)

        # Add the user's entry into the database
        db.execute('INSERT INTO users (username, hash) VALUES (?, ?);',
                   request.form.get('username'), generate_password_hash(request.form.get('password')))

        # Redirect user to home page
        return render_template("login.html")

    else:
        return render_template('register.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)
