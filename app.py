import os
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

def run_web():
    app.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    # Lance le serveur web
    Thread(target=run_web, daemon=True).start()
    # Tu peux laisser ton code bot ici normalement...
