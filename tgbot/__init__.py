from datetime import datetime
import os
import pathlib
from uuid import uuid4
import zipfile
from setuptools import Command
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CallbackContext,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    CallbackQueryHandler,
    RegexHandler
)
from bot.models import Region, User
from utils import distribute


root = pathlib.Path(__file__).resolve().parent.parent
admins = [1238844694]


NAME, NUMBER, REGION, BIRTH, TASKS, POST = range(6)

minimum_year,maximum_year = 1990, datetime.now().year
tasks_number = 10




class Bot(Updater):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__("1955026889:AAFfjBn0PRv-z3-QA_yx2uG_e86XbvF8tho")

        not_start = ~Filters.regex("^/start$")
        self.conversation = ConversationHandler(
            [
                CommandHandler('start', self.start),
                CommandHandler('post', self.post)
            ],
            {
                NAME: [
                    MessageHandler(Filters.text & not_start, self.name)
                ],
                NUMBER: [
                    MessageHandler(Filters.contact & not_start, self.number)
                ],
                REGION: [
                    MessageHandler(Filters.text & not_start, self.region)
                ],
                BIRTH: [
                    RegexHandler(r"^\d{4}$", self.birth)
                ],
                TASKS: [
                    MessageHandler(Filters.document & not_start, self.tasks)
                ],
                POST: [
                    MessageHandler(Filters.photo, self.photo),
                    CommandHandler('skip', self.skip),
                    MessageHandler(Filters.text & not_start, self.text),
                    CallbackQueryHandler(self.send, pattern="^send_current_post")
                ]
            },
            [
                CommandHandler('start', self.start),
                CommandHandler('post', self.post)
            ]
        )
        self.dispatcher.add_handler(self.conversation)
        self.start_polling()
        self.idle()
    

    def start(self, update:Update, context:CallbackContext):
        """start a new conversation"""
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if not user:
            context.user_data['register'] = {}
            update.message.reply_text("Assalom alekum Xush kelibsiz Ism Familyangizni kiriting!",reply_markup=ReplyKeyboardRemove())
            return NAME
        else:
            c = user.curent_task()
            if c:

                update.message.reply_text("Topshiriqlarni yuboring!")
                update.message.reply_text(c.description)
                return TASKS
            else:
                update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
    def name(self, update:Update, context:CallbackContext):
        if len(update.message.text.split()) > 1:
            context.user_data['register']['name'] = update.message.text
            update.message.reply_text("Telefon raqamingizni yuboring!", reply_markup=ReplyKeyboardMarkup(
                [[
                    KeyboardButton("Yuborish", request_contact=True)
                ]]
            , resize_keyboard=True))
            return NUMBER
        else:
            update.message.reply_text("Iltimos ismingizni to'g'ri yozing!")
    

    def number(self, update:Update, context:CallbackContext):
        context.user_data['register']['number'] = update.message.contact.phone_number
        update.message.reply_text("Endi viloyatingizni tanlang!", reply_markup=ReplyKeyboardMarkup(
            distribute([reg.name for reg in Region.objects.all() ], 2)
        , resize_keyboard=True))
        return REGION
    def region(self, update:Update, context:CallbackContext):
        region = Region.objects.filter(name=update.message.text).first()
        if region:
            context.user_data['register']['region'] = region
            update.message.reply_text("Endi tug'ilgan yilingizni  yuboring!",reply_markup=ReplyKeyboardRemove())
            return BIRTH
        else:
            update.message.reply_text("Viloyat topilmadi!")
            return REGION
    
    def birth(self, update:Update, context:CallbackContext):
        if update.message.text.isdigit():
            year = int(update.message.text.strip())
            if year > minimum_year and year < maximum_year:
                user:User = User.objects.create(chat_id=update.message.from_user.id, **context.user_data['register'], birthday=year)
                update.message.reply_text("Iltimos endi topshiriqlarni yuboring!")
                c = user.curent_task()
                if c:
                    update.message.reply_text(c.description)
                    return TASKS
                else:
                    update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")

                return TASKS
            else:
                update.message.reply_text(f"Tug'ilgan yilingiz 1990 va {datetime.now().year-15} oralig'ida bo'lishi kerak!")
                return BIRTH
        else:
            update.message.reply_text("Tug'ilgan yilingizni to'g'ri kiriting")
            return BIRTH

    def tasks(self, update:Update, context:CallbackContext):
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if user:
            if user.tasks().count() < tasks_number:
                file = update.message.document.get_file().download(f"files/{str(uuid4())}_{update.message.document.file_name}")
                user.add_task(file)
                c = user.curent_task()
                if c:
                    update.message.reply_text(c.description)
                    return TASKS
                else:
                    update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
                    zipFile = zipfile.ZipFile(f"{user.chat_id}_{user.name}.zip", 'w')
                    tasks = user.tasks()
                    for task in tasks:
                        print(f"{root}")
                        zipFile.write(os.path.join(root, task.document), os.path.relpath(os.path.join(root, task.document)))
                        os.remove(task.document)
                    zipFile.close()
                    for admin in admins:
                        context.bot.send_document(chat_id=admin,document=open(f"{user.chat_id}_{user.name}.zip", 'rb'))
                    

            else:   
                update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
        
    def post(self, update:Update, context:CallbackContext):
        if update.message.from_user.id in admins:
            context.user_data['post'] = {}
            update.message.reply_text("Iltimos post uchun suratni yuboring yoki /skip kommandasini yuboring!")
            return POST
    
    def skip(self, update:Update, context:CallbackContext):
        context.user_data['post']['image'] = None
        update.message.reply_text("Iltimos endi post uchun matn yuboring!")
        return POST
    def photo(self, update:Update, context:CallbackContext):
        context.user_data['post']['image'] = update.message.photo
        update.message.reply_text("Iltimos endi post uchun matn yuboring!")
        return POST
    
    def text(self, update:Update, context:CallbackContext):
        context.user_data['post']['text'] = update.message.text
        update.message.reply_text("marhamat sizning postingiz!\n\nMaq'ul bo'lsa yuborish tugmasini bosing!")
        if context.user_data['post']['image']:
            update.message.reply_photo(photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Yuborish!", callback_data="send_current_post")
                    ]
                ]
            ))
            return POST
        else:
            update.message.reply_text(context.user_data['post']['text'], reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Yuborish!", callback_data="send_current_post")
                    ]
                ]
            ))
            return POST
        
    def send(self, update:Update, context:CallbackContext):
        users = User.objects.all()
        for user in  users:
            try:
                if context.user_data['post']['image']:
                    context.bot.send_photo(chat_id=user.chat_id, photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'])
                else:
                    context.bot.send_message(user.chat_id,context.user_data['post']['text'])
            except Exception as e:
                print(e)
        update.callback_query.message.reply_text("Habar barcha bot foydalanuvchilarga yuborildi!")
        return -1