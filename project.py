import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, Markup
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from Levenshtein import distance
from random import sample, choice
import string

from help_functions import apology, login_required, emojify


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["emojify"] = emojify

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cards.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/dashboard")
@login_required
def dashboard():
    # show dashboard with all the sets of cards, possibly search function for public sets
    decks = db.execute("SELECT name FROM sets WHERE user_id = ?", session["user_id"])
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    return render_template("dashboard.html", decks=decks, username=username)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        if not request.form.get("password"):
            return apology("must provide password", 403)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username / password", 403)
        session["user_id"] = rows[0]["id"]
        return redirect("/dashboard")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username")
        if len(db.execute("SELECT * FROM users WHERE username = ?", username)) != 0:
            return apology("username taken")
        if not password or not confirmation:
            return apology("must provide password and confirm")
        if password != confirmation:
            return apology("password and confirmation do not match")
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))
        return redirect("/dashboard")
    else:
        return render_template("register.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    sets = db.execute("SELECT name FROM sets WHERE user_id = ?", session["user_id"])
    if request.method == "POST":
        key = request.form.get("key").strip()
        value = request.form.get("value").strip()
        set = request.form.get("set")
        if not key or not value or not set:
            return apology("must provide both sides of flashcard and stack", 403)
        # check for duplicate
        set_id = db.execute("SELECT id FROM sets WHERE name = ? AND user_id = ?", set, session["user_id"])[0]["id"]
        lookup_key = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND key = ?", session["user_id"], set_id, key)
        if len(lookup_key) != 0:
            flash("Card already exists!")
        else:
            db.execute("INSERT INTO cards (user_id, set_id, key, value) VALUES (?, ?, ?, ?)", session["user_id"], set_id, key, value)
            flash("Flashcard was added to your deck!")
    return render_template("add.html", sets=sets)


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    if request.method == "POST":
        user_solution = request.form.get("value").strip()
        # check solution with Levenshtein
        solution = db.execute("SELECT key, value, shelf FROM cards WHERE id = ?", session["card_id"])[0]
        dist = distance(user_solution, solution["value"], score_cutoff=1)
        if dist <= 1:
            if solution["shelf"] < 7:
                shelf_new = solution["shelf"] + 1
                db.execute("UPDATE cards SET shelf = ? WHERE id = ?", shelf_new, session["card_id"])
            if dist == 0:
                return render_template("quiz_solution.html", result="correct! :partying_face:", card=solution)
            else:
                return render_template("quiz_solution.html", result="almost correct! (Watch your spelling :nerd_face:)", card=solution)
        else:
            if solution["shelf"] >= 1:
                shelf_new = solution["shelf"] - 1
                db.execute("UPDATE cards SET shelf = ? WHERE id = ?", shelf_new, session["card_id"])
            return render_template("quiz_solution.html", result="wrong, keep studying :brain:", card=solution)

    else:
        cards_0 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 0", session["user_id"], session["set_id"])
        cards_1 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 1", session["user_id"], session["set_id"])
        cards_2 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 2", session["user_id"], session["set_id"])
        cards_3 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 3", session["user_id"], session["set_id"])
        cards_4 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 4", session["user_id"], session["set_id"])
        cards_5 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 5", session["user_id"], session["set_id"])
        cards_6 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 6", session["user_id"], session["set_id"])
        cards_7 = db.execute("SELECT * FROM cards WHERE user_id = ? AND set_id = ? AND shelf = 7", session["user_id"], session["set_id"])
        pre_shelves = [cards_0, cards_1, cards_2, cards_3, cards_4, cards_5, cards_6, cards_7]
        pre_weights = [8, 7, 6, 5, 4, 3, 2, 1]
        shelves = []
        weights = []
        for i in range(8):
            if len(pre_shelves[i]) != 0:
                shelves.append(pre_shelves[i])
                weights.append(pre_weights[i])
        if len(shelves) == 0:
            flash("Add some cards to this deck first!")
            return redirect("/add")
        else:
            chosen_shelf = sample(shelves, counts=weights, k=1)[0]
            chosen_card = choice(chosen_shelf)
            session["card_id"] = chosen_card["id"]
            return render_template("quiz.html", chosen_card=chosen_card)



@app.route("/pre_quiz", methods=["GET", "POST"])
@login_required
def pre_quiz():
    sets = db.execute("SELECT name FROM sets WHERE user_id = ?", session["user_id"])
    if request.method == "POST":
        set = request.form.get("set")
        if not set:
            flash("Please select deck")
            return render_template("pre_quiz.html", sets=sets)
        session["set_id"] = db.execute("SELECT id FROM sets WHERE user_id = ? AND name = ?", session["user_id"], set)[0]["id"]
        return redirect("/quiz")
    else:
        return render_template("pre_quiz.html", sets=sets)

@app.route("/quiz_solution")
@login_required
def quiz_solution():
    return render_template("quiz_solution.html")


@app.route("/add_deck", methods=["GET", "POST"])
@login_required
def add_deck():
    if request.method == "POST":
        set = request.form.get("deck")
        if not set:
            return apology("Missing deck name", 403)
        set_lookup = db.execute("SELECT * FROM sets WHERE name = ? AND user_id = ?", set, session["user_id"])
        if len(set_lookup) != 0:
            flash("A deck with this name already exists in your collection, please choose a different name")
        else:
            db.execute("INSERT INTO sets (user_id, name) VALUES (?, ?)", session["user_id"], set)
            flash("New deck was added to your collection!")
        return render_template("add_deck.html")
    else:
        return render_template("add_deck.html")