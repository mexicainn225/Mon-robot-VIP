import os
import logging
from flask import Flask, render_template
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__)
TOKEN = os.environ.get("TOKEN")

@app.route('/')
def home():
    return render_template('index.html')

async def start(update, context):
    message = (
        "Bienvenue sur le bot 1win 🚀\n\n"
        "Pour débloquer tes accès, suis ces étapes :\n\n"
        "1. Inscris-toi ici : https://lkbb.cc/78634e\n"
        "2. Utilise le code promo : COK225\n"
        "3. Effectue une recharge sur ton compte.\n"
        "4. Envoie ton ID 1win ici pour validation.\n\n"
        "Dès que c'est fait, tu pourras accéder aux signaux !"
    )
    await update.message.reply_text(message)

def main():
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()

if __name__ == '__main__':
    main()
