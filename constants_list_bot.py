from constantsdb import ConstantsDB
from flask import Flask, request
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import constantsutil as c_util

TOKEN   = os.environ.get('API_TOKEN', '')
APP_URL = f"{os.environ.get('HEROKU_APP_URL', '')}/{TOKEN}"

bot     = telebot.TeleBot(TOKEN)
server  = Flask(__name__)
db      = ConstantsDB()
currentMenuItems = db.get_first_level_parents()

BACK_ICON    = u"\u2934"
FOLDER_ICON  = u'\uD83D\uDCC2'.encode('utf-16', 'surrogatepass').decode('utf-16') # non-BMP unicode char
BACK_COMMAND = "Back " + BACK_ICON

INTRODUCTION_TEXT = '''Hi! I know many Math and Physics constants' values.
Send me the name of a constant and I will tell you its value.
Did not succeed? Try searching it in the menu below.
If you want me to add a new constant to the list, contact me:
kootlook.applications at gmail.com.'''

def makeKeyboard():

    markup = ReplyKeyboardMarkup()

    if not c_util.is_root_node(currentMenuItems[0]):
        # if current level is not root one, add Back button
        markup.add(KeyboardButton(text=BACK_COMMAND))

    for item in currentMenuItems:
        
        if c_util.is_constant(item):
            markup.add(KeyboardButton(text=item["name"]))
        else:
            markup.add(KeyboardButton(text=FOLDER_ICON +" "+item["name"]))

    return markup

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(chat_id=message.chat.id,
                     text=INTRODUCTION_TEXT,
                     reply_markup=makeKeyboard(),
                     parse_mode='HTML')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def answer(message):
    global currentMenuItems

    user_text = message.text
    answer_text = 'List of constants'
    if user_text == BACK_COMMAND:
        # go one level up
        parent = db.get_item(currentMenuItems[0]['parent_id'])
        if c_util.is_root_node(parent):
            # root node level
            answer_text = 'List of constants'
            currentMenuItems = db.get_first_level_parents()
        else:
            answer_text = f"List of constants in {parent['name']} section"
            # get list of siblings of the parent
            currentMenuItems = db.get_children(parent['parent_id'])
    else:
        # go one level down
        constant_name = user_text.strip(FOLDER_ICON).strip()
        constant_id   = c_util.get_menuitems_id(currentMenuItems, constant_name)

        if constant_id is not None:
            # user pressed menu button with a constant name
            children = db.get_children(constant_id)
            
            if children is not None:
                # show list of constants at lower level
                parent = db.get_item(constant_id)
                answer_text = f"List of constants in {parent['name']} section"
                currentMenuItems = children
            else:
                # send constant value in a message
                const = db.get_item(constant_id)
                
                bot.send_message(chat_id=message.chat.id,
                                text=f"{const['name']} : {const['value']} {const['unit']}",
                                parse_mode='HTML')
                return
        else:
            # did not find the constant
            bot.reply_to(message, f"Sorry, no constant was found for query: {message.text}")
            return

    bot.send_message(chat_id=message.chat.id,
                     text=answer_text,
                     reply_markup=makeKeyboard(),
                     parse_mode='HTML')

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200

@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))