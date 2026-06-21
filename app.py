import os
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

# Supprimé : la route /verifier-vip qui causait des erreurs 500

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    # Ici, ajoute le reste de ton code Telegram pour qu'ils tournent ensemble
