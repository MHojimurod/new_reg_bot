


from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

from bot.models import Region, User, ZoomUser
from utils import distribute
from .constants import *


class Zoom:
    def zoomga_yozilish_handler(self, update:Update, context:CallbackContext):
        user = ZoomUser.objects.filter(chat_id=update.message.from_user.id).first()
        if not user:
            
            user2 = User.objects.filter(chat_id=update.message.from_user.id).first()
            if user2:
                ZoomUser.objects.create(chat_id=update.message.from_user.id, name=user2.name, number=user2.number)
                update.message.reply_text("Siz treningga muvoffaqiyatli yozildingiz!", reply_markup=ReplyKeyboardMarkup(
            [[
                shogird_tushish
            ]]
        ,resize_keyboard=True))
                return -1
            else:
                update.message.reply_text("Ism familyangizni kiriting!")
                return ZOOM_NAME
        else:
            update.message.reply_text("Siz allaqachon ro'yhatdan o'tib bo'ldingiz!")
            return -1




    def name_zoom(self, update:Update, context:CallbackContext):
        if len(update.message.text.split()) > 1:
            context.user_data['zoom']['name'] = update.message.text
            update.message.reply_text("Telefon raqamingizni yuboring!", reply_markup=ReplyKeyboardMarkup(
                [[
                    KeyboardButton("Yuborish", request_contact=True)
                ]]
            , resize_keyboard=True))
            return ZOOM_NUMBER
        else:
            update.message.reply_text("Iltimos ismingizni to'g'ri yozing!")
            return ZOOM_NAME
    

    def number_zoom(self, update:Update, context:CallbackContext):
        context.user_data['zoom']['number'] = update.message.contact.phone_number
        ZoomUser.objects.create(chat_id=update.message.from_user.id, **context.user_data['zoom'])
        update.message.reply_text("Siz muvoffaqiyatli ro'yhatdan o'tdingiz!", reply_markup=ReplyKeyboardMarkup(
            [[
                "Menu"
            ]]
        ,resize_keyboard=True) )
        return -1