import xlsxwriter

from bot.models import User, ZoomUser





def makeexcelData():
    workbook = xlsxwriter.Workbook('data.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'FIO')
    worksheet.write('B1', 'Viloyat')
    worksheet.write('C1', "Tug'ulgan yil")
    worksheet.write('D1', 'Telefon raqam')
    users: list[User] = User.objects.all()
    for user in range(users.count()):
        worksheet.write(f"A{user + 2}", users[user].name)
        worksheet.write(f"B{user + 2}", users[user].region.name)
        worksheet.write(f"C{user + 2}", users[user].birthday)
        worksheet.write(f"D{user + 2}", users[user].number)
    workbook.close()

    return open(workbook.filename, 'rb')


def makeexcelDataZoom():
    workbook = xlsxwriter.Workbook('zoom.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'FIO')
    worksheet.write('B1', 'Telefon raqam')
    users: list[User] = ZoomUser.objects.all()
    for user in range(users.count()):
        worksheet.write(f"A{user + 2}", users[user].name)
        worksheet.write(f"B{user + 2}", users[user].number)
    workbook.close()

    return open(workbook.filename, 'rb')