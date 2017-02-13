# -*- coding: utf-8 -*-

import config
import telebot
import baza

bot = telebot.TeleBot(config.token) #@quickbase_bot

password_set=["111","222","333"]  #пароль доступа
id_pass = []                      #сюда кладутся id пользователей
gen_doc=[]                        #тут записываем инфу перед записью в базу
stop_set = ["Стоп","стоп","stop","Stop"]  # набор слов для выхода из систем

def save_to_base(gen_doc,message):             # функция записи в базу
    db = baza.Basesql('base_doc.db', 'users')  # подключение к бд
    db.insert_db(gen_doc[0], gen_doc[1], gen_doc[2], gen_doc[3], gen_doc[4]) # добавляем в базу инфу в 4 поля
    print(len(gen_doc))
    if len(gen_doc) >= 5:                      #or message.text in stop_set:  #колличество элементов в списке
        gen_doc.clear()                        #очистка списка если больше или равно 5
        gen_doc.append(message.chat.id)        # добавялем в начало списка id для дальнейшей работы и добавления новых данных
        print("to new list for doc = ",gen_doc)

def find_all_user_doc(message):
    db = baza.Basesql('base_doc.db', 'users') # подключение к бд
    a = db.mass_row()                         #выбираем все строки
    for i in range(len(a)):
        bot.send_message(message.from_user.id,", ".join(a[i])) # печатаем строки из базы

def state_mes (message):                #функция проверющая состояние пользователя
    if message.text in stop_set:        # если  слово в стоп листе
        if message.chat.id in id_pass : # если пользователь авторизован
            bot.send_message(message.from_user.id,"You logged off") # сообщение о выходе из систем
            id_pass.remove(message.chat.id)   #удаляем id пользователя из списка

@bot.message_handler(commands = ["start","help"])
def start(message):
    bot.send_message(message.from_user.id,"Hi, enter the password if you are not logged in")

@bot.message_handler(commands=["find"],func = lambda message: message.chat.id in id_pass) # запуск поиска всей инфы из базы
def find_row(message):              # запускам функцию печати из базы 
    find_all_user_doc(message)

@bot.message_handler(func = lambda message: message.text not in password_set and message.chat.id not in id_pass)
def state_access(message):
    return bot.send_message(message.from_user.id,"Password error!")

@bot.message_handler(func = lambda message: message.text in password_set) #авторизация по паролю
def save_new_id(message):
    bot.send_message(message.from_user.id,"The correct password!")
    if  len(gen_doc) == 0:                          #если список пуст значит добавляем в начало списка id пользователя
        gen_doc.append(message.chat.id)
        
    if message.chat.id not in id_pass:              #если id нет в списке значит добавляем 
        id_pass.append(message.chat.id)
        bot.send_message(message.from_user.id,"Your ID")
        bot.send_message(message.from_user.id, message.chat.id )
    else:
        bot.send_message(message.from_user.id,"You are already in the database")


@bot.message_handler(func = lambda message: message.chat.id in id_pass)    # если авторизация выполнена 
def new_doc(message):
    state_mes(message)
    if message.text not in stop_set: 
        gen_doc.append(message.text)    #добавляем в список, слова введеные с клавиатуры
        print(gen_doc)
    if message.text == "end":           #если введено слово end деламе запись в базу 
        save_to_base(gen_doc,message)


bot.polling(none_stop=True)
