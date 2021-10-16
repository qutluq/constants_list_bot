from constantsdb import ConstantsDB
from flask import Flask, request
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import constantsutil as c_util

TOKEN   = os.environ.get('API_TOKEN', '')
APP_URL = f"{os.environ.get('HEROKU_APP_URL', '')}/{TOKEN}"

bot     = telebot.TeleBot(TOKEN)
server  = Flask(__name__)
db      = ConstantsDB()

currentMenuItems = db.get_first_level_parents()
BACK_COMMAND = "BACK_COMMAND"
BACK_ICON    = u"\u2934"
FOLDER_ICON  = u'\uD83D\uDCC2'.encode('utf-16', 'surrogatepass').decode('utf-16') # non-BMP unicode char

def makeKeyboard():

    markup = InlineKeyboardMarkup()

    if not c_util.is_root_node(currentMenuItems[0]):
        # if current level is not root one, add Back button
        markup.add(InlineKeyboardButton(text="Back " + BACK_ICON, callback_data=BACK_COMMAND))

    for item in currentMenuItems:
        
        if c_util.is_constant(item):
            markup.add(InlineKeyboardButton(text=item["name"], callback_data=item["id"]))
        else:
            markup.add(InlineKeyboardButton(text=FOLDER_ICON +" "+item["name"], callback_data=item["id"]))

    return markup

@bot.message_handler(commands=['start'])
def start(message):

    bot.send_message(chat_id=message.chat.id,
                     text="List of constants",
                     reply_markup=makeKeyboard(),
                     parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    global currentMenuItems

    if call.data == BACK_COMMAND:
        # go one level up
        parent = db.get_item(currentMenuItems[0]['parent_id'])
        if c_util.is_root_node(parent):
            # root node level
            currentMenuItems = db.get_first_level_parents()
        else:
            # get list of siblings of the parent
            currentMenuItems = db.get_children(parent['parent_id'])
    else:
        # go one level down
        constant_id = call.data
        children = db.get_children(constant_id)

        if children is not None:
            # show list of constants at lower level
            currentMenuItems = children
        else:
            # send constant value in a message
            const = db.get_item(constant_id)
            
            bot.send_message(chat_id=call.from_user.id,
                            text=f"{const['name']} : {const['value']} {const['unit']}",
                            parse_mode='HTML')
            return

    bot.send_message(chat_id=call.from_user.id,
                     text="List of constants",
                     reply_markup=makeKeyboard(),
                     parse_mode='HTML')

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo(message):

    const = db.get_item(message.text)
    if const is not None:
        # found the constant
        bot.reply_to(message, f"{const['name']} : {const['value']} {const['unit']}")
    else:
        # did not find the constant
        bot.reply_to(message, f"Sorry, no constant was found for query: {message.text}")

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