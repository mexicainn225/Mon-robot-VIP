import os
from flask import Flask, render_template
from threading import Thread
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='.')
TOKEN = os.environ.get("TOKEN")

@app.route('/')
def home():
    return render_template('index.html')

def run_web():
    # Render demande d'utiliser la variable PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT TELEGRAM ---
async def start(update, context):
    await update.message.reply_text("Bienvenue ! Cliquez sur le bouton ci-dessous pour accéder aux signaux.")

if __name__ == '__main__':
    # Lance le serveur web en arrière-plan
    Thread(target=run_web, daemon=True).start()
    
    # Lance le bot
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()
