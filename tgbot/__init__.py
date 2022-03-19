from datetime import datetime
import os
import pathlib
from time import sleep, time
from uuid import uuid4
import zipfile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message, PassportElementErrorSelfie, ReplyKeyboardMarkup, ReplyKeyboardRemove, ReplyMarkup, Update
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
from bot.models import Region, Task, User, ZoomUser
from excel import makeexcelData
from tgbot.post import Post
from tgbot.zoom import Zoom
from utils import distribute

from .constants import *



root = pathlib.Path(__file__).resolve().parent.parent









class Bot(Updater, Zoom, Post):
    def __init__(self, *args, **kwargs):
        # super(Bot, self).__init__("5263596793:AAGp-Mwn4tw0v1u0TsxbhtInPmt-yDYzvBI")
        super(Bot, self).__init__("1955026889:AAFD98J6x8rW_0pftC4kktkTARDJALfrPGs")

        not_start = ~Filters.regex("^/start$")
        not_post = ~Filters.regex("^/post$")



        self.shogird_tushish_conversation = ConversationHandler(
            [
                MessageHandler(Filters.regex(f"^{shogird_tushish}$"), self.shogird),
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
                    RegexHandler(r"^\d{4}$", self.birth),
                    MessageHandler(Filters.text & not_start, self.birthday_month_year)
                ],
                TASKS: [
                    CommandHandler('start', self.start),
                    MessageHandler(Filters.regex("^(Ha|Qayta yuborish)") & not_start & not_post, self.yes_no),
                    MessageHandler((Filters.text | Filters.document)  & not_post , self.answer_sent_user),
                ],
            },
            [
                CommandHandler('start', self.start),
            ]
        )

        self.zoom_conversation = ConversationHandler(
            [
                MessageHandler(Filters.regex(f"^{zoomga_yozilish}$") & not_start,  self.zoomga_yozilish_handler),
            ],
            {
                ZOOM_NAME: [
                    MessageHandler(Filters.text & not_start, self.name_zoom)
                ],
                ZOOM_NUMBER: [
                    MessageHandler(Filters.contact & not_start, self.number_zoom)
                ],
            },
            [
                CommandHandler('start', self.start),
            ]
        )

        self.post_conversation = ConversationHandler(
            [
                CommandHandler('post', self.post_start),
            ],
            {
                POST_TYPE: [
                    MessageHandler(Filters.text, self.post_type)
                ],
                POST_IMAGE: [
                    MessageHandler(Filters.photo, self.post_image),
                    CommandHandler('skip', self.skip)
                    ],
                POST_TEXT: [MessageHandler(Filters.text & not_start, self.post_text)],
                CHECK_POST: [
                    CallbackQueryHandler(self.send_post, pattern="^send_current_post"),
                    CallbackQueryHandler(self.error_post, pattern="^error_post")
                    ]
            },
            [
                
            ]
        )

        # self.dispatcher.add_handler(CommandHandler('post', self.post_))
        self.dispatcher.add_handler(CommandHandler('data', self.data))
        self.dispatcher.add_handler(CallbackQueryHandler(self.accept_task, pattern="^accept_answer"))
        self.dispatcher.add_handler(CallbackQueryHandler(self.reject_task, pattern="^reject_answer"))
        self.dispatcher.add_handler(self.shogird_tushish_conversation)
        self.dispatcher.add_handler(self.zoom_conversation)
        self.dispatcher.add_handler(self.post_conversation)
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.start_polling()
        self.idle()
    
    def shogird(self, update:Update, context:CallbackContext):
        """start a new conversation"""
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if not user:
            context.user_data['register'] = {}
            update.message.reply_text("Assalom alekum Xush kelibsiz Ism Familyangizni kiriting!",reply_markup=ReplyKeyboardRemove())
            return NAME
        else:
            if user.panding_answer():
                update.message.reply_text("Iltimos yuborgan javobingizni javobi kelishini kuting!")
                return TASKS
            c = user.curent_task()
            if c:

                update.message.reply_text("Topshiriqlarni yuboring!")
                update.message.reply_html(c.description + "\n<b>.docx .pdf text</b> formatida yuboring!",
                                          reply_markup=ReplyKeyboardRemove())
                return TASKS
            else:
                update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
    

    # def start(self, update:Update, context:CallbackContext):
    #     """start a new conversation"""
    #     user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
    #     if not user:
    #         context.user_data['register'] = {}
    #         update.message.reply_text("Assalom alekum Xush kelibsiz Ism Familyangizni kiriting!",reply_markup=ReplyKeyboardRemove())
    #         return NAME
    #     else:
    #         if user.panding_answer():
    #             update.message.reply_text("Iltimos yuborgan javobingizni javobi kelishini kuting!")
    #             return TASKS
    #         c = user.curent_task()
    #         if c:

    #             update.message.reply_text("Topshiriqlarni yuboring!")
    #             update.message.reply_html(c.description + "\n<b>.docx .pdf text</b> formatida yuboring!",
    #                                       reply_markup=ReplyKeyboardRemove())
    #             return TASKS
    #         else:
    #             update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")

    def start(self, update:Update, context:CallbackContext):
        # user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        # if not user:
        context.user_data['register'] = {}
        context.user_data['zoom'] = {}
        update.message.reply_text("Assalom alekum Xush kelibsiz!\n\nTanlang!",reply_markup=ReplyKeyboardMarkup(
            [
                [
                    shogird_tushish,
                    (zoomga_yozilish if not ZoomUser.objects.filter(chat_id=update.message.from_user.id).exists() else "") 
                ]
            ]
        , resize_keyboard=True))
        return ConversationHandler.END
        # else:
            # print('xxxx')

    def birthday_month_year(self, update:Update, context:CallbackContext):
        update.message.reply_text("Iltimos faqat tug'ilgan yilingizni yozing: Masalan: 2002")
        return BIRTH


    def accept_task(self, update:Update, context:CallbackContext):
        # user:User = User.objects.filter(chat_id=update.callback_query.from_user.id).first()
        # if user.panding_answer():
        #     update.callback_query.answer("Sizda yuborilgan javobingizni kiriting!")
        #     return TASKS
        # else:
        #     update.callback_query.answer("Sizda yuborilgan javobingizni kiriting!")
        #     return TASKS
        data = update.callback_query.data.split(":")
        task:Task = Task.objects.filter(id=int(data[1])).first()
        if task:
            task.accept()
            update.callback_query.answer("Javobingiz qabul qilindi!")
            for message in task.messages():
                context.bot.edit_message_caption(message.chat_id, message.message_id, caption="Bu javob tasdiqlandi!")
            try:
                context.bot.send_message(task.user.chat_id,
                    "Sizning javobingiz qabul qilindi!\nKeyingi topshiriqqa o'tishingiz mumkin!")
            except:...
            c = task.user.curent_task()
            if c:
                context.bot.send_message(task.user.chat_id, c.description + "\n<b>.docx .pdf text</b> formatida yuboring!", parse_mode="HTML")
                return TASKS
            else:
                context.bot.send_message(
                    task.user.chat_id, "Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
                zipFile = zipfile.ZipFile(f"{task.user.chat_id}_{task.user.name}.zip", 'w')
                tasks = task.user.tasks()
                for task in tasks:
                    print(f"{root}")
                    zipFile.write(os.path.join(root, task.document), os.path.relpath(os.path.join(root, task.document)))
                    os.remove(task.document)
                zipFile.close()
                for admin in admins:
                    context.bot.send_document(chat_id=admin,document=open(f"{task.user.chat_id}_{task.user.name}.zip", 'rb'))
            return TASKS
    
    def reject_task(self, update:Update, context:CallbackContext):
        data = update.callback_query.data.split(":")
        task:Task = Task.objects.filter(id=int(data[1])).first()
        if task:
            task.reject()
            update.callback_query.answer("Javobingiz qabul qilindi!")
            for message in task.messages():
                context.bot.edit_message_caption(
                    message.chat_id, message.message_id, caption="Bu javob rad etib bo'lindi!!")
            c = task.user.curent_task()
            try:
                context.bot.send_message(task.user.chat_id,
                "Sizning javobingiz rad etildi!\nIstasangiz qayta yuboring")
            except:...
            if c:
                try:
                    context.bot.send_message(task.user.chat_id, c.description +
                                     "\n<b>.docx .pdf text</b> formatida yuboring!", parse_mode="HTML")
                except:...
                return TASKS
            else:
                context.bot.send_message(
                    task.user.chat_id, "Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
                zipFile = zipfile.ZipFile(f"{task.user.chat_id}_{task.user.name}.zip", 'w')
                tasks = task.user.tasks()
                for task in tasks:
                    print(f"{root}")
                    zipFile.write(os.path.join(root, task.document), os.path.relpath(os.path.join(root, task.document)))
                    os.remove(task.document)
                zipFile.close()
                for admin in admins:
                    try:
                        context.bot.send_document(chat_id=admin,document=open(f"{task.user.chat_id}_{task.user.name}.zip", 'rb'))
                    except:...
            return TASKS
    
    def answer_sent_user(self, update:Update, context:CallbackContext):
        if update.message.text == "/start":
            return self.start(update, context)
        print(update.message.text)
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if user.panding_answer():
                update.message.reply_text("Iltimos yuborgan javobingizni javobi kelishini kuting!")
                return TASKS
        if update.message.text:
            context.user_data['current_data'] = update.message.text
            context.user_data['current_data_type'] = 0
            update.message.reply_text("To'liq javobingiz shumi yoki qayta yuboarsizmi!", reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "Ha", "Qayta yuborish"
                    ]
                ]
            , resize_keyboard=True))
        
        elif update.message.document:
            context.user_data['current_data_type'] = 1
            context.user_data['current_data'] = update.message.document.get_file().download(f"files/{user.curent_task().id}_{str(uuid4())}_{update.message.document.file_name}")
            update.message.reply_text("To'liq javobingiz shumi yoki qayta yuboarsizmi!", reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        "Ha", "Qayta yuborish"
                    ]
                ]
            , resize_keyboard=True))
        
    def yes_no(self, update:Update, context:CallbackContext):
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if update.message.text.lower() == "ha":
            data = context.user_data['current_data']
            
            if user:
                if user.tasks().count() < tasks_number:
                    if context.user_data['current_data_type'] == 0:
                        filename = f"files/{user.curent_task().id}_{str(uuid4())}_answer.txt"
                        file = open(filename, 'w')
                        file.write(data)
                        file.close()
                    else:
                        filename = context.user_data['current_data']
                    answer: Task = user.add_task(filename, context.user_data['current_data_type'])
                    for admin in admins:
                        try:
                            # message:Message = context.bot.send_message(admin, "gdfgdfg", reply_markup=InlineKeyboardMarkup(
                            #     [
                            #         [
                            #             InlineKeyboardButton( "Qabul qilish", callback_data=f"accept_answer:{answer.id}"),
                            #             InlineKeyboardButton( "Rad etish", callback_data=f"reject_answer:{answer.id}")
                            #         ]
                            #     ]
                            # ))
                            message:Message = context.bot.send_document(admin, document=open(filename, 'rb'), reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton( "Qabul qilish", callback_data=f"accept_answer:{answer.id}"),
                                        InlineKeyboardButton( "Rad etish", callback_data=f"reject_answer:{answer.id}")
                                    ]
                                ]
                            ))
                            answer.send(message)

                        except Exception as e:
                            print(e)
                    update.message.reply_text("Javobingiz tekishirilmoqda.Agar siz topshiriqdan o'tsangiz o'zimiz habar beramiz", reply_markup=ReplyKeyboardRemove())
                else:   
                    update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz", reply_markup=ReplyKeyboardRemove())
                



        elif update.message.text.lower() == "qayta yuborish":
            update.message.reply_html(user.curent_task(
            ).description + "<b>.docx .pdf text</b> formatida yuboring!", reply_markup=ReplyKeyboardRemove())
            return TASKS
    

    
    

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
                update.message.reply_text("Muvaffaqiyatli ro'yxatdan o'tdingiz!\nIltimos endi topshiriqlarni yuboring!")
                c = user.curent_task()
                if c:
                    update.message.reply_html(
                        c.description + "\n<b>.docx .pdf text</b> formatida yuboring!", reply_markup=ReplyKeyboardRemove())
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
                file = update.message.document.get_file().download(f"files/{user.curent_task().id}_{str(uuid4())}_{update.message.document.file_name}")
                user.add_task(file)
                c = user.curent_task()
                if c:
                    update.message.reply_html(
                        c.description + "\n<b>.docx .pdf text</b> formatida yuboring!", reply_markup=ReplyKeyboardRemove())
                    return TASKS
                else:
                    update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz", reply_markup=ReplyKeyboardRemove())
                    zipFile = zipfile.ZipFile(f"{user.chat_id}_{user.name}.zip", 'w')
                    tasks = user.tasks()
                    for task in tasks:
                        zipFile.write(os.path.join(root, task.document), os.path.relpath(os.path.join(root, task.document)))
                        os.remove(task.document)
                    zipFile.close()
                    for admin in admins:
                        context.bot.send_document(chat_id=admin,document=open(f"{user.chat_id}_{user.name}.zip", 'rb'))
                    

            else:   
                update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz")
    
    def error_type(self, update:Update, context:CallbackContext):
        update.message.reply_html("Kechirasiz javoblaringizni faqat <b>.docx .pdf text</b> formatida yubora olasiz!",
                                  reply_markup=ReplyKeyboardRemove())


    def task_text(self, update:Update, context:CallbackContext):
        user:User = User.objects.filter(chat_id=update.message.from_user.id).first()
        if user:
            if user.tasks().count() < tasks_number:
                filename = f"files/{user.curent_task().id}_{str(uuid4())}_answer.txt"
                file = open(filename, 'w')
                file.write(update.message.text)
                file.close()
                user.add_task(filename)
                c = user.curent_task()
                if c:
                    update.message.reply_html(
                        c.description + "\n<b>.docx .pdf text</b> formatida yuboring!", reply_markup=ReplyKeyboardRemove())
                    return TASKS
                else:
                    update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz", reply_markup=ReplyKeyboardRemove())
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
                update.message.reply_text("Siz topshiriqlarni yakunladingiz ishtirokingiz uchun raxmat. Biz sizga tez orada aloqaga chiqamiz", reply_markup=ReplyKeyboardRemove())
    


        
    
    
    
        
    
    
    def data(self, update:Update, context:CallbackContext):
        if update.message.from_user.id in admins:
            update.message.from_user.send_document(makeexcelData(), 'data.xlsx')
