import os
import logging
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

# Configuration du logging pour suivre les erreurs dans les logs de Render
logging.basicConfig(level=logging.INFO)

# Initialisation de Flask
# Assure-toi d'avoir un dossier 'templates' avec 'index.html' à l'intérieur
app = Flask(__name__, template_folder='templates')

# Récupération du Token depuis les variables d'environnement de Render
TOKEN = os.environ.get("TOKEN")

# --- ROUTE WEB ---
@app.route('/')
def home():
    return render_template('index.html')

# Fonction pour démarrer le serveur web
def run_web():
    # Render définit automatiquement le port via une variable d'environnement
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- LOGIQUE BOT TELEGRAM ---
async def start(update, context):
    await update.message.reply_text(
        "🚀 **BIENVENUE SUR SIGNAL GAME** ✈️\n\n"
        "Cliquez sur le bouton ci-dessous pour accéder à vos signaux en direct."
    )

if __name__ == '__main__':
    # 1. Lancement du serveur Web en arrière-plan
    Thread(target=run_web, daemon=True).start()
    
    # 2. Lancement du Bot Telegram
    if not TOKEN:
        logging.error("Le TOKEN est manquant ! Vérifie tes variables d'environnement sur Render.")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        
        logging.info("Bot et Serveur lancés avec succès !")
        bot_app.run_polling()
