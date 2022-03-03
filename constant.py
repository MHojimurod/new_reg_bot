from telegram import KeyboardButton


FIO, CONTACT,REGION,BIRTH = range(4)



def regions():
    data = [
        [KeyboardButton("Toshkent sh"),KeyboardButton("Toshken v")],
        [KeyboardButton("Andijon"),KeyboardButton("Namangan")],
        [KeyboardButton("Farg'ona"),KeyboardButton("Jizzax")],
        [KeyboardButton("Sirdaryo"),KeyboardButton("Surxondaryo")],
        [KeyboardButton("Xorazm"),KeyboardButton("Qashqadaryo")],
        [KeyboardButton("Samarqand"),KeyboardButton("Navoiy")],
        [KeyboardButton("Buxoro"),KeyboardButton("Qoraqalpog'iston")],
    ]
    return data