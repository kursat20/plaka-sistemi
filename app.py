from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, os, random, datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

app = Flask(__name__)
app.secret_key = "supersecret"
app.permanent_session_lifetime = datetime.timedelta(minutes=10)

BASE_DIR = os.path.dirname(os.path.abspath(_file_))
DB = os.path.join(BASE_DIR, "database.db")

ALLOWED_PLATES = [
"34ABC01","34ABC02","34ABC03","34ABC04","34ABC05",
"06XYZ01","06XYZ02","35IZM01","16BUR01","07ANT01"
]

def connect():
    return sqlite3.connect(DB)

def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        plate TEXT,
        password TEXT,
        card TEXT,
        cvv TEXT,
        expiry TEXT,
        balance INTEGER
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

def generate_card():
    card = str(random.randint(100000000,999999999))
    cvv = str(random.randint(100,999))
    expiry = f"{random.randint(1,12):02d}/{random.randint(26,30)}"
    return card, cvv, expiry

def login_required():
    return "user_id" in session

@app.route("/")
def home():
    if not login_required():
        return redirect("/login")
    return render_template("home.html", name=session["name"])

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form["name"]
        plate = request.form["plate"]
        password = request.form["password"]

        if plate not in ALLOWED_PLATES:
            return "Plaka sistemde kayıtlı değil!"

        card, cvv, expiry = generate_card()

        conn = connect()
        c = conn.cursor()
        c.execute("INSERT INTO users (name,plate,password,card,cvv,expiry,balance) VALUES (?,?,?,?,?,?,?)",
                  (name,plate,password,card,cvv,expiry,1000))
        conn.commit()
        conn.close()

        return f"""
        Kayıt başarılı!<br>
        Kart No: {card}<br>
        CVV: {cvv}<br>
        Son Kullanma: {expiry}<br>
        <a href='/login'>Giriş Yap</a>
        """

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        password = request.form["password"]
        conn = connect()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE password=?", (password,))
        user = c.fetchone()
        conn.close()

        if user:
            session.permanent=True
            session["user_id"]=user[0]
            session["name"]=user[1]
            session["plate"]=user[2]
            return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/araclarim")
def araclarim():
    if not login_required():
        return redirect("/login")

    conn=connect()
    c=conn.cursor()
    c.execute("SELECT * FROM fines WHERE plate=?", (session["plate"],))
    fines=c.fetchall()
    conn.close()

    return render_template("araclarim.html", fines=fines)

@app.route("/pay/<int:id>", methods=["POST"])
def pay(id):
    if not login_required():
        return redirect("/login")

    card=request.form["card"]
    cvv=request.form["cvv"]
    expiry=request.form["expiry"]
    password=request.form["password"]

    conn=connect()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE id=?", (session["user_id"],))
    user=c.fetchone()

    if user[4]==card and user[5]==cvv and user[6]==expiry and user[3]==password:
        c.execute("SELECT amount FROM fines WHERE id=?", (id,))
        fine=c.fetchone()
        if user[7]>=fine[0]:
            new_balance=user[7]-fine[0]
            c.execute("UPDATE users SET balance=? WHERE id=?", (new_balance,user[0]))
            c.execute("UPDATE fines SET status='Paid' WHERE id=?", (id,))
            conn.commit()
            conn.close()
            return redirect("/araclarim")

    conn.close()
    return "Banka doğrulama"


