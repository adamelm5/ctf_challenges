from flask import Flask, request, session, redirect, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hospital-ctf-secret-2025")

FLAG = "HOSPITAL{three_cves_one_attack_chain}"
PHASE1 = "N3T-7QX-29"
PHASE2 = "archive.hospital.local"
PHASE3 = "archive"

HTML = """
<!DOCTYPE html><html><head><title>Hospital Information System</title></head>
<body style="font-family:sans-serif;max-width:900px;margin:50px auto">
<h1>Hospital Information System</h1>
{% if state == 0 %}
  <p>Bienvenue sur le portail d'information hospitalier.</p>
  <ul>
    <li><a href="#">Portail patient</a></li>
    <li><a href="#">Informations medicales</a></li>
    <li><a href="#">Assistance technique</a></li>
    <li><a href="https://{{ host }}:8444">Espace personnel</a></li>
  </ul>
  <form method="POST" action="/submit/phase1">
    <input name="answer" placeholder="mot de passe SSH decouvert" style="width:400px">
    <button>Valider phase 1</button>
  </form>
  <p><em>Progression: 0 / 100</em></p>
{% elif state == 1 %}
  <p>Phase 1 validee (30 pts)</p>
  <p><strong>Phase 2 - Diagnostic DNS</strong></p>
  <p>SSH : <code>ssh netops@{{ host }} -p 2223</code></p>
  <form method="POST" action="/submit/phase2">
    <input name="answer" placeholder="hostname decouvert dans le core dump" style="width:400px">
    <button>Valider phase 2</button>
  </form>
  <p><em>Progression: 30 / 100</em></p>
{% elif state == 2 %}
  <p>Phase 2 validee (35 pts)</p>
  <p><strong>Phase 3 - Application archive</strong></p>
  <p>Application : <a href="http://{{ host }}:8082">http://{{ host }}:8082</a></p>
  <p>Identifiants : archive / (voir core dump)</p>
  <form method="POST" action="/submit/phase3">
    <input name="answer" placeholder="whoami output apres exploitation" style="width:400px">
    <button>Valider phase 3</button>
  </form>
  <p><em>Progression: 65 / 100</em></p>
{% elif state == 3 %}
  <p>Phase 3 validee (25 pts)</p>
  <p><strong>Phase 4 - Flag final</strong></p>
  <form method="POST" action="/submit/flag">
    <input name="answer" placeholder="HOSPITAL{...}" style="width:400px">
    <button>Soumettre le flag</button>
  </form>
  <p><em>Progression: 90 / 100</em></p>
{% elif state == 4 %}
  <h2>CHALLENGE COMPLETED</h2>
  <p>Score: 100 / 100</p>
{% endif %}
<hr>
<p style="text-align:center;color:#888">&copy; 2025 - Hospital Information System</p>
</body></html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, host=os.environ.get("HOST_IP", "127.0.0.1"),
                                  state=session.get("state", 0))

@app.route("/submit/phase1", methods=["POST"])
def p1():
    if session.get("state", 0) != 0: return redirect("/")
    if request.form.get("answer", "").strip() == PHASE1: session["state"] = 1
    return redirect("/")

@app.route("/submit/phase2", methods=["POST"])
def p2():
    if session.get("state", 0) != 1: return redirect("/")
    if request.form.get("answer", "").strip() == PHASE2: session["state"] = 2
    return redirect("/")

@app.route("/submit/phase3", methods=["POST"])
def p3():
    if session.get("state", 0) != 2: return redirect("/")
    if request.form.get("answer", "").strip() == PHASE3: session["state"] = 3
    return redirect("/")

@app.route("/submit/flag", methods=["POST"])
def pf():
    if session.get("state", 0) != 3: return redirect("/")
    if request.form.get("answer", "").strip() == FLAG: session["state"] = 4
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
