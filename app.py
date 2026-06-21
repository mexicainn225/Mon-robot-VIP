import os
import logging
from flask import Flask, request, jsonify, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from pymongo import MongoClient

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_ID = "5724620019"

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
    player_id = str(data.get('player_id', '')).strip()
    user = users_col.find_one({"player_id": player_id})
    if user and user.get('is_vip'):
        return jsonify({"status": "VIP"}), 200
    return jsonify({"status": "NON_VIP"}), 403

def run_web(): 
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

# --- LOGIQUE BOT TELEGRAM ---
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("🚀 Bienvenue ! Envoyez votre **ID Joueur** pour l'activation.")

async def handle_message(update, context):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Inconnu"

    if text.isdigit() and len(text) > 5:
        users_col.update_one({"telegram_id": user_id}, {"$set": {"player_id": text, "is_vip": False}}, upsert=True)
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 Demande d'activation : `{text}` par @{username}")
        await update.message.reply_text("⏳ Demande envoyée à l'admin.")

async def valider_joueur(update, context):
    if str(update.effective_user.id) != ADMIN_ID: return
    if context.args:
        target_id = context.args[0]
        users_col.update_one({"player_id": target_id}, {"$set": {"is_vip": True}})
        await update.message.reply_text(f"✅ ID {target_id} activé.")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider_joueur))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
