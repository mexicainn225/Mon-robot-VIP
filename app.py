import os
import logging
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CONFIGURATION ---
# Assure-toi que le dossier 'templates' existe et contient 'index.html'
app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")

# --- SERVEUR WEB ---
@app.route('/')
def home():
    return render_template('index.html')

def run_web():
    # Render attribue dynamiquement un port, il faut le récupérer
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT TELEGRAM ---
async def start(update, context):
    await update.message.reply_text("🚀 Bienvenue sur la plateforme ! Cliquez sur le bouton pour accéder aux signaux.")

if __name__ == '__main__':
    # Lancement du serveur web en arrière-plan
    Thread(target=run_web, daemon=True).start()
    
    # Vérification que le TOKEN est bien présent
    if not TOKEN:
        logging.error("Le TOKEN Telegram est manquant dans les variables d'environnement.")
    else:
        # Lancement du bot
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.run_polling()
