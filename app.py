import os
import database # Importe le fichier database.py
from flask import Flask, render_template, request
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019 # ID Admin configuré

# URL exacte de ton service sur Render
URL_WEBAPP = "https://fifa-bot-rnbr.onrender.com"

@app.route('/')
def home():
    return render_template('index.html')

async def start(update, context):
    user_id = update.effective_user.id
    
    # Si l'utilisateur est déjà validé, on lui redonne l'accès direct
    if database.est_valide(user_id):
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
        await update.message.reply_text("Re-bonjour champion ! Voici ton accès direct :", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        message = (
            "Bienvenue sur le bot FIFA VIP ⚽\n\n"
            "Pour débloquer tes accès aux pronostics, suis ces étapes :\n\n"
            "1️⃣ Inscris-toi sur Melbet ici : https://lkbb.cc/78634e\n"
            "2️⃣ Utilise le code promo : COK225\n"
            "3️⃣ Effectue une recharge sur ton compte.\n"
            "4️⃣ Envoie ton ID Melbet ici pour validation."
        )
        await update.message.reply_text(message)

async def handle_message(update, context):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # On enregistre l'ID Melbet et on met le statut à 'pending'
    database.ajouter_utilisateur(user_id, message_text)
    
    await update.message.reply_text("ID Melbet reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
    
    # Prévenir l'admin (toi)
    await context.bot.send_message(
        chat_id=TON_ID_ADMIN, 
        text=f"🚨 Nouvelle demande FIFA :\nUser ID: {user_id}\nID Melbet: {message_text}\n\nTape: /valider {user_id}"
    )

async def valider(update, context):
    # Vérification de sécurité : seul l'admin peut valider
    if update.effective_user.id != TON_ID_ADMIN:
        return
    
    if context.args:
        user_id_a_valider = int(context.args[0])
        database.valider_utilisateur(user_id_a_valider)
        
        # Envoi automatique du bouton WebApp à l'utilisateur validé
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application FIFA", web_app=WebAppInfo(url=URL_WEBAPP))]]
        await context.bot.send_message(
            chat_id=user_id_a_valider,
            text="✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accéder aux pronos FIFA.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(f"Utilisateur {user_id_a_valider} validé avec succès !")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Flask tourne en arrière-plan dans un thread
    Thread(target=run_web, daemon=True).start()
    
    # Le Bot Telegram tourne dans le thread principal (ce qui évite tous les bugs de polling)
    if TOKEN:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("valider", valider))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("Bot démarré en mode polling...")
        bot_app.run_polling(drop_pending_updates=True)
    else:
        print("❌ ERREUR : Aucun TOKEN trouvé !")
