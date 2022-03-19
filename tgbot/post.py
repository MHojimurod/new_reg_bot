from time import sleep
import time
from telegram import *
from telegram.ext import *
from .constants import *
from bot.models import User, ZoomUser


class Post:
    def post_start(self, update: Update, context: CallbackContext):
        if update.message.from_user.id in admins:
            context.user_data['post'] = {}
            update.message.reply_text("Iltimos postni kimlarga yuborilishini tanlang!", reply_markup=ReplyKeyboardMarkup([
                [
                    "Trening ishtirokchilariga",
                    "Shogirdlarga"
                ],
                [
                    "Hammaga"
                ]
            ], resize_keyboard=True))
            return POST_TYPE

    def post_type(self, update: Update, context: CallbackContext):
        context.user_data['post']['type'] = 0 if update.message.text == "Trening ishtirokchilariga" else (
            1 if update.message.text == "Shogirdlarga" else 2)
        update.message.reply_text(
            "Iltimos endi post uchun suratni yuboring yoki /skip buyrug'ini yuboring!")
        return POST_IMAGE

    def skip(self, update: Update, context: CallbackContext):
        context.user_data['post']['image'] = None
        update.message.reply_text(
            "Iltimos endi post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_TEXT

    def post_image(self, update: Update, context: CallbackContext):
        context.user_data['post']['image'] = update.message.photo
        update.message.reply_text(
            "Iltimos endi post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST_TEXT

    def post_text(self, update: Update, context: CallbackContext):
        context.user_data['post']['text'] = update.message.text
        context.user_data['post']['text_entities'] = update.message.entities

        update.message.reply_text(
            "marhamat sizning postingiz!\n\nMaq'ul bo'lsa yuborish tugmasini bosing!")
        if context.user_data['post']['image']:
            update.message.reply_photo(photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'],
            caption_entities=context.user_data['post']['text_entities'],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Yuborish!", callback_data="send_current_post"),
                        InlineKeyboardButton(
                            "Qayta yozish", callback_data="error_post")
                    ]
                ]
            ))
            return CHECK_POST
        else:
            update.message.reply_text(context.user_data['post']['text'],
            entities=context.user_data['post']['text_entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Yuborish!", callback_data="send_current_post"),
                        InlineKeyboardButton(
                            "Qayta yozish", callback_data="error_post")
                    ]
                ]
            ))
            return CHECK_POST

    def send_post(self, update: Update, context: CallbackContext):
        users = (User.objects.all(),) if context.user_data['post']['type'] == 1 else ((ZoomUser.objects.all(
        ),) if context.user_data['post']['type'] == 0 else (User.objects.all(), ZoomUser.objects.all()))
        sent_ids = []
        peer = 0
        for types in users:
            for user in types:
                peer += 1
                if user.id in sent_ids:
                    continue
                sent_ids.append(user.id)
                if context.user_data['post']['image']:
                    try:
                        self.bot.send_photo(
                            chat_id=user.chat_id,
                            caption_entities=context.user_data['post']['text_entities'],
                            photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'])
                    except:
                        pass
                else:
                    try:
                        self.bot.send_message(
                            chat_id=user.chat_id,
                            entities=context.user_data['post']['text_entities'],
                            text=context.user_data['post']['text'])
                    except:
                        pass
                if peer == 25:
                    time.sleep(0.5)
                    peer = 0
        text = "Habar barcha trening qatnashchilariga yuborildi!" if context.user_data['post']['type'] == 0 else (
            "Habar barcha shogirdlarga yuborildi!" if context.user_data['post']['type'] == 1 else "Habar barcha foydalanuvchilarga yuborildi!")
        update.callback_query.message.reply_text(
            f"Habar barcha foydalanuvchilarga yuborildi!")
        return -1

    def error_post(self, update: Update, context: CallbackContext):
        context.user_data['post'] = {}
        update.message.reply_text(
            "Iltimos postni kimlarga yuborilishini tanlang!", reply_markup=ReplyKeyboardMarkup([
                [
                    "Trening ishtirokchilariga",
                    "Shogirdlarga"
                ],
                [
                    "Hammaga"
                ]
            ], resize_keyboard=True))
        return POST_TYPE
    
    def post_forward(self, update:Update, context:CallbackContext):
        if not update.message.from_user.id in admins:
            return -1
        text = update.message.text if update.message.text else update.message.caption
        img = update.message.photo
        context.user_data['post']['text'] = text
        context.user_data['post']['image'] = img
        context.user_data['post']['text_entities'] = update.message.entities if update.message.entities else update.message.caption_entities
        update.message.reply_text(
            "marhamat sizning postingiz!\n\nMaq'ul bo'lsa yuborish tugmasini bosing!")
        if context.user_data['post']['image']:
            update.message.reply_photo(photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'],
            caption_entities=context.user_data['post']['text_entities'],
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Yuborish!", callback_data="send_current_post"),
                        InlineKeyboardButton(
                            "Qayta yozish", callback_data="error_post")
                    ]
                ]
            ))
            return CHECK_POST
        else:
            update.message.reply_text(context.user_data['post']['text'],
            entities=context.user_data['post']['text_entities'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Yuborish!", callback_data="send_current_post"),
                        InlineKeyboardButton(
                            "Qayta yozish", callback_data="error_post")
                    ]
                ]
            ))
            return CHECK_POST


        # Post.post_send(update, context)
        # return -1

    # def post_image(self, update:Update, context:CallbackContext):
    #     context.user_data['post']['image'] = update.message.photo
    #     update.message.reply_text("Iltimos endi post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
    #     return POST

    # def post_text(self, update:Update, context:CallbackContext):
    #     context.user_data['post']['text'] = update.message.text
    #     update.message.reply_text("marhamat sizning postingiz!\n\nMaq'ul bo'lsa yuborish tugmasini bosing!")
    #     if context.user_data['post']['image']:
    #         update.message.reply_photo(photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'], reply_markup=InlineKeyboardMarkup(
    #             [
    #                 [
    #                     InlineKeyboardButton("Yuborish!", callback_data="send_current_post")
    #                 ]
    #             ]
    #         ))
    #         return POST
    #     else:
    #         update.message.reply_text(context.user_data['post']['text'], reply_markup=InlineKeyboardMarkup(
    #             [
    #                 [
    #                     InlineKeyboardButton("Yuborish!", callback_data="send_current_post")
    #                 ]
    #             ]
    #         ))
    #         return POST

    # def send(self, update:Update, context:CallbackContext):
    #     users = User.objects.all()
    #     peer = 0
    #     for user in users:
    #         try:
    #             if context.user_data['post']['image']:
    #                 context.bot.send_photo(chat_id=user.chat_id, photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'])
    #             else:
    #                 context.bot.send_message(user.chat_id,context.user_data['post']['text'])
    #         except Exception as e:
    #             print(e)
    #         peer += 1
    #         if peer == 20:
    #             sleep(2)

    #     update.callback_query.message.reply_text("Habar barcha bot foydalanuvchilarga yuborildi!")
    #     return -1
