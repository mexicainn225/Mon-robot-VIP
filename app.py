import os
from flask import Flask, render_template, request
from threading import Thread
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

app = Flask(__name__)
# Assurez-vous que votre variable d'environnement TOKEN est bien configurée sur votre hébergeur
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = "5724620019"

# --- PARTIE FLASK (Gestion accès) ---
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
    return "Accès refusé. Envoie ton ID 1win au bot pour validation.", 403

# --- PARTIE BOT (Gestion validation) ---
async def valider(update, context):
    if str(update.effective_user.id) == ADMIN_ID and context.args:
        with open('utilisateurs.txt', 'a') as f:
            f.write(context.args[0] + '\n')
        await update.message.reply_text(f"ID {context.args[0]} validé avec succès ✅")
    else:
        await update.message.reply_text("Commande réservée à l'administrateur.")

async def recevoir_id(update, context):
    joueur_id = update.effective_user.id
    # Transmet l'ID au bot de l'admin
    await context.bot.send_message(ADMIN_ID, f"🚨 Nouvel ID reçu !\nID 1win: {update.message.text}\nID Telegram: {joueur_id}\n\nPour valider, tape: /valider {joueur_id}")
    await update.message.reply_text("Ton ID a été transmis à l'administrateur. Tu seras notifié dès validation.")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

if __name__ == '__main__':
    # Lance le serveur web en arrière-plan
    Thread(target=run_web).start()
    
    # Lance le bot Telegram
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("valider", valider))
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), recevoir_id))
    bot_app.run_polling()
