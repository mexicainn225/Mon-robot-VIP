import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')
client = MongoClient(os.environ.get("MONGO_URI"))
db = client['plateforme_db']
users_col = db['users']

ADMIN_ID = "5724620019"
WEBAPP_URL = "https://mon-robot-vip-1.onrender.com" 

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
    user_id = str(update.effective_user.id)
    user = users_col.find_one({"telegram_id": user_id})
    is_vip = user.get('is_vip', False) if user else False
    await update.message.reply_text("🚀 BIENVENUE SUR SIGNAL MEXICAIN 🇨🇮\nEnvoyez votre ID Joueur.", reply_markup=get_keyboard(is_vip))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    if text.isdigit() and len(text) > 5:
        users_col.update_one({"telegram_id": user_id}, {"$set": {"player_id": text, "is_vip": False}}, upsert=True)
        keyboard = [[InlineKeyboardButton("✅ Confirmer", callback_data=f"val_{user_id}"), InlineKeyboardButton("❌ Refuser", callback_data=f"ref_{user_id}")]]
        await context.bot.send_message(ADMIN_ID, f"🔔 Nouvelle demande ID: `{text}`\nUser: {update.effective_user.username}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        await update.message.reply_text("⏳ Demande envoyée, patientez.")

async def button_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = data.split("_")[1]
    if data.startswith("val_"):
        users_col.update_one({"telegram_id": user_id}, {"$set": {"is_vip": True}})
        await query.edit_message_text(f"✅ Utilisateur {user_id} validé.")
        await context.bot.send_message(user_id, "🎉 Accès VIP activé !", reply_markup=get_keyboard(True))
    else:
        await query.edit_message_text(f"❌ Utilisateur {user_id} refusé.")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(os.environ.get("TOKEN")).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_query))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
