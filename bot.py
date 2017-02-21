# -*- coding: utf-8 -*-

import config
import telebot
import baza
import re
import csv
import os

bot = telebot.TeleBot(config.token) #@quickbase_bot

password_set=["111","222","333"]  #пароль доступа
id_pass = []                      #сюда id пользователей
gen_dic={}                          #словарь для составления последовательности перед записьюй в бд
stop_set = ["Стоп","стоп","stop","Stop"]  # набор слов для выхода из систем
check_find = {}                         #чек список для функции поиска по дате 
exit_key = "end"


def post_file(message):
    db = baza.Basesql('base_doc.db', 'users')
    a = db.mass_row()

    name_file = '{0}.csv'.format(message.chat.id)
    with open(name_file, 'w',encoding="cp1251") as csv_file:
        csv_writer = csv.writer(csv_file,delimiter=';',quotechar='|')
        for num,item in enumerate(a):
            csv_writer.writerow(a[num])

    with open(name_file, 'rb') as doc:
        bot.send_document(message.chat.id, doc)
    os.remove(name_file)

def save_to_base(gen_dic,message):             # функция записи в базу
    db = baza.Basesql('base_doc.db', 'users')  # подключение к бд
    if len(gen_dic[message.chat.id])<5:        # если длинна слдоваря меньше 5
        numm=5-len(gen_dic[message.chat.id])   # подсчитваем колличество нехватающих элементов , если юзер ввел только 4 то numm будет равен 1
        for i in range(numm):
            gen_dic[message.chat.id].append(0)  #добавляем  в список  недостоющие элементы   =  нули
        db.insert_db(gen_dic[message.chat.id][0], gen_dic[message.chat.id][1], gen_dic[message.chat.id][2], 
                     gen_dic[message.chat.id][3], gen_dic[message.chat.id][4]) # добавляем в базу инфу в 4 поля, тут с нулями вместе незаполенных элементов
    else:
        db.insert_db(gen_dic[message.chat.id][0], gen_dic[message.chat.id][1], gen_dic[message.chat.id][2], 
                     gen_dic[message.chat.id][3], gen_dic[message.chat.id][4])  # тут ввод если юзер ввел всю необходимую инфу
        
    print(len(gen_dic[message.chat.id]))
    
    if len(gen_dic[message.chat.id]) >= 5:      #колличество элементов в списке должно быть больше или равно 5
        gen_dic[message.chat.id].clear()        # очистка списка после записи в бд
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

@bot.message_handler(content_types=["text"],func = lambda message: message.chat.id in id_pass
                     and check_find[message.chat.id]== 1)
def date_find_doc(message):  #поиск по дате 
    datafind = re.findall(r'\d{2}.\d{2}.\d{4}',message.text)  # в поиск проходит только дата , регулярка
    if check_find[message.chat.id]== 1 and datafind and message.text != exit_key:  #
        db = baza.Basesql('base_doc.db', 'users')
        a = db.date_find_row(datafind[0]) # так как после нахождения даты получается список, берем по первому элементу списка
        if a :  #если записи есть в базе (TRUE)
            for i in range(len(a)):
                bot.send_message(message.from_user.id,", ".join(a[i]))
            check_find[message.chat.id] = 0 # обнуляем счетчик
        else:
            bot.send_message(message.from_user.id, "Contracts with the date not found")
    if check_find[message.chat.id]== 1 and not datafind and message.text != exit_key: # если введена дата не в формате 00.00.0000
        bot.send_message(message.from_user.id,"You have entered the date")
    if message.text == exit_key:
        check_find[message.chat.id] = 0
        bot.send_message(message.from_user.id, "You came out of the search function by date")

def state_mes (message):                #функция проверющая состояние пользователя
    if message.text in stop_set:        # если  слово в стоп листе
        if message.chat.id in id_pass : # если пользователь авторизован
            bot.send_message(message.from_user.id,"You logged off") # сообщение о выходе из систем
            id_pass.remove(message.chat.id)   #удаляем id пользователя из списка
            gen_dic[message.chat.id]=[]       #обнуляем список
            gen_dic[message.chat.id].append(message.chat.id)  #добавляем в список айди для дальнейшей записи в базу 


@bot.message_handler(commands = ["start","help"])
def start(message):
    bot.send_message(message.from_user.id,"Hi, enter the password if you are not logged in")

@bot.message_handler(commands=["find","findmy","datafind","savefile"],func = lambda message: message.chat.id in id_pass) # запуск поиска всей инфы из базы
def find_row(message):              # запускам функцию печати из базы 
    if message.text =="/find":
        find_all_user_doc(message)
    if message.text == "/findmy":
        find_my_list(message)
    if message.text == "/datafind":
        bot.send_message(message.from_user.id,"Enter the data") 
        check_find[message.chat.id]=1    #после предложения ввода даты счетчик устанвливаем в положение 1 
    if message.text =="/savefile":
        post_file(message)
             
@bot.message_handler(func = lambda message: message.text not in password_set and message.chat.id not in id_pass)
def state_access(message):
    return bot.send_message(message.from_user.id,"Password error!")

@bot.message_handler(func = lambda message: message.text in password_set) #авторизация по паролю
def save_new_id(message):
    bot.send_message(message.from_user.id,"The correct password!")
    bot.send_message(message.from_user.id, """To enter data into the database enter in the chat, first name, number,start date,end date and type in chat the word 'end' is the key, meaning the beginning of the record to the database.""")
    check_find[message.chat.id]= 0

    if message.chat.id not in id_pass:              #если id нет в списке значит добавляем

        id_pass.append(message.chat.id)
        bot.send_message(message.from_user.id,"Your ID")
        bot.send_message(message.from_user.id, message.chat.id )
    else:
        bot.send_message(message.from_user.id,"You are already in the database")

@bot.message_handler(func = lambda message: message.chat.id in id_pass and check_find[message.chat.id] == 0)    # если авторизация выполнена 
def new_doc(message):
    state_mes(message)                          #отключение от системы
    if message.chat.id not in gen_dic.keys():   #если айди не в словаре
        gen_dic[message.chat.id]=[]             #создаем по ключу  пустой список
        if message.text not in stop_set:        #если ввод не в стоп листе
            gen_dic[message.chat.id].append(message.chat.id)  #добавляем в список первым элементом айди юзера
            gen_dic[message.chat.id].append(message.text)     #после уже добавляем ввод пользователя
            print(gen_dic[message.chat.id])
        if message.text == exit_key:           #если введено слово end деламе запись в базу
            gen_dic[message.chat.id].remove(exit_key)  #удаляем слово из списка что бы она не попало в базу
            save_to_base(gen_dic,message)           # передаем словарь в функцию записи в базу
    else:
        if message.text not in stop_set:
            gen_dic[message.chat.id].append(message.text)
            print(gen_dic[message.chat.id])
        if message.text == exit_key:           #если введено слово end деламе запись в базу
            gen_dic[message.chat.id].remove(exit_key)
            save_to_base(gen_dic,message)

bot.polling(none_stop=True)

