import os
import logging
from threading import Thread

from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    WebAppInfo
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================
# CONFIGURATION
# ==========================

TOKEN = os.environ.get("TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")

ADMIN_ID = 5724620019

client = MongoClient(MONGO_URI)
db = client["plateforme_db"]
users_col = db["users"]

app = Flask(__name__, template_folder="templates")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ==========================
# FLASK
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/verifier-vip", methods=["POST"])
def verifier_vip():

    data = request.json

    telegram_id = str(data.get("telegram_id"))

    user = users_col.find_one({
        "telegram_id": telegram_id,
        "is_vip": True
    })

    if user:
        return jsonify({
            "status": "VIP"
        }), 200

    return jsonify({
        "status": "NON_VIP"
    }), 403


def run_web():
    app.run(
        host="0.0.0.0",
        port=10000
    )


Thread(target=run_web, daemon=True).start()

# ==========================
# BOT TELEGRAM
# ==========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    user = users_col.find_one({
        "telegram_id": user_id
    })

    message = (
        "🚀 BIENVENUE SUR SIGNAL MEXICAIN 🇨🇮\n\n"
        "Gagnez en toute sérénité avec nos signaux exclusifs !\n\n"
        "Pour activer votre accès, envoyez simplement votre ID Joueur."
    )

    if user and user.get("is_vip"):

        keyboard = ReplyKeyboardMarkup(
            [[
                KeyboardButton(
                    text="🚀 GAME HACK",
                    web_app=WebAppInfo(
                        url="https://mon-robot-vip-1.onrender.com"
                    )
                )
            ]],
            resize_keyboard=True,
            persistent=True
        )

        await update.message.reply_text(
            message,
            reply_markup=keyboard
        )

    else:

        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardRemove()
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    user_id = str(update.effective_user.id)

    username = update.effective_user.username or "Inconnu"

    user = users_col.find_one({
        "telegram_id": user_id
    })

    if user and user.get("is_vip"):

        await update.message.reply_text(
            "✅ Votre accès VIP est déjà activé."
        )

        return

    if text.isdigit():

        users_col.update_one(
            {
                "telegram_id": user_id
            },
            {
                "$set": {
                    "telegram_id": user_id,
                    "player_id": text,
                    "username": username,
                    "is_vip": False
                }
            },
            upsert=True
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🔔 Nouvelle demande\n\n"
                f"Utilisateur : @{username}\n"
                f"Telegram ID : {user_id}\n"
                f"Player ID : {text}\n\n"
                f"/valider {user_id}"
            )
        )

        await update.message.reply_text(
            "⏳ Votre demande a été envoyée à l'administrateur."
        )

    else:

        await update.message.reply_text(
            "❌ Envoyez uniquement votre ID Joueur."
        )


async def valider(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Utilisation : /valider TELEGRAM_ID"
        )
        return

    target_id = context.args[0]

    users_col.update_one(
        {
            "telegram_id": target_id
        },
        {
            "$set": {
                "is_vip": True
            }
        }
    )

    keyboard = ReplyKeyboardMarkup(
        [[
            KeyboardButton(
                text="🚀 GAME HACK",
                web_app=WebAppInfo(
                    url="https://TON-SITE.onrender.com"
                )
            )
        ]],
        resize_keyboard=True,
        persistent=True
    )

    await update.message.reply_text(
        f"✅ {target_id} est maintenant VIP."
    )

    try:

        await context.bot.send_message(
            chat_id=target_id,
            text="🎉 Félicitations ! Votre accès VIP est activé.",
            reply_markup=keyboard
        )

    except Exception:
        pass


# ==========================
# LANCEMENT
# ==========================

if __name__ == "__main__":

    bot = ApplicationBuilder().token(TOKEN).build()

    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("valider", valider))
    bot.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    bot.run_polling()
