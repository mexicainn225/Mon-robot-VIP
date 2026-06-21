import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from flask import Flask, render_template, jsonify, request
from threading import Thread

app = Flask(__name__, template_folder='templates')
# Liste des IDs autorisés (Ajoute les IDs Telegram ici)
vip_users = ["5724620019"] 

WEBAPP_URL = "https://mon-robot-vip-1.onrender.com" 

@app.route('/')
def home(): return render_template('index.html')

@app.route('/verifier-vip', methods=['POST'])
def verifier_vip():
    data = request.json
    tid = str(data.get('player_id'))
    if tid in vip_users:
        return jsonify({"status": "VIP"}), 200
    return jsonify({"status": "NON_VIP"}), 403

def run_web(): app.run(host='0.0.0.0', port=10000)
Thread(target=run_web, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([[KeyboardButton("🎮 GAME HACK", web_app=WebAppInfo(url=WEBAPP_URL))]], resize_keyboard=True)
    await update.message.reply_text("🚀 BIENVENUE SUR SIGNAL MEXICAIN 🇨🇮\nCliquez sur le bouton ci-dessous.", reply_markup=kb)

if __name__ == '__main__':
    bot_app = ApplicationBuilder().token(os.environ.get("TOKEN")).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.run_polling()
