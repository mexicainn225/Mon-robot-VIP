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

# Connexion MongoDB avec timeout pour la stabilité
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client['plateforme_db']
users_col = db['users'] 

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- SERVEUR WEB ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/verifier-vip', methods=['POST'])
def verifier_vip():
    try:
        data = request.json
        # Nettoyage strict : on force en string et on enlève les espaces
        player_id = str(data.get('player_id', '')).strip()
        
        if not player_id:
            return jsonify({"status": "MISSING_ID"}), 400

        user = users_col.find_one({"player_id": player_id})
        
        if user and user.get('is_vip') == True:
            logging.info(f"Accès VIP autorisé pour l'ID: {player_id}")
            return jsonify({"status": "VIP"}), 200
            
        logging.warning(f"Accès refusé pour l'ID: {player_id}")
        return jsonify({"status": "NON_VIP"}), 403
    except Exception as e:
        logging.error(f"Erreur serveur : {e}")
        return jsonify({"status": "ERROR"}), 500

def run_web(): 
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_web, daemon=True).start()

# --- LOGIQUE BOT TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🚀 **BIENVENUE SUR SIGNAL MEXICAIN** 🇨🇮\n\n"
        "Gagnez en toute sérénité avec nos signaux exclusifs !\n\n"
        "**Comment activer votre accès ?**\n"
        "1️⃣ Inscrivez-vous sur : https://lkbb.cc/78634e\n"
        "2️⃣ Utilisez le code promo : **COK225**\n"
        "3️⃣ Rechargez votre compte.\n"
        "4️⃣ Envoyez votre **ID Joueur** dans ce bot pour validation.\n\n"
        "*Votre compte sera activé par l'administrateur après vérification.*"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "Inconnu"

    # Vérification si déjà VIP
    user = users_col.find_one({"telegram_id": user_id})
    if user and user.get('is_vip'):
        await update.message.reply_text("✅ Vous êtes déjà membre VIP ! Accédez à la Web App.")
        return

    # Si le message est un ID (chiffres seulement)
    if text.isdigit() and len(text) > 5:
        users_col.update_one(
            {"telegram_id": user_id}, 
            {"$set": {"player_id": text, "is_vip": False}}, 
            upsert=True
        )
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 **Nouvelle demande d'activation**\n\n👤 Utilisateur : @{username} (ID: {user_id})\n🆔 ID Joueur : `{text}`\n\n👉 Utilisez `/valider {user_id}` pour confirmer."
        )
        await update.message.reply_text("⏳ **Demande envoyée !**\n\nL'administrateur va vérifier votre inscription sous peu.")
    else:
        await update.message.reply_text("❌ **Format invalide.**\n\nEnvoyez votre **ID de joueur** (ex: 987654321) pour être activé.")

async def valider_joueur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != ADMIN_ID: return
    if context.args:
        target_id = context.args[0]
        users_col.update_one({"telegram_id": target_id}, {"$set": {"is_vip": True}})
        await update.message.reply_text(f"✅ Joueur {target_id} activé.")
        try:
            await context.bot.send_message(chat_id=target_id, text="🎉 **Félicitations !** Votre accès VIP est confirmé.")
        except: pass
    else:
        await update.message.reply_text("❌ Usage : /valider [ID_TELEGRAM]")

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider_joueur))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
