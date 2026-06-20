import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Petit serveur web pour rendre Render "heureux" (Hébergement gratuit)
app = Flask(__name__)

@app.route('/')
def home():
    return "Le robot est en ligne !"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# Lancement du serveur web en arrière-plan
Thread(target=run_web).start()

# 2. Configuration du bot Telegram
TOKEN = os.environ.get("TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Récupère le nom du jeu envoyé par ta Web App
    game_name = update.effective_message.web_app_data.data
    
    # Message de réponse automatique
    await update.message.reply_text(f"🚀 Analyse en cours pour : {game_name}...\n\n✅ Signal : 2.45x")

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré !")
    else:
        # Initialisation du bot
        bot_app = ApplicationBuilder().token(TOKEN).build()
        
        # Ce filtre écoute les clics provenant de ta Mini App
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot est en ligne et prêt à recevoir les signaux !")
        bot_app.run_polling()
