import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from pymongo import MongoClient

# --- CONFIGURATION ---
# Utilisation de os.getenv pour la sécurité (à configurer dans les variables d'environnement de Render)
TOKEN = os.getenv("TELEGRAM_TOKEN")
# Remplace par ton URL MongoDB (si tu utilises MongoDB Atlas, elle ressemble à mongodb+srv://...)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "robot_vip_db"

# Vérification du token
if not TOKEN:
    raise ValueError("Le token Telegram n'est pas défini. Vérifie ta variable d'environnement TELEGRAM_TOKEN.")

# Connexion MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_col = db["users"]

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# --- MESSAGES ---
WELCOME_MESSAGE = (
    "🚀 **Bienvenue sur le Robot Signal !**\n\n"
    "Pour accéder à nos signaux exclusifs et activer votre accès, suivez ces étapes :\n\n"
    "1️⃣ **Inscrivez-vous** ici : https://lkbb.cc/78634e\n"
    "2️⃣ **Envoyez-nous votre ID utilisateur** (ID de jeu) pour validation.\n\n"
    "Code promo : **COK225**"
)

# --- FONCTIONS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    user_input = update.message.text.strip()
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username

    # Si l'utilisateur envoie un ID (composé uniquement de chiffres)
    if user_input.isdigit():
        users_col.update_one(
            {"telegram_id": telegram_id},
            {"$set": {
                "game_id": user_input,
                "username": username,
                "status": "pending_verification"
            }},
            upsert=True
        )
        await update.message.reply_text(
            f"✅ **ID {user_input} bien reçu !**\n\n"
            "Votre compte est en cours de vérification par notre équipe.\n"
            "Vous serez notifié dès l'activation."
        )
    else:
        await update.message.reply_text("❌ Veuillez envoyer un ID de jeu valide (chiffres uniquement).")

# --- LANCEMENT ---
if __name__ == '__main__':
    # Initialisation du bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot démarré avec succès...")
    app.run_polling()
