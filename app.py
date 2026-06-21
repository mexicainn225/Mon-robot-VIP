import os
import logging
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='templates')

# Lecture du TOKEN et de MONGO_URI depuis les variables d'environnement
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_ID = "5724620019"

# Vérification de sécurité du Token
if not TOKEN:
    raise ValueError("Le token Telegram n'est pas défini. Vérifie ta variable d'environnement TOKEN dans Render.")

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

# Démarrage du serveur web dans un thread séparé
Thread(target=run_web, daemon=True).start()

# --- BOT TELEGRAM ---
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🚀 **BIENVENUE SUR SIGNAL MEXICAIN** 🇨🇮\n\n"
        "Gagnez en toute sérénité avec nos signaux exclusifs !\n\n"
        "Pour activer votre accès, envoyez simplement votre **ID Joueur**."
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

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
    if text.isdigit() and len(text) > 5:
        users_col.update_one({"telegram_id": user_id}, {"$set": {"player_id": text, "is_vip": False}}, upsert=True)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 **Nouvelle demande d'activation**\n\n👤 Utilisateur : @{username}\n🆔 ID Joueur : `{text}`\n\n👉 Utilisez `/valider {user_id}` pour confirmer."
        )
        await update.message.reply_text("⏳ **Demande envoyée !** L'administrateur validera votre accès sous peu.")
    else:
        await update.message.reply_text("❌ **Format invalide.** Envoyez votre ID de joueur (ex: 987654321).")

async def valider_joueur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID: return
    if context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}})
        await update.message.reply_text(f"✅ Joueur {target_id} activé.")
        try:
            await context.bot.send_message(chat_id=target_id, text="🎉 **Félicitations !** Votre accès VIP est confirmé.")
        except: pass

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider_joueur))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
