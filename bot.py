
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# On récupère le token depuis les variables d'environnement de Render
TOKEN = os.environ.get("TOKEN")

# Configuration des logs pour voir ce qui se passe sur Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Récupère le nom du jeu envoyé par ta Web App
    game_name = update.effective_message.web_app_data.data
    
    # Message de réponse automatique
    await update.message.reply_text(f"🚀 Analyse en cours pour : {game_name}...\n\n✅ Signal : 2.45x")

if __name__ == '__main__':
    if not TOKEN:
        print("Erreur : Le token n'est pas configuré dans les variables d'environnement !")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        # Ce filtre écoute les clics provenant de ta Mini App
        app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
        
        print("Le bot est en ligne et prêt à recevoir les signaux !")
        app.run_polling()
