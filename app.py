from flask import Flask, render_template, request

app = Flask(_name_)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sorgula", methods=["POST"])
def sorgula():
    plaka = request.form["plaka"].upper()

    if plaka == "01ADN01":
        ceza = "100 TL Ceza Var"
    else:
        ceza = "Ceza Yok"

    return render_template("sonuc.html", plaka=plaka, ceza=ceza)

@app.route("/kamera")
def kamera():
    return render_template("kamera.html")

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=3000)
