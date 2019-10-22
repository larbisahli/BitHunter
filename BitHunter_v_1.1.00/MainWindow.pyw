# -*- coding: utf-8 -*-
"""
###################################
#                                 #
#       Author: Larbi Sahli       #
#                                 #
#  https://github.com/Larbi-Sahli #
#                                 #
###################################
"""

from json import JSONDecodeError

from os.path import expanduser
import matplotlib
import onetimepad
from PyQt5 import QtCore, QtGui, QtWidgets
import os
import sqlite3
import requests
import datetime
import time, traceback
import threading
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pandas import np
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from matplotlib import style
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from requests.exceptions import ConnectionError
import hashlib
from playsound import playsound

key = "8bd305eff112e6a5289f4d0c43b412d06a7285d7c23510fb87d156703b06dcb6"

# the key to encrypt and decrypt the user comments (Notes)


def hash_password(password):
    # hashing the username + the hashed password = identity (used to create unique database tables)
    return hashlib.sha256(password.encode()).hexdigest()


conn_sign = sqlite3.connect('pre_database.db', check_same_thread=False)
c_sign = conn_sign.cursor()


class ExtractData0:

    def __init__(self, _id_, name):
        self._id_ = _id_
        self.name = name

    def get_data(self):
        try:
            c_sign.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': self._id_})
            return c_sign.fetchall()
        except sqlite3.Error:
            pass


username = onetimepad.decrypt(eval(ExtractData0(1, "log_save").get_data()[0][1])["username"], key)
password = eval(ExtractData0(1, "log_save").get_data()[0][1])["password"]
identity = hash_password(str(username) + str(password))

conn = sqlite3.connect(f'{identity}.db', check_same_thread=False)
c = conn.cursor()
api = conn.cursor()

"""
the api is the cursor for updates, this is to prevent any Recursive use of cursors while using other tables at the same 
time as the update happened."""
"""
====Tables cursor====
rate_N .c
rate_p .c
ADD .c
comments .c
open_trade .c
save_ .c
graph_{year} .c
graph .c
journal .c
----------
api .api
wallet .api
Currency_api .api
notify .api
==============
"""

lock = threading.Lock()


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.0f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


"""Database management"""


class Table:

    def __init__(self, cursor, name):
        self.name = name
        self.cursor = cursor

    def create_table(self):
        self.cursor.execute(f"""CREATE TABLE {self.name}(
        id INTEGER PRIMARY KEY,
        data STRING
        )""")

    def drop_table(self):
        sql = f"DROP TABLE {self.name}"
        with conn:
            self.cursor.execute(sql)

    def check_table(self):
        try:
            with conn:
                self.cursor.execute(f"select * from '{self.name}'")
            return True
        except sqlite3.Error:
            return False


"""Use with, this tool allows you to create a temporary cursor 
that will be closed once you return to your previous indentation level."""


class InsertData:

    def __init__(self, cursor, _id_, _data_, name):
        self._id_ = _id_
        self._data_ = _data_
        self.name = name
        self.cursor = cursor

    def insert_data(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"INSERT INTO {self.name} VALUES (:id, :data)",
                                    {'id': self._id_, 'data': self._data_})
        finally:
            lock.release()

    def update_data(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"""UPDATE {self.name} SET data = :data WHERE id = :id""",
                                    {'id': self._id_, 'data': self._data_})

        except Exception:
            pass
        finally:
            lock.release()


class ExtractData:

    def __init__(self, cursor, _id_, name):
        self._id_ = _id_
        self.name = name
        self.cursor = cursor

    def get_data(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': self._id_})
                return self.cursor.fetchall()
        except Exception:
            pass
        finally:
            lock.release()

    def check_data(self):
        if str(ExtractData(self.cursor, self._id_, self.name).get_data()) != '[]':
            return True
        else:
            return False

    def delete(self):
        try:
            lock.acquire(True)
            with conn:
                self.cursor.execute(f"DELETE from {self.name} WHERE id = :id", {'id': self._id_})
        finally:
            lock.release()


# =========================api===============================

class API:  # class for API and the update loop (every)
    @staticmethod
    def stop_threads():
        return ExtractData(c_sign, 1, 'close').get_data()[0][1]

    @staticmethod
    def every(delay, task):
        next_time = time.time() + delay
        while True:
            if int(API.stop_threads()) != 0:  # this is to break the loop after the program closed
                time.sleep(max(0, next_time - time.time()))
                try:
                    task()
                except TypeError:
                    traceback.print_exc()
                # skip tasks if we are behind schedule:
                next_time += (time.time() - next_time) // delay * delay + delay
            else:
                break

    @staticmethod
    def btc():
        try:
            bitStampTick = requests.get('https://www.bitstamp.net/api/ticker/')
            status = bitStampTick.status_code
        except ConnectionError:
            status = 404
            pass
        if status == 200:
            try:
                xbtc = float(bitStampTick.json()['last'])
                btc = str(f"{int(xbtc):,d}") + "." + str(round(abs(xbtc - int(xbtc)), 2)).split(".")[1]
                return btc, xbtc
            except JSONDecodeError:
                return None
        else:
            return None

    @staticmethod
    def eth():
        try:
            bitStampTick = requests.get('https://www.bitstamp.net/api/v2/ticker/ethusd/')
            status = bitStampTick.status_code
        except ConnectionError:
            status = 404
            pass
        if status == 200:
            try:
                return bitStampTick.json()['last']
            except JSONDecodeError:
                return None
        else:
            return None

    @staticmethod
    def ltc():
        try:
            bitStampTick = requests.get('https://www.bitstamp.net/api/v2/ticker/ltcusd/')
            status = bitStampTick.status_code
        except ConnectionError:
            status = 404
            pass
        if status == 200:
            try:
                return bitStampTick.json()['last']
            except JSONDecodeError:
                return None
        else:
            return None

    @staticmethod
    def usd_sgd():
        key = '077fb69010a469f915e61de5995457d5'  # use your own key :)
        date_id = datetime.date.today().day + datetime.date.today().month + datetime.date.today().year
        if Table(api, 'api').check_table():
            sgd = eval(ExtractData(c, 1, "api").get_data()[0][1])["api"]
        else:
            sgd = 1.388501
        try:
            if not Table(api, 'api').check_table():
                Table(api, 'api').create_table()
                usdsgd = requests.get(f"http://www.apilayer.net/api/live?access_key={key}&format=1")
                sgd = usdsgd.json()["quotes"]["USDSGD"]
                data = {"api": sgd, "date": date_id}
                InsertData(api, 1, str(data), 'api').insert_data()
            elif eval(ExtractData(api, 1, "api").get_data()[0][1])["date"] != date_id:
                usdsgd = requests.get(f"http://www.apilayer.net/api/live?access_key={key}&format=1")
                sgd = usdsgd.json()["quotes"]["USDSGD"]
                data = {"api": sgd, "date": date_id}
                InsertData(api, 1, str(data), 'api').update_data()
                sgd = eval(ExtractData(api, 1, "api").get_data()[0][1])["api"]
                return sgd
        except Exception:
            pass
        except JSONDecodeError:
            pass
        except ConnectionError:
            pass
        return sgd


class MyMplCanvas(FigureCanvas):  # graph init

    def __init__(self, parent=None, width=10, height=10, dpi=100, change="ALL"):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.graph_launcher(change)

    def graph_launcher(self, change):
        global c
        global identity
        register_matplotlib_converters()
        # print(style.available)
        dates_in_string = []
        y = []
        if Table(c, f'graph_{identity}').check_table() and change == "ALL":
            c.execute(f"select * from 'graph_{identity}'")
            count = c.fetchall()
            for i in range(len(count)):
                dates_in_string.append(eval(count[i][1])["date"])
                y.append(eval(count[i][1])["result"])

        elif change != "ALL":
            try:
                month, year = change.split("/")
                data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])

                for i in data:
                    dates_in_string.append(i[0])
                    y.append(i[1])

            except ValueError:
                if Table(c, f'graph_{identity}').check_table():
                    c.execute(f"select * from 'graph_{identity}'")
                    count = c.fetchall()
                    for i in range(len(count)):
                        dates_in_string.append(eval(count[i][1])["date"])
                        y.append(eval(count[i][1])["result"])
        else:
            pass
        # ------------*********------------
        dates_datetime = []
        for d in dates_in_string:
            dates_datetime.append(datetime.datetime.strptime(d, "%m-%d-%Y"))

        dates_float = matplotlib.dates.date2num(dates_datetime)
        y = np.array(y)
        x = np.array(dates_float)
        pos_data = y.copy()
        neg_data = y.copy()
        pos_data[pos_data <= 0] = np.nan
        neg_data[neg_data >= 0] = np.nan

        # ***************
        # self.axes.plot_date(x, y, linestyle='-', color="gray", marker='')
        self.axes.plot_date(x, pos_data, linestyle='', label="▲ gain", color="lime", marker='o')
        self.axes.plot_date(x, neg_data, linestyle='', label="▼ loss", color="r", marker='o')

        self.axes.axhline(0, color="w", linewidth=1)
        monthsFmt = DateFormatter("%b '%d")
        self.axes.spines["left"].set_color("w")
        self.axes.spines["left"].set_linewidth(2)
        self.axes.spines["right"].set_visible(False)
        self.axes.spines["top"].set_visible(False)
        self.axes.spines["bottom"].set_visible(False)
        self.axes.tick_params(axis="x", colors="w",
                              labelsize=8, rotation=20)
        self.axes.set_title('PERFORMANCE GRAPH')
        self.axes.set_ylabel('Your Trading RESULT in BTC')
        self.axes.legend(shadow=True, fancybox=True)
        self.axes.xaxis.set_major_formatter(monthsFmt)
        self.axes.autoscale_view()
        style.use("dark_background")
        self.show()


class Ui_MainWindow(object):
    def __init__(self):
        self.noti_act()
        self.opentrade_act()

    def combo_comments(self):  # combobox in the comments section
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        date_id = str(self.note_combo.currentText())
        try:
            id_ = int(date_id.split("/")[0]) + int(date_id.split("/")[1]) + int(date_id.split("/")[2])
            if Table(c, f'comments_{identity}').check_table() and \
                    ExtractData(c, id_, f'comments_{identity}').check_data():
                encrypt = eval(ExtractData(c, id_, f'comments_{identity}').get_data()[0][1])["note"]
                text = onetimepad.decrypt(encrypt, key)
            else:
                text = ""
                pass
            self.comment_TextEdit.setPlainText(_translate("MyAPP", f"{text}"))

        except Exception:
            pass

    def save_comments(self):  # saving the comments
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        text = str(self.comment_TextEdit.toPlainText())
        encrypt = onetimepad.encrypt(text, key)
        date_id = str(self.comment_input.text())
        try:
            id_ = int(date_id.split("/")[0]) + int(date_id.split("/")[1]) + int(date_id.split("/")[2])

            if not Table(c, f'comments_{identity}').check_table():
                Table(c, f'comments_{identity}').create_table()
                data = {"date": date_id, "note": str(encrypt)}
                InsertData(c, id_, str(data), f'comments_{identity}').insert_data()

            else:
                if ExtractData(c, id_, f'comments_{identity}').check_data():
                    if text == "":
                        msg = QMessageBox()
                        msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                        msg.setIcon(QMessageBox.Question)
                        msg.setText("Warning")
                        msg.setInformativeText(f'Saving an empty note will delete everything in this note {date_id}.\n'
                                               "Proceed?")
                        msg.setWindowTitle("Warning!")
                        msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
                        retval = msg.exec_()
                        if retval == QMessageBox.Yes:
                            data = {"date": date_id, "note": str(encrypt)}
                            InsertData(c, id_, str(data), f'comments_{identity}').update_data()
                        else:
                            self.extract_comments()

                    else:
                        data = {"date": date_id, "note": str(encrypt)}
                        InsertData(c, id_, str(data), f'comments_{identity}').update_data()
                else:
                    data = {"date": date_id, "note": str(encrypt)}
                    InsertData(c, id_, str(data), f'comments_{identity}').insert_data()

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Input Error")
            msg.setInformativeText("Please enter the correct format\nMonth/Date/Year with the forward slash.")
            msg.setWindowTitle("input-Error")
            msg.exec_()
            self.comment_input.setText(_translate("MyAPP", ""))
            pass

    def extract_comments(self):  # extract comments from the table and show it
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        date_id = str(self.comment_input.text())
        try:
            id_ = int(date_id.split("/")[0]) + int(date_id.split("/")[1]) + int(date_id.split("/")[2])

            if Table(c, f'comments_{identity}').check_table() and \
                    ExtractData(c, id_, f'comments_{identity}').check_data():
                encrypt = eval(ExtractData(c, id_, f'comments_{identity}').get_data()[0][1])["note"]
                text = onetimepad.decrypt(encrypt, key)
            else:
                text = ""
                pass
            self.comment_TextEdit.setPlainText(_translate("MyAPP", f"{text}"))

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Input Error")
            msg.setInformativeText("Please enter the correct format\nMonth/Date/Year with the forward slash.")
            msg.setWindowTitle("input-Error")
            msg.exec_()
            self.comment_input.setText(_translate("MyAPP", ""))
            pass

    def btc_to_sato(self):  # btc to sato converter
        try:
            _translate = QtCore.QCoreApplication.translate
            btc_v = str(self.comment_input_2.text())
            x_value = float(btc_v) * 100000000
            value = f"{int(x_value):,d}"
            self.label_4.setText(_translate("MyAPP", f"{value} SAT"))
        except Exception:
            pass

    def rate(self, change="ALL"):  # handling the rate section
        global c
        global identity
        try:
            if Table(c, f'ADD_{identity}').check_table() and change == "ALL":
                total_gain = float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"])
                total_loss = float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"])
            elif change != "ALL":

                try:
                    month, year = change.split("/")
                    data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                    result_p = []
                    result_n = []
                    for i in data:
                        if i[1] > 0:
                            result_p.append(i[1])
                        else:
                            result_n.append(i[1])
                    total_gain = sum(result_p)
                    total_loss = sum(result_n)
                except ValueError:
                    if Table(c, f'ADD_{identity}').check_table():
                        total_gain = float(eval(ExtractData(c, 0, f'ADD_{identity}').
                                                get_data()[0][1])["total_gain"])
                        total_loss = float(eval(ExtractData(c, 0, f'ADD_{identity}').
                                                get_data()[0][1])["total_loss"])
                    else:
                        total_loss = 0
                        total_gain = 0
            else:
                total_loss = 0
                total_gain = 0

            pure_result = total_loss + total_gain

            if total_gain < 9 and total_gain != 0:
                g_value = f"+{round(total_gain, 5)}"
                g_color = "#008400"
            elif total_gain < 99 and total_gain != 0:
                g_value = f"+{round(total_gain, 4)}"
                g_color = "#008400"
            elif total_gain < 999 and total_gain != 0:
                g_value = f"+{round(total_gain, 3)}"
                g_color = "#008400"
            else:
                g_value = "0"
                g_color = "#333"

            if total_loss > -9 and total_loss != 0:
                l_value = f"{round(total_loss, 5)}"
                l_color = "#bf0000"
            elif total_loss > -99 and total_loss != 0:
                l_value = f"{round(total_loss, 4)}"
                l_color = "#bf0000"
            elif total_loss > -999 and total_loss != 0:
                l_value = f"{round(total_loss, 3)}"
                l_color = "#bf0000"
            else:
                l_value = "0"
                l_color = "#333"

            if pure_result > 0:
                if pure_result < 9:
                    x_value = f"+{round(pure_result, 5)}"
                elif pure_result < 99:
                    x_value = f"+{round(pure_result, 4)}"

                elif pure_result < 999:
                    x_value = f"+{round(pure_result, 3)}"
                else:
                    x_value = f"{round(pure_result, 1)}"

                x_color = "#008400"

            elif pure_result < 0:
                if pure_result > -9:
                    x_value = f"{round(pure_result, 5)}"
                elif pure_result > -99:
                    x_value = f"{round(pure_result, 4)}"

                elif pure_result > -999:
                    x_value = f"{round(pure_result, 3)}"
                else:
                    x_value = f"{round(pure_result, 1)}"
                x_color = "#bf0000"
            else:
                x_value = "0"
                x_color = "#333"

            _translate = QtCore.QCoreApplication.translate

            def fetch(name):
                try:
                    c.execute(f"select * from '{name}'")
                    return c.fetchall()
                except Exception:
                    pass

            if Table(c, f'rate_P_{identity}').check_table() and change == "ALL":
                p = len(fetch(f'rate_P_{identity}'))
                n = len(fetch(f'rate_N_{identity}'))

                self.win_rate_win.setText(_translate("MyAPP", f"{p}"))
                self.win_rate_loss.setText(_translate("MyAPP", f"{n}"))
            elif change != "ALL":

                try:
                    month, year = change.split("/")
                    data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                    result_p = []
                    result_n = []
                    for i in data:
                        if i[1] > 0:
                            result_p.append(i[1])
                        else:
                            result_n.append(i[1])
                    p = len(result_p)
                    n = len(result_n)
                    self.win_rate_win.setText(_translate("MyAPP", f"{p}"))
                    self.win_rate_loss.setText(_translate("MyAPP", f"{n}"))
                except ValueError:
                    if Table(c, f'rate_P_{identity}').check_table():
                        p = len(fetch(f'rate_P_{identity}'))
                        n = len(fetch(f'rate_N_{identity}'))

                        self.win_rate_win.setText(_translate("MyAPP", f"{p}"))
                        self.win_rate_loss.setText(_translate("MyAPP", f"{n}"))
                    else:
                        p = 0
                        n = 0
            else:
                p = 0
                n = 0

            if p > n:
                percentage = (p / (n + p)) * 100
            elif n > p:
                percentage = (n / (n + p)) * -100
            elif n == p:
                percentage = 0

            if percentage > 0:
                self.win_rate_win_2.setText(_translate("MyAPP", f"+{int(percentage)}%"))
                self.win_rate_win_2.setStyleSheet("border-radius:15px;\n"
                                                  "background-color: rgb(211, 211, 211);\n"
                                                  "color: #008400;\n"
                                                  "font: 63 17pt \"Yu Gothic UI Semibold\";")
            elif percentage < 0:
                self.win_rate_win_2.setText(_translate("MyAPP", f"{int(percentage)}%"))
                self.win_rate_win_2.setStyleSheet("border-radius:15px;\n"
                                                  "background-color: rgb(211, 211, 211);\n"
                                                  "color: #c30000;\n"
                                                  "font: 63 17pt \"Yu Gothic UI Semibold\";")
            else:
                self.win_rate_win_2.setText(_translate("MyAPP", f"{int(percentage)}%"))
                self.win_rate_win_2.setStyleSheet("border-radius:15px;\n"
                                                  "background-color: rgb(211, 211, 211);\n"
                                                  "color: #000000;\n"
                                                  "font: 63 17pt \"Yu Gothic UI Semibold\";")

            self.label_29.setText(_translate("MyAPP",
                                             "<html><head/><body><p><span style=\" font-size:8pt; "
                                             "font-weight:600;\">Total Gains</span>: <span style=\" font-weight:600; "
                                             f"color:{g_color};\">{g_value}₿</span></p></body></html>"))
            self.label_30.setText(_translate("MyAPP",
                                             "<html><head/><body><p><span style=\" font-size:8pt; "
                                             "font-weight:600;\">Total Losses</span>: <span style=\" font-weight:600; "
                                             f"color:{l_color};\">{l_value}₿</span></p></body></html>"))
            self.label_31.setText(_translate("MyAPP",
                                             "<html><head/><body><p><span style=\" font-size:8pt; "
                                             "font-weight:600;\">Pure "
                                             "Profit</span>: <span style=\" font-weight:600; "

                                             f"color:{x_color};\">{x_value}₿</span></p></body></html>"))

        except Exception:
            pass

    def update(self):  # price updates
        global api
        global identity
        try:
            _translate = QtCore.QCoreApplication.translate
            btc_ = API.btc()
            eth_ = API.eth()
            ltc_ = API.ltc()
            if btc_ is not None and eth_ is not None and ltc_ is not None:
                _btc_ = btc_[0]
                data = (btc_[1], eth_, ltc_)

                try:
                    if not Table(api, 'Currency_api').check_table():
                        Table(api, 'Currency_api').create_table()
                        InsertData(api, 1, str(data), 'Currency_api').insert_data()
                except sqlite3.OperationalError:
                    pass
                except SystemError:
                    pass
                except Exception:
                    pass

                if eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[0] < btc_[1]:
                    self.BTC_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-weight:600;\">BTC / USDT</span><span style=\" "
                                                               f"font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-weight:600; color:#009100;\""
                                                               f">${_btc_} </span></p></body></html>"))
                elif eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[0] > btc_[1]:
                    self.BTC_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-weight:600;\">BTC / USDT</span><span style=\" "
                                                               f"font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-weight:600; color:#bf0000;\""
                                                               f">${_btc_} </span></p></body></html>"))
                if eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[1] < eth_:
                    self.ETH_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-weight:600;\">ETH / USDT</span><span style=\" "
                                                               f"font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-weight:600; color:#009100;\""
                                                               f">${eth_}</span></p></body></html>"))
                elif eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[1] > eth_:
                    self.ETH_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-weight:600;\">ETH / USDT</span><span style=\" "
                                                               f"font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-weight:600; color:#bf0000;\""
                                                               f">${eth_}</span></p></body></html>"))

                if eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[2] < ltc_:
                    self.LTC_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-size:10pt; font-weight:600;\""
                                                               f">LTC / USDT</span><span style=\" "
                                                               f"font-size:10pt; font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-size:10pt; font-weight:600; color:#009100;\""
                                                               f">${ltc_}</span></p></body></html>"))

                elif eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[2] > ltc_:
                    self.LTC_Priceusd_color.setText(_translate("MainWindow",
                                                               f"<html><head/><body><p><span style=\" "
                                                               f"font-size:10pt; font-weight:600;\""
                                                               f">LTC / USDT</span><span style=\" "
                                                               f"font-size:10pt; font-weight:600; color:#d3d3d3;\""
                                                               f">.....</span><span style=\" "
                                                               f"font-size:10pt; font-weight:600; color:#bf0000;\""
                                                               f">${ltc_}</span></p></body></html>"))
                else:
                    pass

                if Table(api, 'Currency_api').check_table():
                    InsertData(api, 1, str(data), 'Currency_api').update_data()
                # ----------------notification-----------------
                noti_data = ExtractData(api, 1, f'notify_{identity}').get_data()

                if float(eval(noti_data[0][1])["BTC"][1]) != 0:
                    if int(eval(noti_data[0][1])["BTC"][0]) >= int(eval(noti_data[0][1])["BTC"][1]):
                        if int(eval(noti_data[0][1])["BTC"][1]) >= int(btc_[1]):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (0, 0), "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                                           float(eval(noti_data[0][1])["ETH"][1])),
                                    "LTC": (float(eval(noti_data[0][1])["LTC"][0]),
                                            float(eval(noti_data[0][1])["LTC"][1])), "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                    elif int(eval(noti_data[0][1])["BTC"][0]) <= int(eval(noti_data[0][1])["BTC"][1]):
                        if int(eval(noti_data[0][1])["BTC"][1]) <= int(btc_[1]):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (0, 0), "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                                           float(eval(noti_data[0][1])["ETH"][1])),
                                    "LTC": (float(eval(noti_data[0][1])["LTC"][0]),
                                            float(eval(noti_data[0][1])["LTC"][1])), "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                else:
                    pass
                if float(eval(noti_data[0][1])["ETH"][1]) != 0:
                    if int(eval(noti_data[0][1])["ETH"][0]) >= int(eval(noti_data[0][1])["ETH"][1]):
                        if int(eval(noti_data[0][1])["ETH"][1]) >= int(eth_):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                            float(eval(noti_data[0][1])["BTC"][1])), "ETH": (0, 0),
                                    "LTC": (float(eval(noti_data[0][1])["LTC"][0]),
                                            float(eval(noti_data[0][1])["LTC"][1])), "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                    elif int(eval(noti_data[0][1])["ETH"][0]) <= int(eval(noti_data[0][1])["ETH"][1]):
                        if int(eval(noti_data[0][1])["ETH"][1]) <= int(eth_):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                            float(eval(noti_data[0][1])["BTC"][1])), "ETH": (0, 0),
                                    "LTC": (float(eval(noti_data[0][1])["LTC"][0]),
                                            float(eval(noti_data[0][1])["LTC"][1])), "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                else:
                    pass
                if float(eval(noti_data[0][1])["LTC"][1]) != 0:
                    if int(eval(noti_data[0][1])["LTC"][0]) >= int(eval(noti_data[0][1])["LTC"][1]):
                        if int(eval(noti_data[0][1])["LTC"][1]) >= int(ltc_):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                            float(eval(noti_data[0][1])["BTC"][1])),
                                    "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                            float(eval(noti_data[0][1])["ETH"][1])), "LTC": (0, 0),
                                    "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                    elif int(eval(noti_data[0][1])["LTC"][0]) <= int(eval(noti_data[0][1])["LTC"][1]):
                        if int(eval(noti_data[0][1])["LTC"][1]) <= int(ltc_):
                            ring = eval(noti_data[0][1])["ring"]
                            playsound(os.path.join("Images", f"{ring}.mp3"))
                            data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                            float(eval(noti_data[0][1])["BTC"][1])),
                                    "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                            float(eval(noti_data[0][1])["ETH"][1])), "LTC": (0, 0), "ring": ring}
                            InsertData(api, 1, str(data), f'notify_{identity}').update_data()
                        else:
                            pass
                else:
                    pass
            else:
                pass
        except Exception:
            pass

    def journal_buy(self):
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:

            if Table(c, f'open_trade_{identity}').check_table():
                amount = round(eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["amount"], 1)
                entry = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["entry"]
                exit_ = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["exit"]
                date = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["date"]

                if amount == 0 and entry == 0 and exit_ == 0 and date == 0:
                    amount = str(self.input_amount_BS.text())
                    entry = str(self.input_Entry_BS.text())
                    exit_ = str(self.input_Exit_BS.text())

                    if self.checkBox.isChecked():
                        self.allow()
                        date = datetime.date.today()
                        month = date.month
                        day = date.day
                        year = date.year
                    elif not self.checkBox.isChecked():

                        try:
                            month, day, year = str(self.input_amount_BS_2.text()).split("/")

                        except Exception:
                            msg = QMessageBox()
                            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Input Error")
                            msg.setInformativeText(
                                "Please enter the correct format\nMonth/Date/Year with the forward slash.")
                            msg.setWindowTitle("input-Error")
                            msg.exec_()
                            self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                    else:
                        month, day, year = str(self.input_amount_BS_2.text()).split("/")
                else:
                    month, day, year = str(date).split("-")

                data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
            else:
                amount = str(self.input_amount_BS.text())
                entry = str(self.input_Entry_BS.text())
                exit_ = str(self.input_Exit_BS.text())

                if self.checkBox.isChecked():
                    self.allow()
                    date = datetime.date.today()
                    month = date.month
                    day = date.day
                    year = date.year
                elif not self.checkBox.isChecked():

                    try:
                        month, day, year = str(self.input_amount_BS_2.text()).split("/")
                    except Exception:
                        msg = QMessageBox()
                        msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Input Error")
                        msg.setInformativeText(
                            "Please enter the correct format\nMonth/Date/Year with the forward slash.")
                        msg.setWindowTitle("input-Error")
                        msg.exec_()
                        self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                else:
                    month, day, year = str(self.input_amount_BS_2.text()).split("/")

            if ((int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or
                 int(month) == 8 or int(month) == 10 or int(month) == 12) and int(day) <= 31) or \
                    (int(month) == 2 and int(day) <= 28) or \
                    ((int(month) == 4 or int(month) == 6 or int(month) == 9 or int(month) == 11) and
                     int(day) <= 30):

                result = ((float(exit_) - float(entry)) / float(entry)) * (float(amount) * (1 / float(API.btc()[1])))

                if result > 0:
                    _result = "+" + str(round(result, 5))
                else:
                    _result = str(round(result, 5))

                date_str = str(month) + "-" + str(day) + "-" + str(year)

                data = {"date": date_str, "amount": "▲ " + str(amount), "entry": entry, "exit": exit_,
                        "result": _result}

                graph_data = {"date": date_str, "result": result}

                # ------------------------------------- #
                if not Table(c, f'journal_{identity}').check_table():
                    Table(c, f'journal_{identity}').create_table()
                    Table(c, f'graph_{identity}').create_table()
                    Table(c, f'rate_P_{identity}').create_table()
                    Table(c, f'rate_N_{identity}').create_table()
                    Table(c, f'ADD_{identity}').create_table()
                    Table(c, f'graph_{year}_{identity}').create_table()
                    Table(c, f'combobox_{identity}').create_table()

                    combo_data = [int(month)]

                    InsertData(c, year, str(combo_data), f'combobox_{identity}').insert_data()

                    M_data = [(date_str, round(result, 5))]

                    InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()
                    InsertData(c, 0, str(graph_data), f'graph_{identity}').insert_data()
                    InsertData(c, 0, str(data), f'journal_{identity}').insert_data()

                    if result > 0:
                        rate_value = result
                        InsertData(c, 0, str(rate_value), f'rate_p_{identity}').insert_data()

                        add_data = {"total_gain": result, "total_loss": 0}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()

                    else:
                        rate_value = result
                        InsertData(c, 0, str(rate_value), f'rate_N_{identity}').insert_data()

                        add_data = {"total_gain": 0, "total_loss": result}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()

                else:

                    if ExtractData(c, year, f'combobox_{identity}').check_data():
                        combo_data = eval(ExtractData(c, year, f'combobox_{identity}').get_data()[0][1])

                        if int(month) not in combo_data:
                            combo_data.append(int(month))
                            InsertData(c, year, str(combo_data), f'combobox_{identity}').update_data()
                        else:
                            pass
                    else:
                        combo_data = [int(month)]
                        InsertData(c, year, str(combo_data), f'combobox_{identity}').insert_data()

                    # ----------------------------------
                    c.execute(f"select * from 'journal_{identity}'")
                    count = c.fetchall()

                    if count == 1:
                        value = 0
                    else:
                        if Table(c, f"save_{identity}").check_table():
                            value = ExtractData(c, 1, f"save_{identity}").get_data()[0][1] + len(count)
                        else:
                            value = len(count)

                    InsertData(c, (value - 1) + 1, str(data), f'journal_{identity}').insert_data()
                    InsertData(c, (value - 1) + 1, str(graph_data), f'graph_{identity}').insert_data()

                    if result > 0:
                        rate_value = result
                        InsertData(c, (value - 1) + 1, str(rate_value), f'rate_p_{identity}').insert_data()

                        add_data = {"total_gain":
                                        float(
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"])
                                        + result, "total_loss":
                                        eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"]}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    else:
                        rate_value = result
                        InsertData(c, (value - 1) + 1, str(rate_value), f'rate_N_{identity}').insert_data()

                        add_data = {"total_gain":
                                        eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"]
                            , "total_loss":
                                        float(
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"])
                                        + result}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    # ---------------------------------------

                    if Table(c, f'graph_{year}_{identity}').check_table():
                        if ExtractData(c, month, f'graph_{year}_{identity}').check_data():
                            M_data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                            M_data.append((date_str, round(result, 5)))
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').update_data()
                        else:
                            M_data = [(date_str, round(result, 5))]
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                    if not Table(c, f'graph_{year}_{identity}').check_table():
                        Table(c, f'graph_{year}_{identity}').create_table()
                        M_data = [(date_str, round(result, 5))]
                        InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                    self.input_amount_BS.setText(_translate("MyAPP", ""))
                    self.input_Entry_BS.setText(_translate("MyAPP", ""))
                    self.input_Exit_BS.setText(_translate("MyAPP", ""))
                    self.input_amount_BS_2.setText(_translate("MyAPP", ""))
            else:
                pass

        except Exception:
            pass

    def journal_sell(self):  # sell calculator, with data management, insert data in database
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            if Table(c, f'open_trade_{identity}').check_table():
                amount = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["amount"]
                entry = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["entry"]
                exit_ = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["exit"]
                date = eval(ExtractData(c, 2, f'open_trade_{identity}').get_data()[0][1])["date"]

                if amount == 0 and entry == 0 and exit_ == 0 and date == 0:
                    amount = str(self.input_amount_BS.text())
                    entry = str(self.input_Entry_BS.text())
                    exit_ = str(self.input_Exit_BS.text())

                    if self.checkBox.isChecked():
                        self.allow()
                        date = datetime.date.today()
                        month = date.month
                        day = date.day
                        year = date.year
                    elif not self.checkBox.isChecked():

                        try:
                            month, day, year = str(self.input_amount_BS_2.text()).split("/")
                        except Exception:
                            msg = QMessageBox()
                            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Input Error")
                            msg.setInformativeText(
                                "Please enter the correct format\nMonth/Date/Year with the forward slash.")
                            msg.setWindowTitle("input-Error")
                            msg.exec_()
                            self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                    else:
                        month, day, year = str(self.input_amount_BS_2.text()).split("/")
                else:
                    month, day, year = str(date).split("-")
                    pass

                data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
            else:
                amount = str(self.input_amount_BS.text())
                entry = str(self.input_Entry_BS.text())
                exit_ = str(self.input_Exit_BS.text())

                if self.checkBox.isChecked():
                    self.allow()
                    date = datetime.date.today()
                    month = date.month
                    day = date.day
                    year = date.year
                elif not self.checkBox.isChecked():

                    try:
                        month, day, year = str(self.input_amount_BS_2.text()).split("/")
                    except Exception:
                        msg = QMessageBox()
                        msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText("Input Error")
                        msg.setInformativeText(
                            "Please enter the correct format\nMonth/Date/Year with the forward slash.")
                        msg.setWindowTitle("input-Error")
                        msg.exec_()
                        self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                else:
                    month, day, year = str(self.input_amount_BS_2.text()).split("/")

            if ((int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or
                 int(month) == 8 or int(month) == 10 or int(month) == 12) and int(day) <= 31) or \
                    (int(month) == 2 and int(day) <= 28) or \
                    ((int(month) == 4 or int(month) == 6 or int(month) == 9 or int(month) == 11) and
                     int(day) <= 30):

                result = ((float(entry) - float(exit_)) / float(entry)) * (float(amount) * (1 / float(API.btc()[1])))

                if result >= 0:
                    _result = "+" + str(round(result, 5))
                else:
                    _result = str(round(result, 5))

                date_str = str(month) + "-" + str(day) + "-" + str(year)

                data = {"date": date_str, "amount": "▼ " + str(amount), "entry": entry, "exit": exit_,
                        "result": _result}

                graph_data = {"date": date_str, "result": result}

                # --------------------------------

                if not Table(c, f'journal_{identity}').check_table():
                    Table(c, f'journal_{identity}').create_table()
                    Table(c, f'graph_{identity}').create_table()
                    Table(c, f'rate_P_{identity}').create_table()
                    Table(c, f'rate_N_{identity}').create_table()
                    Table(c, f'ADD_{identity}').create_table()
                    Table(c, f'graph_{year}_{identity}').create_table()
                    Table(c, f'combobox_{identity}').create_table()

                    combo_data = [int(month)]

                    InsertData(c, year, str(combo_data), f'combobox_{identity}').insert_data()

                    M_data = [(date_str, round(result, 5))]

                    InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()
                    InsertData(c, 0, str(graph_data), f'graph_{identity}').insert_data()
                    InsertData(c, 0, str(data), f'journal_{identity}').insert_data()

                    if result > 0:
                        rate_value = result
                        InsertData(c, 0, str(rate_value), f'rate_p_{identity}').insert_data()

                        add_data = {"total_gain": result, "total_loss": 0}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()

                    else:
                        rate_value = result
                        InsertData(c, 0, str(rate_value), f'rate_N_{identity}').insert_data()

                        add_data = {"total_gain": 0, "total_loss": result}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()

                else:

                    if ExtractData(c, year, f'combobox_{identity}').check_data():
                        combo_data = eval(ExtractData(c, year, f'combobox_{identity}').get_data()[0][1])

                        if int(month) not in combo_data:
                            combo_data.append(int(month))
                            InsertData(c, year, str(combo_data), f'combobox_{identity}').update_data()
                        else:
                            pass
                    else:
                        combo_data = [int(month)]
                        InsertData(c, year, str(combo_data), f'combobox_{identity}').insert_data()

                    # ------------------------------
                    c.execute(f"select * from 'journal_{identity}'")
                    count = c.fetchall()

                    if count == 1:
                        value = 0
                    else:
                        if Table(c, f"save_{identity}").check_table():
                            value = ExtractData(c, 1, f"save_{identity}").get_data()[0][1] + len(count)
                        else:
                            value = len(count)

                    InsertData(c, (value - 1) + 1, str(data), f'journal_{identity}').insert_data()
                    InsertData(c, (value - 1) + 1, str(graph_data), f'graph_{identity}').insert_data()

                    if result > 0:
                        rate_value = result
                        InsertData(c, (value - 1) + 1, str(rate_value), f'rate_p_{identity}').insert_data()

                        add_data = {"total_gain":
                                        float(
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"])
                                        + result, "total_loss":
                                        eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"]}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    else:
                        rate_value = result
                        InsertData(c, (value - 1) + 1, str(rate_value), f'rate_N_{identity}').insert_data()

                        add_data = {"total_gain":
                                        eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"]
                            , "total_loss":
                                        float(
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"])
                                        + result}
                        InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    # ---------------------------------------
                    # """
                    if Table(c, f'graph_{year}_{identity}').check_table():
                        if ExtractData(c, month, f'graph_{year}_{identity}').check_data():
                            M_data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                            M_data.append((date_str, round(result, 5)))
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').update_data()
                        else:
                            M_data = [(date_str, round(result, 5))]
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                    if not Table(c, f'graph_{year}_{identity}').check_table():
                        Table(c, f'graph_{year}_{identity}').create_table()
                        M_data = [(date_str, round(result, 5))]
                        InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                    self.input_amount_BS.setText(_translate("MyAPP", ""))
                    self.input_Entry_BS.setText(_translate("MyAPP", ""))
                    self.input_Exit_BS.setText(_translate("MyAPP", ""))
                    self.input_amount_BS_2.setText(_translate("MyAPP", ""))
            else:
                pass

        except Exception:
            pass

    def user_wallet(self):  # wallet
        global api
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            input_wallet = str(self.input_wallet_balance.text())
            _btc_ = API.btc()
            if _btc_ is not None:
                if input_wallet == "":
                    if Table(api, f'wallet_{identity}').check_table():
                        wallet = eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"]

                    else:
                        wallet = 0
                        if not Table(api, f'wallet_{identity}').check_table():
                            Table(api, f'wallet_{identity}').create_table()
                            wallet_ = {"wallet": wallet}
                            InsertData(api, 1, str(wallet_), f'wallet_{identity}').insert_data()
                else:
                    try:
                        wallet_input = int(input_wallet)
                    except ValueError:
                        a, b, e = str(input_wallet).split(",")
                        wallet_input = a + b + e
                    wallet_ = {"wallet": int(wallet_input)}
                    InsertData(api, 1, str(wallet_), f'wallet_{identity}').update_data()
                    wallet = str(eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"])

                self.input_wallet_balance.setText(f"{int(wallet):,d}")
                xusd = round(((float(wallet) * 0.00000001) * _btc_[1]), 2)
                usd = str(f"{int(xusd):,d}") + "." + str(round(abs(xusd - int(xusd)), 2)).split(".")[1]

                xsgd = round(float(API.usd_sgd()) * xusd, 2)
                sgd = str(f"{int(xsgd):,d}") + "." + str(round(abs(xsgd - int(xsgd)), 2)).split(".")[1]

                btc_ = round((float(wallet) * 0.00000001), 4)
                self.output_wallet_USD.setText(_translate("MyAPP", f"$ {usd}"))
                self.output_wallet_SGD.setText(_translate("MyAPP", f"S$ {sgd}"))
                self.output_wallet_BTC.setText(_translate("MyAPP", f"₿ {btc_}"))
                return usd, sgd, btc_
            else:
                return 0, 0, 0

        except Exception:
            if Table(api, f'wallet_{identity}').check_table():
                wallet = str(eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"])
                self.input_wallet_balance.setText(f"{int(wallet):,d}")
            else:
                self.input_wallet_balance.setText(_translate("MyAPP", ""))
            pass

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1760, 989)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/Images/MainWinTite.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("*{background-color: rgb(211, 211, 211);}\n""")
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_23 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_23.setObjectName("gridLayout_23")
        self.line_8 = QtWidgets.QFrame(self.centralwidget)
        self.line_8.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_8.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.gridLayout_23.addWidget(self.line_8, 2, 2, 1, 1)
        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        self.line_6.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.gridLayout_23.addWidget(self.line_6, 4, 3, 1, 2)
        self.gridLayout_19 = QtWidgets.QGridLayout()
        self.gridLayout_19.setContentsMargins(12, 0, 12, -1)
        self.gridLayout_19.setObjectName("gridLayout_19")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_19.addWidget(self.line_3, 0, 3, 1, 1)
        self.label_journal = QtWidgets.QLabel(self.centralwidget)
        self.label_journal.setStyleSheet("font: 75 10pt \"Bahnschrift\";")
        self.label_journal.setFrameShape(QtWidgets.QFrame.Box)
        self.label_journal.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_journal.setLineWidth(2)
        self.label_journal.setObjectName("label_journal")
        self.gridLayout_19.addWidget(self.label_journal, 0, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_15.setObjectName("label_15")
        self.gridLayout_19.addWidget(self.label_15, 0, 1, 1, 1)
        self.input_modify = QtWidgets.QLineEdit(self.centralwidget)
        self.input_modify.setStyleSheet("*{\n"
                                        "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "}\n"
                                        "QLineEdit{\n"
                                        "border-radius:8px;\n"
                                        "background-color: rgb(240, 240, 240);\n"
                                        "}")
        self.input_modify.setObjectName("input_modify")

        self.input_modify.returnPressed.connect(self.modify)
        self.input_modify.returnPressed.connect(self.make_journal)

        self.gridLayout_19.addWidget(self.input_modify, 0, 2, 1, 1)
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_16.setObjectName("label_16")
        self.gridLayout_5.addWidget(self.label_16, 0, 1, 1, 1)
        self.input_delete = QtWidgets.QLineEdit(self.centralwidget)
        self.input_delete.setStyleSheet("\n"
                                        "QLineEdit{\n"
                                        "border-radius:8px;\n"
                                        "background-color: rgb(240, 240, 240);\n"
                                        "}\n"
                                        "\n"
                                        "*{\n"
                                        "font: 75 11pt \"MS Shell Dlg 2\";\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "}")
        self.input_delete.setObjectName("input_delete")

        self.input_delete.returnPressed.connect(self.delete)
        self.input_delete.returnPressed.connect(self.make_journal)

        self.gridLayout_5.addWidget(self.input_delete, 0, 2, 1, 1)
        self.gridLayout_19.addLayout(self.gridLayout_5, 0, 5, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_19, 2, 3, 1, 2)
        self.line_7 = QtWidgets.QFrame(self.centralwidget)
        self.line_7.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.gridLayout_23.addWidget(self.line_7, 6, 2, 1, 1)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_23.addWidget(self.line, 7, 2, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_2.addWidget(self.line_2, 0, 0, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_2, 1, 0, 1, 5)
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.output_wallet_SGD = QtWidgets.QLabel(self.centralwidget)
        self.output_wallet_SGD.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";\n"
                                             "color: rgb(50, 0, 150);")
        self.output_wallet_SGD.setObjectName("output_wallet_SGD")
        self.gridLayout_4.addWidget(self.output_wallet_SGD, 0, 10, 1, 1)

        self.output_wallet_SGD.setFixedWidth(133)

        self.output_wallet_BTC = QtWidgets.QLabel(self.centralwidget)
        self.output_wallet_BTC.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";\n"
                                             "color: rgb(50, 0, 150);")
        self.output_wallet_BTC.setObjectName("output_wallet_BTC")
        self.output_wallet_BTC.setFixedWidth(90)

        self.gridLayout_4.addWidget(self.output_wallet_BTC, 0, 6, 1, 1)
        self.output_wallet_USD = QtWidgets.QLabel(self.centralwidget)
        self.output_wallet_USD.setStyleSheet("font: 12pt \"MS Shell Dlg 2\";\n"
                                             "color: rgb(50, 0, 150);")
        self.output_wallet_USD.setObjectName("output_wallet_USD")
        self.output_wallet_USD.setFixedWidth(133)

        self.gridLayout_4.addWidget(self.output_wallet_USD, 0, 14, 1, 1)
        self.input_wallet_balance = QtWidgets.QLineEdit(self.centralwidget)
        self.input_wallet_balance.setStyleSheet("*{\n"
                                                "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                                "color: rgb(0, 0, 0);\n"
                                                "}\n"
                                                "\n"
                                                "QLineEdit{\n"
                                                "border-radius:8px;\n"
                                                "background-color: rgb(240, 240, 240);\n"
                                                "}")
        self.input_wallet_balance.setObjectName("input_wallet_balance")

        self.input_wallet_balance.returnPressed.connect(self.user_wallet)

        self.gridLayout_4.addWidget(self.input_wallet_balance, 0, 2, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setStyleSheet("color: rgb(0, 0, 0);\n"
                                    "font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_11.setObjectName("label_11")
        self.gridLayout_4.addWidget(self.label_11, 0, 1, 1, 1)
        self.line_11 = QtWidgets.QFrame(self.centralwidget)
        self.line_11.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_11.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.gridLayout_4.addWidget(self.line_11, 0, 8, 1, 1)
        self.line_9 = QtWidgets.QFrame(self.centralwidget)
        self.line_9.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_9.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.gridLayout_4.addWidget(self.line_9, 0, 4, 1, 1)
        self.line_12 = QtWidgets.QFrame(self.centralwidget)
        self.line_12.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_12.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.gridLayout_4.addWidget(self.line_12, 0, 12, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 5, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem2, 0, 9, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem3, 0, 7, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem4, 0, 11, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem5, 0, 13, 1, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem6, 0, 15, 1, 1)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem7, 0, 0, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_4, 0, 3, 1, 2)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.LTC_Priceusd_color = QtWidgets.QLabel(self.centralwidget)
        self.LTC_Priceusd_color.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.LTC_Priceusd_color.setObjectName("LTC_Priceusd_color")
        self.LTC_Priceusd_color.setFixedWidth(200)
        self.gridLayout_3.addWidget(self.LTC_Priceusd_color, 0, 9, 1, 1)

        self.line_10 = QtWidgets.QFrame(self.centralwidget)
        self.line_10.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_10.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.gridLayout_3.addWidget(self.line_10, 0, 0, 1, 1)

        self.gridLayout_11 = QtWidgets.QGridLayout()
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout_11.addWidget(self.line_5, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_11, 0, 3, 1, 1)
        self.line_13 = QtWidgets.QFrame(self.centralwidget)
        self.line_13.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_13.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_13.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_13.setObjectName("line_13")
        self.gridLayout_3.addWidget(self.line_13, 0, 11, 1, 1)
        self.ETH_Priceusd_color = QtWidgets.QLabel(self.centralwidget)
        self.ETH_Priceusd_color.setStyleSheet("font: 10pt \"Palatino Linotype\";")
        self.ETH_Priceusd_color.setObjectName("ETH_Priceusd_color")
        self.ETH_Priceusd_color.setFixedWidth(200)

        self.gridLayout_3.addWidget(self.ETH_Priceusd_color, 0, 5, 1, 1)
        self.BTC_Priceusd_color = QtWidgets.QLabel(self.centralwidget)
        self.BTC_Priceusd_color.setStyleSheet("font: 10pt \"Palatino Linotype\";")
        self.BTC_Priceusd_color.setObjectName("BTC_Priceusd_color")
        self.BTC_Priceusd_color.setFixedWidth(200)

        self.gridLayout_3.addWidget(self.BTC_Priceusd_color, 0, 1, 1, 1)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout_7.addWidget(self.line_4, 0, 0, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_7, 0, 7, 1, 1)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem8, 0, 4, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem9, 0, 8, 1, 1)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem10, 0, 0, 1, 1)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem11, 0, 6, 1, 1)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem12, 0, 10, 1, 1)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem13, 0, 2, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_3, 0, 0, 1, 3)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_28 = QtWidgets.QLabel(self.centralwidget)
        self.label_28.setFrameShape(QtWidgets.QFrame.Box)
        self.label_28.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_28.setMidLineWidth(1)
        self.label_28.setScaledContents(False)
        self.label_28.setWordWrap(False)
        self.label_28.setObjectName("label_28")
        self.label_28.setFixedWidth(180)
        self.gridLayout_8.addWidget(self.label_28, 0, 3, 1, 1)
        self.label_30 = QtWidgets.QLabel(self.centralwidget)
        self.label_30.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_30.setFrameShape(QtWidgets.QFrame.Box)
        self.label_30.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_30.setMidLineWidth(1)
        self.label_30.setScaledContents(False)
        self.label_30.setWordWrap(False)
        self.label_30.setObjectName("label_30")
        self.label_30.setFixedWidth(180)
        self.gridLayout_8.addWidget(self.label_30, 0, 1, 1, 1)
        self.label_29 = QtWidgets.QLabel(self.centralwidget)
        self.label_29.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_29.setFrameShape(QtWidgets.QFrame.Box)
        self.label_29.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_29.setMidLineWidth(1)
        self.label_29.setScaledContents(False)
        self.label_29.setWordWrap(False)
        self.label_29.setObjectName("label_29")
        self.label_29.setFixedWidth(180)
        self.gridLayout_8.addWidget(self.label_29, 0, 0, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.centralwidget)
        self.label_31.setStyleSheet("font: 75 9pt \"MS Shell Dlg 2\";")
        self.label_31.setFrameShape(QtWidgets.QFrame.Box)
        self.label_31.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_31.setMidLineWidth(1)
        self.label_31.setScaledContents(False)
        self.label_31.setWordWrap(False)
        self.label_31.setObjectName("label_31")
        self.label_31.setFixedWidth(180)
        self.gridLayout_8.addWidget(self.label_31, 0, 2, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_8, 2, 0, 1, 2)
        self.gridLayout_16 = QtWidgets.QGridLayout()
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.frame_5 = QtWidgets.QFrame(self.centralwidget)
        self.frame_5.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setLineWidth(0)
        self.frame_5.setObjectName("frame_5")
        self.gridLayout_17 = QtWidgets.QGridLayout(self.frame_5)
        self.gridLayout_17.setObjectName("gridLayout_17")
        # =========================TABLE========================
        self.TABLE_Widget = QtWidgets.QTableWidget(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.TABLE_Widget.setFont(font)
        self.TABLE_Widget.setStyleSheet("\n"
                                        "font: 75 13pt \"Bahnschrift\";\n"
                                        "\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
                                        "y2:0, stop:1 rgba(105, 105, 105,240));\n "
                                        "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                        "stop:1 rgba(181, 181, 181, 100));\n "
                                        "\n"
                                        "")
        self.TABLE_Widget.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.TABLE_Widget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.TABLE_Widget.setLineWidth(0)
        self.TABLE_Widget.setMidLineWidth(0)
        self.TABLE_Widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.TABLE_Widget.setTabKeyNavigation(True)
        self.TABLE_Widget.setAlternatingRowColors(True)
        self.TABLE_Widget.setShowGrid(True)
        self.TABLE_Widget.setGridStyle(QtCore.Qt.SolidLine)
        self.TABLE_Widget.setCornerButtonEnabled(True)
        self.TABLE_Widget.setObjectName("TABLE_Widget")
        self.TABLE_Widget.setColumnCount(6)
        # -----------------------
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.TABLE_Widget.setHorizontalHeaderItem(5, item)
        # ----------------------------------
        self.TABLE_Widget.horizontalHeader().setCascadingSectionResizes(False)
        self.TABLE_Widget.verticalHeader().setCascadingSectionResizes(True)
        self.TABLE_Widget.horizontalHeader().setVisible(True)
        self.TABLE_Widget.horizontalHeader().setHighlightSections(True)
        self.TABLE_Widget.horizontalHeader().setStretchLastSection(True)
        self.TABLE_Widget.verticalHeader().setVisible(False)
        self.TABLE_Widget.verticalHeader().setSortIndicatorShown(False)
        # self.TABLE_Widget.verticalHeader().setStretchLastSection(True)
        self.gridLayout_17.addWidget(self.TABLE_Widget, 0, 0, 1, 1)

        # ----------------------------------------------
        self.gridLayout_16.addWidget(self.frame_5, 0, 0, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_16, 6, 3, 1, 2)
        self.line_14 = QtWidgets.QFrame(self.centralwidget)
        self.line_14.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_14.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_14.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_14.setObjectName("line_14")
        self.gridLayout_23.addWidget(self.line_14, 4, 0, 1, 2)
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.gridLayout_14 = QtWidgets.QGridLayout()
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.gridLayout_10.addLayout(self.gridLayout_14, 2, 0, 1, 1)
        self.toolBox_2 = QtWidgets.QToolBox(self.centralwidget)
        self.toolBox_2.setEnabled(True)
        self.toolBox_2.setToolTip("")
        self.toolBox_2.setAutoFillBackground(False)
        self.toolBox_2.setStyleSheet("color: rgb(0, 0, 0);\n"
                                     "font: 75 12pt \"Bahnschrift\";")
        self.toolBox_2.setObjectName("toolBox_2")
        self.page_5 = QtWidgets.QWidget()
        self.page_5.setGeometry(QtCore.QRect(0, 0, 771, 291))
        self.page_5.setObjectName("page_5")
        self.gridLayout_15 = QtWidgets.QGridLayout(self.page_5)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.Graph_frame = QtWidgets.QFrame(self.page_5)
        self.Graph_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.Graph_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Graph_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Graph_frame.setObjectName("Graph_frame")
        self.gridLayout_15.addWidget(self.Graph_frame, 0, 0, 1, 1)
        self.toolBox_2.addItem(self.page_5, "")
        self.page_6 = QtWidgets.QWidget()
        self.page_6.setGeometry(QtCore.QRect(0, 0, 771, 291))
        self.page_6.setObjectName("page_6")
        # ---------------------
        self.groupBox = QtWidgets.QGroupBox(self.page_6)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 331, 71))
        self.groupBox.setStyleSheet("font: 75 italic 10pt \"Palatino Linotype\";\n"
                                    "color:  rgb(50, 0, 150);")
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setGeometry(QtCore.QRect(260, 15, 71, 22))
        self.comboBox_2.setStyleSheet("*{\n"
                                      "color: rgb(0, 0, 0);\n"
                                      "    \n"
                                      "font: 9pt \"MS Shell Dlg 2\";\n"
                                      "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
                                      "y2:0, stop:0 rgba(255, 255, 255, 255), stop:0.233831 rgba(0, 0, 0, 224));\n "
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "\n"
                                      "")
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")

        self.comboBox_4 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_4.setGeometry(QtCore.QRect(260, 43, 71, 22))
        self.comboBox_4.setStyleSheet("*{\n"
                                      "color: rgb(0, 0, 0);\n"
                                      "    \n"
                                      "font: 9pt \"MS Shell Dlg 2\";\n"
                                      "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
                                      "y2:0, stop:0 rgba(255, 255, 255, 255), stop:0.233831 rgba(0, 0, 0, 224));\n "
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "\n"
                                      "")
        self.comboBox_4.setObjectName("comboBox_4")
        self.comboBox_4.currentIndexChanged.connect(self.sound_ring)
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")
        self.comboBox_4.addItem("")

        self.label_currency = QtWidgets.QLabel(self.groupBox)
        self.label_currency.setStyleSheet("font: 75 9pt \"Palatino Linotype\";"
                                          "    color: rgb(0, 0, 0);\n")
        self.label_currency.setGeometry(QtCore.QRect(190, 16, 65, 20))
        self.label_currency.setObjectName("label_currency")

        self.label_ring = QtWidgets.QLabel(self.groupBox)
        self.label_ring.setStyleSheet("font: 75 9pt \"Palatino Linotype\";"
                                      "    color: rgb(0, 0, 0);\n")
        self.label_ring.setGeometry(QtCore.QRect(190, 43, 65, 20))
        self.label_ring.setObjectName("label_ring")

        self.comment_input_3 = QtWidgets.QLineEdit(self.groupBox)
        self.comment_input_3.setGeometry(QtCore.QRect(110, 40, 70, 20))
        self.comment_input_3.setStyleSheet("\n"
                                           "QLineEdit{\n"
                                           "border-radius:10px;\n"
                                           "    color: rgb(0, 0, 0);\n"
                                           "background-color: rgb(240, 240, 240);\n"
                                           "}")
        self.comment_input_3.setObjectName("comment_input_3")
        self.Calc_btn_right_2 = QtWidgets.QPushButton(self.groupBox)
        self.Calc_btn_right_2.setGeometry(QtCore.QRect(10, 40, 82, 20))
        self.Calc_btn_right_2.setStyleSheet("*{\n"
                                            "color:  rgb(211, 211, 211);\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:hover{\n"
                                            "color: rgb(255, 255, 255);\n"
                                            ";\n"
                                            "    \n"
                                            "    background-color: rgb(0, 0, 0);\n"
                                            "\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton{\n"
                                            "border: 1px solid  #333;\n"
                                            "background:  rgb(0, 0, 0);\n"
                                            "border-radius:10px;\n"
                                            "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                            "}\n"
                                            "\n"
                                            "\n"
                                            "QPushButton:hover{\n"
                                            "\n"
                                            "color: rgb(225, 255, 255);\n"
                                            "    background-color: rgb(0, 0, 0);\n"
                                            "border-radius:10px;\n"
                                            "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:pressed \n"
                                            "{\n"
                                            " border: 2px inset   rgb(225, 255, 255);\n"
                                            "background-color: #333;\n"
                                            "}")
        self.Calc_btn_right_2.setObjectName("Calc_btn_right_2")
        self.Calc_btn_right_2.clicked.connect(self.notification)

        self.groupBox_2 = QtWidgets.QGroupBox(self.page_6)
        self.groupBox_2.setGeometry(QtCore.QRect(0, 90, 511, 81))
        self.groupBox_2.setStyleSheet("font: 75 italic 10pt \"Palatino Linotype\";\n"
                                      "color:  rgb(50, 0, 150);")
        self.groupBox_2.setFlat(False)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName("groupBox_2")

        # *********************
        self.groupBox_3 = QtWidgets.QGroupBox(self.page_6)
        self.groupBox_3.setGeometry(QtCore.QRect(0, 190, 511, 91))
        self.groupBox_3.setStyleSheet("font: 75 italic 10pt \"Palatino Linotype\";\n"
                                      "color:  rgb(50, 0, 150);")
        self.groupBox_3.setFlat(False)
        self.groupBox_3.setCheckable(False)
        self.groupBox_3.setObjectName("groupBox_3")
        # ********************
        self.comboBox_3 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_3.setGeometry(QtCore.QRect(440, 40, 61, 20))
        self.comboBox_3.setStyleSheet("*{\n"
                                      "color: rgb(0, 0, 0);\n"
                                      "    \n"
                                      "font: 9pt \"MS Shell Dlg 2\";\n"
                                      "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
                                      "y2:0, stop:0 rgba(255, 255, 255, 255), stop:0.233831 rgba(0, 0, 0, 224));\n "
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "\n"
                                      "")
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")

        # ********************
        self.about_btn = QtWidgets.QPushButton(self.page_6)
        self.about_btn.setGeometry(QtCore.QRect(690, 10, 81, 21))
        self.about_btn.setStyleSheet("\n"
                                     "\n"
                                     "*{\n"
                                     "color:rgb(1, 1, 1);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton{\n"
                                     "border: 1px solid rgb(0,0, 0);\n"
                                     "background:  rgb(211, 211, 211);\n"
                                     "border-radius:10px;\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                     "}\n"
                                     "\n"
                                     "\n"
                                     "QPushButton:hover{\n"
                                     "\n"
                                     "color: rgb(211, 211, 211);\n"
                                     "    background-color: rgb(1, 0, 1);\n"
                                     "border-radius:10px;\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:pressed \n"
                                     "{\n"
                                     " border: 2px inset    rgb(0, 170, 0);\n"
                                     "background-color: #333;\n"
                                     "}")
        self.about_btn.setObjectName("about_btn")
        self.about_btn.clicked.connect(self.about)
        # ********************
        self.export_btn = QtWidgets.QPushButton(self.groupBox_2)
        self.export_btn.setGeometry(QtCore.QRect(10, 40, 101, 20))
        self.export_btn.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      ";\n"
                                      "    \n"
                                      "    background-color: rgb(0, 0, 0);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(0, 0, 0);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(0, 0, 0);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.clicked.connect(self.download)

        # **************
        self.import_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.import_btn.setGeometry(QtCore.QRect(10, 40, 101, 20))
        self.import_btn.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      ";\n"
                                      "    \n"
                                      "    background-color: rgb(0, 0, 0);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(0, 0, 0);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(0, 0, 0);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        self.import_btn.setObjectName("import_btn")
        self.import_btn.clicked.connect(self.Import)
        # ***************

        self.progressBar = QtWidgets.QProgressBar(self.groupBox_2)
        self.progressBar.setGeometry(QtCore.QRect(130, 40, 301, 20))
        self.progressBar.setStyleSheet("*{font: 9pt \"MV Boli\";\n"
                                       "color: rgb(0, 0, 0);}\n"
                                       "\n"
                                       "\n"
                                       "\n"
                                       "QProgressBar{\n"
                                       "    border: 3px solid #333;\n"
                                       "    border-radius: 5px;\n"
                                       "    text-align: center\n"
                                       "}\n"
                                       "\n"
                                       "QProgressBar::chunk {\n"
                                       "    background-color:rgb(0, 230, 0);\n"
                                       "    width: 10px;\n"
                                       "    margin:1px;\n"
                                       "}\n"
                                       "")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")

        # *********************
        self.progressBar_2 = QtWidgets.QProgressBar(self.groupBox_3)
        self.progressBar_2.setGeometry(QtCore.QRect(130, 40, 301, 20))
        self.progressBar_2.setStyleSheet("*{font: 9pt \"MV Boli\";\n"
                                         "color: rgb(0, 0, 0);}\n"
                                         "\n"
                                         "\n"
                                         "\n"
                                         "QProgressBar{\n"
                                         "    border: 3px solid #333;\n"
                                         "    border-radius: 5px;\n"
                                         "    text-align: center\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color:rgb(0, 230, 0);\n"
                                         "    width: 10px;\n"
                                         "    margin:1px;\n"
                                         "}\n"
                                         "")
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar_2.setTextVisible(True)
        self.progressBar_2.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar_2.setInvertedAppearance(False)
        self.progressBar_2.setObjectName("progressBar_2")
        # ---------------------
        self.toolBox_2.addItem(self.page_6, "")
        self.gridLayout_10.addWidget(self.toolBox_2, 0, 0, 1, 1)
        self.toolBox = QtWidgets.QToolBox(self.centralwidget)
        self.toolBox.setStyleSheet("*{color: rgb(0, 0, 0);\n"
                                   "font: 75 12pt \"Bahnschrift\";}")
        self.toolBox.setObjectName("toolBox")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 771, 302))
        self.page_3.setStyleSheet("background-color: rgb(211, 211, 211);")
        self.page_3.setObjectName("page_3")
        self.gridLayout_22 = QtWidgets.QGridLayout(self.page_3)
        self.gridLayout_22.setObjectName("gridLayout_22")
        self.gridLayout_21 = QtWidgets.QGridLayout()
        self.gridLayout_21.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_21.setObjectName("gridLayout_21")
        self.label_note = QtWidgets.QLabel(self.page_3)
        self.label_note.setStyleSheet("font: 75 10pt \"Bahnschrift\";")
        self.label_note.setFrameShape(QtWidgets.QFrame.Box)
        self.label_note.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_note.setLineWidth(2)
        self.label_note.setObjectName("label_note")
        self.gridLayout_21.addWidget(self.label_note, 0, 1, 1, 1)
        self.comment_btn_save = QtWidgets.QPushButton(self.page_3)
        self.comment_btn_save.setStyleSheet("*{\n"
                                            "color: rgb(255, 255, 255);\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:hover{\n"
                                            "color: rgb(255, 255, 255);\n"
                                            ";\n"
                                            "    \n"
                                            "    background-color: rgb(0, 0, 0);\n"
                                            "\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton{\n"
                                            "border: 1px solid  #333;\n"
                                            "background:  rgb(0, 0, 0);\n"
                                            "border-radius:10px;\n"
                                            "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                            "}\n"
                                            "\n"
                                            "\n"
                                            "QPushButton:hover{\n"
                                            "\n"
                                            "color: rgb(225, 150, 0);\n"
                                            "    background-color: rgb(0, 0, 0);\n"
                                            "border-radius:10px;\n"
                                            "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:pressed \n"
                                            "{\n"
                                            " border: 2px inset   rgb(225, 150, 0);\n"
                                            "background-color: #333;\n"
                                            "}")
        self.comment_btn_save.setObjectName("comment_btn_save")

        self.comment_btn_save.clicked.connect(self.save_comments)
        self.comment_btn_save.clicked.connect(self.act_comment_combo)

        self.gridLayout_21.addWidget(self.comment_btn_save, 0, 3, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.page_3)
        self.label_12.setStyleSheet("font: 63 italic  8pt \"Segoe UI Semibold\";")
        self.label_12.setObjectName("label_12")
        self.gridLayout_21.addWidget(self.label_12, 0, 5, 1, 1)
        self.comment_input = QtWidgets.QLineEdit(self.page_3)
        self.comment_input.setStyleSheet("\n"
                                         "QLineEdit{\n"
                                         "border-radius:8px;\n"
                                         "background-color: rgb(240, 240, 240);\n"
                                         "}background-color: rgb(255, 255, 255);")
        self.comment_input.setObjectName("comment_input")

        self.comment_input.returnPressed.connect(self.extract_comments)

        self.gridLayout_21.addWidget(self.comment_input, 0, 9, 1, 1)
        self.line_15 = QtWidgets.QFrame(self.page_3)
        self.line_15.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_15.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_15.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_15.setObjectName("line_15")
        self.gridLayout_21.addWidget(self.line_15, 0, 4, 1, 1)
        spacerItem14 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_21.addItem(spacerItem14, 0, 2, 1, 1)
        spacerItem15 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_21.addItem(spacerItem15, 0, 1, 1, 1)
        self.gridLayout_22.addLayout(self.gridLayout_21, 2, 0, 1, 1)

        self.note_combo = QtWidgets.QComboBox(self.page_3)
        self.note_combo.setStyleSheet("*{\n"
                                      "color: rgb(0, 0, 0);\n"
                                      "    \n"
                                      "font: 11pt \"MS Shell Dlg 2\";\n"
                                      "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                      "stop:0 rgba(211, 211, 211, 255), stop:0.233831 rgba(0, 0, 0, 224));\n "
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "\n"
                                      "")
        self.note_combo.setObjectName("note_combo")
        self.note_combo.currentIndexChanged.connect(self.combo_comments)
        self.gridLayout_21.addWidget(self.note_combo, 0, 6, 1, 1)

        self.label_12 = QtWidgets.QLabel(self.page_3)
        self.label_12.setStyleSheet("font: 63 italic  8pt \"Segoe UI Semibold\";")
        self.label_12.setObjectName("label_12")
        self.gridLayout_21.addWidget(self.label_12, 0, 8, 1, 1)

        self.label_20 = QtWidgets.QLabel(self.page_3)
        self.label_20.setStyleSheet("font: 63 italic  8pt \"Segoe UI Semibold\";")
        self.label_20.setObjectName("label_20")
        self.gridLayout_21.addWidget(self.label_20, 0, 5, 1, 1)

        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_21.addItem(spacerItem16, 0, 7, 1, 1)

        self.gridLayout_18 = QtWidgets.QGridLayout()
        self.gridLayout_18.setObjectName("gridLayout_18")
        spacerItem16 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_18.addItem(spacerItem16, 0, 3, 1, 1)
        self.minw = QtWidgets.QLabel(self.page_3)
        self.minw.setStyleSheet("color: rgb(0, 0, 0);\n"
                                "font: 9pt \"Palatino Linotype\"")
        self.minw.setObjectName("minw")
        self.gridLayout_18.addWidget(self.minw, 0, 2, 1, 1)

        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setStyleSheet("*{\n"
                                    "color: rgb(0, 0, 0);\n"
                                    "    \n"
                                    "font: 11pt \"MS Shell Dlg 2\";\n"
                                    "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                    "stop:0 rgba(211, 211, 211, 255), stop:0.233831 rgba(0, 0, 0, 224));\n "
                                    "}\n"
                                    "\n"
                                    "\n"
                                    "\n"
                                    "")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.currentIndexChanged.connect(self.selectionchange)
        self.gridLayout_8.addWidget(self.comboBox, 0, 4, 1, 1)

        spacerItem17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_18.addItem(spacerItem17, 0, 5, 1, 1)
        self.maxl = QtWidgets.QLabel(self.page_3)
        self.maxl.setStyleSheet("color: rgb(0, 0, 0);\n"
                                "font: 9pt \"Palatino Linotype\"")
        self.maxl.setObjectName("maxl")
        self.gridLayout_18.addWidget(self.maxl, 0, 4, 1, 1)
        spacerItem18 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_18.addItem(spacerItem18, 0, 1, 1, 1)
        self.minl = QtWidgets.QLabel(self.page_3)
        self.minl.setStyleSheet("color: rgb(0, 0, 0);\n"
                                "font: 9pt \"Palatino Linotype\"")
        self.minl.setObjectName("minl")
        self.gridLayout_18.addWidget(self.minl, 0, 6, 1, 1)
        self.maxw = QtWidgets.QLabel(self.page_3)
        self.maxw.setStyleSheet("color: rgb(0, 0, 0);\n"
                                "font: 9pt \"Palatino Linotype\"")
        self.maxw.setObjectName("maxw")
        self.gridLayout_18.addWidget(self.maxw, 0, 0, 1, 1)
        self.gridLayout_22.addLayout(self.gridLayout_18, 0, 0, 1, 1)
        self.comment_TextEdit = QtWidgets.QPlainTextEdit(self.page_3)
        self.comment_TextEdit.setStyleSheet("color: rgb(0, 0, 0);\n"
                                            "font: italic 10pt \"Yu Gothic UI\";")
        self.comment_TextEdit.setObjectName("comment_TextEdit")
        self.gridLayout_22.addWidget(self.comment_TextEdit, 3, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.line_16 = QtWidgets.QFrame(self.page_3)
        self.line_16.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_16.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_16.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_16.setObjectName("line_16")
        self.verticalLayout.addWidget(self.line_16)
        self.gridLayout_22.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.toolBox.addItem(self.page_3, "")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 771, 284))
        self.page_4.setObjectName("page_4")
        self.label_32 = QtWidgets.QLabel(self.page_4)
        self.label_32.setGeometry(QtCore.QRect(360, 90, 301, 21))
        self.label_32.setStyleSheet("background-color: rgb(211, 211, 211);font: 75 8pt \"Sitka Small\";\n"
                                    "\n"
                                    "color: rgb(0, 0, 0);")
        self.label_32.setWordWrap(True)
        self.label_32.setObjectName("label_32")
        self.label_37 = QtWidgets.QLabel(self.page_4)
        self.label_37.setGeometry(QtCore.QRect(360, 60, 301, 21))
        self.label_37.setStyleSheet("background-color: rgb(211, 211, 211);font: 75 8pt \"Sitka Small\";\n"
                                    "\n"
                                    "color: rgb(0, 0, 0);\n"
                                    "\n"
                                    "")
        self.label_37.setWordWrap(True)
        self.label_37.setObjectName("label_37")
        self.label_38 = QtWidgets.QLabel(self.page_4)
        self.label_38.setGeometry(QtCore.QRect(360, 120, 301, 20))
        self.label_38.setStyleSheet("background-color: rgb(211, 211, 211);font: 75 8pt \"Sitka Small\";\n"
                                    "\n"
                                    "color: rgb(0, 0, 0);")
        self.label_38.setWordWrap(True)
        self.label_38.setObjectName("label_38")
        self.Calc_btn_right = QtWidgets.QPushButton(self.page_4)
        self.Calc_btn_right.setGeometry(QtCore.QRect(470, 243, 141, 21))
        self.Calc_btn_right.setStyleSheet("*{\n"
                                          "color: rgb(255, 255, 255);\n"
                                          "}\n"
                                          "\n"
                                          "QPushButton:hover{\n"
                                          "color: rgb(255, 255, 255);\n"
                                          ";\n"
                                          "    \n"
                                          "    background-color: rgb(0, 0, 0);\n"
                                          "\n"
                                          "}\n"
                                          "\n"
                                          "QPushButton{\n"
                                          "border: 1px solid  #333;\n"
                                          "background:  rgb(0, 0, 0);\n"
                                          "border-radius:10px;\n"
                                          "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                          "}\n"
                                          "\n"
                                          "\n"
                                          "QPushButton:hover{\n"
                                          "\n"
                                          "color: rgb(225, 150, 0);\n"
                                          "    background-color: rgb(0, 0, 0);\n"
                                          "border-radius:10px;\n"
                                          "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                          "}\n"
                                          "\n"
                                          "QPushButton:pressed \n"
                                          "{\n"
                                          " border: 2px inset   rgb(225, 150, 0);\n"
                                          "background-color: #333;\n"
                                          "}")
        self.Calc_btn_right.setObjectName("Calc_btn_right")
        self.Calc_btn_right.clicked.connect(self.profit_calc)

        # *******************
        self.add_btn = QtWidgets.QPushButton(self.page_4)
        self.add_btn.setGeometry(QtCore.QRect(670, 195, 140, 20))
        self.add_btn.setStyleSheet("*{\n"
                                   "color: rgb(0, 0, 0);\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton:hover{\n"
                                   "color: rgb(255, 255, 255);\n"
                                   ";\n"
                                   "    \n"
                                   "    background-color: rgb(0, 0, 0);\n"
                                   "\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton{\n"
                                   "border: 1px solid  #333;\n"
                                   "background:  rgb(212, 211, 211);\n"
                                   "border-radius:10px;\n"
                                   "font: 75 6pt \"Sitka Small\";\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "QPushButton:hover{\n"
                                   "\n"
                                   "color: rgb(211, 211, 211);\n"
                                   "    background-color: rgb(0, 0, 0);\n"
                                   "border-radius:10px;\n"
                                   "font: 75 6pt \"Sitka Small\";\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton:pressed \n"
                                   "{\n"
                                   " border: 2px inset   rgb(225, 150, 0);\n"
                                   "background-color: #333;\n"
                                   "}")
        self.add_btn.setObjectName("add_btn")
        self.add_btn.clicked.connect(self.add_to_wallet)
        # *******************
        self.input_Calc_Profit_left = QtWidgets.QLineEdit(self.page_4)
        self.input_Calc_Profit_left.setGeometry(QtCore.QRect(440, 210, 201, 21))
        self.input_Calc_Profit_left.setStyleSheet("\n"
                                                  "QLineEdit{\n"
                                                  "border-radius:10px;\n"
                                                  "background-color: rgb(240, 240, 240);\n"
                                                  "}")
        self.input_Calc_Profit_left.setText("")
        self.input_Calc_Profit_left.setObjectName("input_Calc_Profit_left")
        self.input_Calc_Risk_left = QtWidgets.QLineEdit(self.page_4)
        self.input_Calc_Risk_left.setGeometry(QtCore.QRect(440, 180, 201, 21))
        self.input_Calc_Risk_left.setStyleSheet("\n"
                                                "QLineEdit{\n"
                                                "border-radius:10px;\n"
                                                "background-color: rgb(240, 240, 240);\n"
                                                "}")
        self.input_Calc_Risk_left.setText("")

        self.input_Calc_Risk_left.setObjectName("input_Calc_Risk_left")
        self.label_4 = QtWidgets.QLabel(self.page_4)
        self.label_4.setGeometry(QtCore.QRect(550, 7, 171, 25))
        self.label_4.setStyleSheet("background-color: rgb(211, 211, 211);\n"
                                   "font: 11pt \"Cambria Math\";\n"
                                   "\n"
                                   "color: rgb(0, 0, 0);")
        self.label_4.setFrameShape(QtWidgets.QFrame.Box)
        self.label_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_4.setLineWidth(1)

        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.comment_input_2 = QtWidgets.QLineEdit(self.page_4)
        self.comment_input_2.setGeometry(QtCore.QRect(370, 10, 171, 21))
        self.comment_input_2.setStyleSheet("\n"
                                           "QLineEdit{\n"
                                           "border-radius:10px;\n"
                                           "background-color: rgb(240, 240, 240);\n"
                                           "}")
        self.comment_input_2.setText("")
        self.comment_input_2.setObjectName("comment_input_2")

        self.comment_input_2.returnPressed.connect(self.btc_to_sato)

        self.label_40 = QtWidgets.QLabel(self.page_4)
        self.label_40.setGeometry(QtCore.QRect(360, 180, 75, 16))
        self.label_40.setObjectName("label_40")
        self.label_41 = QtWidgets.QLabel(self.page_4)
        self.label_41.setGeometry(QtCore.QRect(360, 210, 77, 16))
        self.label_41.setObjectName("label_41")
        self.print_result_Calc_left_1 = QtWidgets.QLabel(self.page_4)
        self.print_result_Calc_left_1.setGeometry(QtCore.QRect(670, 60, 171, 21))
        self.print_result_Calc_left_1.setStyleSheet("background-color: rgb(211, 211, 211);\n"
                                                    "font: 10pt \"Cambria Math\";\n"
                                                    "\n"
                                                    "color: rgb(0, 0, 0);")
        self.print_result_Calc_left_1.setObjectName("print_result_Calc_left_1")
        self.print_result_Calc_left_2 = QtWidgets.QLabel(self.page_4)
        self.print_result_Calc_left_2.setGeometry(QtCore.QRect(670, 90, 171, 21))
        self.print_result_Calc_left_2.setStyleSheet("background-color: rgb(211, 211, 211);\n"
                                                    "font: 10pt \"Cambria Math\";\n"
                                                    "color: rgb(0, 0, 0);")
        self.print_result_Calc_left_2.setObjectName("print_result_Calc_left_2")
        self.print_result_Calc_left_3 = QtWidgets.QLabel(self.page_4)
        self.print_result_Calc_left_3.setGeometry(QtCore.QRect(670, 120, 171, 21))
        self.print_result_Calc_left_3.setStyleSheet("background-color: rgb(211, 211, 211);\n"
                                                    "font: 10pt \"Cambria Math\";\n"
                                                    "color: rgb(0, 0, 0);")
        self.print_result_Calc_left_3.setObjectName("print_result_Calc_left_3")
        self.line_17 = QtWidgets.QFrame(self.page_4)
        self.line_17.setGeometry(QtCore.QRect(330, 10, 1, 251))
        self.line_17.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_17.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_17.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_17.setObjectName("line_17")
        self.input_entry = QtWidgets.QLineEdit(self.page_4)
        self.input_entry.setGeometry(QtCore.QRect(110, 120, 201, 21))
        self.input_entry.setStyleSheet("\n"
                                       "QLineEdit{\n"
                                       "border-radius:10px;\n"
                                       "background-color: rgb(240, 240, 240);\n"
                                       "}")
        self.input_entry.setText("")
        self.input_entry.setObjectName("input_entry")
        self.input_ordersize = QtWidgets.QLineEdit(self.page_4)
        self.input_ordersize.setGeometry(QtCore.QRect(110, 150, 201, 21))
        self.input_ordersize.setStyleSheet("\n"
                                           "QLineEdit{\n"
                                           "border-radius:10px;\n"
                                           "background-color: rgb(240, 240, 240);\n"
                                           "}")
        self.input_ordersize.setText("")
        self.input_ordersize.setObjectName("input_ordersize")
        self.input_risk_right = QtWidgets.QLineEdit(self.page_4)
        self.input_risk_right.setGeometry(QtCore.QRect(110, 180, 201, 21))
        self.input_risk_right.setStyleSheet("\n"
                                            "QLineEdit{\n"
                                            "border-radius:10px;\n"
                                            "background-color: rgb(240, 240, 240);\n"
                                            "}")
        self.input_risk_right.setText("")
        self.input_risk_right.setObjectName("input_risk_right")
        self.input_stop = QtWidgets.QLineEdit(self.page_4)
        self.input_stop.setGeometry(QtCore.QRect(110, 210, 201, 21))
        self.input_stop.setStyleSheet("\n"
                                      "QLineEdit{\n"
                                      "border-radius:10px;\n"
                                      "background-color: rgb(240, 240, 240);\n"
                                      "}")
        self.input_stop.setText("")
        self.input_stop.setObjectName("input_stop")
        self.Calc_btn_left = QtWidgets.QPushButton(self.page_4)
        self.Calc_btn_left.setGeometry(QtCore.QRect(135, 243, 141, 21))
        self.Calc_btn_left.setStyleSheet("*{\n"
                                         "color: rgb(255, 255, 255);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "color: rgb(255, 255, 255);\n"
                                         ";\n"
                                         "    \n"
                                         "    background-color: rgb(0, 0, 0);\n"
                                         "\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton{\n"
                                         "border: 1px solid  #333;\n"
                                         "background:  rgb(0, 0, 0);\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "\n"
                                         "color: rgb(225, 150, 0);\n"
                                         "    background-color: rgb(0, 0, 0);\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:pressed \n"
                                         "{\n"
                                         " border: 2px inset   rgb(225, 150, 0);\n"
                                         "background-color: #333;\n"
                                         "}")
        self.Calc_btn_left.setObjectName("Calc_btn_left")
        self.Calc_btn_left.clicked.connect(self.order_calc)

        self.label_42 = QtWidgets.QLabel(self.page_4)
        self.label_42.setGeometry(QtCore.QRect(30, 120, 55, 21))
        self.label_42.setObjectName("label_42")
        self.label_46 = QtWidgets.QLabel(self.page_4)
        self.label_46.setGeometry(QtCore.QRect(30, 150, 81, 21))
        self.label_46.setObjectName("label_46")
        self.label_47 = QtWidgets.QLabel(self.page_4)
        self.label_47.setGeometry(QtCore.QRect(30, 180, 71, 21))
        self.label_47.setObjectName("label_47")
        self.label_48 = QtWidgets.QLabel(self.page_4)
        self.label_48.setGeometry(QtCore.QRect(30, 210, 55, 21))
        self.label_48.setObjectName("label_48")
        self.resut_output = QtWidgets.QLabel(self.page_4)
        self.resut_output.setGeometry(QtCore.QRect(18, 2, 302, 34))
        self.resut_output.setStyleSheet("background-color: rgb(211, 211, 211);\n"
                                        "font: 75 10pt \"Sylfaen\";\n"
                                        "\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "\n"
                                        "")
        self.resut_output.setFrameShape(QtWidgets.QFrame.Box)
        self.resut_output.setFrameShadow(QtWidgets.QFrame.Raised)
        self.resut_output.setLineWidth(2)
        self.resut_output.setWordWrap(True)
        self.resut_output.setObjectName("resut_output")
        self.line_18 = QtWidgets.QFrame(self.page_4)
        self.line_18.setGeometry(QtCore.QRect(336, 40, 427, 1))
        self.line_18.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_18.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_18.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_18.setObjectName("line_18")
        self.line_24 = QtWidgets.QFrame(self.page_4)
        self.line_24.setGeometry(QtCore.QRect(10, 10, 1, 251))
        self.line_24.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_24.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_24.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_24.setObjectName("line_24")

        self.line_26 = QtWidgets.QFrame(self.page_4)
        self.line_26.setGeometry(QtCore.QRect(336, 274, 427, 1))
        self.line_26.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_26.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_26.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_26.setObjectName("line_26")
        self.line_27 = QtWidgets.QFrame(self.page_4)
        self.line_27.setGeometry(QtCore.QRect(13, 274, 311, 1))
        self.line_27.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_27.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_27.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_27.setObjectName("line_27")

        self.radioButton_ordersize = QtWidgets.QRadioButton(self.page_4)
        self.radioButton_ordersize.setGeometry(QtCore.QRect(30, 40, 121, 21))
        self.radioButton_ordersize.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_ordersize.toggled.connect(self.order_input_off)
        self.radioButton_ordersize.setObjectName("radioButton_ordersize")

        self.radioButton_risk = QtWidgets.QRadioButton(self.page_4)
        self.radioButton_risk.setGeometry(QtCore.QRect(30, 60, 111, 21))
        self.radioButton_risk.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_risk.toggled.connect(self.order_input_off)
        self.radioButton_risk.setObjectName("radioButton_risk")

        self.radioButton_Riskpercentage_right = QtWidgets.QCheckBox(self.page_4)
        self.radioButton_Riskpercentage_right.setGeometry(QtCore.QRect(170, 40, 151, 20))
        self.radioButton_Riskpercentage_right.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_Riskpercentage_right.stateChanged.connect(self.select_radiobutton)
        self.radioButton_Riskpercentage_right.setObjectName("radioButton_Riskpercentage_right")

        self.radioButton_Risksato_right = QtWidgets.QCheckBox(self.page_4)
        self.radioButton_Risksato_right.setGeometry(QtCore.QRect(170, 60, 151, 20))
        self.radioButton_Risksato_right.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_Risksato_right.stateChanged.connect(self.select_radiobutton)
        self.radioButton_Risksato_right.setObjectName("radioButton_Risksato_right")

        self.radioButton_Riskpercentage_left = QtWidgets.QRadioButton(self.page_4)
        self.radioButton_Riskpercentage_left.setGeometry(QtCore.QRect(360, 150, 149, 20))
        self.radioButton_Riskpercentage_left.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_Riskpercentage_left.toggled.connect(self.select_profit_lable)
        self.radioButton_Riskpercentage_left.setObjectName("radioButton_Riskpercentage_left")

        self.Radiobtn_Risksato_left = QtWidgets.QRadioButton(self.page_4)
        self.Radiobtn_Risksato_left.setGeometry(QtCore.QRect(600, 150, 131, 20))
        self.Radiobtn_Risksato_left.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.Radiobtn_Risksato_left.toggled.connect(self.select_profit_lable)
        self.Radiobtn_Risksato_left.setObjectName("Radiobtn_Risksato_left")

        self.radioButton_stop = QtWidgets.QRadioButton(self.page_4)
        self.radioButton_stop.setGeometry(QtCore.QRect(30, 80, 95, 21))
        self.radioButton_stop.setStyleSheet("font: 9pt \"Palatino Linotype\";")
        self.radioButton_stop.toggled.connect(self.order_input_off)
        self.radioButton_stop.setObjectName("radioButton_stop")

        self.toolBox.addItem(self.page_4, "")
        self.gridLayout_10.addWidget(self.toolBox, 1, 0, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_10, 5, 0, 2, 2)
        self.gridLayout_13 = QtWidgets.QGridLayout()
        self.gridLayout_13.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_13.setSpacing(7)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.toolButton_4 = QtWidgets.QToolButton(self.frame)
        self.toolButton_4.setGeometry(QtCore.QRect(80, 5, 127, 57))
        self.toolButton_4.setStyleSheet("border-radius:20px;\n"
                                        "background-color: rgb(51, 51, 51);")
        self.toolButton_4.setText("")
        self.toolButton_4.setObjectName("toolButton_4")
        self.win_rate_loss = QtWidgets.QToolButton(self.frame)
        self.win_rate_loss.setGeometry(QtCore.QRect(86, 11, 114, 46))
        self.win_rate_loss.setStyleSheet("border-radius:15px;\n"
                                         "background-color: rgb(211, 211, 211);\n"
                                         "font: 63 17pt \"Yu Gothic UI Semibold\";\n"
                                         "color: #c30000;")
        self.win_rate_loss.setObjectName("win_rate_loss")
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setGeometry(QtCore.QRect(10, 10, 61, 20))
        self.label_7.setStyleSheet("font: 63 italic 10pt \"Segoe UI Semibold\";\n"
                                   "color: rgb(170, 0, 0);\n"
                                   "font: 75 12pt \"Times New Roman\";")
        self.label_7.setObjectName("label_7")
        self.gridLayout_13.addWidget(self.frame, 0, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.toolButton_5 = QtWidgets.QToolButton(self.frame_2)
        self.toolButton_5.setGeometry(QtCore.QRect(80, 5, 127, 57))
        self.toolButton_5.setStyleSheet("border-radius:20px;\n"
                                        "background-color: rgb(51, 51, 51);")
        self.toolButton_5.setText("")
        self.toolButton_5.setObjectName("toolButton_5")
        self.win_rate_win = QtWidgets.QToolButton(self.frame_2)
        self.win_rate_win.setGeometry(QtCore.QRect(86, 11, 114, 46))
        self.win_rate_win.setStyleSheet("border-radius:15px;\n"
                                        "background-color: rgb(211, 211, 211);\n"
                                        "color:#008400;\n"
                                        "font: 63 17pt \"Yu Gothic UI Semibold\";")
        self.win_rate_win.setObjectName("win_rate_win")
        self.label_8 = QtWidgets.QLabel(self.frame_2)
        self.label_8.setGeometry(QtCore.QRect(10, 10, 61, 20))
        self.label_8.setStyleSheet("color: rgb(0, 170, 0);\n"
                                   "font: 63 italic 12pt \"Segoe UI Semibold\";\n"
                                   "font: 75 12pt \"Times New Roman\";")
        self.label_8.setObjectName("label_8")
        self.gridLayout_13.addWidget(self.frame_2, 0, 1, 1, 1)
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.toolButton_6 = QtWidgets.QToolButton(self.frame_3)
        self.toolButton_6.setGeometry(QtCore.QRect(80, 5, 127, 57))
        self.toolButton_6.setStyleSheet("border-radius:20px;\n"
                                        "background-color: rgb(51, 51, 51);")
        self.toolButton_6.setText("")
        self.toolButton_6.setObjectName("toolButton_6")
        self.win_rate_win_2 = QtWidgets.QToolButton(self.frame_3)
        self.win_rate_win_2.setGeometry(QtCore.QRect(86, 11, 114, 46))
        self.win_rate_win_2.setStyleSheet("border-radius:15px;\n"
                                          "background-color: rgb(211, 211, 211);\n"
                                          "color: #008400;\n"
                                          "font: 63 17pt \"Yu Gothic UI Semibold\";")
        self.win_rate_win_2.setObjectName("win_rate_win_2")
        self.label_10 = QtWidgets.QLabel(self.frame_3)
        self.label_10.setGeometry(QtCore.QRect(10, 10, 61, 20))
        self.label_10.setStyleSheet("color: rgb(0, 0, 0);\n"
                                    "font: 63 italic 12pt \"Segoe UI Semibold\";\n"
                                    "font: 75 12pt \"Times New Roman\";")
        self.label_10.setObjectName("label_10")
        self.gridLayout_13.addWidget(self.frame_3, 0, 2, 1, 1)
        self.gridLayout_23.addLayout(self.gridLayout_13, 7, 0, 1, 2)
        self.gridLayout_25 = QtWidgets.QGridLayout()
        self.gridLayout_25.setObjectName("gridLayout_25")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setStyleSheet("color: rgb(0, 170, 0);\n"
                                    "font: 9pt \"MS Shell Dlg 2\";")
        self.label_13.setObjectName("label_13")
        self.gridLayout_25.addWidget(self.label_13, 0, 18, 1, 1)

        self.input_amount_BS_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.input_amount_BS_2.setStyleSheet("*{\n"
                                             "font: 63 10pt \"Bahnschrift SemiBold SemiConden\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background-color: rgb(240, 240, 240);\n"
                                             "}")
        self.input_amount_BS_2.setObjectName("input_amount_BS_2")

        self.gridLayout_25.addWidget(self.input_amount_BS_2, 1, 1, 1, 1)

        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setStyleSheet("color: rgb(255, 0, 0);\n"
                                    "font: 9pt \"MS Shell Dlg 2\";")
        self.label_17.setObjectName("label_17")
        self.gridLayout_25.addWidget(self.label_17, 2, 18, 1, 1)
        self.gridLayout_24 = QtWidgets.QGridLayout()
        self.gridLayout_24.setObjectName("gridLayout_24")
        self.line_23 = QtWidgets.QFrame(self.centralwidget)
        self.line_23.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_23.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_23.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_23.setObjectName("line_23")
        self.gridLayout_24.addWidget(self.line_23, 0, 0, 1, 1)
        self.gridLayout_25.addLayout(self.gridLayout_24, 1, 17, 1, 1)
        spacerItem19 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_25.addItem(spacerItem19, 1, 11, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.centralwidget)
        self.label_19.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_19.setObjectName("label_19")
        self.gridLayout_25.addWidget(self.label_19, 1, 13, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_18.setObjectName("label_18")
        self.gridLayout_25.addWidget(self.label_18, 1, 9, 1, 1)
        self.input_amount_BS = QtWidgets.QLineEdit(self.centralwidget)
        self.input_amount_BS.setStyleSheet("*{\n"
                                           "font: 63 10pt \"Bahnschrift SemiBold SemiConden\";\n"
                                           "color: rgb(0, 0, 0);\n"
                                           "}\n"
                                           "QLineEdit{\n"
                                           "border-radius:8px;\n"
                                           "background-color: rgb(240, 240, 240);\n"
                                           "}")
        self.input_amount_BS.setObjectName("input_amount_BS")
        self.gridLayout_25.addWidget(self.input_amount_BS, 1, 6, 1, 1)
        self.input_Entry_BS = QtWidgets.QLineEdit(self.centralwidget)
        self.input_Entry_BS.setStyleSheet("\n"
                                          "QLineEdit{\n"
                                          "border-radius:8px;\n"
                                          "background-color: rgb(240, 240, 240);\n"
                                          "}\n"
                                          "\n"
                                          "*{\n"
                                          "font: 63 10pt \"Bahnschrift SemiBold SemiConden\";\n"
                                          "color: rgb(0, 0, 0);\n"
                                          "}")
        self.input_Entry_BS.setObjectName("input_Entry_BS")
        self.gridLayout_25.addWidget(self.input_Entry_BS, 1, 10, 1, 1)
        self.input_Exit_BS = QtWidgets.QLineEdit(self.centralwidget)
        self.input_Exit_BS.setStyleSheet("\n"
                                         "QLineEdit{\n"
                                         "border-radius:8px;\n"
                                         "background-color: rgb(240, 240, 240);\n"
                                         "}\n"
                                         "*{\n"
                                         "font: 63 10pt \"Bahnschrift SemiBold SemiConden\";\n"

                                         "color: rgb(0, 0, 0);\n"
                                         "}")
        self.input_Exit_BS.setObjectName("input_Exit_BS")
        self.gridLayout_25.addWidget(self.input_Exit_BS, 1, 14, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_9.setObjectName("label_9")
        self.gridLayout_25.addWidget(self.label_9, 1, 5, 1, 1)
        self.btn_SELL = QtWidgets.QPushButton(self.centralwidget)
        self.btn_SELL.setStyleSheet("\n"
                                    "\n"
                                    "*{\n"
                                    "color: rgb(255, 0, 0);\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:hover{\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "    \n"
                                    "background-color: rgb(0, 170, 0);\n"
                                    "\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton{\n"
                                    "border: 1px solid  #333;\n"
                                    "background:  rgb(0, 0, 0);\n"
                                    "border-radius:10px;\n"
                                    "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                    "}\n"
                                    "\n"
                                    "\n"
                                    "QPushButton:hover{\n"
                                    "\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "    background-color: rgb(0, 0, 0);\n"
                                    "border-radius:10px;\n"
                                    "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:pressed \n"
                                    "{\n"
                                    " border: 2px inset   rgb(255, 0, 0);\n"
                                    "background-color: #333;\n"
                                    "}")
        self.btn_SELL.setObjectName("btn_SELL")

        self.btn_SELL.clicked.connect(self.calc_openTradeSELL)

        self.gridLayout_25.addWidget(self.btn_SELL, 2, 17, 1, 1)
        self.btn_BUY = QtWidgets.QPushButton(self.centralwidget)
        self.btn_BUY.setStyleSheet("\n"
                                   "\n"
                                   "*{\n"
                                   "color: rgb(0, 208, 0);\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton:hover{\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "    \n"
                                   "background-color: rgb(0, 170, 0);\n"
                                   "\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton{\n"
                                   "border: 1px solid  #333;\n"
                                   "background:  rgb(0, 0, 0);\n"
                                   "border-radius:10px;\n"
                                   "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "QPushButton:hover{\n"
                                   "\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "    background-color: rgb(0, 0, 0);\n"
                                   "border-radius:10px;\n"
                                   "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton:pressed \n"
                                   "{\n"
                                   " border: 2px inset    rgb(0, 170, 0);\n"
                                   "background-color: #333;\n"
                                   "}")
        self.btn_BUY.setObjectName("btn_BUY")

        self.btn_BUY.clicked.connect(self.calc_openTradeBUY)

        self.gridLayout_25.addWidget(self.btn_BUY, 0, 17, 1, 1)
        spacerItem20 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_25.addItem(spacerItem20, 1, 0, 1, 1)
        spacerItem21 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_25.addItem(spacerItem21, 1, 3, 1, 1)
        spacerItem22 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_25.addItem(spacerItem22, 1, 7, 1, 1)
        self.line_19 = QtWidgets.QFrame(self.centralwidget)
        self.line_19.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_19.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_19.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_19.setObjectName("line_19")
        self.gridLayout_25.addWidget(self.line_19, 1, 8, 1, 1)
        self.line_20 = QtWidgets.QFrame(self.centralwidget)
        self.line_20.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_20.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_20.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_20.setObjectName("line_20")
        self.gridLayout_25.addWidget(self.line_20, 1, 12, 1, 1)
        self.line_22 = QtWidgets.QFrame(self.centralwidget)
        self.line_22.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_22.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_22.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_22.setObjectName("line_22")
        self.gridLayout_25.addWidget(self.line_22, 1, 4, 1, 1)

        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setStyleSheet("font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_14.setObjectName("label_14")
        self.gridLayout_25.addWidget(self.label_14, 1, 0, 1, 1)

        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setChecked(True)
        self.checkBox.stateChanged.connect(self.allow)
        self.gridLayout_25.addWidget(self.checkBox, 2, 1, 1, 1)

        self.open_trade = QtWidgets.QCheckBox(self.centralwidget)
        self.open_trade.setStyleSheet("color: rgb(0, 0, 158);\n"
                                      "font: 75 9pt \"Palatino Linotype\";\n"
                                      "color:rgb(85, 0, 255);")
        self.open_trade.setObjectName("open_trade")
        self.open_trade.stateChanged.connect(self.opentrade)
        self.gridLayout_25.addWidget(self.open_trade, 0, 1, 1, 1)

        self.input_amount_BS_2.setReadOnly(True)

        self.gridLayout_23.addLayout(self.gridLayout_25, 7, 3, 1, 2)

        self.gridLayout_23.addLayout(self.gridLayout_25, 7, 3, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1735, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.toolBox_2.setCurrentIndex(0)
        self.toolBox_2.layout().setSpacing(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # --------------------------------------------
        _translate = QtCore.QCoreApplication.translate
        self.TABLE_Widget.setSortingEnabled(False)
        item = self.TABLE_Widget.horizontalHeaderItem(0)
        item.setText(_translate("MyAPP", "ID"))
        item = self.TABLE_Widget.horizontalHeaderItem(1)
        item.setText(_translate("MyAPP", "DATE"))
        item = self.TABLE_Widget.horizontalHeaderItem(2)
        item.setText(_translate("MyAPP", "AMOUNT"))
        item = self.TABLE_Widget.horizontalHeaderItem(3)
        item.setText(_translate("MyAPP", "ENTRY"))
        item = self.TABLE_Widget.horizontalHeaderItem(4)
        item.setText(_translate("MyAPP", "EXIT"))
        item = self.TABLE_Widget.horizontalHeaderItem(5)
        item.setText(_translate("MyAPP", "RESULT"))
        __sortingEnabled = self.TABLE_Widget.isSortingEnabled()
        self.TABLE_Widget.setSortingEnabled(False)
        # ==========================call when the program starts=============================
        threading.Thread(target=lambda: API.every(30, self.update)).start()
        threading.Thread(target=lambda: API.every(40, self.user_wallet)).start()
        self.make_journal()
        self.user_wallet()
        self.open_active()
        self.act_comment_combo()

        # =====================

    def act_comment_combo(self):  # write note dates in the combobox
        _translate = QtCore.QCoreApplication.translate
        self.note_combo.clear()

        if Table(c, f'comments_{identity}').check_table():
            c.execute(f"select * from 'comments_{identity}'")
            count = c.fetchall()
        else:
            count = ""

        for i in range(len(count)):
            date = eval(count[len(count) - i - 1][1])["date"]
            self.note_combo.addItem("")
            self.note_combo.setItemText(i, _translate("MainWindow", f"{date}"))

    def opentrade_act(self):  # open trade starting state
        try:
            if not Table(c, f'open_trade_{identity}').check_table():
                Table(c, f'open_trade_{identity}').create_table()

                data = {"date": 0, "amount": 0,
                        "entry": 0, "state": "closed"}
                InsertData(c, 1, str(data), f'open_trade_{identity}').insert_data()

                data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                InsertData(c, 2, str(data_), f'open_trade_{identity}').insert_data()
            else:
                pass
        except Exception:
            pass

    def noti_act(self):  # create notification table for the first time
        global api
        global identity
        try:
            ring = "long-chime-sound"
            if not Table(api, f'notify_{identity}').check_table():
                Table(api, f'notify_{identity}').create_table()
                data = {"BTC": (0, 0), "ETH": (0, 0), "LTC": (0, 0), "ring": ring}
                InsertData(api, 1, str(data), f'notify_{identity}').insert_data()
                r_data = {"1": 1, "2": 1, "3": 1}
                InsertData(api, 2, str(r_data), f'notify_{identity}').insert_data()
            else:
                pass
        except Exception:
            pass

    def make_journal(self):  # call functions for generating the journal data
        try:
            self.row()
            self.table()
            self.rate()
            self.graph_combobox()
            self.graph("ALL")
            self.data_size()
        except Exception:
            pass

    def data_size(self):  # dispay the user's database size
        global identity
        _translate = QtCore.QCoreApplication.translate
        size = file_size(f'{identity}.db')

        self.label_28.setText(_translate("MainWindow",
                                         f"<html><head/><body><p><span style=\" font-size:9pt;\">DATA SIZE : "
                                         f"</span><span style=\" font-size:9pt; font-weight:600; color:#000000;\">"
                                         f" {size}</span></p></body></html>"))

    def graph(self, change="ALL"):  # display the graph
        global c
        global identity
        try:
            canvas = MyMplCanvas(self.Graph_frame, width=20, height=20, change=change)
            canvas.setGeometry(QtCore.QRect(10, 10, 750, 269))
            _translate = QtCore.QCoreApplication.translate

            def fet(name):
                c.execute(f"select * from '{name}'")
                return c.fetchall()

            if change == "ALL":
                if Table(c, f'rate_P_{identity}').check_table():
                    p = fet(f'rate_P_{identity}')
                    n = fet(f'rate_N_{identity}')
                    y_p = []
                    y_n = []
                    if len(p) >= 1:
                        for i in range(len(p)):
                            y_p.append(p[i][1])
                    else:
                        y_p = [0]

                    if len(n) >= 1:
                        for x in range(len(n)):
                            y_n.append(n[x][1])
                    else:
                        y_n = [0]

                    self.maxw.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MAX Gain: <span style=\" "
                                                 "color:#009100;\">+</span><span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#009100;\">{round(max(y_p), 5)}₿</span></p></body></html>"))
                    self.minw.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MIN Gain: <span style=\" "
                                                 "color:#009100;\">+</span><span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#009100;\">{round(min(y_p), 5)}₿</span></p></body></html>"))
                    self.maxl.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MAX Loss: <span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#c30000;\">{round(min(y_n), 5)}₿</span></p></body></html>"))
                    self.minl.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MIN Loss: <span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#c30000;\">{round(max(y_n), 5)}₿</span></p></body></html>"))
                else:
                    pass
            else:
                try:
                    month, year = change.split("/")  # year in graph_{year}
                    data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                    y_p = []
                    y_n = []
                    for i in data:
                        if i[1] > 0:
                            y_p.append(i[1])
                        else:
                            y_n.append(i[1])

                    if len(y_p) == 0:
                        y_p = [0]
                    else:
                        pass
                    if len(y_n) == 0:
                        y_n = [0]
                    else:
                        pass

                    self.maxw.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MAX Gain: <span style=\" "
                                                 "color:#009100;\">+</span><span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#009100;\">{round(max(y_p), 5)}₿</span></p></body></html>"))
                    self.minw.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MIN Gain: <span style=\" "
                                                 "color:#009100;\">+</span><span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#009100;\">{round(min(y_p), 5)}₿</span></p></body></html>"))
                    self.maxl.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MAX Loss: <span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#c30000;\">{round(min(y_n), 5)}₿</span></p></body></html>"))
                    self.minl.setText(_translate("MyAPP",
                                                 "<html><head/><body><p>MIN Loss: <span "
                                                 "style=\" font-size:9pt; font-weight:600; "
                                                 f"color:#c30000;\">{round(max(y_n), 5)}₿</span></p></body></html>"))

                except Exception:
                    if Table(c, f'rate_P_{identity}').check_table():
                        p = fet(f'rate_P_{identity}')
                        n = fet(f'rate_N_{identity}')
                        y_p = []
                        y_n = []
                        if len(p) >= 1:
                            for i in range(len(p)):
                                y_p.append(p[i][1])
                        else:
                            y_p = [0]

                        if len(n) >= 1:
                            for x in range(len(n)):
                                y_n.append(n[x][1])
                        else:
                            y_n = [0]

                        self.maxw.setText(_translate("MyAPP",
                                                     "<html><head/><body><p>MAX Gain: <span style=\" "
                                                     "color:#009100;\">+</span><span "
                                                     "style=\" font-size:9pt; font-weight:600; "
                                                     f"color:#009100;\">{round(max(y_p), 5)}₿</span></p></body></html>"))
                        self.minw.setText(_translate("MyAPP",
                                                     "<html><head/><body><p>MIN Gain: <span style=\" "
                                                     "color:#009100;\">+</span><span "
                                                     "style=\" font-size:9pt; font-weight:600; "
                                                     f"color:#009100;\">{round(min(y_p), 5)}₿</span></p></body></html>"))
                        self.maxl.setText(_translate("MyAPP",
                                                     "<html><head/><body><p>MAX Loss: <span "
                                                     "style=\" font-size:9pt; font-weight:600; "
                                                     f"color:#c30000;\">{round(min(y_n), 5)}₿</span></p></body></html>"))
                        self.minl.setText(_translate("MyAPP",
                                                     "<html><head/><body><p>MIN Loss: <span "
                                                     "style=\" font-size:9pt; font-weight:600; "
                                                     f"color:#c30000;\">{round(max(y_n), 5)}₿</span></p></body></html>"))
        except Exception:
            pass

    @staticmethod
    def check():
        global c
        global identity
        try:
            c.execute(f"select * from 'journal_{identity}'")
            count = c.fetchall()
            return len(count)
        except Exception:
            pass

    def delete(self):  # deleting data from database
        global c
        global identity

        _translate = QtCore.QCoreApplication.translate

        id_ = str(self.input_delete.text())
        if id_ == "":
            pass
        else:
            try:
                int(id_)
                try:
                    before = self.check()

                    id_ = str(self.input_delete.text())
                    sign_value = eval(ExtractData(c, id_, f'journal_{identity}').get_data()[0][1])["result"]
                    date_str = eval(ExtractData(c, id_, f'journal_{identity}').get_data()[0][1])["date"]

                    if Table(c, f'journal_{identity}').check_table():
                        ExtractData(c, id_, f'journal_{identity}').delete()
                        ExtractData(c, id_, f'graph_{identity}').delete()

                        if not Table(c, f"save_{identity}").check_table():
                            Table(c, f"save_{identity}").create_table()
                            data = before - self.check()
                            InsertData(c, 1, str(data), f"save_{identity}").insert_data()
                        else:
                            data = ExtractData(c, 1, f"save_{identity}").get_data()[0][1] + (
                                    before - self.check())
                            InsertData(c, 1, str(data), f"save_{identity}").update_data()

                        result = float(sign_value)
                        if result < 0:
                            # -------------------------------------add------------------------------------------
                            ExtractData(c, id_, f'rate_N_{identity}').delete()

                            add_data = {"total_gain":
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                "total_gain"]
                                , "total_loss": float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()
                                                           [0][1])["total_loss"]) - result}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                        else:
                            ExtractData(c, id_, f'rate_p_{identity}').delete()

                            add_data = {"total_gain":
                                            float(
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_gain"]
                                            ) - result, "total_loss":
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                "total_loss"]}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                        # *****************************************

                        year = int(date_str.split("-")[2])
                        month = int(date_str.split("-")[0])
                        if Table(c, f'graph_{year}_{identity}').check_table():

                            tups = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])

                            value = (str(date_str), result)
                            for t in range(len(tups)):
                                if tups[t] == value:
                                    index = t
                                    break
                                else:
                                    index = None

                            if index is None:
                                pass
                            else:

                                remove_value = tups[index]
                                tups.remove(remove_value)

                                M_data = tups
                                InsertData(c, month, str(M_data), f'graph_{year}_{identity}').update_data()
                        self.input_delete.setText(_translate("MyAPP", ""))

                    else:
                        pass
                except Exception:
                    msg = QMessageBox()
                    msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Error")
                    msg.setInformativeText(f'The ID {id_} cannot be found.')
                    msg.setWindowTitle("ID Error")
                    msg.exec_()
                    self.input_delete.setText(_translate("MyAPP", ""))
            except Exception:
                pass

    def modify(self):  # modifying data in the database
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            pss = 0
            data = str(self.input_modify.text())
            id_, amount, entry, exit_, SB = data.split("/")
            x = ""
            result = 0
            if SB.lower() == "buy":
                result = ((float(exit_) - float(entry)) / float(entry)) * (float(amount) * (1 / float(API.btc()[1])))
                x = "▲"
                pss = 1
            elif SB.lower() == "sell":
                result = ((float(entry) - float(exit_)) / float(entry)) * (float(amount) * (1 / float(API.btc()[1])))
                x = "▼"
                pss = 1
            else:
                msg = QMessageBox()
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Input Error")
                msg.setInformativeText("Please enter the correct format\nID/Amount/Entry/Exit/(Sell or Buy)\n"
                                       "with the forward slash.")
                msg.setWindowTitle("input-Error")
                msg.exec_()

            if pss == 1:
                if result > 0:
                    _result = "+" + str(round(result, 5))
                else:
                    _result = str(round(result, 5))

                if SB.lower() == "buy" or SB.lower() == "sell":
                    date_str = eval(ExtractData(c, id_, f'journal_{identity}').get_data()[0][1])["date"]

                    try:
                        old_result = float(
                            eval(ExtractData(c, id_, f'journal_{identity}').get_data()[0][1])["result"])
                    except TypeError:
                        old_result = float(eval(ExtractData(c, id_, f'journal_{identity}').get_data()[0][1])
                                           ["result"].split("+")[1])

                    data = {"date": date_str, "amount": f"{x} " + str(amount), "entry": entry, "exit": exit_,
                            "result": _result}

                    graph_data = {"date": date_str, "result": result}
                    # journal
                    InsertData(c, id_, str(data), f'journal_{identity}').update_data()
                    # graph
                    InsertData(c, id_, str(graph_data), f'graph_{identity}').update_data()
                    self.input_modify.setText(_translate("MyAPP", ""))
                    # rate_p
                    # rate_n

                    if result > 0:

                        # -------------------------------------add-----------------------------------------
                        if old_result > 0:
                            rate_value = result
                            InsertData(c, id_, str(rate_value), f'rate_p_{identity}').update_data()

                            add_data = {"total_gain":
                                            (float(
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_gain"]
                                            ) - float(old_result)) + result, "total_loss":
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                "total_loss"]}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()
                        else:

                            rate_value = result
                            InsertData(c, id_, str(rate_value), f'rate_p_{identity}').insert_data()

                            # -------------------save----------------------
                            ExtractData(c, id_, f'rate_N_{identity}').delete()

                            if not Table(c, f"save_{identity}").check_table():
                                Table(c, f"save_{identity}").create_table()
                                data = 1
                                InsertData(c, 1, str(data), f"save_{identity}").insert_data()
                            else:
                                data = int(ExtractData(c, 1, f"save_{identity}").get_data()[0][1]) + 1
                                InsertData(c, 1, str(data), f"save_{identity}").update_data()

                            add_data = {"total_gain":
                                            float(
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_gain"]
                                            ) + result, "total_loss":
                                            (float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()
                                                        [0][1])["total_loss"]) - float(old_result))}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    else:

                        # -------------------------------------add------------------------------------------
                        if old_result < 0:
                            rate_value = result
                            InsertData(c, id_, str(rate_value), f'rate_N_{identity}').update_data()

                            add_data = {"total_gain":
                                            eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                "total_gain"]
                                , "total_loss": float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()
                                                           [0][1])["total_loss"] - float(old_result)) + result}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()
                        else:

                            rate_value = result
                            InsertData(c, id_, str(rate_value), f'rate_N_{identity}').insert_data()
                            # -------------------save----------------------
                            ExtractData(c, id_, f'rate_P_{identity}').delete()
                            if not Table(c, f"save_{identity}").check_table():
                                Table(c, f"save_{identity}").create_table()
                                data = 1
                                InsertData(c, 1, str(data), f"save_{identity}").insert_data()
                            else:
                                data = int(ExtractData(c, 1, f"save_{identity}").get_data()[0][1]) + 1
                                InsertData(c, 1, str(data), f"save_{identity}").update_data()

                            add_data = {"total_gain":
                                            float(
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_gain"]
                                            ) - old_result, "total_loss":
                                            (float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()
                                                        [0][1])["total_loss"]) + result)}
                            InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                    year = int(date_str.split("-")[2])
                    month = int(date_str.split("-")[0])
                    if Table(c, f'graph_{year}_{identity}').check_table():

                        tups = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])

                        value = (str(date_str), old_result)
                        for t in range(len(tups)):
                            if tups[t] == value:
                                index = t
                                break
                            else:
                                index = None

                        if index is None:
                            pass
                        else:

                            append_value = (date_str, round(result, 5))
                            remove_value = tups[index]

                            tups.insert(index, append_value)
                            tups.remove(remove_value)

                            M_data = tups
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').update_data()
            else:
                pass

        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Input Error")
            msg.setInformativeText("Please enter the correct format\nID/Amount/Entry/Exit/(Sell or Buy)\n"
                                   "with the forward slash.")
            msg.setWindowTitle("input-Error")
            msg.exec_()
            pass

    def exe(self):  # fetchall data in journal table
        global c
        global identity
        c.execute(f"select * from 'journal_{identity}'")
        return c.fetchall()

    def row(self):  # initialize the qtable rows
        global c
        global identity
        try:

            if not Table(c, f'journal_{identity}').check_table():
                count = ""
                pass
            else:
                count = self.exe()

            self.TABLE_Widget.setRowCount(len(count) + 1)

            ###################################################
            state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

            if state != "closed":
                state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]
                if state == "BUY":  # bg green (0, 255, 0)
                    bg = QtGui.QColor(0, 255, 0)
                    fg = QtGui.QColor(0, 0, 0)
                    bgd = QtCore.Qt.Dense2Pattern
                elif state == "SELL":  # red (255, 0, 0)
                    bg = QtGui.QColor(255, 0, 0)
                    fg = QtGui.QColor(0, 0, 0)
                    bgd = QtCore.Qt.Dense2Pattern
                else:
                    bg = QtGui.QColor(51, 51, 51)
                    fg = QtGui.QColor(255, 255, 255)
                    bgd = QtCore.Qt.SolidPattern
            else:
                bg = QtGui.QColor(51, 51, 51)
                fg = QtGui.QColor(255, 255, 255)
                bgd = QtCore.Qt.SolidPattern
            # **************Open*******************
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont()
            font.setBold(True)
            font.setItalic(False)
            font.setUnderline(False)
            font.setWeight(75)
            font.setStrikeOut(False)
            font.setKerning(True)
            font.setStyleStrategy(QtGui.QFont.PreferDefault)
            item.setFont(font)
            brush = QtGui.QBrush(bg)  # bg
            brush.setStyle(bgd)  # bgd
            item.setBackground(brush)
            brush = QtGui.QBrush(fg)  # fg
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setForeground(brush)
            self.TABLE_Widget.setItem(0, 0, item)
            # *****************date******************
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont()
            item.setFont(font)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setForeground(brush)
            # --
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.TABLE_Widget.setItem(0, 1, item)
            # *****************amount*******************
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont()
            item.setFont(font)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setForeground(brush)
            # --
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.TABLE_Widget.setItem(0, 2, item)
            # *****************entry********************
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont()
            item.setFont(font)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setForeground(brush)
            # --
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.TABLE_Widget.setItem(0, 3, item)
            # *******************exit*********************

            item = QtWidgets.QTableWidgetItem()
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.TABLE_Widget.setItem(0, 4, item)
            # *******************result*********************
            item = QtWidgets.QTableWidgetItem()
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            self.TABLE_Widget.setItem(0, 5, item)
            # -----------------------------------------------

            k = 0
            for i in range(1, len(count) + 1):
                item = QtWidgets.QTableWidgetItem()
                self.TABLE_Widget.setItem(i, 0, item)
                item = QtWidgets.QTableWidgetItem()
                self.TABLE_Widget.setItem(i, 1, item)
                item = QtWidgets.QTableWidgetItem()
                self.TABLE_Widget.setItem(i, 2, item)
                item = QtWidgets.QTableWidgetItem()
                self.TABLE_Widget.setItem(i, 3, item)
                item = QtWidgets.QTableWidgetItem()
                self.TABLE_Widget.setItem(i, 4, item)
                item = QtWidgets.QTableWidgetItem()

                sign = float(eval(count[(len(count) - 1) - k][1])['result'])
                if sign >= 0:
                    brush = QtGui.QBrush(QtGui.QColor(3, 100, 64))
                else:
                    brush = QtGui.QBrush(QtGui.QColor(139, 0, 0))
                brush.setStyle(QtCore.Qt.NoBrush)
                item.setForeground(brush)
                self.TABLE_Widget.setItem(k + 1, 5, item)
                k += 1
        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Program Error")
            msg.setInformativeText('Something went wrong restart your program and try again.')
            msg.setWindowTitle("Program-Error")
            msg.exec_()

    def table(self):  # insert data in qtable
        global c
        global api
        global identity

        try:
            if not Table(c, f'journal_{identity}').check_table():
                count = ""
                journal_data = ""
                pass
            else:
                count = self.exe()
                journal_data = count

            # ===========================================
            _translate = QtCore.QCoreApplication.translate
            self.TABLE_Widget.setSortingEnabled(False)
            item = self.TABLE_Widget.horizontalHeaderItem(0)
            item.setText(_translate("MyAPP", "ID"))
            item = self.TABLE_Widget.horizontalHeaderItem(1)
            item.setText(_translate("MyAPP", "DATE"))
            item = self.TABLE_Widget.horizontalHeaderItem(2)
            item.setText(_translate("MyAPP", "AMOUNT"))
            item = self.TABLE_Widget.horizontalHeaderItem(3)
            item.setText(_translate("MyAPP", "ENTRY"))
            item = self.TABLE_Widget.horizontalHeaderItem(4)
            item.setText(_translate("MyAPP", "EXIT"))
            item = self.TABLE_Widget.horizontalHeaderItem(5)
            item.setText(_translate("MyAPP", "RESULT"))
            __sortingEnabled = self.TABLE_Widget.isSortingEnabled()
            self.TABLE_Widget.setSortingEnabled(False)

            # ****************
            state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]
            if state != "closed":
                state = "       Open   "
                x_amount = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"]
                amount = f" ${x_amount}"
                date = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                x_entry = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"]
                entry = f" ${x_entry}"

            else:
                date = datetime.date.today()
                month = date.month
                day = date.day
                year = date.year
                state = "       Closed   "
                amount = " "
                date = str(month) + "-" + str(day) + "-" + str(year)
                entry = " "

            item = self.TABLE_Widget.item(0, 0)
            item.setText(_translate("MyAPP", f" {state}"))
            item = self.TABLE_Widget.item(0, 1)
            item.setText(_translate("MyAPP", f" {date}"))
            item = self.TABLE_Widget.item(0, 2)
            item.setText(_translate("MyAPP", f" {amount}"))
            item = self.TABLE_Widget.item(0, 3)
            item.setText(_translate("MyAPP", f" {entry}"))
            item = self.TABLE_Widget.item(0, 4)
            item.setText(_translate("MyAPP", " "))
            item = self.TABLE_Widget.item(0, 5)
            item.setText(_translate("MyAPP", " "))
            # ----------------
            if Table(api, 'Currency_api').check_table():
                btc_ = eval(ExtractData(api, 1, 'Currency_api').get_data()[0][1])[0]
            else:
                try:
                    btc_ = API.btc()[1]
                except Exception:
                    btc_ = 0
            k = 0
            for i in range(1, len(count) + 1):
                item = self.TABLE_Widget.item(i, 0)
                item.setText(_translate("MyAPP", f"               {journal_data[(len(count) - 1) - k][0]}"))
                item = self.TABLE_Widget.item(i, 1)
                item.setText(_translate("MyAPP", f" {eval(journal_data[(len(count) - 1) - k][1])['date']}"))
                item = self.TABLE_Widget.item(i, 2)
                item.setText(_translate("MyAPP", f" {eval(journal_data[(len(count) - 1) - k][1])['amount']} $"))
                item = self.TABLE_Widget.item(i, 3)
                item.setText(_translate("MyAPP", f"$ {eval(journal_data[(len(count) - 1) - k][1])['entry']}"))
                item = self.TABLE_Widget.item(i, 4)
                item.setText(_translate("MyAPP", f"$ {eval(journal_data[(len(count) - 1) - k][1])['exit']}"))
                item = self.TABLE_Widget.item(i, 5)
                item.setText(
                    _translate("MyAPP",
                               f"{eval(journal_data[(len(count) - 1) - k][1])['result']}₿  =>  "
                               f"{round(float(eval(journal_data[(len(count) - 1) - k][1])['result']) * btc_, 2)}$"))
                k += 1
            self.TABLE_Widget.setSortingEnabled(__sortingEnabled)
            self.TABLE_Widget.sortItems(1, QtCore.Qt.DescendingOrder)
        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Program Error")
            msg.setInformativeText('Something went wrong restart your program and try again.')
            msg.setWindowTitle("Program-Error")
            msg.exec_()

    def graph_combobox(self):  # combobox for the graph
        global c
        global identity
        try:
            _translate = QtCore.QCoreApplication.translate
            self.comboBox.clear()

            self.comboBox.addItem("")
            self.comboBox.setItemText(0, _translate("MyAPP", "All"))

            if Table(c, f'combobox_{identity}').check_table():
                c.execute(f"select * from 'combobox_{identity}' ")
                count = c.fetchall()
                count.sort()
                counter = 1
                for i in range(1, len(count) + 1):
                    year = count[i - 1][0]
                    for j in range(len(eval(count[i - 1][1]))):
                        sorted = eval(count[i - 1][1])
                        sorted.sort()
                        month = sorted[j]
                        date = str(month) + "/" + str(year)
                        self.comboBox.addItem("")
                        self.comboBox.setItemText(counter, _translate("MyAPP", f"{date}"))
                        counter += 1
            else:
                pass
        except Exception:
            pass

    # ---------------**********----------------
    def notification(self):
        global api
        global identity
        try:
            btc_ = API.btc()
            eth_ = API.eth()
            ltc_ = API.ltc()
            if btc_ is not None and eth_ is not None and ltc_ is not None:
                text = self.comment_input_3.text()
                combo = str(self.comboBox_2.currentText())
                noti_data = ExtractData(api, 1, f'notify_{identity}').get_data()
                if combo == "BTC":
                    data = {"BTC": (btc_[1], text), "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                                            float(eval(noti_data[0][1])["ETH"][1])),
                            "LTC": (float(eval(noti_data[0][1])["LTC"][0]), float(eval(noti_data[0][1])["LTC"][1])),
                            "ring": eval(noti_data[0][1])["ring"]}
                elif combo == "ETH":
                    data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                    float(eval(noti_data[0][1])["BTC"][1])),
                            "ETH": (eth_, text),
                            "LTC": (float(eval(noti_data[0][1])["LTC"][0]), float(eval(noti_data[0][1])["LTC"][1])),
                            "ring": eval(noti_data[0][1])["ring"]}
                else:
                    data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                                    float(eval(noti_data[0][1])["BTC"][1])),
                            "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                                    float(eval(noti_data[0][1])["ETH"][1])), "LTC": (ltc_, text),
                            "ring": eval(noti_data[0][1])["ring"]}

                InsertData(api, 1, str(data), f'notify_{identity}').update_data()
            else:
                pass
        except Exception:
            pass

    def select_profit_lable(self):
        _translate = QtCore.QCoreApplication.translate

        if self.radioButton_Riskpercentage_left.isChecked():
            self.label_40.setText(_translate("MainWindow", "Risk (%)"))
            self.label_41.setText(_translate("MainWindow", "Profit (%)"))
        elif self.Radiobtn_Risksato_left.isChecked():
            self.label_40.setText(_translate("MainWindow", "Risk (sat)"))
            self.label_41.setText(_translate("MainWindow", "Profit (sat)"))
        else:
            pass

    def select_radiobutton(self):
        _translate = QtCore.QCoreApplication.translate
        if self.radioButton_Riskpercentage_right.isChecked() is True:
            self.radioButton_Risksato_right.setChecked(False)
            self.label_47.setText(_translate("MainWindow", "Risk (%)"))
        else:
            pass

        if self.radioButton_Risksato_right.isChecked() is True:
            self.radioButton_Riskpercentage_right.setChecked(False)
            self.label_47.setText(_translate("MainWindow", "Risk (sat)"))
        else:
            pass

    def allow(self):
        _translate = QtCore.QCoreApplication.translate
        if self.checkBox.isChecked():
            self.input_amount_BS_2.setReadOnly(True)
            self.input_amount_BS_2.setText(_translate("MyAPP", ""))
        else:
            self.input_amount_BS_2.setReadOnly(False)
            self.input_amount_BS_2.setText(_translate("MyAPP", ""))

    def selectionchange(self):
        text = str(self.comboBox.currentText())
        self.graph(text)
        self.rate(text)

    def download(self):  # download data from journal table
        global c
        global identity
        try:
            text = str(self.comboBox_3.currentText())
            input_dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', expanduser("~"))
            if not Table(c, f'journal_{identity}').check_table():
                count = ""
                journal_data = "Your Journal Is Empty!"
                pass
            else:
                count = self.exe()
                journal_data = count
            i = 0
            if text == "HTML":
                with open(os.path.join(f"{input_dir}", "Hunter_Historical _Data.html"), "a", encoding="utf-8") as f:
                    f.write(html_1 + "\n")
                    for _ in range(len(count)):
                        self.progressBar.setProperty("value", (100 / len(count) * i))
                        data = eval(journal_data[(len(count) - 1) - i][1])
                        if data["amount"].split(" ")[0] == "▲":
                            color = "#009100"
                        else:
                            color = "#bf0000"
                        data_ = {'date': data["date"], 'amount': f'<span style=\"color:{color}\">'
                        f'{data["amount"].split(" ")[0]}</span> {data["amount"].split(" ")[1]}',
                                 'entry': data["entry"], 'exit': data["exit"], 'result': data["result"]}

                        f.write("<li><h3>" + str(data_) + "</h3></li>" + "\n")
                        i += 1

                    f.write(html_2 + "\n")
                self.progressBar.setProperty("value", 100)
            else:
                if text == "TXT":
                    value = "txt"
                elif text == "JSON":
                    value = "json"
                elif text == "TXT":
                    value = "txt"
                else:
                    value = "txt"
                with open(os.path.join(f"{input_dir}", f"Hunter_Historical _Data.{value}"), "a",
                          encoding="utf-8") as f:
                    for _ in range(len(count)):
                        self.progressBar.setProperty("value", (100 / len(count) * i))
                        data = eval(journal_data[(len(count) - 1) - i][1])
                        f.write(str(data) + "\n")
                        i += 1
                self.progressBar.setProperty("value", 100)

        except Exception:
            pass

    def sound_ring(self):  # save the ring tune
        global api
        global identity
        try:
            r_data = ExtractData(api, 2, f'notify_{identity}').get_data()
            text = str(self.comboBox_4.currentText())
            if text == "chime":
                ring = "long-chime-sound"

                data = {"1": 0, "2": eval(r_data[0][1])["2"], "3": eval(r_data[0][1])["3"]}
                InsertData(api, 2, str(data), f'notify_{identity}').update_data()
                if eval(r_data[0][1])["1"] == 1:
                    playsound(os.path.join("Images", f"{ring}.mp3"))

            elif text == "oringz":
                ring = "oringz"

                data = {"1": eval(r_data[0][1])["1"], "2": 0, "3": eval(r_data[0][1])["3"]}
                InsertData(api, 2, str(data), f'notify_{identity}').update_data()
                if eval(r_data[0][1])["2"] == 1:
                    playsound(os.path.join("Images", f"{ring}.mp3"))
            elif text == "runaway":
                ring = "runaway"

                data = {"1": eval(r_data[0][1])["1"], "2": eval(r_data[0][1])["2"], "3": 0}
                InsertData(api, 2, str(data), f'notify_{identity}').update_data()
                if eval(r_data[0][1])["3"] == 1:
                    playsound(os.path.join("Images", f"{ring}.mp3"))
            else:
                ring = "long-chime-sound"
                pass
            noti_data = ExtractData(api, 1, f'notify_{identity}').get_data()
            x_data = {"BTC": (float(eval(noti_data[0][1])["BTC"][0]),
                              float(eval(noti_data[0][1])["BTC"][1])),
                      "ETH": (float(eval(noti_data[0][1])["ETH"][0]),
                              float(eval(noti_data[0][1])["ETH"][1])),
                      "LTC": (float(eval(noti_data[0][1])["LTC"][0]),
                              float(eval(noti_data[0][1])["LTC"][1])),
                      "ring": ring}
            InsertData(api, 1, str(x_data), f'notify_{identity}').update_data()
        except Exception:
            pass

    # -------------*********Calculator********-------------

    def add_to_wallet(self):  # add the calculated amount into the wallet
        global api
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            wallet = self.profit_calc()
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
            msg.setIcon(QMessageBox.Question)
            msg.setText("Warning")
            msg.setInformativeText(
                f'Are you sure you want to add \n{f"{wallet[1]:,d}"} Sato to your wallet balance?\n'
                "Proceed?")
            msg.setWindowTitle("Warning!")
            msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            retval = msg.exec_()
            if retval == QMessageBox.Yes:
                wallet_ = {"wallet": wallet[0]}
                InsertData(api, 1, str(wallet_), f'wallet_{identity}').update_data()
                self.input_wallet_balance.setText(_translate("MyAPP", ""))
                self.user_wallet()
            else:
                pass

        except Exception:
            pass

    def order_input_off(self):
        if self.radioButton_ordersize.isChecked() is True:
            self.input_ordersize.setReadOnly(True)
        else:
            self.input_ordersize.setReadOnly(False)

        if self.radioButton_risk.isChecked() is True:
            self.input_risk_right.setReadOnly(True)
        else:
            self.input_risk_right.setReadOnly(False)

        if self.radioButton_stop.isChecked() is True:
            self.input_stop.setReadOnly(True)
        else:
            self.input_stop.setReadOnly(False)

    def order_calc(self):  # calculator
        global api
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            if self.radioButton_ordersize.isChecked() is False and \
                    self.radioButton_risk.isChecked() is False and \
                    self.radioButton_stop.isChecked() is False:
                msg = QMessageBox()
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Selection Error")
                msg.setInformativeText('Error Please Select Your Options.')
                msg.setWindowTitle("input-Error")
                msg.exec_()
            elif self.radioButton_Riskpercentage_right.isChecked() is False and \
                    self.radioButton_Risksato_right.isChecked() is False:
                msg = QMessageBox()
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Selection Error")
                msg.setInformativeText('Error Please Select Your Risk Options.')
                msg.setWindowTitle("input-Error")
                msg.exec_()
                # --------------------------
            else:
                wallet = int(eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"])
                if self.radioButton_ordersize.isChecked() is True:
                    entry = float(self.input_entry.text())
                    stop = float(self.input_stop.text())
                    X_risk = (float(self.input_risk_right.text()) / 100)
                    if self.radioButton_Riskpercentage_right.isChecked() is True:
                        quantity = (X_risk * wallet * (0.00000001) * entry * stop) / (entry - stop)
                        self.resut_output.setText(_translate("MainWindow", f"The order size: {round(quantity, 2)}"))

                    elif self.radioButton_Risksato_right.isChecked() is True:
                        risk = (X_risk / wallet)
                        quantity = ((risk / (wallet * 0.00000001)) * 100) * (
                            0.00000001) * wallet * entry * stop / (entry - stop)
                        self.resut_output.setText(_translate("MainWindow", f"The order size: {round(quantity, 2)}"))

                elif self.radioButton_risk.isChecked() is True:
                    entry = float(self.input_entry.text())
                    stop = float(self.input_stop.text())
                    a_quantity = float(self.input_ordersize.text())
                    try:
                        if self.radioButton_Riskpercentage_right.isChecked() is True:
                            Risk = (a_quantity * (entry - stop)) / (wallet * (0.00000001) * entry * stop) * 100
                            risk = str(round(Risk, 2)) + ' %'
                            self.resut_output.setText(_translate("MainWindow", f"The Risk: {risk}"))
                        elif self.radioButton_Risksato_right.isChecked() is True:
                            risk = (a_quantity * (entry - stop)) / (wallet * (0.00000001) * entry * stop)
                            risk = str(f"{int(round(risk, 2) * wallet):,d}") + ' Sat'
                            self.resut_output.setText(_translate("MainWindow", f"The Risk in Sat: {risk}"))
                    except Exception:
                        pass
                elif self.radioButton_stop.isChecked() is True:
                    wallet = int(wallet)
                    entry = float(self.input_entry.text())
                    a_quantity = float(self.input_ordersize.text())
                    x_risk = float(self.input_risk_right.text())
                    X_risk = (x_risk / 100)
                    if self.radioButton_Riskpercentage_right.isChecked() is True:
                        stop = (a_quantity * entry) / (X_risk * wallet * (0.00000001) * entry + a_quantity)
                        self.resut_output.setText(_translate("MainWindow", f"The Stop: {round(stop, 2)}"))
                    elif self.radioButton_Risksato_right.isChecked() is True:
                        risk = (x_risk / wallet)
                        stop = (a_quantity * entry) / ((risk / (wallet * (0.00000001)) * 100) * (
                            0.00000001) * wallet * entry + a_quantity)
                        self.resut_output.setText(_translate("MainWindow", f"The Stop: {round(stop, 2)}"))
        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Input Error")
            msg.setInformativeText(
                "☺ Whoops, that's an error!\nPlease enter a numeric input\nOR Your Wallet Balance.")
            msg.setWindowTitle("input-Error")
            msg.exec_()

    def profit_calc(self):  # calculator
        global api
        global identity
        _translate = QtCore.QCoreApplication.translate
        if self.radioButton_Riskpercentage_left.isChecked() is False and \
                self.Radiobtn_Risksato_left.isChecked() is False:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Selection Error")
            msg.setInformativeText('Error Please Select Your Risk Options.')
            msg.setWindowTitle("input-Error")
            msg.exec_()
        else:
            try:
                if self.radioButton_Riskpercentage_left.isChecked() is True:
                    wallet = int(eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"])
                    profit = float(self.input_Calc_Profit_left.text())
                    risk = float(self.input_Calc_Risk_left.text())
                    result = ((wallet * (risk / 100)) * (profit / 100)) / wallet
                    risk_ = str(round((result * 100), 2)) + ' %'
                    sato_value = str(f"{int(round((result * wallet), 4)):,d}") + ' Sat'
                    self.print_result_Calc_left_3.setText(_translate("MainWindow", f"{risk_}"))
                    self.print_result_Calc_left_1.setText(_translate("MainWindow", f"{sato_value}"))
                    # ------

                    add_ = int((round(result * wallet, 4)))
                    add_value = int((round(result * wallet, 4))) + wallet
                    sato_ = f"{add_value:,d}"
                    self.print_result_Calc_left_2.setText(_translate("MainWindow", f"{sato_} Sat"))
                elif self.Radiobtn_Risksato_left.isChecked() is True:
                    wallet = int(eval(ExtractData(api, 1, f'wallet_{identity}').get_data()[0][1])["wallet"])
                    profit = float(self.input_Calc_Profit_left.text())
                    risk = float(self.input_Calc_Risk_left.text())
                    x = wallet * (((risk / wallet) * 100) / 100)
                    result = (x * (((profit / x) * 100) / 100)) / wallet
                    risk_ = str(round(result * 100, 2)) + ' %'
                    self.print_result_Calc_left_3.setText(_translate("MainWindow", f"{risk_}"))
                    sato_value = str(f"{int(round(result * wallet, 4)):,d}") + ' Sat'
                    self.print_result_Calc_left_1.setText(_translate("MainWindow", f"{sato_value}"))
                    # -----------
                    add_ = int((round(result * wallet, 4)))
                    add_value = int((round(result * wallet, 4))) + wallet
                    sato_ = f"{add_value:,d}"
                    self.print_result_Calc_left_2.setText(_translate("MainWindow", f"{sato_} Sat"))
                return add_value, add_
            except Exception:
                msg = QMessageBox()
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Input Error")
                msg.setInformativeText(
                    "Whoops, that's an error!\nPlease enter a numeric input\nOR Your Wallet Balance.")
                msg.setWindowTitle("input-Error")
                msg.exec_()

    # -----------------****************-----------------

    def Import(self):  # import data into the database
        global c
        global identity
        file_path = QFileDialog.getOpenFileName(None, 'Select Your Backup File:', expanduser("~"))[0]
        # ----------------------------------------
        if not Table(c, f'journal_{identity}').check_table():
            Table(c, f'journal_{identity}').create_table()
            Table(c, f'graph_{identity}').create_table()
            Table(c, f'combobox_{identity}').create_table()
        else:
            pass
        count = self.exe()

        if count == 1:
            x_value = 0
        else:
            if Table(c, f"save_{identity}").check_table():
                x_value = ExtractData(c, 1, f"save_{identity}").get_data()[0][1] + len(count)
            else:
                x_value = len(count)

        i = 0
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    # ----date
                    # ['2', '20', '2019'] 2-20-2019
                    month, day, year = eval(line)["date"].split("-")

                    if ((int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or
                         int(month) == 8 or int(month) == 10 or int(month) == 12) and int(day) <= 31) or \
                            (int(month) == 2 and int(day) <= 28) or \
                            ((int(month) == 4 or int(month) == 6 or int(month) == 9 or int(month) == 11) and
                             int(day) <= 30):

                        date_str = str(eval(line)["date"])
                        result = float(eval(line)["result"])

                        # --------
                        self.progressBar_2.setProperty("value", (100 / len(lines) * i))
                        # --------
                        if str(eval(line)["amount"]).split(" ")[0] == "â–²" or str(eval(line)["amount"]).split(" ")[
                            0] == "▲":
                            value = "▲ "
                        else:
                            value = "▼ "

                        data = {"date": eval(line)["date"],
                                "amount": f"{value}" + str(eval(line)["amount"]).split(" ")[1],
                                "entry": eval(line)["entry"], "exit": eval(line)["exit"],
                                "result": eval(line)["result"]}

                        graph_data = {"date": date_str, "result": result}

                        # ---------------------------------journal&graph--------------------------------

                        InsertData(c, (x_value - 1) + 1, str(data), f'journal_{identity}').insert_data()
                        InsertData(c, (x_value - 1) + 1, str(graph_data), f'graph_{identity}').insert_data()

                        # ------graph_year =========================================================

                        if Table(c, f'graph_{year}_{identity}').check_table():
                            if ExtractData(c, month, f'graph_{year}_{identity}').check_data():
                                M_data = eval(ExtractData(c, month, f'graph_{year}_{identity}').get_data()[0][1])
                                M_data.append((date_str, round(result, 5)))
                                InsertData(c, month, str(M_data), f'graph_{year}_{identity}').update_data()
                            else:
                                M_data = [(date_str, round(result, 5))]
                                InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                        if not Table(c, f'graph_{year}_{identity}').check_table():
                            Table(c, f'graph_{year}_{identity}').create_table()
                            M_data = [(date_str, round(result, 5))]
                            InsertData(c, month, str(M_data), f'graph_{year}_{identity}').insert_data()

                        # ------combobox ===========================================================

                        if ExtractData(c, year, f'combobox_{identity}').check_data():
                            combo_data = eval(ExtractData(c, year, f'combobox_{identity}').get_data()[0][1])
                            if int(month) not in combo_data:
                                combo_data.append(int(month))
                                InsertData(c, year, str(combo_data), f'combobox_{identity}').update_data()
                            else:
                                pass
                        else:
                            combo_data = [int(month)]
                            InsertData(c, year, str(combo_data), f'combobox_{identity}').insert_data()

                        # ------rate_p&rate_N&ADD===============================================================

                        if not Table(c, f'rate_P_{identity}').check_table() and \
                                not Table(c, f'rate_N_{identity}').check_table() and \
                                not Table(c, f'ADD_{identity}').check_table():

                            Table(c, f'rate_P_{identity}').create_table()
                            Table(c, f'rate_N_{identity}').create_table()
                            Table(c, f'ADD_{identity}').create_table()

                            if result > 0:
                                rate_value = result
                                InsertData(c, 0, str(rate_value), f'rate_p_{identity}').insert_data()

                                add_data = {"total_gain": result, "total_loss": 0}
                                InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()

                            else:
                                rate_value = result
                                InsertData(c, 0, str(rate_value), f'rate_N_{identity}').insert_data()

                                add_data = {"total_gain": 0, "total_loss": result}
                                InsertData(c, 0, str(add_data), f'ADD_{identity}').insert_data()
                        else:
                            if result > 0:
                                rate_value = result
                                InsertData(c, (x_value - 1) + 1, str(rate_value), f'rate_p_{identity}').insert_data()

                                add_data = {"total_gain":
                                                float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                          "total_gain"])
                                                + result, "total_loss":
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_loss"]}
                                InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                            else:
                                rate_value = result
                                InsertData(c, (x_value - 1) + 1, str(rate_value), f'rate_N_{identity}').insert_data()

                                add_data = {"total_gain":
                                                eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                    "total_gain"]
                                    , "total_loss":
                                                float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])[
                                                          "total_loss"])
                                                + result}
                                InsertData(c, 0, str(add_data), f'ADD_{identity}').update_data()

                        # ********************
                        x_value += 1
                        i += 1

                        # ********************
            self.progressBar_2.setProperty("value", 100)
            self.make_journal()
        except Exception:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("File Error")
            msg.setInformativeText(
                "You got this error because of the following reasons.\n"
                "1- Choose the right file that you download from BitHunter Journal with "
                "(txt or json file format). \n2- Your file is possibly corrupted.\n"
                "3- Connection error try again!")
            msg.setWindowTitle("File-Error")
            msg.exec_()
            pass

    def opentrade(self):  # open the trade
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        self.checkBox.setEnabled(True)
        state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

        if not state != "closed":
            # ------------------color float------------------
            item = QtWidgets.QTableWidgetItem()
            font = QtGui.QFont()
            font.setBold(True)
            font.setItalic(False)
            font.setUnderline(False)
            font.setWeight(75)
            font.setStrikeOut(False)
            font.setKerning(True)
            font.setStyleStrategy(QtGui.QFont.PreferDefault)
            item.setFont(font)
            brush = QtGui.QBrush(QtGui.QColor(51, 51, 51))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item.setBackground(brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setForeground(brush)
            self.TABLE_Widget.setItem(0, 0, item)

            # -----------------------------------------------

            if self.open_trade.isChecked():
                self.input_amount_BS_2.setReadOnly(True)
                self.input_Exit_BS.setReadOnly(True)
                self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                self.input_Exit_BS.setText(_translate("MyAPP", ""))
                # -------------------------------------------------
                item = self.TABLE_Widget.item(0, 0)
                item.setText(_translate("MyAPP", "       Open   "))
                self.input_amount_BS_2.setReadOnly(True)
            else:
                self.input_amount_BS_2.setReadOnly(False)
                self.input_Exit_BS.setReadOnly(False)
                self.input_amount_BS_2.setText(_translate("MyAPP", ""))
                self.input_Exit_BS.setText(_translate("MyAPP", ""))
                # --------------------------------------------------
                item = self.TABLE_Widget.item(0, 0)
                item.setText(_translate("MyAPP", "       Closed   "))
                self.input_amount_BS_2.setReadOnly(True)
        else:
            pass

    def open_active(self):  # open the trade check state
        global c
        global identity
        state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]
        if state != "closed":
            _translate = QtCore.QCoreApplication.translate
            self.open_trade.setChecked(True)
            self.open_trade.setEnabled(False)
            self.checkBox.setEnabled(False)
            self.input_amount_BS_2.setReadOnly(True)
            self.input_Exit_BS.setReadOnly(True)
            self.input_amount_BS_2.setText(_translate("MyAPP", ""))
            self.input_Exit_BS.setText(_translate("MyAPP", ""))
        else:
            pass

    def calc_openTradeBUY(self):  # open the trade buy calculator
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate

        if self.open_trade.isChecked():
            try:
                amount = float(self.input_amount_BS.text())
                entry = float(self.input_Entry_BS.text())

                self.open_trade.setEnabled(False)
                self.checkBox.setEnabled(False)

                date = datetime.date.today()
                month = date.month
                day = date.day
                year = date.year

                date_str = str(month) + "-" + str(day) + "-" + str(year)
                state_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

                if state_ == "closed":

                    data = {"date": date_str, "amount": amount,
                            "entry": entry, "state": "BUY"}
                    InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()

                    data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                    InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()

                else:
                    state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

                    if state == "BUY":  # *****
                        date_str_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                        amount_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"])
                        entry_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"])

                        x_amount = amount_ + amount

                        x_entry = ((amount_ * entry_) + (amount * entry)) / x_amount

                        data = {"date": date_str_, "amount": x_amount,
                                "entry": round(x_entry, 1), "state": "BUY"}

                        InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                    elif state == "SELL":
                        date_str_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                        amount_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"])
                        entry_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"])

                        x_amount = amount_ - amount

                        if x_amount > 0:
                            data = {"date": date_str_, "amount": x_amount,
                                    "entry": entry_, "state": "SELL"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                            data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_sell()
                            self.make_journal()
                        elif x_amount < 0:
                            data = {"date": date_str, "amount": abs(x_amount),
                                    "entry": entry, "state": "BUY"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                            data_ = {"date": date_str_, "amount": amount_, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_sell()
                            self.make_journal()
                        elif x_amount == 0:
                            data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_sell()
                            self.make_journal()

                            self.open_trade.setChecked(False)
                            self.open_trade.setEnabled(True)
                            self.checkBox.setChecked(True)
                            self.checkBox.setEnabled(True)

                            self.input_amount_BS_2.setReadOnly(False)
                            self.input_Exit_BS.setReadOnly(False)

                            data = {"date": 0, "amount": 0,
                                    "entry": 0, "state": "closed"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()

                            data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()

                # ========================================================
                state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]
                if state != "closed":
                    if state == "BUY":  # bg green (0, 255, 0)
                        bg = QtGui.QColor(0, 255, 0)
                        fg = QtGui.QColor(0, 0, 0)
                        bgd = QtCore.Qt.Dense2Pattern
                    elif state == "SELL":  # red (255, 0, 0)
                        bg = QtGui.QColor(255, 0, 0)
                        fg = QtGui.QColor(0, 0, 0)
                        bgd = QtCore.Qt.Dense2Pattern
                    else:
                        bg = QtGui.QColor(51, 51, 51)
                        fg = QtGui.QColor(255, 255, 255)
                        bgd = QtCore.Qt.SolidPattern
                else:
                    bg = QtGui.QColor(51, 51, 51)
                    fg = QtGui.QColor(255, 255, 255)
                    bgd = QtCore.Qt.SolidPattern
                # **************Open*******************
                item = QtWidgets.QTableWidgetItem()
                font = QtGui.QFont()
                font.setBold(True)
                font.setItalic(False)
                font.setUnderline(False)
                font.setWeight(75)
                font.setStrikeOut(False)
                font.setKerning(True)
                font.setStyleStrategy(QtGui.QFont.PreferDefault)
                item.setFont(font)
                brush = QtGui.QBrush(bg)  # bg
                brush.setStyle(bgd)  # bgd
                item.setBackground(brush)
                brush = QtGui.QBrush(fg)  # fg
                brush.setStyle(QtCore.Qt.NoBrush)
                item.setForeground(brush)
                self.TABLE_Widget.setItem(0, 0, item)

                # =================================================

                if state != "closed":
                    state = "       Open   "
                    x_amount = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"]
                    amount = f" ${x_amount}"
                    date = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                    x_entry = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"]
                    entry = f" ${x_entry}"

                else:
                    date = datetime.date.today()
                    month = date.month
                    day = date.day
                    year = date.year
                    state = "       Closed   "
                    amount = " "
                    date = str(month) + "-" + str(day) + "-" + str(year)
                    entry = " "

                item = self.TABLE_Widget.item(0, 0)
                item.setText(_translate("MyAPP", f" {state}"))
                item = self.TABLE_Widget.item(0, 1)
                item.setText(_translate("MyAPP", f" {date}"))
                item = self.TABLE_Widget.item(0, 2)
                item.setText(_translate("MyAPP", f" {amount}"))
                item = self.TABLE_Widget.item(0, 3)
                item.setText(_translate("MyAPP", f" {entry}"))
                item = self.TABLE_Widget.item(0, 4)
                item.setText(_translate("MyAPP", " "))
                item = self.TABLE_Widget.item(0, 5)
                item.setText(_translate("MyAPP", " "))

                self.input_amount_BS.setText(_translate("MyAPP", ""))
                self.input_Entry_BS.setText(_translate("MyAPP", ""))

            except Exception:
                pass
        else:
            self.journal_buy()
            self.make_journal()

    def calc_openTradeSELL(self):  # open the trade sell calculator
        global c
        global identity
        _translate = QtCore.QCoreApplication.translate
        if self.open_trade.isChecked():
            try:

                amount = float(self.input_amount_BS.text())
                entry = float(self.input_Entry_BS.text())

                self.open_trade.setEnabled(False)
                self.checkBox.setEnabled(False)

                date = datetime.date.today()
                month = date.month
                day = date.day
                year = date.year

                date_str = str(month) + "-" + str(day) + "-" + str(year)
                state_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

                if state_ == "closed":

                    data = {"date": date_str, "amount": amount,
                            "entry": entry, "state": "SELL"}
                    InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()

                    data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                    InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()

                else:
                    state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

                    if state == "SELL":  # *****
                        date_str_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                        amount_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"])
                        entry_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"])

                        x_amount = amount_ + amount

                        x_entry = ((amount_ * entry_) + (amount * entry)) / x_amount

                        data = {"date": date_str_, "amount": x_amount,
                                "entry": round(x_entry, 1), "state": "SELL"}

                        InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                    elif state == "BUY":
                        date_str_ = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                        amount_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"])
                        entry_ = float(
                            eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"])

                        x_amount = amount_ - amount
                        if x_amount > 0:
                            data = {"date": date_str_, "amount": x_amount,
                                    "entry": entry_, "state": "BUY"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                            data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_buy()
                            self.make_journal()
                        elif x_amount < 0:
                            data = {"date": date_str, "amount": abs(x_amount),
                                    "entry": entry, "state": "SELL"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()
                            data_ = {"date": date_str_, "amount": amount_, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_buy()
                            self.make_journal()
                        elif x_amount == 0:
                            data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()
                            self.journal_buy()
                            self.make_journal()
                            self.open_trade.setChecked(False)
                            self.open_trade.setEnabled(True)
                            self.checkBox.setChecked(True)
                            self.checkBox.setEnabled(True)

                            self.input_amount_BS_2.setReadOnly(False)
                            self.input_Exit_BS.setReadOnly(False)

                            data = {"date": 0, "amount": 0,
                                    "entry": 0, "state": "closed"}
                            InsertData(c, 1, str(data), f'open_trade_{identity}').update_data()

                            data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                            InsertData(c, 2, str(data_), f'open_trade_{identity}').update_data()

                # ========================================================
                state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]

                if state != "closed":
                    state = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["state"]
                    if state == "BUY":  # bg green (0, 255, 0)
                        bg = QtGui.QColor(0, 255, 0)
                        fg = QtGui.QColor(0, 0, 0)
                        bgd = QtCore.Qt.Dense2Pattern
                    elif state == "SELL":  # red (255, 0, 0)
                        bg = QtGui.QColor(255, 0, 0)
                        fg = QtGui.QColor(0, 0, 0)
                        bgd = QtCore.Qt.Dense2Pattern
                    else:
                        bg = QtGui.QColor(51, 51, 51)
                        fg = QtGui.QColor(255, 255, 255)
                        bgd = QtCore.Qt.SolidPattern
                else:
                    bg = QtGui.QColor(51, 51, 51)
                    fg = QtGui.QColor(255, 255, 255)
                    bgd = QtCore.Qt.SolidPattern
                # **************Open*******************
                item = QtWidgets.QTableWidgetItem()
                font = QtGui.QFont()
                font.setBold(True)
                font.setItalic(False)
                font.setUnderline(False)
                font.setWeight(75)
                font.setStrikeOut(False)
                font.setKerning(True)
                font.setStyleStrategy(QtGui.QFont.PreferDefault)
                item.setFont(font)
                brush = QtGui.QBrush(bg)  # bg
                brush.setStyle(bgd)  # bgd
                item.setBackground(brush)
                brush = QtGui.QBrush(fg)  # fg
                brush.setStyle(QtCore.Qt.NoBrush)
                item.setForeground(brush)
                self.TABLE_Widget.setItem(0, 0, item)
                # =======================================================
                if state != "closed":
                    state = "       Open   "
                    x_amount = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["amount"]
                    amount = f" ${x_amount}"
                    date = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["date"]
                    x_entry = eval(ExtractData(c, 1, f'open_trade_{identity}').get_data()[0][1])["entry"]
                    entry = f" ${x_entry}"

                else:
                    date = datetime.date.today()
                    month = date.month
                    day = date.day
                    year = date.year
                    state = "       Closed   "
                    amount = " "
                    date = str(month) + "-" + str(day) + "-" + str(year)
                    entry = " "

                item = self.TABLE_Widget.item(0, 0)
                item.setText(_translate("MyAPP", f" {state}"))
                item = self.TABLE_Widget.item(0, 1)
                item.setText(_translate("MyAPP", f" {date}"))
                item = self.TABLE_Widget.item(0, 2)
                item.setText(_translate("MyAPP", f" {amount}"))
                item = self.TABLE_Widget.item(0, 3)
                item.setText(_translate("MyAPP", f" {entry}"))
                item = self.TABLE_Widget.item(0, 4)
                item.setText(_translate("MyAPP", " "))
                item = self.TABLE_Widget.item(0, 5)
                item.setText(_translate("MyAPP", " "))
                # ====================================
                self.input_amount_BS.setText(_translate("MyAPP", ""))
                self.input_Entry_BS.setText(_translate("MyAPP", ""))

            except Exception:
                pass
        else:
            self.journal_sell()
            self.make_journal()

    def about(self):  # about window
        from about import Ui_Form
        self.ui = Ui_Form()
        self.Form = QtWidgets.QWidget()
        self.ui.setupUi(self.Form)
        self.Form.show()

    def retranslateUi(self, MainWindow):
        global username
        global identity
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BitHunter Journal"))
        self.label_journal.setText(
            _translate("MainWindow", f"{username.upper()}\'s Trading Journal"))
        self.label_15.setText(_translate("MainWindow", "Modify:"))
        self.input_modify.setPlaceholderText(_translate("MainWindow", "ID/Amount/Entry/Exit/sell or buy"))
        self.comment_input_2.setPlaceholderText(_translate("MainWindow", "        BTC to SAT"))
        self.label_16.setText(_translate("MainWindow", " Delete:"))
        self.input_delete.setPlaceholderText(_translate("MainWindow", "                ID "))

        self.output_wallet_SGD.setText(_translate("MainWindow", "S$ 0,0"))
        self.output_wallet_BTC.setText(_translate("MainWindow", "₿ 0.0"))
        self.output_wallet_USD.setText(_translate("MainWindow", "$ 0,0"))

        self.label_11.setText(_translate("MainWindow", "Your Wallet in Satoshi :"))

        btc_ = API.btc()
        eth_ = API.eth()
        ltc_ = API.ltc()
        if btc_ is not None and eth_ is not None and ltc_ is not None:
            self.LTC_Priceusd_color.setText(_translate("MainWindow",
                                                       f"<html><head/><body><p><span style=\" font-size:10pt; "
                                                       f"font-weight:600;\">LTC / USDT</span><span style=\" "
                                                       f"font-size:10pt; font-weight:600; "
                                                       f"color:#d3d3d3;\">.....</span><span style=\" font-size:10pt; "
                                                       f"font-weight:600; color:#009100;\">$"
                                                       f"{ltc_}</span></p></body></html>"))
            self.ETH_Priceusd_color.setText(_translate("MainWindow",
                                                       f"<html><head/><body><p><span style=\" "
                                                       f"font-weight:600;\">ETH / USDT</span><span style=\" "
                                                       f"font-weight:600; color:#d3d3d3;\">.....</span><span style=\" "
                                                       f"font-weight:600; color:#bf0000;\">$"
                                                       f"{eth_}</span></p></body></html>"))
            self.BTC_Priceusd_color.setText(_translate("MainWindow",
                                                       f"<html><head/><body><p><span style=\" font-weight:600;\">BTC "
                                                       f"/ USDT</span><span style=\" font-weight:600; "
                                                       f"color:#d3d3d3;\">.....</span><span style=\" font-weight:600; "
                                                       f"color:#bf0000;\">${btc_[0]} </span></p></body></html>"))

        else:

            self.LTC_Priceusd_color.setText(_translate("MainWindow",
                                                       "<html><head/><body><p><span style=\" font-size:10pt; "
                                                       "font-weight:600;\">LTC / USDT</span><span style=\" "
                                                       "font-size:10pt; font-weight:600; "
                                                       "color:#d3d3d3;\">.....</span><span style=\" font-size:10pt; "
                                                       "font-weight:600; color:#009100;\">$ "
                                                       "⌛</span></p></body></html>"))
            self.ETH_Priceusd_color.setText(_translate("MainWindow",
                                                       "<html><head/><body><p><span style=\" font-weight:600;\">ETH / "
                                                       "USDT</span><span style=\" font-weight:600; "
                                                       "color:#d3d3d3;\">.....</span><span style=\" font-weight:600; "
                                                       "color:#bf0000;\">$ ⌛</span></p></body></html>"))
            self.BTC_Priceusd_color.setText(_translate("MainWindow",
                                                       "<html><head/><body><p><span style=\" font-weight:600;\">BTC / "
                                                       "USDT</span><span style=\" font-weight:600; "
                                                       "color:#d3d3d3;\">.....</span><span style=\" font-weight:600; "
                                                       "color:#bf0000;\">$ ⌛ </span></p></body></html>"))

        if file_size(f'{identity}.db') is None:
            size = "0 bytes"
        else:
            size = file_size(f'{identity}.db')

        self.label_28.setText(_translate("MainWindow",
                                         f"<html><head/><body><p><span style=\" font-size:9pt;\">DATA SIZE : "
                                         f"</span><span style=\" font-size:9pt; font-weight:600; color:#000000;\">"
                                         f" {size}</span></p></body></html>"))

        self.label_30.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" font-size:8pt; "
                                         "font-weight:600;\">Total Losses</span>: <span style=\" font-weight:600; "
                                         "color:#bf0000;\">0₿</span></p></body></html>"))
        self.label_29.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" font-size:8pt; "
                                         "font-weight:600;\">Total Wins</span>: <span style=\" font-weight:600; "
                                         "color:#008400;\">0₿</span></p></body></html>"))
        self.label_31.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" font-size:8pt; font-weight:600;\">Pure "
                                         "Profit</span>: <span style=\" font-weight:600; "
                                         "color:#008400;\">0₿</span></p></body></html>"))

        # --------------------------------------------

        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_5), _translate("MainWindow", ""))
        self.label_note.setText(_translate("MainWindow", f"{username.upper()}\'s Daily Notes"))
        self.comment_btn_save.setText(_translate("MainWindow", "       Save       "))
        self.label_12.setText(_translate("MainWindow", "FIND NOTE:"))
        self.comment_input.setPlaceholderText(_translate("MainWindow", "    MM/DD/YYYY"))
        self.input_amount_BS_2.setPlaceholderText(_translate("MainWindow", "   MM/DD/YYYY"))

        self.minw.setText(_translate("MainWindow",
                                     "<html><head/><body><p><span style=\" font-weight:600;\">MIN Gain:</span><span "
                                     "style=\" color:#00b000;\">+</span><span style=\" font-size:9pt; "
                                     "font-weight:600; color:#00b000;\">0₿</span></p></body></html>"))

        self.maxl.setText(_translate("MainWindow",
                                     "<html><head/><body><p><span style=\" font-weight:600;\">MAX Loss:</span><span "
                                     "style=\" color:#c30000;\">-</span><span style=\" font-size:9pt; "
                                     "font-weight:600; color:#c30000;\">0₿</span></p></body></html>"))
        self.minl.setText(_translate("MainWindow",
                                     "<html><head/><body><p><span style=\" font-weight:600;\">MIN Loss:</span><span "
                                     "style=\" font-weight:600; color:#c30000;\">-</span><span style=\" "
                                     "font-size:9pt; font-weight:600; color:#c30000;\">0₿</span></p></body></html>"))
        self.maxw.setText(_translate("MainWindow",
                                     "<html><head/><body><p><span style=\" font-weight:600;\">MAX Gain:</span><span "
                                     "style=\" color:#00b000;\">+</span><span style=\" font-size:9pt; "
                                     "font-weight:600; color:#00b000;\">0₿</span></p></body></html>"))
        self.comment_TextEdit.setPlainText(_translate("MainWindow", ""))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("MainWindow", "NOTE"))
        self.label_32.setText(_translate("MainWindow", "The new value of your wallet balance."))
        self.label_37.setText(_translate("MainWindow", "The new profit in your wallet balance."))
        self.label_38.setText(_translate("MainWindow", "The profit percentage of your wallet balance."))
        self.Calc_btn_right.setText(_translate("MainWindow", "CALCULATE"))
        self.add_btn.setText(_translate("MainWindow", "Add Profit To My wallet"))
        self.label_4.setText(_translate("MainWindow", "0 SAT"))
        self.label_40.setText(_translate("MainWindow", "Risk"))
        self.label_41.setText(_translate("MainWindow", "Profit"))
        self.print_result_Calc_left_1.setText(_translate("MainWindow", "0"))
        self.print_result_Calc_left_2.setText(_translate("MainWindow", "0"))
        self.print_result_Calc_left_3.setText(_translate("MainWindow", "0"))
        self.Calc_btn_left.setText(_translate("MainWindow", "CALCULATE"))
        self.label_42.setText(_translate("MainWindow", "Entry"))
        self.label_46.setText(_translate("MainWindow", "Order size"))
        self.label_47.setText(_translate("MainWindow", "Risk"))
        self.label_48.setText(_translate("MainWindow", "Stop"))
        self.resut_output.setText(_translate("MainWindow", " "))
        self.radioButton_ordersize.setText(_translate("MainWindow", "Order Size"))
        self.radioButton_risk.setText(_translate("MainWindow", "The Risk"))
        self.radioButton_Riskpercentage_right.setText(_translate("MainWindow", "Risk in Percentage"))
        self.radioButton_Risksato_right.setText(_translate("MainWindow", "Risk in Satoshi"))
        self.radioButton_Riskpercentage_left.setText(_translate("MainWindow", "Risk in Percentage"))
        self.Radiobtn_Risksato_left.setText(_translate("MainWindow", "Risk in Satoshi"))
        self.radioButton_stop.setText(_translate("MainWindow", "The Stop"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("MainWindow", "CALCULATOR"))
        self.win_rate_loss.setText(_translate("MainWindow", "0"))
        self.label_7.setText(_translate("MainWindow", "Losses"))
        self.win_rate_win.setText(_translate("MainWindow", "0"))
        self.label_8.setText(_translate("MainWindow", "Wins"))
        self.win_rate_win_2.setText(_translate("MainWindow", "0%"))
        self.label_10.setText(_translate("MainWindow", "Rate"))
        self.label_13.setText(_translate("MainWindow", "   ▲   "))
        self.label_17.setText(_translate("MainWindow", "   ▼  "))
        self.label_19.setText(_translate("MainWindow", "Exit:"))
        self.label_18.setText(_translate("MainWindow", "Entry:"))
        self.label_9.setText(_translate("MainWindow", "Amount:"))
        self.label_currency.setText(_translate("MainWindow", "Currency"))
        self.label_ring.setText(_translate("MainWindow", "Ring"))
        self.btn_SELL.setText(_translate("MainWindow", "     SELL    "))
        self.btn_BUY.setText(_translate("MainWindow", "      BUY       "))
        self.checkBox.setText(_translate("MainWindow", "Current Date"))
        self.label_14.setText(_translate("MainWindow", "Date:"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_5), _translate("MainWindow", "PERFORMANCE GRAPH"))
        self.toolBox_2.setItemText(self.toolBox_2.indexOf(self.page_6),
                                   _translate("MainWindow", "NOTIFICATION | DOWNLOAD | IMPORT"))
        self.groupBox.setTitle(_translate("MainWindow", "Price Notification:"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "BTC"))
        self.comboBox_2.setItemText(1, _translate("MainWindow", "ETH"))
        self.comboBox_2.setItemText(2, _translate("MainWindow", "LTC"))

        self.comboBox_4.setItemText(0, _translate("MainWindow", "chime"))
        self.comboBox_4.setItemText(1, _translate("MainWindow", "oringz"))
        self.comboBox_4.setItemText(2, _translate("MainWindow", "runaway"))

        self.comboBox_3.setItemText(0, _translate("MainWindow", "HTML"))
        self.comboBox_3.setItemText(1, _translate("MainWindow", "TXT"))
        self.comboBox_3.setItemText(2, _translate("MainWindow", "JSON"))

        self.Calc_btn_right_2.setText(_translate("MainWindow", "Notify me"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Download Backup data."))
        self.groupBox_3.setTitle(_translate("MainWindow", "Import Backup data."))
        self.export_btn.setText(_translate("MainWindow", "Download "))
        self.import_btn.setText(_translate("MainWindow", "Import "))
        self.progressBar.setFormat(_translate("MainWindow", "%p%"))
        self.open_trade.setText(_translate("MainWindow", "Open Trade"))
        self.about_btn.setText(_translate("MainWindow", "About"))
        self.label_12.setText(_translate("MainWindow", "Note:"))
        self.label_20.setText(_translate("MainWindow", "Note Date:"))


def G_L_P():  # for gain loss and pure profit data
    global c
    global identity
    if Table(c, f'ADD_{identity}').check_table():
        total_gain = float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_gain"])
        total_loss = float(eval(ExtractData(c, 0, f'ADD_{identity}').get_data()[0][1])["total_loss"])
    else:
        total_loss = 0
        total_gain = 0

    pure_profit = total_loss + total_gain
    if pure_profit > 0:
        color = "#008400"
    else:
        color = "#bf0000"
    return total_gain, total_loss, pure_profit, color


"""this is for downloading the user's data as an html file"""
icoDirectory = os.path.join(f"{os.getcwd()}", "Images\\MainWinTite.png")
html_1 = """<!DOCTYPE html>

<html lang="en" dir="ltr">
<head>
  <style>
    #head {
      list-style-type: none;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background-color: #333333;
    }
    #data_list{
      color: black;
    }
    #head li {
      float: left;
    }
    li h2 {
      display: block;
      color: rgb(211, 211, 211);
      text-align: center;
      padding: 16px;
      text-decoration: none;
    }
    li h6 {
      display: block;
      color: orange;
      text-align: center;
      padding: 5px;
      border: 1px rgb(211,211,211) solid;
      text-decoration: none;
    }
    li h5{
      display: block;
      color: rgb(211, 211, 211);
      text-align: left;
      padding: 16px;
      text-decoration: none;
    }

    li h1:hover {
      background-color: #111111;
    }
  </style>
""" + f"""
<link rel="icon" href="{icoDirectory}">
</head>
<body bgcolor= '#D3D3D3'>

<ul id="head">
""" + f"""
  <li><h2>{username.upper()}'s trading historical data</h2></li>
  <li><h6>BitHunter Journal</h6></li>
  <li><h5>Total Gains: <span style="color:#008400">+{round(G_L_P()[0], 5)}</span>₿</h6></li>
  <li><h5>Tota Losses: <span style="color:#bf0000">{round(G_L_P()[1], 5)}</span>₿</h6></li>
  <li><h5>Pure Profit: <span style="color:{G_L_P()[3]}">+{round(G_L_P()[2], 5)}</span>₿</h6></li>

</ul>

<ul id="data_list">
"""

html_2 = """</ul>
</body>
</html>"""

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.graph("ALL")
    sys.exit(app.exec_())
