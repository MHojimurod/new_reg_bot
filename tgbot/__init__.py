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
from bot.models import Region, Task, User
from excel import makeexcelData
from utils import distribute



root = pathlib.Path(__file__).resolve().parent.parent
admins = [1238844694,429121485]


NAME, NUMBER, REGION, BIRTH, TASKS, POST = range(6)

minimum_year,maximum_year = 1950, datetime.now().year-14
tasks_number = 10





class Bot(Updater):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__("5263596793:AAGp-Mwn4tw0v1u0TsxbhtInPmt-yDYzvBI")
        # super(Bot, self).__init__("1955026889:AAFD98J6x8rW_0pftC4kktkTARDJALfrPGs")
        not_start = ~Filters.regex("^/start$")
        not_post = ~Filters.regex("^/post$")
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
                    MessageHandler(Filters.regex("^(Ha|Qayta yuborish)") & not_start & not_post, self.yes_no),
                    MessageHandler((Filters.text | Filters.document) & not_start & not_post, self.answer_sent_user),
                    # MessageHandler(Filters.document & not_start, self.tasks),
                    # MessageHandler((Filters.text & not_start) & ~Filters.regex("^/"), self.task_text),
                    # MessageHandler((Filters.text & not_start))
                ],
                POST: [
                    MessageHandler(Filters.photo, self.photo),
                    CommandHandler('skip', self.skip),
                    MessageHandler(Filters.text & not_start, self.text),
                    CallbackQueryHandler(self.send, pattern="^send_current_post", run_async=True),
                    MessageHandler((Filters.all & not_start), self.error_type)
                ]
            },
            [
                CommandHandler('start', self.start),
                CommandHandler('post', self.post)
            ]
        )
        self.dispatcher.add_handler(CommandHandler('data', self.data))
        self.dispatcher.add_handler(CallbackQueryHandler(self.accept_task, pattern="^accept_answer"))
        self.dispatcher.add_handler(CallbackQueryHandler(self.reject_task, pattern="^reject_answer"))
        self.dispatcher.add_handler(self.conversation)
        self.start_polling()
        self.idle()
    
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
                "Sizning javobingiz rad etildi!\nIstasangiz qayta yuboring yoki bo'ttan yoqolin!")
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
    

    def start(self, update:Update, context:CallbackContext):
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
    


    def post(self, update:Update, context:CallbackContext):
        if update.message.from_user.id in admins:
            context.user_data['post'] = {}
            update.message.reply_text("Iltimos post uchun suratni yuboring yoki /skip kommandasini yuboring!")
            return POST
    
    def skip(self, update:Update, context:CallbackContext):
        context.user_data['post']['image'] = None
        update.message.reply_text("Iltimos endi post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
        return POST
    def photo(self, update:Update, context:CallbackContext):
        context.user_data['post']['image'] = update.message.photo
        update.message.reply_text("Iltimos endi post uchun matn yuboring!", reply_markup=ReplyKeyboardRemove())
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
        peer = 0
        for user in users:
            try:
                if context.user_data['post']['image']:
                    context.bot.send_photo(chat_id=user.chat_id, photo=context.user_data['post']['image'][-1], caption=context.user_data['post']['text'])
                else:
                    context.bot.send_message(user.chat_id,context.user_data['post']['text'])
            except Exception as e:
                print(e)
            peer += 1
            if peer == 20:
                sleep(2)
            
        update.callback_query.message.reply_text("Habar barcha bot foydalanuvchilarga yuborildi!")
        return -1
    
    def data(self, update:Update, context:CallbackContext):
        if update.message.from_user.id in admins:
            update.message.from_user.send_document(makeexcelData(), 'data.xlsx')