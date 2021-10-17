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

    if not c_util.is_topmost_node(currentMenuItems[0]):
        # if current level is not topmost one, add Back button
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


def display_constant_or_menuitems(message, parent_id):
    '''Display a constant, or a folder. 
    If parent_id is not an actual id, e.g. empty string, the top_most folder will be displayed
    '''
    global currentMenuItems

    const = db.get_item(parent_id)
    if const is not None:

        if c_util.is_constant(const):
            # it is leaf node i.e. constant, send constant value in a message
            const = db.get_item(parent_id)
            
            bot.send_message(chat_id=message.chat.id,
                            text=f"{const['name']}\nvalue  : {const['value']}\nunit   : {const['unit']}\nsystem : {const['unit_system']}",
                            parse_mode='HTML')
            return
        else:
            # it is parent node, it's children
            answer_text = f"List of topics in {const['name']} section"
            if c_util.is_constant(currentMenuItems[0]):
                answer_text = f"List of constants in {const['name']} section"

    else:
        # it is topmost level, display topmost parents
        answer_text = 'List of constants'

    bot.send_message(chat_id=message.chat.id,
                text=answer_text,
                reply_markup=makeKeyboard(),
                parse_mode='HTML')

def update_current_menu_items(parent_id):
    '''update menu items with children of the parent
    args: parent_id - id of the parent
    '''
    global currentMenuItems

    level = db.get_level(parent_id)
    temp = currentMenuItems

    if level == 0:
        currentMenuItems = db.get_first_level_parents()
    elif (level == 1) or (level == 2):
        currentMenuItems = db.get_children(parent_id)

    if (currentMenuItems is None) or len(currentMenuItems) == 0:
        # heroku server do not log exceptions, so print it
        currentMenuItems = temp
        print('ERROR: currentMenuItems list must not be empty')
        raise Exception('currentMenuItems list must not be empty')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def answer(message):
    global currentMenuItems

    user_text = message.text
    if user_text == BACK_COMMAND:
        # go one level up
        parent = db.get_item(currentMenuItems[0]['parent_id'])

        if parent is None:
            # we are at the topmost level there's no way up
            return

        if c_util.is_topmost_node(parent):
            parents_parent_id = ''
        else:
            parents_parent_id = parent['parent_id']
        
        constant_id = parents_parent_id

    else:
        # go one level down or display constant's value
        constant_name = user_text.strip(FOLDER_ICON).strip()

        # if user pressed menu item, we will get non-empty constant_id
        constant_id  = c_util.get_menuitems_id(currentMenuItems, constant_name)
        if constant_id is None:
            # user typed the name of the constant, try searching close matches 
            # among names of constants and folders in db
            constant_id = db.search(constant_name)
            if constant_id is None:
                bot.reply_to(message, f"No constant found with name matching: `{message.text}`. Try searching menu.")
                return
    
    update_current_menu_items(parent_id = constant_id)
    display_constant_or_menuitems(message, constant_id)


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