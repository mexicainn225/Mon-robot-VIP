import os
import logging
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

# Configuration des logs pour voir l'erreur dans Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='.')

@app.route('/')
def home():
    return render_template('index.html')

def run_web():
    try:
        port = int(os.environ.get("PORT", 10000))
        logger.info(f"Démarrage du serveur web sur le port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Erreur serveur web : {e}")

async def start(update, context):
    await update.message.reply_text("Bienvenue ! Accédez aux signaux via le bouton.")

if __name__ == '__main__':
    TOKEN = os.environ.get("TOKEN")
    if not TOKEN:
        logger.error("ERREUR : La variable d'environnement 'TOKEN' est manquante !")
        exit(1)

    # Lancer le serveur web
    Thread(target=run_web, daemon=True).start()
    
    # Lancer le bot
    logger.info("Démarrage du bot Telegram...")
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()
