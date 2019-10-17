
"""
            ####################################
            #                                  #
            #       Author: Larbi Sahli        #
            #                                  #
            #  https://github.com/Larbi-Sahli  #
            #                                  #
            ####################################
"""

import hashlib
import sqlite3
import threading
import onetimepad

# The key to encrypt and decrypt the user's personal data
key = "8bd305eff112e6a5289f4d0c43b412d06a7285d7c23510fb87d156703b06dcb6"


def hash_(password_):
    # hashing the username + the hashed password = identity (used to create unique database tables)
    return hashlib.sha256(password_.encode()).hexdigest()


def encrypt(data):
    return onetimepad.encrypt(data, key)


def decrypt(encrypted_data):
    return onetimepad.decrypt(encrypted_data, key)


# =================== <Database management> =====================

# Tables: journal, Notes, Pre_values, BTC_H_daily, BTC_H_weekly, BTC_H_monthly, sign


class Table:

    def __init__(self, name):
        self._name = name
        self._cursor = api if self._name in ["BTC_H_daily", "BTC_H_weekly", "BTC_H_monthly"] else c

    def create(self):
        if self._name.split("_")[0] == "Journal":
            c.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                id INTEGER PRIMARY KEY,
                                month TEXT,
                                year TEXT,
                                date TEXT,
                                amount REAL,
                                entry REAL,
                                exit REAL,
                                result REAL
                                )""")
        elif self._name.split("_")[0] == "Notes":
            c.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                title TEXT PRIMARY KEY,
                                date TEXT,
                                Note TEXT
                                )""")
        elif self._name.split("_")[0] == "Pre_values":
            c.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                id INTEGER PRIMARY KEY,
                                Wallet INTEGER,
                                Notify INTEGER,
                                Currency_exchange TEXT,
                                Open_trade TEXT,
                                combo INTEGER
                                )""")

        elif self._name.split("_")[0] in ["BTC_H_daily", "BTC_H_weekly", "BTC_H_monthly"]:
            api.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}( dwm INTEGER , date TEXT, price REAL )""")
            # we will be using thread to download bitcoin historical data online and upload it in database
            # we gonna need a temporary cursor (api) for that

        else:
            c.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                            username TEXT PRIMARY KEY,
                                            password TEXT,
                                            pass TEXT
                                            )""")

    def drop(self):
        sql = f"DROP TABLE {self._name}"
        with conn:
            self._cursor.execute(sql)

    @property
    def check(self):
        try:
            with conn:
                query = f"SELECT name from sqlite_master WHERE type='table' AND name='{self._name}';"
                result = self._cursor.execute(query).fetchone()
            return False if result is None else result[0] == self._name
        except sqlite3.Error:
            pass


""" Using 'with', will allows us to create a temporary cursor 
that will be closed once you return to your previous indentation level. """


class Sign:

    def __init__(self, password, username):

        self.pass_ = hash_(str(username))
        self.username = encrypt(str(username))
        self.password = encrypt(str(password))

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("INSERT INTO sign VALUES (:username, :password, :pass)",
                          {"pass": self.pass_, "password": self.password, 'username': self.username})
        except sqlite3.Error:
            pass
        finally:
            lock.release()


class Journal:

    def __init__(self, id_, month, year, date, amount, entry, exit_, result):
        self.id_ = id_
        self.date = date
        self.month = month
        self.year = year
        self.amount = amount
        self.entry = entry
        self.exit_ = exit_
        self.result = result

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("INSERT INTO Journal VALUES (:id, :month, :year, :date, :amount, :entry, :exit, :result)",
                          {"id": self.id_, 'month': self.month, 'year': self.year, 'date': self.date,
                           "amount": self.amount, "entry": self.entry, "exit": self.exit_, "result": self.result})
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("""UPDATE Journal SET amount = :amount, entry = :entry, exit = :exit,
                              result = :result WHERE id = :id""", {"id": self.id_, "amount": self.amount,
                                                                   "entry": self.entry, "exit": self.exit_,
                                                                   "result": self.result})
        except sqlite3.Error:
            pass
        finally:
            lock.release()


class Notes:

    def __init__(self, title, date, note):
        self.title = title
        self.date = date
        self.note = note

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("INSERT INTO Notes VALUES (:title, :date, :note)",
                          {'title': self.title, 'date': self.date, 'note': self.note})
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("""UPDATE Notes SET date = :date, note = :note WHERE title = :title""",
                          {'title': self.title, 'date': self.date, 'note': self.note})
        except sqlite3.Error:
            pass
        finally:
            lock.release()


class Pre_values:

    def __init__(self, id_, wallet, notify, currency, open_trade, combo):
        self.id_ = id_
        self.wallet = wallet
        self.notify = notify
        self.currency = currency
        self.open_trade = open_trade
        self.combo = combo

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("INSERT INTO pre_values VALUES (:id, :wallet, :notify, :currency, :open_trade, :combo)",
                          {'id': self.id_, 'wallet': self.wallet, 'notify': self.notify,
                           'currency': self.currency, 'open_trade': self.open_trade, 'combo': self.combo})
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute("""UPDATE pre_values SET :wallet, :notify, :currency, :open_trade, :combo
                              WHERE id = :id""",
                          {'id': self.id_, 'wallet': self.wallet, 'notify': self.notify,
                           'currency': self.currency, 'open_trade': self.open_trade, 'combo': self.combo})
        except sqlite3.Error:
            pass
        finally:
            lock.release()


class Historical_data:

    def __init__(self, value, date, price, name):
        self._value = value
        self._date = date
        self._price = price
        self._name = name

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                api.execute(f"INSERT INTO {self._name} VALUES (:dwm, :date, :price)",
                            {'dwm': self._value, 'date': self._date, 'price': self._price})
        except sqlite3.Error:
            pass
        finally:
            lock.release()


class Extract:

    def __init__(self, name):
        self.name = name
        self.cursor = api if self.name in ["BTC_H_daily", "BTC_H_weekly", "BTC_H_monthly"] else c

    def get_by_id(self, id_):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': id_})
                return [id_ for id_ in self.cursor.fetchall()[0]]
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def get_by_column(self, column=None, cell=None):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"SELECT * FROM {self.name} WHERE {column}= :column", {'column': cell})
                return [cell for cell in self.cursor.fetchall()[0]]
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def check_cell(self, id_):
        if len(Extract(self.name).get_by_id(id_)) != 0:
            return True
        else:
            return False

    def delete(self, where=None, cell=None):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"DELETE from {self.name} WHERE {where} = :column", {'column': cell})
        finally:
            lock.release()

    def select_column(self, column):
        try:
            lock.acquire(True)
            with conn:
                return [column[0] for column in self.cursor.execute(f"SELECT {column} FROM {self.name}")]
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def fetchall(self):
        c.execute(f"select * from '{self.name}'")
        return c.fetchall()

    def __len__(self):
        return len(self.select_column("id"))


conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
api = conn.cursor()
lock = threading.Lock()

#Journal(201, 3, 2019, "xxxx", 2344,2345, 2355,-0.345).insert()

#print(Extract(f'Journal').select_column("result"))


"""
the .api is the cursor for updates, this is to prevent any 
Recursive use of cursors while using other tables at the same 
time as the update happened."""
"""
====Tables and cursor====
 table-1: journal .c => rate_N .c  [x for x in a if x < 0 ] -  and sum()
                        rate_p .c  [x for x in a if x >= 0 ] + and sum()
                        ADD .c      sum(list)

 table-2: Notes .c

 table-3:  Pre_values => ["wallet .c", "notify .c", "Currency_api .c", "open_trade .c, combo_Month".]

 table-4-5-6: BTC_H_daily .api, BTC_H_weekly .api, BTC_H_monthly .api 

 table-7 sign

==============
"""
