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
app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['plateforme_db']
users_col = db['users'] 

# --- SERVEUR WEB ---
@app.route('/')
def home(): 
    return render_template('index.html')

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
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue ! Entrez le code d'activation (ex: COK225) pour commencer.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    # 1. Vérification du code d'activation
    if text == "COK225":
        context.user_data['waiting_for_id'] = True
        await update.message.reply_text("✅ Code valide ! Maintenant, envoyez-moi votre ID de joueur pour terminer l'inscription.")
    
    # 2. Enregistrement de l'ID après le code
    elif context.user_data.get('waiting_for_id'):
        player_id = text
        users_col.update_one(
            {"player_id": player_id}, 
            {"$set": {"is_vip": True, "telegram_id": user_id}}, 
            upsert=True
        )
        context.user_data['waiting_for_id'] = False
        await update.message.reply_text("🎉 Inscription réussie ! Vous êtes maintenant VIP.")
    
    else:
        await update.message.reply_text("Envoyez 'COK225' pour commencer votre inscription.")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # La logique de signal reste inchangée
    game_name = update.effective_message.web_app_data.data
    await update.message.reply_text(f"✅ **Signal {game_name}**\n\n🎯 **Cote : {round(random.uniform(1.5, 12.5), 2)}x**")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    bot_app.run_polling()
