import os
import hmac
import hashlib
import json
from flask import Flask, render_template, request, jsonify
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler
from pymongo import MongoClient

# Configuration
app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
ADMIN_ID = 5724620019

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client['bot_database']
users_col = db['utilisateurs']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check_access', methods=['POST'])
def check_access():
    init_data = request.json.get('initData')
    if not init_data:
        return jsonify({"allowed": False}), 403

    # Vérification de la signature Telegram (Sécurité)
    data_dict = dict(x.split('=') for x in init_data.split('&'))
    check_hash = data_dict.pop('hash')
    data_check_string = "\n".join([f"{k}={v}" for k, v in sorted(data_dict.items())])
    
    secret_key = hashlib.sha256(TOKEN.encode()).digest()
    hmac_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if hmac_string != check_hash:
        return jsonify({"allowed": False}), 403

    # Vérification dans la base MongoDB
    user_info = json.loads(data_dict['user'])
    user_id = user_info['id']
    
    # Accès automatique pour toi (Admin) ou si présent dans MongoDB
    if user_id == ADMIN_ID or users_col.find_one({"user_id": user_id}):
        return jsonify({"allowed": True})
    
    return jsonify({"allowed": False})

async def start(update, context):
    message = (
        "Bienvenue sur le bot 1win 🚀\n\n"
        "Pour débloquer tes accès, suis ces étapes :\n\n"
        "1️⃣ Inscris-toi ici : https://lkbb.cc/78634e\n"
        "2️⃣ Utilise le code promo : COK225\n"
        "3️⃣ Effectue une recharge sur ton compte.\n"
        "4️⃣ Envoie ton ID 1win ici pour validation.\n\n"
        "Dès que c'est fait, tu pourras accéder aux signaux ! ✅"
    )
    await update.message.reply_text(message)

async def valider(update, context):
    if update.effective_user.id == ADMIN_ID:
        try:
            target_id = int(context.args[0])
            users_col.update_one({"user_id": target_id}, {"$set": {"user_id": target_id}}, upsert=True)
            await update.message.reply_text(f"✅ Utilisateur {target_id} validé !")
        except:
            await update.message.reply_text("❌ Erreur. Usage: /valider <ID>")
    else:
        await update.message.reply_text("⛔ Accès refusé.")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Démarrage du serveur web
    Thread(target=run_web).start()
    
    # Démarrage du bot
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.run_polling()
