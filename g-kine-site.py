from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "g_kine_secret_change_moi_2026")
DB = "database.db"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Moustapha1")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rendez_vous
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL, tel TEXT NOT NULL,
                  service TEXT NOT NULL, date TEXT NOT NULL, heure TEXT NOT NULL,
                  message TEXT, statut TEXT DEFAULT 'En attente', date_creation TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT NOT NULL,
                  contenu TEXT NOT NULL, date TEXT)''')

    # Articles de démarrage
    if c.execute('SELECT COUNT(*) FROM posts').fetchone()[0] == 0:
        posts_de_base = [
            ("5 Exercices pour soulager le mal de dos à Bafoussam",
             "Le mal de dos touche beaucoup de personnes. Voici 5 étirements simples à faire chaque matin. Notre équipe de kiné à G KINÉ Bafoussam vous accompagne pour un programme personnalisé.",
             datetime.now().strftime("%d/%m/%Y")),
            ("Massage thérapeutique à Bafoussam : Pour qui?",
             "Le massage thérapeutique soulage les douleurs musculaires, le stress et aide à la récupération sportive. Chez G KINÉ nous faisons un bilan avant chaque séance.",
             datetime.now().strftime("%d/%m/%Y")),
            ("Bienvenue chez G KINÉ",
             "Centre de rééducation fonctionnelle et massage thérapeutique à Bafoussam. Prenez rendez-vous en ligne et bénéficiez de soins professionnels.",
             datetime.now().strftime("%d/%m/%Y"))
        ]
        c.executemany("INSERT INTO posts (titre,contenu,date) VALUES (?,?,?)", posts_de_base)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/rdv', methods=['POST'])
def rdv():
    data = request.form
    date_creation = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = get_db()
    conn.execute("INSERT INTO rendez_vous (nom,tel,service,date,heure,message,date_creation) VALUES (?,?,?,?,?,?,?)",
                 (data['nom'],data['tel'],data['service'],data['date'],data['heure'],data['message'],date_creation))
    conn.commit()
    conn.close()
    flash("Votre demande a bien été envoyée! Nous vous contactons sous 2h pour confirmer.", "success")
    return redirect(url_for('index') + '#rdv')

@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        else:
            flash("Mot de passe incorrect", "error")

    if 'admin' not in session:
        return render_template('login.html')

    conn = get_db()
    rdvs = conn.execute('SELECT * FROM rendez_vous ORDER BY date DESC, heure DESC').fetchall()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', rdvs=rdvs, posts=posts)

@app.route('/poster', methods=['POST'])
def poster():
    if 'admin' not in session: return redirect('/admin')
    data = request.form
    date = datetime.now().strftime("%d/%m/%Y")
    conn = get_db()
    conn.execute("INSERT INTO posts (titre,contenu,date) VALUES (?,?,?)", (data['titre'],data['contenu'],date))
    conn.commit()
    conn.close()
    flash("Article publié!", "success")
    return redirect('/admin')

@app.route('/valider_rdv/<int:id>')
def valider_rdv(id):
    if 'admin' not in session: return redirect('/admin')
    conn = get_db()
    conn.execute("UPDATE rendez_vous SET statut='Confirmé' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
