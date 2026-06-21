import os
import logging
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")

# --- SERVEUR WEB ---
@app.route('/')
def home(): 
    # Affiche directement ta page index.html sans aucune condition
    return render_template('index.html')

def run_web(): 
    # Utilise le port fourni par Render ou 10000 par défaut
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- LOGIQUE BOT TELEGRAM ---
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update, context):
    await update.message.reply_text("🚀 **BIENVENUE SUR SIGNAL MEXICAIN**\n\nCliquez sur le bouton pour accéder aux signaux.")

if __name__ == '__main__':
    # Lance le serveur web
    Thread(target=run_web, daemon=True).start()
    
    # Lance le bot Telegram
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()
