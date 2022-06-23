from datetime import datetime


#admins = [1238844694,429121485,2047287023,897491469,5087614516,1025888307]
admins = [1286879045, 897491469, 5267553371, 1025888307, 1238844694, 429121485]
NAME, NUMBER, REGION, BIRTH, TASKS, POST, ZOOM_NUMBER, ZOOM_NAME, POST_TYPE, POST_IMAGE, POST_TEXT, POST_SEND, CHECK_POST = range(1,14)
print(NAME, NUMBER, REGION, BIRTH, TASKS, POST, ZOOM_NUMBER, ZOOM_NAME)

minimum_year,maximum_year = datetime.now().year, datetime.now().year-14
tasks_number = 10

shogird_tushish = "Shogird tushish"
zoomga_yozilish = "Treningga yozilish"
