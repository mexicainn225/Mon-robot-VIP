import os
from flask import Flask, render_template
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler

app = Flask(__name__, template_folder='templates')
TOKEN = os.environ.get("TOKEN")

@app.route('/')
def home():
    return render_template('index.html')

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def start(update, context):
    await update.message.reply_text("🚀 Bienvenue ! Accédez aux signaux via le bouton ci-dessous.")

if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    if TOKEN:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.run_polling()
