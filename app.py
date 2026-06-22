import os
import database # Importe le fichier database.py que tu as créé
from flask import Flask, render_template, request
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
TON_ID_ADMIN = 5724620019 # ID Admin configuré

@app.route('/')
def home():
    return render_template('index.html')

async def start(update, context):
    user_id = update.effective_user.id
    
    # Si l'utilisateur est déjà validé, on lui redonne l'accès direct
    if database.est_valide(user_id):
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application", web_app=WebAppInfo(url="https://mon-robot-vip-1.onrender.com"))]]
        await update.message.reply_text("Re-bonjour ! Voici ton accès :", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        message = (
            "Bienvenue sur le bot 1win 🚀\n\n"
            "Pour débloquer tes accès, suis ces étapes :\n\n"
            "1️⃣ Inscris-toi ici : https://lkbb.cc/78634e\n"
            "2️⃣ Utilise le code promo : COK225\n"
            "3️⃣ Effectue une recharge sur ton compte.\n"
            "4️⃣ Envoie ton ID 1win ici pour validation."
        )
        await update.message.reply_text(message)

async def handle_message(update, context):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # On enregistre l'ID 1win et on met le statut à 'pending'
    database.ajouter_utilisateur(user_id, message_text)
    
    await update.message.reply_text("ID reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅")
    
    # Prévenir l'admin (toi)
    await context.bot.send_message(
        chat_id=TON_ID_ADMIN, 
        text=f"🚨 Nouvelle demande :\nUser ID: {user_id}\nID 1win: {message_text}\n\nTape: /valider {user_id}"
    )

async def valider(update, context):
    # Vérification de sécurité : seul l'admin peut valider
    if update.effective_user.id != TON_ID_ADMIN:
        return
    
    if context.args:
        user_id_a_valider = int(context.args[0])
        database.valider_utilisateur(user_id_a_valider)
        
        # Envoi automatique du bouton WebApp à l'utilisateur validé
        keyboard = [[InlineKeyboardButton("🚀 Lancer l'Application", web_app=WebAppInfo(url="https://mon-robot-vip-1.onrender.com"))]]
        await context.bot.send_message(
            chat_id=user_id_a_valider,
            text="✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accéder aux signaux.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(f"Utilisateur {user_id_a_valider} validé avec succès !")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=run_web).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot_app.run_polling()
