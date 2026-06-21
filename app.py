import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_ID = "5724620019" # Ton ID Admin
WEBAPP_URL = "https://ton-app.onrender.com"

client = MongoClient(MONGO_URI)
db = client['plateforme_db']
users_col = db['users'] 

# --- FONCTION CLAVIER ---
def get_keyboard(is_vip):
    if is_vip:
        return ReplyKeyboardMarkup([[KeyboardButton("🎮 GAME HACK", web_app=WebAppInfo(url=WEBAPP_URL))]], resize_keyboard=True)
    return ReplyKeyboardMarkup([[KeyboardButton("📝 Envoyer ID Joueur")]], resize_keyboard=True)

# --- SERVEUR WEB ---
@app.route('/')
def home(): return render_template('index.html')

@app.route('/verifier-vip', methods=['POST'])
def verifier_vip():
    data = request.json
    player_id = str(data.get('player_id'))
    # Recherche dans la base de données
    user = users_col.find_one({"player_id": player_id})
    if user and user.get('is_vip'):
        return jsonify({"status": "VIP"}), 200
    return jsonify({"status": "NON_VIP"}), 403

def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web, daemon=True).start()

# --- BOT TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = users_col.find_one({"telegram_id": user_id})
    is_vip = user.get('is_vip', False) if user else False
    
    await update.message.reply_text("👋 Bienvenue ! Si vous êtes VIP, le bouton apparaîtra.", reply_markup=get_keyboard(is_vip))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Inconnu"

    if text.isdigit() and len(text) > 5:
        # Stocke l'ID joueur
        users_col.update_one({"telegram_id": user_id}, {"$set": {"player_id": text, "is_vip": False}}, upsert=True)
        
        # --- CORRECTION : ENVOI À L'ADMIN ---
        await context.bot.send_message(
            chat_id=ADMIN_ID, 
            text=f"🔔 **Nouvelle demande**\n👤 @{username}\n🆔 ID : `{text}`\n\nPour valider : `/valider {user_id}`"
        )
        await update.message.reply_text("✅ ID reçu ! L'administrateur a été notifié.")

async def valider(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID and context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}})
        
        # --- RECONNAISSANCE AUTO ---
        await context.bot.send_message(
            chat_id=target_id, 
            text="🎉 **Félicitations !** Votre accès VIP est activé. Appuyez sur le menu.", 
            reply_markup=get_keyboard(True)
        )

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT, handle_message))
    bot_app.run_polling()
