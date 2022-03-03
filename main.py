   
from re import U
from turtle import up
from matplotlib import use
from telegram import (Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,
                      InlineKeyboardMarkup)
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler,ConversationHandler,CallbackContext

from database import Database
from datetime import datetime
import json
from constant import BIRTH, FIO,CONTACT,regions,REGION

database:Database = Database("bot.db")
def start(update:Update,context:CallbackContext):
    json_data = json.load(open("text.json"))
    user = update.message.from_user
    db_user = database.check_user(user.id)
    if db_user:
        if db_user["name"] is None:
            update.message.reply_html(text=json_data["name"])
            return FIO
        return full_name(update,context)
    else:
        database.create_user(user.id,datetime.now())
        update.message.reply_text(json_data['start'])

def full_name(update:Update,context:CallbackContext):
    json_data = json.load(open("text.json"))
    user = update.message.from_user
    db_user = database.check_user(user.id)
    if db_user["name"] is not None:
        if db_user["contact"] is None:
            update.message.reply_text(text=json_data["phone"],reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Yuborish",request_contact=True)]],resize_keyboard=True))
            return CONTACT
        return contact(update,context)
    else:
        if " " in update.message.text:
            database.update_user(1,user.id,update.message.text)
            update.message.reply_text(text=json_data["phone"],reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Yuborish",request_contact=True)]],resize_keyboard=True))
            return CONTACT
        else:
            update.message.reply_html(json_data['invalid_name'])
            return FIO

def contact(update:Update,context:CallbackContext):
    con = update.message.contact
    json_data = json.load(open("text.json"))
    user = update.message.from_user
    db_user = database.check_user(user.id)
    if db_user["contact"] is not None:
        if db_user["region"] is None:
            update.message.reply_text(text=json_data["region"],reply_markup=ReplyKeyboardMarkup(regions(),resize_keyboard=True))
            return REGION
    else:
        database.update_user(2,user.id,con["phone_number"])
    return contact(update,context)


def region(update:Update,context:CallbackContext):
    text = update.message.text
    json_data = json.load(open("text.json"))
    user = update.message.from_user
    db_user = database.check_user(user.id)
    if db_user["region"] is not None:
        if db_user["birth"] is None:
            update.message.reply_text(text=json_data["birth"],reply_markup=ReplyKeyboardRemove())
            return BIRTH
        
    else:
        database.update_user(3,user.id,text)
    return region(update,context)


def birth(update,context):
    text = update.message.text
    json_data = json.load(open("text.json"))
    user = update.message.from_user
    db_user = database.check_user(user.id)
    if db_user["birth"] is not None:
        if db_user["birth"] is None:
            update.message.reply_text(text=json_data["birth"],reply_markup=ReplyKeyboardRemove())
            return BIRTH
        return region(update,context)

        
    else:
        if text.isdigit():
            if 1940<int(text)<2000:
                database.update_user(4,user.id,text)
                return region(update,context)
            else:
                update.message.reply_text(json_data['range_birth'])
        else:
            update.message.reply_text(json_data['invalid_birth'])

def main():
    updater = Updater("1955026889:AAFfjBn0PRv-z3-QA_yx2uG_e86XbvF8tho")
    dispatcher = updater.dispatcher
    not_start = ~Filters.regex("^(\/start)")
    conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', start),
                # MessageHandler(Filters.regex(
                        # "^(Sotib olish|Купить)"), buy),
                    # MessageHandler(Filters.regex(
                        # "^(Sotib olingan|Купленные)"), purchased),
                    # MessageHandler(Filters.regex(
                        # "^(Mening ballarim|Мои баллы)"), my_balls),
                    # CallbackQueryHandler(get_promotion, pattern="^get_promotion"),
                # CommandHandler('language', change_language),
            ],
            states={
                FIO: [MessageHandler(Filters.text, full_name)],
                CONTACT: [MessageHandler(Filters.contact, contact)],
                REGION: [MessageHandler(Filters.text, region)],
                BIRTH: [MessageHandler(Filters.text, birth)],
                # NAME: [MessageHandler(Filters.text & not_start, name)],
                # NUMBER: [MessageHandler(Filters.contact & not_start, number), MessageHandler(Filters.all & not_start, invalid_number)],
            
            },
            fallbacks=[
                CommandHandler('start', start),
            ]
        )
    dispatcher.add_handler(conversation)
    # dispatcher.add_handler(CallbackQueryHandler(self.order_accept, pattern="^order_accepted"))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
