# -*- coding: utf-8 -*-

import config
import telebot
import baza
import re

bot = telebot.TeleBot(config.token) #@quickbase_bot

password_set=["111","222","333"]  #пароль доступа
id_pass = []                      #сюда кладутся id пользователей
gen_dic={}
stop_set = ["Стоп","стоп","stop","Stop"]  # набор слов для выхода из систем
check_find = {}

def save_to_base(gen_dic,message):             # функция записи в базу
    db = baza.Basesql('base_doc.db', 'users')  # подключение к бд
    db.insert_db(gen_dic[message.chat.id][0], gen_dic[message.chat.id][1], gen_dic[message.chat.id][2], 
                         gen_dic[message.chat.id][3], gen_dic[message.chat.id][4]) # добавляем в базу инфу в 4 поля
    print(len(gen_dic[message.chat.id]))
    if len(gen_dic[message.chat.id]) >= 5:      #колличество элементов в списке
        gen_dic[message.chat.id].clear()
        gen_dic[message.chat.id].append(message.chat.id)        # добавялем в начало списка id для дальнейшей работы и добавления новых данных
        print("to new list for doc = ",gen_dic)

def find_all_user_doc(message):  # печать всех записей
    db = baza.Basesql('base_doc.db', 'users') # подключение к бд
    a = db.mass_row()                         #выбираем все строки
    for i in range(len(a)):
        bot.send_message(message.from_user.id,", ".join(a[i])) # печатаем строки из базы
        
def find_my_list(message): #печать строк сделанных только под id юзера
    db = baza.Basesql('base_doc.db', 'users')   # подключение к бд
    a = db.select_single(message.chat.id)       #выбираем только записи сделанные пользователем
    for i in range(len(a)):
        bot.send_message(message.from_user.id,", ".join(a[i])) 

@bot.message_handler(content_types=["text"],func = lambda message: message.chat.id in id_pass and check_find[message.chat.id]== 1)
def date_find_doc(message):
    print("data find")
    if check_find[message.chat.id]== 1:
        datafind = re.findall(r'\d{2}.\d{2}.\d{4}',message.text)
        print(datafind)
        db = baza.Basesql('base_doc.db', 'users')
        a = db.date_find_row(datafind[0])
        for i in range(len(a)):
            bot.send_message(message.from_user.id,", ".join(a[i]))
        check_find[message.chat.id] = 0

def state_mes (message):                #функция проверющая состояние пользователя
    if message.text in stop_set:        # если  слово в стоп листе
        if message.chat.id in id_pass : # если пользователь авторизован
            bot.send_message(message.from_user.id,"You logged off") # сообщение о выходе из систем
            id_pass.remove(message.chat.id)   #удаляем id пользователя из списка

@bot.message_handler(commands = ["start","help"])
def start(message):
    bot.send_message(message.from_user.id,"Hi, enter the password if you are not logged in")

@bot.message_handler(commands=["find","findmy","datafind"],func = lambda message: message.chat.id in id_pass) # запуск поиска всей инфы из базы
def find_row(message):              # запускам функцию печати из базы 
    if message.text =="/find":
        find_all_user_doc(message)
    if message.text == "/findmy":
        find_my_list(message)
    if message.text == "/datafind":
       bot.send_message(message.from_user.id,"Enter data")
       check_find[message.chat.id]=1
             
@bot.message_handler(func = lambda message: message.text not in password_set and message.chat.id not in id_pass)
def state_access(message):
    return bot.send_message(message.from_user.id,"Password error!")

@bot.message_handler(func = lambda message: message.text in password_set) #авторизация по паролю
def save_new_id(message):
    bot.send_message(message.from_user.id,"The correct password!")
    check_find[message.chat.id]= 0
    print("check_find = " ,check_find[message.chat.id])

    if message.chat.id not in id_pass:              #если id нет в списке значит добавляем

        id_pass.append(message.chat.id)
        bot.send_message(message.from_user.id,"Your ID")
        bot.send_message(message.from_user.id, message.chat.id )
    else:
        bot.send_message(message.from_user.id,"You are already in the database")

@bot.message_handler(func = lambda message: message.chat.id in id_pass and check_find[message.chat.id] == 0)    # если авторизация выполнена 
def new_doc(message):
    state_mes(message)
    if message.chat.id not in gen_dic.keys():
        gen_dic[message.chat.id]=[] 
        if message.text not in stop_set:
            gen_dic[message.chat.id].append(message.chat.id)
            gen_dic[message.chat.id].append(message.text)
            print(gen_dic[message.chat.id])
        if message.text == "end":           #если введено слово end деламе запись в базу 
            save_to_base(gen_dic,message)
    else:
        if message.text not in stop_set:
            gen_dic[message.chat.id].append(message.text)
            print(gen_dic[message.chat.id])
        if message.text == "end":           #если введено слово end деламе запись в базу
            print(message)
            save_to_base(gen_dic,message)
        

bot.polling(none_stop=True)

