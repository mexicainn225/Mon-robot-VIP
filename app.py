import os
import logging
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__)
TOKEN = os.environ.get("TOKEN")

@app.route('/')
def home():
    return "Bot en ligne"

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

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    Thread(target=run_web).start()
    
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()
