from constantsdb import ConstantsDB
from flask import Flask, request
import os
import telebot

TOKEN   = os.environ.get('API_TOKEN', '')
APP_URL = f"{os.environ.get('HEROKU_APP_URL', '')}/{TOKEN}"

bot     = telebot.TeleBot(TOKEN)
server  = Flask(__name__)
db      = ConstantsDB()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo(message):

    const = db.get_item(message.text)
    if const is not None:
        bot.reply_to(message, f"{const['name']} : {const['value']} {const['unit']}")
    else:
        bot.reply_to(message, f"Sorry, no constant was found for: {message.text}")

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

    
#print(db.get_children('classical_mech'))
#print(db.get_item('grav_const_SI'))