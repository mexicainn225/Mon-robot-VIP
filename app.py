import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_ID = "5724620019"
WEBAPP_URL = "https://ton-app.onrender.com" 

client = MongoClient(MONGO_URI)
db = client['plateforme_db']
users_col = db['users'] 

def get_keyboard(is_vip):
    if is_vip:
        return ReplyKeyboardMarkup([[KeyboardButton("🎮 GAME HACK", web_app=WebAppInfo(url=WEBAPP_URL))]], resize_keyboard=True)
    return ReplyKeyboardMarkup([[KeyboardButton("📝 Envoyer ID Joueur")]], resize_keyboard=True)

@app.route('/')
def home(): return render_template('index.html')

@app.route('/verifier-vip', methods=['POST'])
def verifier_vip():
    data = request.json
    player_id = str(data.get('player_id'))
    user = users_col.find_one({"player_id": player_id})
    return jsonify({"status": "VIP" if user and user.get('is_vip') else "NON_VIP"}), 200 if user and user.get('is_vip') else 403

def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue ! Envoyez votre ID Joueur pour commencer.", reply_markup=get_keyboard(False))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    if text.isdigit() and len(text) > 5:
        users_col.update_one({"telegram_id": user_id}, {"$set": {"player_id": text, "is_vip": False}}, upsert=True)
        await update.message.reply_text("⏳ Demande envoyée à l'administrateur. Veuillez patienter.")
    else:
        await update.message.reply_text("❌ Envoyez un ID Joueur valide.")

async def valider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID and context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}})
        await context.bot.send_message(chat_id=target_id, text="🎉 Félicitations, votre accès est activé ! Rafraîchissez le menu.", reply_markup=get_keyboard(True))

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT, handle_message))
    bot_app.run_polling()
