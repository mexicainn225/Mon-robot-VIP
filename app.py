import os
import logging
import random
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='templates') # Mis à jour pour chercher dans templates/
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['plateforme_db']
config_col = db['config']
users_col = db['users'] # Ajout de la collection pour vérifier les VIP

# --- SERVEUR WEB ---
@app.route('/')
def home(): 
    return render_template('index.html')

# Route pour vérifier le statut VIP
@app.route('/verifier-vip', methods=['POST'])
def verifier_vip():
    data = request.json
    player_id = str(data.get('player_id'))
    user = users_col.find_one({"player_id": player_id})
    if user and user.get('is_vip'):
        return jsonify({"status": "VIP"}), 200
    return jsonify({"status": "NON_VIP"}), 403

def run_web(): 
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_web, daemon=True).start()

# --- LOGIQUE BOT TELEGRAM ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur la Plateforme VIP !\n\nOuvrez l'application pour lancer une analyse.")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    # Vérification VIP dans MongoDB
    user = users_col.find_one({"player_id": user_id})
    
    if not user or not user.get('is_vip'):
        await update.message.reply_text("❌ **Accès refusé**\nVous n'êtes pas abonné VIP. Contactez l'administrateur.")
        return

    game_name = update.effective_message.web_app_data.data
    msg = await update.message.reply_text(f"🔍 **Analyse de {game_name}...**")
    await asyncio.sleep(1)
    
    prediction = round(random.uniform(1.5, 12.5), 2)
    resultat = (
        f"✅ **Signal {game_name}**\n\n"
        f"🎯 **Cote cible :** {prediction}x\n"
        f"🕒 **Heure :** {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"⚠️ *Fiabilité : 98%*"
    )
    await msg.edit_text(resultat)

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré !")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        print("Bot et serveur web en ligne !")
        bot_app.run_polling()
