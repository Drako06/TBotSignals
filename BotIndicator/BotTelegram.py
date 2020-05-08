#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import time
import logging
import sqlite3
import datetime
from BotIndicator.Indicator import main
from telegram.ext import Updater, CommandHandler, Filters, ConversationHandler, CallbackQueryHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


(REGISTRO, INICIA, ACTION, SUBMIT, ABONO, METOD) = map(chr, range(6))
#con = sqlite3.connect('C:/Users\AETERNAM124\PycharmProjects\BitBot\DataCript.db')


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
#con = sqlite3.connect('C:/Users\AETERNAM124\PycharmProjects\BitBot\DataCript.db')


#def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
#    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
#    if header_buttons:
#        menu.insert(0, [header_buttons])
#    if footer_buttons:
#       menu.append([footer_buttons])
#   print(menu)
#   return menu

def __message(text, update, buttons):
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=text, reply_markup=keyboard)

def __message_query(text, update, buttons):
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

def start(update, context):
    """Send a message when the command /start is issued."""
    global con
    con = sqlite3.connect('C:/Users\AETERNAM124\PycharmProjects\BitBot\DataCript.db')
    chat_id = update.effective_chat.id
    print(chat_id)
    cursor = con.cursor()
    print("Antes del cursor")
    cursor.execute('SELECT chat_id FROM TB_Users WHERE chat_id = ?', (chat_id,))
    print("despues del select")
    exist = cursor.fetchone()

    print("despues del if chats_id")
    print(exist)

    if not exist:
        if not context.user_data.get('START_OVER'):
            button_list = [[
            InlineKeyboardButton("PruebaGratis", callback_data=str(REGISTRO))]]
            __message("Bienvenido!!! Abre tu cuenta de 10 días de señales totalmente gratis!!", update, button_list)
            return ACTION

    else:
        print("En el ELSE de START")
        return menu_principal(update, context)


def menu_principal(update, contex):
    text = 'Menu Principal'
    button_list = [[InlineKeyboardButton(text='Iniciar Bot', callback_data=str(INICIA))],
                   [InlineKeyboardButton(text='Abonar cuenta', callback_data=str(ABONO))]]
    if update.callback_query:
        __message_query(text, update, button_list)
    else:
        __message(text, update, button_list)
    return ACTION



def fechasFin():
    hora = datetime.datetime.now()
    for i in range(14):

        hora = hora + datetime.timedelta(1)
        if hora.weekday() == 5:
            hora = hora + datetime.timedelta(2)

    return hora

def subscribirPrueba(update, context):
    cursor = con.cursor()
    print("Entramos a la funcion subscribirse")
    print('El id del chat es: ' + str(update.effective_chat.id))
    print('El idName del cliente es: ' + str(update.effective_chat.username))
    print('El nombre del usuario es: ' + str(update.effective_chat.first_name))
    print(update.callback_query.message.date)
    chat_id = update.effective_chat.id
    nombreId = update.effective_chat.username
    nombreUsuario = update.effective_chat.first_name
    fechaInicioPrueba = datetime.datetime.now()
    cursor.execute("INSERT INTO TB_Users (chat_id , nombreId, nombreUsuario, fechaInicioPrueba, fechaFinPrueba, abono,"
                   " fechaInicioAbono, fechaFinAbono) VALUES(?,?,?,?,?,?,?,?)", (chat_id, nombreId, nombreUsuario,
                                                                                 fechaInicioPrueba, fechasFin(), False,
                                                                                 'null', 'null'))

    con.commit()
    context.bot.send_message(chat_id=chat_id, text="Hola! Hemos guardado tus datos! Abora disfruta de 10 días de prueba gratis! :D")
    time.sleep(10)
    return menu_principal(update, context)


def iniciarBot(update, context):
    main()
    return INICIA
def subscribirCuenta(update, context):
    pass

def __format_pattern(key):
    return f'^{key}$'

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
def echo(update, context):
    update.message.reply_text("Hola! para detener el Bot pulsa aqui: /BOT" + '\n' + "Para abonart la cuenta pulsa aqui: /ABONO")


def menu():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("932025784:AAFlROh16EyA1bXS0amF7MQdE63lBKHPtbY", use_context=True)
    con = sqlite3.connect('C:/Users\AETERNAM124\PycharmProjects\BitBot\DataCript.db')
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)],
                                       states={
                                           ACTION: [
                                               CallbackQueryHandler(subscribirPrueba,
                                                                    pattern=__format_pattern(REGISTRO)),
                                               CallbackQueryHandler(iniciarBot,
                                                                    pattern=__format_pattern(INICIA)),
                                                CallbackQueryHandler(menu_principal,
                                                                     pattern=__format_pattern(ABONO))],
                                           ABONO: [
                                               CallbackQueryHandler(subscribirCuenta,
                                                                    pattern=__format_pattern(METOD))
                                           ]
                                       }, fallbacks=[])

    # on different commands - answer in Telegram
    #dp.add_handler(CommandHandler("start", start))
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    menu()
