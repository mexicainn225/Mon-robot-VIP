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
ADMIN_ID = "5724620019" # Ton ID administrateur

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
    msg = (
        "🤖 **COMMENT BÉNÉFICIER DU BOT ?** ⤵️\n\n"
        "Condition obligatoire :\n"
        "➡️ 🟡 Être inscrit avec le code promo **COK225**\n"
        "🔗 https://lkbb.cc/78634e\n\n"
        "➡️ 🟡 RECHARGEZ VOTRE COMPTE ✔️\n\n"
        "➡️ 🟡 Envoyez votre **ID joueur** ici pour être confirmé ✅\n\n"
        "🔒 Signaux illimités avec le code promo COK225"
    )
    await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Inconnu"

    # Vérification si déjà VIP
    user = users_col.find_one({"telegram_id": user_id})
    if user and user.get('is_vip'):
        await update.message.reply_text("✅ Vous êtes déjà membre VIP ! Accédez à la Web App.")
        return

    # Processus d'inscription
    if text == "COK225":
        context.user_data['waiting_for_id'] = True
        await update.message.reply_text("✅ Code valide ! Envoyez-moi maintenant votre ID de joueur pour validation.")
    
    elif context.user_data.get('waiting_for_id') and text.isdigit():
        # Transférer la demande à l'admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 **Nouvelle demande de validation**\n👤 Utilisateur : @{username} (ID: {user_id})\n🆔 ID Joueur : `{text}`"
        )
        await update.message.reply_text("⏳ Demande envoyée à l'admin. Veuillez patienter pour la confirmation.")
        context.user_data['waiting_for_id'] = False
    else:
        await update.message.reply_text("❌ Envoyez 'COK225' pour commencer ou votre ID joueur pour validation.")

async def valider_joueur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID: return
    if context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}}, upsert=True)
        await update.message.reply_text(f"✅ Joueur {target_id} activé.")
        await context.bot.send_message(chat_id=target_id, text="🎉 Votre accès VIP est confirmé !")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider_joueur))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
