import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Serveur Flask pour garder le bot en vie sur Render
app = Flask(__name__)
@app.route('/')
def home(): return "Le robot est en ligne !"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

# 2. Configuration du bot
TOKEN = os.environ.get("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# C'est ici que le bot reçoit le nom du jeu envoyé par ton index.html
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.effective_message.web_app_data.data
    # Réponse du bot quand il reçoit le signal
    await update.message.reply_text(f"🚀 Analyse en cours pour : {game_name}...\n\n✅ Signal : 2.45x")

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré !")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        
        # Filtre crucial qui détecte quand tu cliques sur ton interface
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot est en ligne et prêt à recevoir les signaux !")
        bot_app.run_polling()
