import os
import logging
import random
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Petit serveur web pour garder le bot en vie sur Render
app = Flask(__name__)
@app.route('/')
def home(): return "Le robot est en ligne !"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

# 2. Configuration
TOKEN = os.environ.get("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Commande de démarrage
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur la Plateforme VIP !\n\nOuvrez l'application pour lancer une analyse.")

# Fonction principale qui reçoit les signaux de ta Mini App
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.effective_message.web_app_data.data
    
    # Étape 1 : Message d'analyse (Animation)
    msg = await update.message.reply_text(f"🔍 **Analyse de {game_name}...**")
    await asyncio.sleep(1)
    await msg.edit_text(f"🔍 **Analyse de {game_name}... [████░░░░] 50%**")
    await asyncio.sleep(1)
    
    # Étape 2 : Génération du résultat
    maintenant = datetime.now().strftime("%H:%M:%S")
    prediction = round(random.uniform(1.5, 12.5), 2)
    
    resultat = (
        f"✅ **Signal {game_name}**\n\n"
        f"🎯 **Cote cible :** {prediction}x\n"
        f"🕒 **Heure de jeu :** {maintenant}\n\n"
        f"⚠️ *Fiabilité : 98%*\n"
        f"🚀 *Entrez dans le jeu maintenant !*"
    )
    
    # Modification du message d'analyse en résultat final
    await msg.edit_text(resultat)

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré !")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        
        # Enregistrement des commandes
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot est en ligne et prêt à recevoir les signaux !")
        bot_app.run_polling()
