import os
from flask import Flask, render_template, request
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = "5724620019"

def est_autorise(user_id):
    if str(user_id) == ADMIN_ID: return True
    if not os.path.exists('utilisateurs.txt'): return False
    with open('utilisateurs.txt', 'r') as f:
        return str(user_id) in f.read().splitlines()

@app.route('/')
def home():
    user_id = request.args.get('user_id')
    if est_autorise(user_id):
        return render_template('index.html')
    return "Accès refusé", 403

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

async def valider(update, context):
    if str(update.effective_user.id) == ADMIN_ID and context.args:
        with open('utilisateurs.txt', 'a') as f:
            f.write(context.args[0] + '\n')
        await update.message.reply_text(f"ID {context.args[0]} validé avec succès ✅")

async def recevoir_id(update, context):
    joueur_id = update.effective_user.id
    await context.bot.send_message(ADMIN_ID, f"🚨 Nouvel ID reçu !\nID 1win: {update.message.text}\nID Telegram: {joueur_id}\n\nPour valider, tape: /valider {joueur_id}")
    await update.message.reply_text("Ton ID a été transmis à l'administrateur. Tu seras notifié dès validation.")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    Thread(target=run_web).start()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), recevoir_id))
    bot_app.run_polling()
