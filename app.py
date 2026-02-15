from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

app = Flask(__name__)
app.secret_key = "secretkey"

# DATABASE
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        plate TEXT,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS fines(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT,
        amount INTEGER,
        status TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# Giriş kontrol
def login_required():
    if "user_id" not in session:
        return False
    return True

@app.route("/")
def home():
    if not login_required():
        return redirect("/login")
    return redirect("/dashboard")

# KAYIT
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (name, plate, password) VALUES (?,?,?)",
                  (name, plate, password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# GİRİŞ
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE password=?", (password,))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["plate"] = user[2]
            return redirect("/dashboard")
    return render_template("login.html")

# ADMIN GİRİŞ
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin_panel")
    return render_template("admin_login.html")

@app.route("/admin_panel")
def admin_panel():
    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    return render_template("admin_panel.html", users=users)

@app.route("/delete/<int:user_id>")
def delete(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect("/admin_panel")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")
    now = datetime.datetime.now()
    return render_template("dashboard.html", now=now)

# ARAÇLARIM / CEZA SORGULAMA
@app.route("/araclarim")
def araclarim():
    if not login_required():
        return redirect("/login")

    plate = session["plate"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM fines WHERE plate=?", (plate,))
    fines = c.fetchall()
    conn.close()

    return render_template("araclarim.html", fines=fines)

# ÖDEME
@app.route("/pay/<int:fine_id>")
def pay(fine_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE fines SET status='Paid' WHERE id=?", (fine_id,))
    conn.commit()
    conn.close()
    return redirect("/araclarim")

# PDF MAKBUL
@app.route("/receipt/<int:fine_id>")
def receipt(fine_id):
    file = "receipt.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)

    elements = []

    style_big = ParagraphStyle(name="Big", fontSize=24, textColor=colors.black)
    style_stamp = ParagraphStyle(name="Stamp", fontSize=50, textColor=colors.red)

    elements.append(Paragraph("CEZA MAKBUZU", style_big))
    elements.append(Spacer(1,20))

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM fines WHERE id=?", (fine_id,))
    fine = c.fetchone()
    conn.close()

    elements.append(Paragraph(f"Tutar: {fine[2]} TL", style_big))
    elements.append(Spacer(1,20))

    if fine[3] == "Paid":
        elements.append(Paragraph("ÖDENDİ", style_stamp))

    doc.build(elements)
    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
