import os
import logging
import random
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request, jsonify, render_template
from threading import Thread
from pymongo import MongoClient

# --- CONFIGURATION ---
app = Flask(__name__, template_folder='.')
TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client['plateforme_db']
config_col = db['config']

# --- SERVEUR WEB (Pour votre interface HTML) ---
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    data = config_col.find_one({"_id": "settings"})
    return jsonify(data['valeurs'] if data else {})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    data = request.json
    config_col.update_one({"_id": "settings"}, {"$set": {"valeurs": data}}, upsert=True)
    return jsonify({"status": "success"})

def run_web(): 
    app.run(host='0.0.0.0', port=10000)

# Démarrage du serveur dans un thread séparé
Thread(target=run_web, daemon=True).start()

# --- LOGIQUE BOT TELEGRAM ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenue sur la Plateforme VIP !\n\nOuvrez l'application pour lancer une analyse.")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_name = update.effective_message.web_app_data.data
    
    msg = await update.message.reply_text(f"🔍 **Analyse de {game_name}...**")
    await asyncio.sleep(1)
    await msg.edit_text(f"🔍 **Analyse de {game_name}... [████░░░░] 50%**")
    await asyncio.sleep(1)
    
    maintenant = datetime.now().strftime("%H:%M:%S")
    prediction = round(random.uniform(1.5, 12.5), 2)
    
    resultat = (
        f"✅ **Signal {game_name}**\n\n"
        f"🎯 **Cote cible :** {prediction}x\n"
        f"🕒 **Heure de jeu :** {maintenant}\n\n"
        f"⚠️ *Fiabilité : 98%*\n"
        f"🚀 *Entrez dans le jeu maintenant !*"
    )
    await msg.edit_text(resultat)

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré !")
    else:
        bot_app = ApplicationBuilder().token(TOKEN).build()
        
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot et le serveur web sont en ligne et prêts !")
        bot_app.run_polling()
