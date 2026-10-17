from threading import Thread
import os
import database  # Importe le fichier database.py
from flask import Flask, render_template, request
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

app = Flask(__name__, template_folder='templates', static_folder='static')
TOKEN = os.environ.get('TOKEN')
TON_ID_ADMIN = 5724620019  # ID Admin configuré

WEBAPP_URL = 'https://mon-robot-vip-1.onrender.com'


@app.route('/')
def home():
  return render_template('index.html')


async def start(update, context):
  user_id = update.effective_user.id

  # Si l'utilisateur est déjà validé, on lui redonne l'accès direct
  if database.est_valide(user_id):
    keyboard = [[
        InlineKeyboardButton(
            "🚀 Lancer l'Application", web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    await update.message.reply_text(
        'Re-bonjour ! Voici ton accès :',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
  else:
    message = (
        'Bienvenue sur le bot 1win 🚀\n\n'
        'Pour débloquer tes accès, suis ces étapes :\n\n'
        '1️⃣ Inscris-toi ici : https://lkbb.cc/78634e\n'
        '2️⃣ Utilise le code promo : COK225\n'
        '3️⃣ Effectue une recharge sur ton compte.\n'
        '4️⃣ Envoie ton ID 1win ici pour validation.'
    )
    await update.message.reply_text(message)


async def handle_message(update, context):
  user_id = update.effective_user.id
  message_text = update.message.text

  # On enregistre l'ID 1win et on met le statut à 'pending'
  database.ajouter_utilisateur(user_id, message_text)

  await update.message.reply_text(
      "ID reçu ! J'ai transmis ta demande à l'admin. Attends la validation. ✅"
  )

  # Clavier interactif pour l'Admin
  admin_keyboard = [
      [
          InlineKeyboardButton(
              '✅ Valider l\'accès', callback_data=f'val_{user_id}'
          ),
          InlineKeyboardButton('❌ Mauvais code', callback_data=f'err_{user_id}'),
      ],
      [
          InlineKeyboardButton(
              '💰 Rappel Recharge', callback_data=f'rappel_{user_id}'
          )
      ],
  ]
  admin_markup = InlineKeyboardMarkup(admin_keyboard)

  # Prévenir l'admin (toi) avec boutons interactifs
  await context.bot.send_message(
      chat_id=TON_ID_ADMIN,
      text=(
          f'🚨 **Nouvelle demande :**\n👤 User ID: `{user_id}`\n🆔 ID 1win:'
          f' `{message_text}`'
      ),
      parse_mode='Markdown',
      reply_markup=admin_markup,
  )


# Validation manuelle via commande textuelle (/valider USER_ID)
async def valider(update, context):
  if update.effective_user.id != TON_ID_ADMIN:
    return

  if context.args:
    user_id_a_valider = int(context.args[0])
    database.valider_utilisateur(user_id_a_valider)

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Lancer l'Application", web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    await context.bot.send_message(
        chat_id=user_id_a_valider,
        text=(
            '✅ Félicitations ! Ton ID a été validé. Tu peux maintenant accès'
            ' aux signaux.'
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    await update.message.reply_text(
        f'Utilisateur {user_id_a_valider} validé avec succès !'
    )


# Rappel de recharge manuel via commande textuelle (/rappel USER_ID)
async def rappel(update, context):
  if update.effective_user.id != TON_ID_ADMIN:
    return

  if context.args:
    user_id_a_rappeler = int(context.args[0])
    message_rappel = (
        '⚠️ **RAPPEL RECHARGE :**\n\n'
        'Ton compte a bien été vérifié avec le code promo **COK225**, mais tu'
        ' n\'as pas encore effectué ta **recharge** !\n\n'
        '👉 **Fais ton dépôt sur 1win dès maintenant**, puis renvoie ton ID ici'
        ' pour débloquer l\'accès VIP.'
    )
    try:
      await context.bot.send_message(
          chat_id=user_id_a_rappeler, text=message_rappel, parse_mode='Markdown'
      )
      await update.message.reply_text(
          f'Rappel de recharge envoyé à {user_id_a_rappeler} !'
      )
    except Exception as e:
      await update.message.reply_text(f'Erreur envoi rappel: {e}')


# Gestion des actions des boutons Admin (Callback)
async def admin_callback(update, context):
  query = update.callback_query
  if update.effective_user.id != TON_ID_ADMIN:
    await query.answer('Accès refusé.', show_alert=True)
    return

  await query.answer()
  data = query.data

  if data.startswith('val_'):
    user_id_target = int(data.split('_')[1])
    database.valider_utilisateur(user_id_target)

    keyboard = [[
        InlineKeyboardButton(
            "🚀 Lancer l'Application", web_app=WebAppInfo(url=WEBAPP_URL)
        )
    ]]
    try:
      await context.bot.send_message(
          chat_id=user_id_target,
          text=(
              '✅ Félicitations ! Ton ID a été validé. Tu peux maintenant'
              ' accéder aux signaux.'
          ),
          reply_markup=InlineKeyboardMarkup(keyboard),
      )
    except Exception as e:
      print(f'Erreur envoi validation: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🟢 **STATUT : VALIDÉ & ACTIVÉ**',
        parse_mode='Markdown',
    )

  elif data.startswith('err_'):
    user_id_target = int(data.split('_')[1])
    try:
      await context.bot.send_message(
          chat_id=user_id_target,
          text='❌ Cet ID n’est pas inscrit avec le code COK225.',
      )
    except Exception as e:
      print(f'Erreur envoi erreur: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🔴 **STATUT : REFUSÉ**',
        parse_mode='Markdown',
    )

  elif data.startswith('rappel_'):
    user_id_target = int(data.split('_')[1])
    message_rappel = (
        '⚠️ **RAPPEL RECHARGE :**\n\n'
        'Ton compte a bien été vérifié avec le code promo **COK225**, mais tu'
        ' n\'as pas encore effectué ta **recharge** !\n\n'
        '👉 **Fais ton dépôt sur 1win dès maintenant**, puis renvoie ton ID ici'
        ' pour débloquer l\'accès VIP.'
    )
    try:
      await context.bot.send_message(
          chat_id=user_id_target, text=message_rappel, parse_mode='Markdown'
      )
    except Exception as e:
      print(f'Erreur envoi rappel: {e}')

    await query.edit_message_text(
        text=query.message.text + '\n\n🟡 **STATUT : RAPPEL RECHARGE ENVOYÉ**',
        parse_mode='Markdown',
    )


def run_web():
  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
  Thread(target=run_web).start()

  bot_app = ApplicationBuilder().token(TOKEN).build()
  bot_app.add_handler(CommandHandler('start', start))
  bot_app.add_handler(CommandHandler('valider', valider))
  bot_app.add_handler(CommandHandler('rappel', rappel))
  bot_app.add_handler(CallbackQueryHandler(admin_callback))
  bot_app.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
  )
  bot_app.run_polling()
