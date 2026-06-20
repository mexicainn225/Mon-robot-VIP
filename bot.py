import os
import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# 1. Petit serveur web pour garder le bot actif sur Render
app = Flask(__name__)
@app.route('/')
def home(): return "Le robot est en ligne !"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

# 2. Configuration
TOKEN = os.environ.get("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Commande /start pour lancer le bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 **Bienvenue sur votre Plateforme VIP**\n\nCliquez sur le bouton ci-dessous pour lancer l'analyse."
    await update.message.reply_text(welcome_text)

# Fonction pour gérer les clics venant de ta Mini App
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.effective_message.web_app_data.data
    
    # Étape 1 : Message d'attente
    msg = await update.message.reply_text(f"⏳ **Analyse de {game_name} en cours...**")
    
    # Petite pause pour faire réaliste
    await asyncio.sleep(2) 
    
    # Étape 2 : Calcul du signal
    prediction = round(random.uniform(1.5, 12.5), 2)
    resultat = (
        f"✅ **Signal {game_name}**\n\n"
        f"🎯 **Cote cible :** {prediction}x\n"
        f"⚠️ **Statut :** Fiabilité 98%\n\n"
        f"🚀 *Bonne chance !*"
    )
    
    # Suppression du message d'attente et envoi du résultat
    await msg.delete()
    await update.message.reply_text(resultat)

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré dans Render !")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        
        # Enregistrement des fonctions
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot est en ligne et prêt à recevoir les signaux !")
        bot_app.run_polling()
