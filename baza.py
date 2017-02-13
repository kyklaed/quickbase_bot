# -*- coding: utf-8 -*-
"""
Класс работы с базой данных на чтение из нее,  создан для работ с ботом и базой прилагаемой к курсовой. основная функция
которая используется ботом это случайный выбор записи из базы + попутно подсчет колличества записей в базе.
"""

import sqlite3
import random
#database = 'cooking.db'
class Basesql:

    def __init__(self, database,name_table):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.name_table = name_table

    def insert_db(self, val,val1,val2,val3,val4):
        with self.connection:
            self.cursor.execute("INSERT INTO 'users' ('idchat', 'doc', 'docn', 'datastart', 'dataend') VALUES ('{0}','{1}','{2}','{3}','{4}')".format(val,val1,val2,val3,val4))
            self.connection.commit()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM users').fetchall()

    def select_single(self,rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM users WHERE id = ?', (rownum,)).fetchall()[0]

    def mass_row(self):
        with self.connection:
            return self.cursor.execute('SELECT doc, docn, datastart, dataend FROM users').fetchall()

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM {0}'.format(self.name_table)).fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()


#a =Basesql('cooking.db','vegan')
#print(a.select_random())
#print(a.select_all())
