from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.secret_key = "gizlisifre"

# Sahte ceza verisi
cezalar = {"34ABC01": 100, "06XYZ99": 250}
ADMIN_PASSWORD = "2055"

# Ana sayfa
@app.route('/', methods=['GET', 'POST'])
def index():
    ceza = None
    plaka = None
    if request.method == 'POST':
        plaka = request.form.get('plaka').upper()
        ceza = cezalar.get(plaka, 0)
    return render_template('index.html', plaka=plaka, ceza=ceza)

# Ödeme tamamla - ceza sıfırlanıyor
@app.route('/odeme_tamamla/<plaka>')
def odeme_tamamla(plaka):
    if plaka in cezalar:
        cezalar[plaka] = 0
    return redirect(url_for('index'))

# PDF makbuz
@app.route('/pdf/<plaka>')
def pdf(plaka):
    ceza = cezalar.get(plaka, 0)
    pdf_dosya = f"static/ceza_fotolari/{plaka}_ceza.pdf"
    os.makedirs("static/ceza_fotolari", exist_ok=True)
    c = canvas.Canvas(pdf_dosya)
    c.drawString(100, 750, f"Plaka: {plaka}")
    c.drawString(100, 730, f"Ceza Tutarı: {ceza} TL")
    if ceza > 0:
        c.drawString(100, 710, "Durum: Ödenmedi")
    else:
        c.drawString(100, 710, "Durum: Ödendi")
    c.save()
    return send_file(pdf_dosya, as_attachment=True)

# Admin giriş
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        sifre = request.form.get('sifre')
        if sifre == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', hata="Hatalı şifre")
    return render_template('login.html')

# Admin paneli
@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template('admin.html', cezalar=cezalar)

# Ceza sil
@app.route('/sil/<plaka>')
def sil(plaka):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    cezalar.pop(plaka, None)
    return redirect(url_for('admin_panel'))

if __name__ == "__main__":
    os.makedirs("static/ceza_fotolari", exist_ok=True)
    app.run(debug=True)
