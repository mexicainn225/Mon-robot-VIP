import os
import logging
import random
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# Serveur pour Render
app = Flask(__name__)
@app.route('/')
def home(): return "Le robot est en ligne !"
def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web).start()

TOKEN = os.environ.get("TOKEN")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.effective_message.web_app_data.data
    
    # Message d'attente
    msg = await update.message.reply_text(f"🔍 **Analyse de {game_name}...**")
    await asyncio.sleep(2) # Temps de calcul
    
    # Calculs
    maintenant = datetime.now().strftime("%H:%M:%S")
    prediction = round(random.uniform(1.5, 12.5), 2)
    
    resultat = (
        f"✅ **Signal {game_name}**\n\n"
        f"🎯 **Cote cible :** {prediction}x\n"
        f"🕒 **Heure de jeu :** {maintenant}\n\n"
        f"🚀 *Entrez maintenant !*"
    )
    
    await msg.delete()
    await update.message.reply_text(resultat)

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    bot_app.run_polling()
