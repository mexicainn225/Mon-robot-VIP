import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
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
        "🚀 **BIENVENUE SUR SIGNAL MEXICAIN** 🇨🇮\n\n"
        "Envoyez votre **ID Joueur** pour validation."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    
    if text.isdigit() and len(text) > 5:
        users_col.update_one(
            {"telegram_id": user_id}, 
            {"$set": {"player_id": text, "is_vip": False}}, 
            upsert=True
        )
        await update.message.reply_text("⏳ Demande envoyée à l'administrateur.")
    else:
        await update.message.reply_text("❌ Format invalide. Envoyez votre ID joueur.")

async def valider_joueur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID: return
    if context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}})
        await update.message.reply_text(f"✅ Joueur {target_id} activé.")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider_joueur))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
