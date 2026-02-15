from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Veritabanı oluşturma
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                plate TEXT,
                password TEXT)""")
    conn.commit()
    conn.close()

init_db()

# Giriş kontrol decorator
def login_required(f):
    def wrap(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name, plate, password) VALUES (?, ?, ?)",
                  (name, plate, password))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE password=?", (password,))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = user[1]
            return redirect("/index")

    return render_template("login.html")

@app.route("/admin")
def admin_login():
    return "<h1>Admin Paneli</h1>"

@app.route("/index")
@login_required
def index():
    return render_template("index.html")

@app.route("/kamera")
@login_required
def kamera():
    return render_template("kamera.html")

@app.route("/odeme")
@login_required
def odeme():
    return "<h1>Ödeme Simülasyonu Başarılı ✅</h1>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

