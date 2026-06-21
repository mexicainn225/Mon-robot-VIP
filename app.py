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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    Thread(target=run_web, daemon=True).start()
    if TOKEN:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        bot_app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("🚀 Bienvenue ! Accédez aux signaux.")))
        bot_app.run_polling()
