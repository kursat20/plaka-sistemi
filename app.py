from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
app.secret_key = "secretkey"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# --- DATABASE INIT ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        plate TEXT,
        password TEXT,
        card_no TEXT,
        cvv TEXT,
        expiry TEXT,
        balance INTEGER DEFAULT 0
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

# --- LOGIN REQUIRED ---
def login_required():
    return "user_id" in session

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- HOME / DASHBOARD ---
@app.route("/")
def index():
    if login_required():
        return redirect("/home")
    return render_template("index.html")

@app.route("/home")
def home():
    if not login_required():
        return redirect("/login")
    return render_template("home.html", name=session["name"])

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect("/login")
    return render_template("dashboard.html", name=session["name"])

# --- REGISTER ---
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        plate = request.form["plate"].upper()
        password = request.form["password"]

        allowed_plates = ["34ABC01","06DEF02","35GHI03","07JKL04","01MNO05",
                          "34PQR06","06STU07","35VWX08","07YZA09","01BCD10"]
        if plate not in allowed_plates:
            return render_template("sonuc.html", message="Geçersiz plaka!")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Random banka bilgileri
        card_no = str(100000000 + c.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        cvv = str(100 + c.execute("SELECT COUNT(*) FROM users").fetchone()[0])
        expiry = "12/26"

        c.execute("INSERT INTO users (name, plate, password, card_no, cvv, expiry) VALUES (?,?,?,?,?,?)",
                  (name, plate, password, card_no, cvv, expiry))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# --- LOGIN ---
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["name"] = user[1]
            session["plate"] = user[2]
            return redirect("/home")
        return render_template("sonuc.html", message="Hatalı giriş!")
    return render_template("login.html")

# --- ADMIN ---
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin_panel")
    return render_template("login.html")

@app.route("/admin_panel")
def admin_panel():
    if "admin" not in session:
        return redirect("/admin")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return render_template("admin.html", users=users)

@app.route("/delete/<int:user_id>")
def delete(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect("/admin_panel")

# --- ARAÇLARIM / CEZA ---
@app.route("/araclarim")
def araclarim():
    if not login_required():
        return redirect("/login")
    plate = session["plate"]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM fines WHERE plate=?", (plate,))
    fines = c.fetchall()
    conn.close()
    return render_template("araclarim.html", fines=fines)

@app.route("/pay/<int:fine_id>")
def pay(fine_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE fines SET status='Paid' WHERE id=?", (fine_id,))
    conn.commit()
    conn.close()
    return redirect("/araclarim")

@app.route("/receipt/<int:fine_id>")
def receipt(fine_id):
    file = "receipt.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)
    elements = []
    style_big = ParagraphStyle(name="Big", fontSize=24, textColor=colors.black)
    style_stamp = ParagraphStyle(name="Stamp", fontSize=50, textColor=colors.red)
    elements.append(Paragraph("CEZA MAKBUZU", style_big))
    elements.append(Spacer(1,20))

    conn = sqlite3.connect(DB_PATH)
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

# --- BANKA ---
@app.route("/banka", methods=["GET","POST"])
def banka():
    if not login_required():
        return redirect("/login")
    if request.method == "POST":
        card_no = request.form["card_no"]
        cvv = request.form["cvv"]
        expiry = request.form["expiry"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
        user = c.fetchone()
        conn.close()

        if (user[4]==card_no and user[5]==cvv and user[6]==expiry and user[3]==password):
            return render_template("odeme_basarili.html", amount="Bakiye kontrolü")
        else:
            return render_template("sonuc.html", message="Banka bilgileri hatalı!")
    return render_template("dogrula.html")

# --- KAMERA ---
@app.route("/kamera")
def kamera():
    if not login_required():
        return redirect("/login")
    return render_template("kamera.html")

if _name_ == "_main_":
    app.run(debug=True)




