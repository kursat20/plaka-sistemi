from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Session için gerekli

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Basit kullanıcı verisi (demo)
USERS = {
    "kursat": {"password": "1234"}
}

# Ana sayfa
@app.route("/")
def home():
    if "name" in session:
        return render_template("home.html", name=session["name"])
    return redirect(url_for("login"))

# Login sayfası
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = USERS.get(username.lower())
        if user and user["password"] == password:
            session["name"] = username.capitalize()
            return redirect(url_for("home"))
        return "Kullanıcı adı veya şifre yanlış!"
    return render_template("login.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect(url_for("login"))

# Banka sayfası
@app.route("/banka")
def banka():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("odeme.html")

# Kamera sayfası
@app.route("/kamera")
def kamera():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("kamera.html")

# Araçlar sayfası
@app.route("/araclar")
def araclar():
    if "name" not in session:
        return redirect(url_for("login"))
    # Örnek: araç listesi
    arac_listesi = ["Arac 1", "Arac 2", "Arac 3"]
    return render_template("dashboard.html", araclar=arac_listesi)

# Ödeme başarılı sayfası
@app.route("/odeme_basarili")
def odeme_basarili():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("odeme_basarili.html")

# Admin sayfası
@app.route("/admin")
def admin():
    if "name" not in session or session["name"].lower() != "admin":
        return redirect(url_for("login"))
    return render_template("admin.html")

# Kullanıcı doğrulama
@app.route("/dogrula")
def dogrula():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("dogrula.html")

# Register sayfası
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username.lower() in USERS:
            return "Kullanıcı zaten kayıtlı!"
        USERS[username.lower()] = {"password": password}
        return redirect(url_for("login"))
    return render_template("register.html")

# Sonuç sayfası
@app.route("/sonuc")
def sonuc():
    if "name" not in session:
        return redirect(url_for("login"))
    return render_template("sonuc.html")

# Çalıştırma
if _name_ == "__main__":
    app.run(debug=True)
