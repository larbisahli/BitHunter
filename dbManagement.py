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
        self.cursor = api if self._name.split("_")[0] == "Prevalues" else c

    def create(self):
        try:
            if self._name.split("_")[0] == "Journal":
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                    id INTEGER PRIMARY KEY,
                                    month_year TEXT,
                                    date TEXT,
                                    amount REAL,
                                    entry REAL,
                                    exit REAL,
                                    result REAL
                                    )""")
            elif self._name.split("_")[0] == "Notes":
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                    title TEXT PRIMARY KEY,
                                    date TEXT,
                                    Note TEXT
                                    )""")
            elif self._name.split("_")[0] == "Prevalues":
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                    id TEXT PRIMARY KEY,
                                    data TEXT
                                    )""")

            elif self._name == "Sign":
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self._name}(
                                                username TEXT PRIMARY KEY,
                                                password TEXT,
                                                pass TEXT
                                                )""")
        except Exception:
            pass

    def drop(self):
        try:
            sql = f"DROP TABLE {self._name}"
            with conn:
                self.cursor.execute(sql)
        except Exception:
           pass

    @property
    def check(self):
        try:
            with conn:
                query = f"SELECT name from sqlite_master WHERE type='table' AND name='{self._name}';"
                result = self.cursor.execute(query).fetchone()
            return False if result is None else result[0] == self._name
        except sqlite3.Error:
            pass
        except Exception:
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
        except Exception:
            pass
        finally:
            lock.release()


class Journal:

    def __init__(self, name, id_, month_year, date, amount, entry, exit_, result):
        self.id_ = id_
        self.date = date
        self.month_year = month_year
        self.amount = amount
        self.entry = entry
        self.exit_ = exit_
        self.result = result
        self.name = name

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"INSERT INTO {self.name} VALUES (:id, :month_year, :date, :amount, :entry, :exit, :result)"
                          , {"id": self.id_, 'month_year': self.month_year,'date': self.date,
                             "amount": self.amount, "entry": self.entry, "exit": self.exit_, "result": self.result})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"""UPDATE {self.name} SET amount = :amount, entry = :entry, exit = :exit,
                              result = :result WHERE id = :id""", {"id": self.id_, "amount": self.amount,
                                                                   "entry": self.entry, "exit": self.exit_,
                                                                   "result": self.result})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def update_one(self, value):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"""UPDATE {self.name} SET id = :id_ WHERE id = :id""", {"id": self.id_, "id_": value})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()


class Notes:

    def __init__(self, name, title, date, note):
        self.title = title
        self.date = date
        self.note = note
        self.name = name

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"INSERT INTO {self.name} VALUES (:title, :date, :note)",
                          {'title': self.title, 'date': self.date, 'note': self.note})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"""UPDATE {self.name} SET date = :date, note = :note WHERE title = :title""",
                          {'title': self.title, 'date': self.date, 'note': self.note})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def update_one(self, note):
        try:
            lock.acquire(True)
            with conn:
                c.execute(f"""UPDATE {self.name} SET note = :note WHERE title = :title""",
                          {"title": self.title, "note": note})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()


class Pre_values:

    def __init__(self, name, id_, data):
        self.id_ = id_
        self.data = data
        self.name = name

    def insert(self):
        try:
            lock.acquire(True)
            with conn:
                api.execute(f"INSERT INTO {self.name} VALUES (:id, :data)",
                            {'id': self.id_, 'data': self.data})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def update(self):
        try:
            lock.acquire(True)
            with conn:
                api.execute(f"""UPDATE {self.name} SET data = :data WHERE id = :id""",
                            {'id': self.id_, 'data': self.data})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()


class Extract:

    def __init__(self, name):
        self.name = name
        self.cursor = api if self.name.split("_")[0] == "Prevalues" else c

    def get_by_id(self, id_):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': id_})
                return [id_ for id_ in self.cursor.fetchall()[0]]
        except sqlite3.Error:
            pass
        except Exception:
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
        except Exception:
            pass
        finally:
            lock.release()

    def get_for_graph_combo(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"SELECT id, month_year FROM {self.name};")
                return self.cursor.fetchall()
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def check_cell(self, id_):
        try:
            check = [] if Extract(self.name).get_by_id(id_) is None else Extract(self.name).get_by_id(id_)
            if len(check) != 0:
                return True
            else:
                return False
        except IndexError:
            return False
        except Exception:
            return False

    def check_by(self, column, cell):
        try:
            data = Extract(self.name).get_by_column(column=column, cell=cell)
            final = [] if data is None else data
            if len(final) != 0:
                return True
            else:
                return False
        except IndexError:
            return False
        except Exception:
            return False

    def delete(self, where=None, cell=None):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"DELETE from {self.name} WHERE {where} = :column", {'column': cell})
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def select_column(self, column):
        try:
            lock.acquire(True)
            with conn:
                return [column[0] for column in self.cursor.execute(f"SELECT {column} FROM {self.name}")]
        except sqlite3.Error:
            pass
        except Exception:
            pass
        finally:
            lock.release()

    def fetchall(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"select * from '{self.name}'")
                return c.fetchall()
        except sqlite3.Error:
            return []
        finally:
            lock.release()

    def __len__(self):
        return len(self.select_column("id"))


conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()
api = conn.cursor()
lock = threading.Lock()
