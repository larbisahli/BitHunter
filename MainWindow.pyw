# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.13.0

"""
            ####################################
            #                                  #
            #       Author: Larbi Sahli        #
            #                                  #
            #  https://github.com/Larbi-Sahli  #
            #                                  #
            ####################################
"""
import datetime
import pickle
import time
import traceback
import threading
import image_rc
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from os.path import expanduser
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import Image
import os
from json import JSONDecodeError
import requests
from dbManagement import *


def current_time():
    now = datetime.datetime.now()
    current_time_ = datetime.time(hour=now.hour, minute=now.minute).strftime('%I:%M%p').lstrip('0')
    return current_time_


with open("current_access.txt", "rb") as r:
    dictionary = pickle.load(r)

identity = dictionary["identity"]


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


class API:

    @staticmethod
    def btc():
        try:
            bit_stamp_tick = requests.get('https://www.bitstamp.net/api/ticker/')
            status = bit_stamp_tick.status_code
        except ConnectionError:
            bit_stamp_tick = ""
            status = 404
            pass
        if status == 200:
            try:
                price_float = float(bit_stamp_tick.json()['last'])
                price_str = str(f"{int(price_float):,d}") + "." + str(
                    round(abs(price_float - int(price_float)), 1)).split(".")[1]
                return price_str, price_float
            except JSONDecodeError:
                return None
            except Exception:
                return None
        else:
            return None

    @staticmethod
    def currency_exchange(currency):
        try:
            url = "https://currency-exchange.p.rapidapi.com/exchange"
            querystring = {"q": "1.0", "from": "USD", "to": f"{currency}"}
            # SGD, CAD, EUR, MAD
            headers = {
                'x-rapidapi-host': "currency-exchange.p.rapidapi.com",
                'x-rapidapi-key': "18319ab852msh3867d3eff319f6ep12eaafjsn2e2826a86312"
                # visit the website https://rapidapi.com/ and get your own key, it's free :).
            }
            response = requests.request("GET", url, headers=headers, params=querystring)
        except Exception:
            return None
        return float(response.text)


try:
    old_btc_price = API().btc()[1]
except Exception:
    old_btc_price = 0


class Thread:

    @staticmethod
    def every(delay, task):
        next_time = time.time() + delay
        while True:
            if 1 != 0:  # this is to break the loop after the program closed
                time.sleep(max(0, next_time - time.time()))
                try:
                    task()
                except TypeError:
                    traceback.print_exc()
                # skip tasks if we are behind schedule:
                next_time += (time.time() - next_time) // delay * delay + delay
            else:
                break


class Ui_Form(object):

    def opentrade_init(self):
        _translate = QtCore.QCoreApplication.translate

        if not Extract(f"Prevalues_{identity}").check_cell("opentrade"):
            Table(f"Prevalues_{identity}").create()
            data = {"date": 0, "amount": 0, "entry": 0, "state": "closed"}
            Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).insert()
            data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
            Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).insert()

        dict_ = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])
        amount = dict_["amount"]
        entry = dict_["entry"]
        state = dict_["state"]
        date = dict_["date"]

        print("dictionary", dict_)
        if state != "closed":
            self.checkBox_opentrade.setChecked(True)
            color = "background: rgb(191, 0, 0);" if state == "SELL" else \
                "background: rgb(0, 132, 0);"

            self.trade_date.setText(_translate("Form", f"{date}"))
            self.frame_12.setStyleSheet(color)
            self.trade_amount.setText(_translate("Form", f"{amount}$"))
            self.frame_13.setStyleSheet(color)
            self.trade_entry.setText(_translate("Form", f"{entry}$"))
            self.frame_14.setStyleSheet(color)

            frame_state = "background-image: url(:/images/Images/open_sign_sell.png);" if \
                state == "SELL" else "background-image: url(:/images/Images/open_sign_buy.png);\n"

            self.Trade_state_frame.setStyleSheet(f"{frame_state}"
                                                 "background-color: transparent;")

            self.input_exit_BS.setReadOnly(True)
            self.input_exit_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setStyleSheet("*{\n"
                                             "font: 75 12pt \"Bahnschrift\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background: rgb(100, 100, 100);\n"
                                             "}")

            # -----------------------------------------------

            self.down_bar_label.setText(_translate("Form",
                                                   f"Data Storage Size : {file_size('database.db')}                "
                                                   f"                  Trade open since : {date}                   "
                                                   f"                        "
                                                   "                                                    "
                                                   "                         "
                                                   "                                                    "
                                                   "                         "
                                                   "                                                    "
                                                   f"              {current_time()} "))

        else:
            self.checkBox_opentrade.setChecked(False)
            color = "background: rgb(0, 0, 0);"

            self.trade_date.setText(_translate("Form", ""))
            self.frame_12.setStyleSheet(color)
            self.trade_amount.setText(_translate("Form", ""))
            self.frame_13.setStyleSheet(color)
            self.trade_entry.setText(_translate("Form", ""))
            self.frame_14.setStyleSheet(color)

            self.Trade_state_frame.setStyleSheet("background-image: url(:/images/Images/close_sign.png);\n"
                                                 "background-color: transparent;")

            self.Trade_state_frame.setStyleSheet("background-image: url(:/images/Images/close_sign.png);\n"
                                                 "background-color: transparent;")

            self.input_exit_BS.setReadOnly(False)
            self.input_exit_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setStyleSheet("*{\n"
                                             "font: 75 12pt \"Bahnschrift\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background: rgb(240, 240, 240);\n"
                                             "}")
            # =======
            self.down_bar_label.setText(_translate("Form",
                                                   f"Data Storage Size : {file_size('database.db')}                "
                                                   f"                  Trade closed :                              "
                                                   f"                        "
                                                   "                                                    "
                                                   "                         "
                                                   "                                                    "
                                                   "                         "
                                                   "                                                    "
                                                   f"                   {current_time()} "))

    def journal_buy(self):
        global old_btc_price
        _translate = QtCore.QCoreApplication.translate
        try:

            state = eval(Extract(f"Prevalues_{identity}").get_by_id("opentradeplus")[1])

            amount = state["amount"]
            entry = state["entry"]
            exit_ = state["exit"]
            date = state["date"]

            if amount == 0 and entry == 0 and exit_ == 0 and date == 0:
                amount = str(self.input_amount_BS_3.text())
                entry = str(self.input_entry_BS.text())
                exit_ = str(self.input_exit_BS.text())

                date = datetime.date.today()
                month = date.month
                year = date.year
            else:
                data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()
                month, day, year = str(date).split("-")

            result = ((float(exit_) - float(entry)) / float(entry)) * (float(amount) * (1 / float(old_btc_price)))

            _result = "+" + str(round(result, 5)) if result > 0 else str(round(result, 5))

            Table(f'Journal_{identity}').create()

            count = len(Extract(f"Journal_{identity}").fetchall())

            Journal(name=f"Journal_{identity}", id_=str(count + 1), month=str(month), year=str(year),
                    date=str(date), amount="▲ " + str(amount), entry=str(entry), exit_=str(exit_),
                    result=_result).insert()

            # ---------------------------------------
            self.input_amount_BS_3.setText(_translate("MyAPP", ""))
            self.input_entry_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setText(_translate("MyAPP", ""))

        except Exception as e:
            print("journal buy ", e)

    def journal_sell(self):
        global old_btc_price
        _translate = QtCore.QCoreApplication.translate
        try:

            state = eval(Extract(f"Prevalues_{identity}").get_by_id("opentradeplus")[1])

            amount = state["amount"]
            entry = state["entry"]
            exit_ = state["exit"]
            date = state["date"]

            if amount == 0 and entry == 0 and exit_ == 0 and date == 0:
                amount = str(self.input_amount_BS_3.text())
                entry = str(self.input_entry_BS.text())
                exit_ = str(self.input_exit_BS.text())

                date = datetime.date.today()
                month = date.month
                year = date.year
            else:
                data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()
                month, day, year = str(date).split("-")

            result = ((float(entry) - float(exit_)) / float(entry)) * (float(amount) * (1 / float(old_btc_price)))

            _result = "+" + str(round(result, 5)) if result > 0 else str(round(result, 5))

            Table(f'Journal_{identity}').create()
            print("done yaya")
            count = len(Extract(f"Journal_{identity}").fetchall())

            Journal(name=f"Journal_{identity}", id_=str(count + 1), month=str(month), year=str(year),
                    date=str(date), amount="▼ " + str(amount), entry=str(entry), exit_=str(exit_),
                    result=_result).insert()

            # ---------------------------------------
            self.input_amount_BS_3.setText(_translate("MyAPP", ""))
            self.input_entry_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setText(_translate("MyAPP", ""))

        except Exception as e:
            print("journal sell ", e)

    def update(self):
        global old_btc_price
        _translate = QtCore.QCoreApplication.translate
        btc_price = API().btc()

        print(btc_price)
        if btc_price is not None:
            updated_btc_price = btc_price[1]
            str_btc_price = btc_price[0]
            if updated_btc_price > old_btc_price:
                self.btc_price.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                             "background: transparent;\n"
                                             "color: rgb(0, 132, 0);")
                self.btc_price.setText(_translate("Form", f"{str_btc_price.split('.')[0]}$"))
            elif updated_btc_price < old_btc_price:
                self.btc_price.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                             "background: transparent;\n"
                                             "color: rgb(188, 0, 0);")
                self.btc_price.setText(_translate("Form", f"{str_btc_price.split('.')[0]}$"))
            else:
                self.btc_price.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                             "background: transparent;\n"
                                             "color: rgb(0, 132, 0);")
                self.btc_price.setText(_translate("Form", f"{str_btc_price.split('.')[0]}$"))
            old_btc_price = updated_btc_price

        Table(f"Prevalues_{identity}").create()
        if Extract(f"Prevalues_{identity}").check_cell("currency_api"):
            value = eval(Extract(f"Prevalues_{identity}").get_by_id("currency_api")[1])
            currency_price = value["currency_Price"]

            if Extract(f"Prevalues_{identity}").check_cell("Wallet"):
                input_wallet = Extract(f"Prevalues_{identity}").get_by_id("Wallet")

                input_wallet = input_wallet[1]

                xusd = round(((float(input_wallet) * 0.00000001) * old_btc_price), 1)
                usd = str(f"{int(xusd):,d}") + "." + str(round(abs(xusd - int(xusd)), 1)).split(".")[1]

                xcurrency = round(float(currency_price) * xusd, 1)
                currency = str(f"{int(xcurrency):,d}") + "." + \
                           str(round(abs(xcurrency - int(xcurrency)), 1)).split(".")[1]

                self.wallet_S_label.setText(
                    _translate("Form", f"{self.zero_remover(usd)} $"))
                self.wallet_SS_label.setText(_translate("Form", f"{self.zero_remover(currency)}"))
        else:
            pass

    def user_wallet(self):  # wallet
        global old_btc_price
        global identity
        _translate = QtCore.QCoreApplication.translate
        try:
            input_wallet = str(self.input_wallet_balance.text())
            now = datetime.datetime.now()
            _btc_ = old_btc_price
            currency_ = "SGD"
            currency_price = 0
            if Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                value = eval(Extract(f"Prevalues_{identity}").get_by_id("currency_api")[1])
                currency_price = value["currency_Price"]
                currency_ = value["currency"]
                time_pass = value["time"]
                pass_ = True if time_pass != now.day else False
                pass_0 = False
            else:
                pass_ = True
                pass_0 = True

            currency_price = API.currency_exchange(self.comboBox_currency.currentText()) if pass_0 else \
                API.currency_exchange(currency_) if pass_ else currency_price

            if _btc_ is not None:
                if input_wallet != "":

                    Table(f"Prevalues_{identity}").create()
                    if not Extract(f"Prevalues_{identity}").check_cell("Wallet"):
                        Pre_values(f"Prevalues_{identity}", "Wallet", input_wallet).insert()
                    else:
                        Pre_values(f"Prevalues_{identity}", "Wallet", input_wallet).update()

                    xusd = round(((float(input_wallet) * 0.00000001) * _btc_), 1)
                    usd = str(f"{int(xusd):,d}") + "." + str(round(abs(xusd - int(xusd)), 1)).split(".")[1]

                    xcurrency = round(float(currency_price) * xusd, 1)
                    currency = str(f"{int(xcurrency):,d}") + "." + \
                               str(round(abs(xcurrency - int(xcurrency)), 1)).split(".")[1]

                    btc_ = round((float(input_wallet) * 0.00000001), 5)

                    self.wallet_sato_label.setText(_translate("Form", f"{int(input_wallet):,d} sat"))
                    self.wallet_btc_label.setText(_translate("Form", f"{btc_} ₿"))
                    self.wallet_S_label.setText(
                        _translate("Form", f"{self.zero_remover(usd)} $"))
                    self.wallet_SS_label.setText(_translate("Form", f"{self.zero_remover(currency)}"))

                    if pass_:
                        data = {"currency_Price": currency_price,
                                "currency": self.comboBox_currency.currentText(), "time": now.day}

                        if not Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                            Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).insert()
                        else:
                            Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).update()
            else:
                pass

        except Exception as e:
            print("user wallet ", e)

    @staticmethod
    def zero_remover(value):
        return value if str(value).split('.')[1] != '0' else str(value).split('.')[0]

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1597, 913)
        Form.setFixedSize(1597, 913)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/Images/picabout.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setStyleSheet("*{\n"
                           "background-color: rgb(71,71,80);\n"
                           "\n"
                           "color: rgb(255, 255, 255);\n"
                           "}\n"
                           "\n"
                           "QLabel {\n"
                           "color: rgb(255, 255, 255);\n"
                           "\n"
                           "}\n"
                           "\n"
                           "Line {\n"
                           "background-color: rgb(0, 0, 0);\n"
                           "\n"
                           "}\n"
                           "\n"
                           "QScrollBar:vertical {              \n"
                           "  border: none;\n"
                           "  background:rgb(0, 0, 0);\n"
                           "  width:8px;\n"
                           "  margin: 0px 0px 0px 0px;\n"
                           "        }\n"
                           "QScrollBar::handle:vertical {\n"
                           "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.820896 "
                           "rgba(200, 117, 17, 255), stop:1 rgba(255, 255, 255, 255));\n"
                           "            min-height: 0px;\n"
                           "        }\n"
                           "QScrollBar::add-line:vertical {\n"
                           "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                           "   stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));\n"
                           "\n"
                           "            height: 0px;\n"
                           "            subcontrol-position: bottom;\n"
                           "            subcontrol-origin: margin;\n"
                           "        }\n"
                           "QScrollBar::sub-line:vertical {\n"
                           "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                           "            stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                           "stop:1 rgb(32, 47, 130));\n"
                           "            height: 0 px;\n"
                           "            subcontrol-position: top;\n"
                           "            subcontrol-origin: margin;\n"
                           "        }\n"
                           "\n"
                           "QScrollBar::down-arrow:vertical {\n"
                           "                        /*image:url(:/images/Images/open-label.png);*/\n"
                           "                        height: 40px; \n"
                           "                        width: 40px                              \n"
                           "                      }\n"
                           "\n"
                           "")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(285, 0, 1315, 891))
        self.tabWidget.setStyleSheet("\n"
                                     " \n"
                                     "*{\n"
                                     "\n"
                                     "color: rgb(255, 255, 255);\n"
                                     "    \n"
                                     "font: 75 12pt \"Bahnschrift\";\n"
                                     "border-width: 0px;\n"
                                     "\n"
                                     "}\n"
                                     "\n"
                                     "QTabBar::tab:selected {\n"
                                     "background:  rgb(211, 211, 211);\n"
                                     "background: qlineargradient(spread:pad, x1:0.423, y1:0.625, x2:0.99005, "
                                     "y2:0.188, stop:0 rgba(124, 119, 119, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                     "color: rgb(0, 0, 0);\n"
                                     "}\n"
                                     "\n"
                                     "QTabBar::tab{\n"
                                     "background: rgb(88,88, 88);\n"
                                     "\n"
                                     "}\n"
                                     "")
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.TABLE_Widget = QtWidgets.QTableWidget(self.tab)
        self.TABLE_Widget.setEnabled(True)
        self.TABLE_Widget.setGeometry(QtCore.QRect(306, 40, 1006, 814))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.TABLE_Widget.setFont(font)
        self.TABLE_Widget.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.TABLE_Widget.setAutoFillBackground(False)
        self.TABLE_Widget.setStyleSheet("*{\n"
                                        "font: 14pt \"Bahnschrift\";\n"
                                        "    background-color: rgb(200, 200, 200);\n"
                                        "\n"
                                        "    \n"
                                        "\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "    \n"
                                        "color: rgb(255, 170, 0);\n"
                                        "    color: rgb(0, 0, 0);\n"
                                        "\n"
                                        "selection-background-color:qlineargradient(spread:pad, x1:0, y1:0, "
                                        "x2:1, y2:1, stop:0.726368 rgba(0, 0, 0, 255), stop:1 "
                                        "rgba(255, 255, 255, 255));\n"
                                        "}\n"
                                        "\n"
                                        "\n"
                                        "QScrollBar:vertical {              \n"
                                        "  border: none;\n"
                                        "  background:rgb(0, 0, 0);\n"
                                        "  width:8px;\n"
                                        "  margin: 0px 0px 0px 0px;\n"
                                        "        }\n"
                                        "QScrollBar::handle:vertical {\n"
                                        "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                        "stop:0.820896 rgba(200, 117, 17, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                        "            min-height: 0px;\n"
                                        "        }\n"
                                        "QScrollBar::add-line:vertical {\n"
                                        "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                        "            stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                        "stop:1 rgb(32, 47, 130));\n"
                                        "\n"
                                        "            height: 0px;\n"
                                        "            subcontrol-position: bottom;\n"
                                        "            subcontrol-origin: margin;\n"
                                        "        }\n"
                                        "QScrollBar::sub-line:vertical {\n"
                                        "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                        "            stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                        "stop:1 rgb(32, 47, 130));\n"
                                        "            height: 0 px;\n"
                                        "            subcontrol-position: top;\n"
                                        "            subcontrol-origin: margin;\n"
                                        "        }\n"
                                        "\n"
                                        "QScrollBar::down-arrow:vertical {\n"
                                        "                        /*image:url(:/images/Images/open-label.png);*/\n"
                                        "                        height: 40px; \n"
                                        "                        width: 40px                              \n"
                                        "                      }\n"
                                        "")
        self.TABLE_Widget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.TABLE_Widget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.TABLE_Widget.setLineWidth(0)
        self.TABLE_Widget.setMidLineWidth(0)
        self.TABLE_Widget.setAutoScroll(True)
        self.TABLE_Widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.TABLE_Widget.setTabKeyNavigation(True)
        self.TABLE_Widget.setProperty("showDropIndicator", True)
        self.TABLE_Widget.setDragDropOverwriteMode(True)
        self.TABLE_Widget.setAlternatingRowColors(True)
        self.TABLE_Widget.setShowGrid(True)
        self.TABLE_Widget.setGridStyle(QtCore.Qt.SolidLine)
        self.TABLE_Widget.setWordWrap(True)
        self.TABLE_Widget.setCornerButtonEnabled(True)
        self.TABLE_Widget.setObjectName("TABLE_Widget")
        self.TABLE_Widget.setColumnCount(6)
        # =========================================
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.TABLE_Widget.setHorizontalHeaderItem(5, item)
        # =====================================================

        self.TABLE_Widget.horizontalHeader().setVisible(True)
        self.TABLE_Widget.horizontalHeader().setCascadingSectionResizes(True)
        self.TABLE_Widget.horizontalHeader().setHighlightSections(True)
        self.TABLE_Widget.horizontalHeader().setSortIndicatorShown(True)
        self.TABLE_Widget.horizontalHeader().setStretchLastSection(True)
        self.TABLE_Widget.verticalHeader().setVisible(False)
        self.TABLE_Widget.verticalHeader().setCascadingSectionResizes(False)
        self.TABLE_Widget.verticalHeader().setHighlightSections(True)
        self.TABLE_Widget.verticalHeader().setSortIndicatorShown(False)
        self.TABLE_Widget.verticalHeader().setStretchLastSection(False)
        # ===========================================================
        self.line_2 = QtWidgets.QFrame(self.tab)
        self.line_2.setGeometry(QtCore.QRect(0, 0, 1246, 2))
        self.line_2.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.frame_8 = QtWidgets.QFrame(self.tab)
        self.frame_8.setGeometry(QtCore.QRect(305, 0, 244, 36))
        self.frame_8.setStyleSheet("background: rgba(0, 0, 0, 160);\n"
                                   "")
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.max_gain_1_label = QtWidgets.QLabel(self.frame_8)
        self.max_gain_1_label.setGeometry(QtCore.QRect(120, 0, 111, 35))
        self.max_gain_1_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                            "color: rgb(0, 132, 0);\n"
                                            "background: transparent;")
        self.max_gain_1_label.setObjectName("max_gain_1_label")
        self.label_31 = QtWidgets.QLabel(self.frame_8)
        self.label_31.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_31.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_31.setObjectName("label_31")
        self.frame_9 = QtWidgets.QFrame(self.tab)
        self.frame_9.setGeometry(QtCore.QRect(550, 0, 251, 35))
        self.frame_9.setStyleSheet("background: rgba(0, 0, 0, 160);")
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.min_gain_1_label = QtWidgets.QLabel(self.frame_9)
        self.min_gain_1_label.setGeometry(QtCore.QRect(130, 0, 111, 35))
        self.min_gain_1_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                            "color: rgb(0, 132, 0);\n"
                                            "background: transparent;")
        self.min_gain_1_label.setObjectName("min_gain_1_label")
        self.label_34 = QtWidgets.QLabel(self.frame_9)
        self.label_34.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_34.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_34.setObjectName("label_34")
        self.frame_10 = QtWidgets.QFrame(self.tab)
        self.frame_10.setGeometry(QtCore.QRect(800, 0, 261, 35))
        self.frame_10.setStyleSheet("background: rgba(0, 0, 0, 160);")
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.max_loss_1_label = QtWidgets.QLabel(self.frame_10)
        self.max_loss_1_label.setGeometry(QtCore.QRect(140, 0, 111, 35))
        self.max_loss_1_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                            "color: rgb(191, 0, 0);\n"
                                            "background: transparent;")
        self.max_loss_1_label.setObjectName("max_loss_1_label")
        self.label_36 = QtWidgets.QLabel(self.frame_10)
        self.label_36.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_36.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_36.setObjectName("label_36")
        self.frame_11 = QtWidgets.QFrame(self.tab)
        self.frame_11.setGeometry(QtCore.QRect(1060, 0, 252, 35))
        self.frame_11.setStyleSheet("background: rgba(0, 0, 0, 160);")
        self.frame_11.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_11.setObjectName("frame_11")
        self.min_loss_1_label = QtWidgets.QLabel(self.frame_11)
        self.min_loss_1_label.setGeometry(QtCore.QRect(130, 0, 111, 35))
        self.min_loss_1_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                            "color: rgb(191, 0, 0);\n"
                                            "background: transparent;")
        self.min_loss_1_label.setObjectName("min_loss_1_label")
        self.label_38 = QtWidgets.QLabel(self.frame_11)
        self.label_38.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_38.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_38.setObjectName("label_38")
        self.line_9 = QtWidgets.QFrame(self.tab)
        self.line_9.setGeometry(QtCore.QRect(800, 0, 2, 35))
        self.line_9.setStyleSheet("\n"
                                  "background-color: rgb(184, 184, 0);")
        self.line_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_9.setLineWidth(0)
        self.line_9.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_9.setObjectName("line_9")
        self.line_10 = QtWidgets.QFrame(self.tab)
        self.line_10.setGeometry(QtCore.QRect(550, 0, 2, 35))
        self.line_10.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_10.setLineWidth(0)
        self.line_10.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_10.setObjectName("line_10")
        self.line_11 = QtWidgets.QFrame(self.tab)
        self.line_11.setGeometry(QtCore.QRect(1060, 0, 2, 35))
        self.line_11.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_11.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_11.setLineWidth(0)
        self.line_11.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_11.setObjectName("line_11")
        self.line_12 = QtWidgets.QFrame(self.tab)
        self.line_12.setGeometry(QtCore.QRect(300, 0, 5, 857))
        self.line_12.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_12.setLineWidth(1)
        self.line_12.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.frame_5 = QtWidgets.QFrame(self.tab)
        self.frame_5.setGeometry(QtCore.QRect(0, 2, 301, 854))
        self.frame_5.setStyleSheet("*{background-color: rgb(40, 40, 40);\n"
                                   "\n"
                                   "    background-image: url(:/images/Images/bg_BS.png);\n"
                                   "\n"
                                   "}\n"
                                   "\n"
                                   "QLabel {\n"
                                   "font: 11pt \"Bahnschrift\";\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "background: transparent;\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.input_exit_BS = QtWidgets.QLineEdit(self.frame_5)
        self.input_exit_BS.setGeometry(QtCore.QRect(20, 800, 131, 20))
        self.input_exit_BS.setStyleSheet("*{\n"
                                         "font: 75 12pt \"Bahnschrift\";\n"
                                         "color: rgb(0, 0, 0);\n"
                                         "}\n"
                                         "QLineEdit{\n"
                                         "border-radius:8px;\n"
                                         "background: rgb(240, 240, 240);\n"
                                         "}")
        self.input_exit_BS.setAlignment(QtCore.Qt.AlignCenter)
        self.input_exit_BS.setPlaceholderText("")
        self.input_exit_BS.setObjectName("input_exit_BS")
        self.input_entry_BS = QtWidgets.QLineEdit(self.frame_5)
        self.input_entry_BS.setGeometry(QtCore.QRect(20, 730, 131, 20))
        self.input_entry_BS.setStyleSheet("*{\n"
                                          "font: 75 12pt \"Bahnschrift\";\n"
                                          "color: rgb(0, 0, 0);\n"
                                          "}\n"
                                          "QLineEdit{\n"
                                          "border-radius:8px;\n"
                                          "background: rgb(240, 240, 240);\n"
                                          "}")
        self.input_entry_BS.setAlignment(QtCore.Qt.AlignCenter)
        self.input_entry_BS.setPlaceholderText("")
        self.input_entry_BS.setObjectName("input_entry_BS")
        self.input_amount_BS_3 = QtWidgets.QLineEdit(self.frame_5)
        self.input_amount_BS_3.setGeometry(QtCore.QRect(20, 660, 131, 21))
        self.input_amount_BS_3.setStyleSheet("*{\n"
                                             "font: 75 12pt \"Bahnschrift\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background: rgb(240, 240, 240);\n"
                                             "}")
        self.input_amount_BS_3.setAlignment(QtCore.Qt.AlignCenter)
        self.input_amount_BS_3.setPlaceholderText("")
        self.input_amount_BS_3.setObjectName("input_amount_BS_3")
        self.btn_SELL = QtWidgets.QPushButton(self.frame_5)
        self.btn_SELL.setGeometry(QtCore.QRect(190, 740, 101, 31))
        self.btn_SELL.setStyleSheet("\n"
                                    "\n"
                                    "*{\n"
                                    "color: rgb(255, 0, 0);\n"
                                    "border-radius:15px;\n"
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
                                    "\n"
                                    "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                    "}\n"
                                    "\n"
                                    "\n"
                                    "QPushButton:hover{\n"
                                    "\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background:qlineargradient(spread:pad, x1:0.443, y1:0.670545, x2:0, y2:0.801, "
                                    "stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                    "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:pressed \n"
                                    "{\n"
                                    " border: 2px inset   rgb(255, 0, 0);\n"
                                    "background-color: #333;\n"
                                    "}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/Images/sell__.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_SELL.setIcon(icon1)
        self.btn_SELL.setObjectName("btn_SELL")
        self.btn_SELL.clicked.connect(self.calc_openTradeSELL)

        self.btn_BUY = QtWidgets.QPushButton(self.frame_5)
        self.btn_BUY.setGeometry(QtCore.QRect(190, 700, 101, 31))
        self.btn_BUY.setStyleSheet("\n"
                                   "\n"
                                   "*{\n"
                                   "color: rgb(0, 208, 0);\n"
                                   "border-radius:15px;\n"
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
                                   "\n"
                                   "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "QPushButton:hover{\n"
                                   "\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 "
                                   "rgba(255, 255, 255, 255), stop:0.233831 rgba(0, 0, 0, 224));\n"
                                   "\n"
                                   "\n"
                                   "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                   "}\n"
                                   "\n"
                                   "QPushButton:pressed \n"
                                   "{\n"
                                   " border: 2px inset    rgb(0, 170, 0);\n"
                                   "background-color: #333;\n"
                                   "}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/Images/buy__.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_BUY.setIcon(icon2)
        self.btn_BUY.setObjectName("btn_BUY")
        self.btn_BUY.clicked.connect(self.calc_openTradeBUY)

        self.frame_14 = QtWidgets.QFrame(self.frame_5)
        self.frame_14.setGeometry(QtCore.QRect(0, 500, 301, 41))

        self.frame_14.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_14.setObjectName("frame_14")
        self.trade_entry = QtWidgets.QLabel(self.frame_14)
        self.trade_entry.setGeometry(QtCore.QRect(170, 0, 121, 41))
        self.trade_entry.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                       "color: rgb(211, 211, 211);\n"
                                       "background: transparent;")
        self.trade_entry.setAlignment(QtCore.Qt.AlignCenter)
        self.trade_entry.setObjectName("trade_entry")
        self.label_44 = QtWidgets.QLabel(self.frame_14)
        self.label_44.setGeometry(QtCore.QRect(10, 0, 51, 41))
        self.label_44.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(211, 211, 211);\n"
                                    "background: transparent;")
        self.label_44.setObjectName("label_44")
        self.frame_13 = QtWidgets.QFrame(self.frame_5)
        self.frame_13.setGeometry(QtCore.QRect(0, 420, 301, 41))

        self.frame_13.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_13.setObjectName("frame_13")
        self.trade_amount = QtWidgets.QLabel(self.frame_13)
        self.trade_amount.setGeometry(QtCore.QRect(170, 0, 121, 41))
        self.trade_amount.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                        "color: rgb(211, 211, 211);\n"
                                        "background: transparent;")
        self.trade_amount.setFrameShadow(QtWidgets.QFrame.Raised)
        self.trade_amount.setAlignment(QtCore.Qt.AlignCenter)
        self.trade_amount.setObjectName("trade_amount")
        self.label_42 = QtWidgets.QLabel(self.frame_13)
        self.label_42.setGeometry(QtCore.QRect(10, 0, 71, 41))
        self.label_42.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(211, 211, 211);\n"
                                    "background: transparent;")
        self.label_42.setObjectName("label_42")
        self.frame_12 = QtWidgets.QFrame(self.frame_5)
        self.frame_12.setGeometry(QtCore.QRect(0, 340, 301, 41))

        self.frame_12.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_12.setObjectName("frame_12")
        self.trade_date = QtWidgets.QLabel(self.frame_12)
        self.trade_date.setGeometry(QtCore.QRect(170, 0, 121, 41))
        self.trade_date.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.trade_date.setFrameShadow(QtWidgets.QFrame.Plain)
        self.trade_date.setLineWidth(1)
        self.trade_date.setStyleSheet("font: bold 10pt \"Courier\";\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "background: transparent;")
        self.trade_date.setAlignment(QtCore.Qt.AlignCenter)
        self.trade_date.setObjectName("trade_date")
        self.label_40 = QtWidgets.QLabel(self.frame_12)
        self.label_40.setGeometry(QtCore.QRect(10, 0, 51, 41))
        self.label_40.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(211, 211, 211);\n"
                                    "background: transparent;")
        self.label_40.setObjectName("label_40")
        self.Trade_state_frame = QtWidgets.QFrame(self.frame_5)
        self.Trade_state_frame.setGeometry(QtCore.QRect(100, 230, 101, 91))
        self.Trade_state_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Trade_state_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Trade_state_frame.setObjectName("Trade_state_frame")
        self.input_delete = QtWidgets.QLineEdit(self.frame_5)
        self.input_delete.setGeometry(QtCore.QRect(20, 170, 61, 20))
        self.input_delete.setStyleSheet("*{\n"
                                        "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "}\n"
                                        "QLineEdit{\n"
                                        "border-radius:8px;\n"
                                        "background: rgb(240, 240, 240);\n"
                                        "}")
        self.input_delete.setText("")
        self.input_delete.setAlignment(QtCore.Qt.AlignCenter)
        self.input_delete.setObjectName("input_delete")
        self.label_16 = QtWidgets.QLabel(self.frame_5)
        self.label_16.setGeometry(QtCore.QRect(20, 140, 52, 24))
        self.label_16.setStyleSheet("")
        self.label_16.setObjectName("label_16")
        self.input_wallet_balance = QtWidgets.QLineEdit(self.frame_5)
        self.input_wallet_balance.setGeometry(QtCore.QRect(20, 110, 141, 20))
        self.input_wallet_balance.setStyleSheet("*{\n"
                                                "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                                "color: rgb(0, 0, 0);\n"
                                                "}\n"
                                                "QLineEdit{\n"
                                                "border-radius:8px;\n"
                                                "background: rgb(240, 240, 240);\n"
                                                "}")
        self.input_wallet_balance.setText("")
        self.input_wallet_balance.setAlignment(QtCore.Qt.AlignCenter)
        self.input_wallet_balance.setObjectName("input_wallet_balance")
        self.input_wallet_balance.returnPressed.connect(self.user_wallet)
        # =====================

        self.label_39 = QtWidgets.QLabel(self.frame_5)
        self.label_39.setGeometry(QtCore.QRect(20, 80, 61, 24))
        self.label_39.setStyleSheet("\n"
                                    "font: 63 italic 9pt \"Segoe UI Semibold\";")
        self.label_39.setObjectName("label_39")
        self.input_modify = QtWidgets.QLineEdit(self.frame_5)
        self.input_modify.setGeometry(QtCore.QRect(20, 46, 201, 20))
        self.input_modify.setStyleSheet("*{\n"
                                        "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                        "color: rgb(0, 0, 0);\n"
                                        "}\n"
                                        "QLineEdit{\n"
                                        "border-radius:8px;\n"
                                        "background: rgb(240, 240, 240);\n"
                                        "}")
        self.input_modify.setText("")
        self.input_modify.setAlignment(QtCore.Qt.AlignCenter)
        self.input_modify.setObjectName("input_modify")
        self.pushButton_4 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_4.setEnabled(False)
        self.pushButton_4.setGeometry(QtCore.QRect(150, 656, 31, 31))
        self.pushButton_4.setAutoFillBackground(False)
        self.pushButton_4.setStyleSheet("background-image: url(:/images/Images/S.png);\n"
                                        "\n"
                                        "background-color: transparent;")
        self.pushButton_4.setText("")
        self.pushButton_4.setCheckable(False)
        self.pushButton_4.setChecked(False)
        self.pushButton_4.setFlat(True)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_5.setEnabled(False)
        self.pushButton_5.setGeometry(QtCore.QRect(150, 726, 31, 31))
        self.pushButton_5.setAutoFillBackground(False)
        self.pushButton_5.setStyleSheet("background-image: url(:/images/Images/S.png);\n"
                                        "\n"
                                        "background-color: transparent;")
        self.pushButton_5.setText("")
        self.pushButton_5.setCheckable(False)
        self.pushButton_5.setChecked(False)
        self.pushButton_5.setFlat(True)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_5)
        self.pushButton_6.setEnabled(False)
        self.pushButton_6.setGeometry(QtCore.QRect(150, 796, 31, 31))
        self.pushButton_6.setAutoFillBackground(False)
        self.pushButton_6.setStyleSheet("background-image: url(:/images/Images/S.png);\n"
                                        "\n"
                                        "background-color: transparent;\n"
                                        "\n"
                                        "")
        self.pushButton_6.setText("")
        self.pushButton_6.setCheckable(False)
        self.pushButton_6.setChecked(False)
        self.pushButton_6.setFlat(True)
        self.pushButton_6.setObjectName("pushButton_6")
        self.label_15 = QtWidgets.QLabel(self.frame_5)
        self.label_15.setGeometry(QtCore.QRect(20, 10, 61, 32))
        self.label_15.setStyleSheet("")
        self.label_15.setObjectName("label_15")
        self.btn_BUY_modify = QtWidgets.QPushButton(self.frame_5)
        self.btn_BUY_modify.setEnabled(True)
        self.btn_BUY_modify.setGeometry(QtCore.QRect(230, 20, 61, 31))
        self.btn_BUY_modify.setStyleSheet("\n"
                                          "\n"
                                          "*{\n"
                                          "color: rgb(0, 208, 0);\n"
                                          "border-radius:15px;\n"
                                          "    \n"
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
                                          "background:  rgb(0,0,0);\n"
                                          "\n"
                                          "\n"
                                          "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                          "}\n"
                                          "\n"
                                          "\n"
                                          "QPushButton:hover{\n"
                                          "\n"
                                          "color: rgb(255, 255, 255);\n"
                                          "background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                          "stop:0 rgba(255, 255, 255, 255), stop:0.233831 rgba(0, 0, 0, 224));\n"
                                          "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                          "}\n"
                                          "\n"
                                          "QPushButton:pressed \n"
                                          "{\n"
                                          " border: 2px inset    rgb(0, 170, 0);\n"
                                          "background-color: #333;\n"
                                          "}")
        self.btn_BUY_modify.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/Images/buy__.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        icon3.addPixmap(QtGui.QPixmap(":/images/Images/buy__.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
        self.btn_BUY_modify.setIcon(icon3)
        self.btn_BUY_modify.setObjectName("btn_BUY_modify")
        self.btn_SELL_modify = QtWidgets.QPushButton(self.frame_5)
        self.btn_SELL_modify.setGeometry(QtCore.QRect(230, 60, 61, 31))
        self.btn_SELL_modify.setStyleSheet("\n"
                                           "\n"
                                           "*{\n"
                                           "color: rgb(255, 0, 0);\n"
                                           "border-radius:15px;\n"
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
                                           "\n"
                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                           "}\n"
                                           "\n"
                                           "\n"
                                           "QPushButton:hover{\n"
                                           "\n"
                                           "color: rgb(255, 255, 255);\n"
                                           "background:qlineargradient(spread:pad, x1:0.443, y1:0.670545, x2:0, "
                                           "y2:0.801, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton:pressed \n"
                                           "{\n"
                                           " border: 2px inset   rgb(255, 0, 0);\n"
                                           "background-color: #333;\n"
                                           "}")
        self.btn_SELL_modify.setText("")
        self.btn_SELL_modify.setIcon(icon1)
        self.btn_SELL_modify.setObjectName("btn_SELL_modify")
        self.label_32 = QtWidgets.QLabel(self.frame_5)
        self.label_32.setGeometry(QtCore.QRect(20, 620, 71, 32))
        self.label_32.setStyleSheet("")
        self.label_32.setObjectName("label_32")
        self.label_45 = QtWidgets.QLabel(self.frame_5)
        self.label_45.setGeometry(QtCore.QRect(20, 690, 61, 32))
        self.label_45.setStyleSheet("")
        self.label_45.setObjectName("label_45")
        self.label_46 = QtWidgets.QLabel(self.frame_5)
        self.label_46.setGeometry(QtCore.QRect(20, 760, 61, 32))
        self.label_46.setStyleSheet("")
        self.label_46.setObjectName("label_46")
        self.checkBox_opentrade = QtWidgets.QCheckBox(self.frame_5)
        self.checkBox_opentrade.setEnabled(True)
        self.checkBox_opentrade.setGeometry(QtCore.QRect(10, 570, 131, 31))
        self.checkBox_opentrade.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                              "color: rgb(255, 255, 255);\n"
                                              "background: transparent;")
        self.checkBox_opentrade.setCheckable(True)
        self.checkBox_opentrade.setChecked(False)
        self.checkBox_opentrade.setAutoRepeat(False)
        self.checkBox_opentrade.setTristate(False)
        self.checkBox_opentrade.setObjectName("checkBox_opentrade")
        self.checkBox_opentrade.stateChanged.connect(self.open_trade_combo)

        self.wallet_btn = QtWidgets.QPushButton(self.frame_5)
        self.wallet_btn.setGeometry(QtCore.QRect(170, 104, 28, 28))
        self.wallet_btn.setStyleSheet("\n"
                                      "\n"
                                      "*{\n"
                                      "\n"
                                      "    background-image: url(:/images/Images/ww.png);\n"
                                      "background-color: transparent ;\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "background-color: rgb(66, 66, 66);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid   transparent;\n"
                                      "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset    rgb(0, 0, 0);\n"
                                      "background-color: #333;\n"
                                      "}")
        self.wallet_btn.setText("")
        self.wallet_btn.setObjectName("wallet_btn")

        self.wallet_btn.clicked.connect(self.user_wallet)

        # ================================

        self.delete_btn = QtWidgets.QPushButton(self.frame_5)
        self.delete_btn.setGeometry(QtCore.QRect(85, 166, 28, 28))
        self.delete_btn.setStyleSheet("*{\n"
                                      "background-image: url(:/images/Images/icons8-trash-24.png);\n"
                                      "background-color: transparent ;\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "background-color: rgb(66, 66, 66);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  transparent;\n"
                                      "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset    rgb(0, 0, 0);\n"
                                      "background-color: #333;\n"
                                      "}")
        self.delete_btn.setText("")
        self.delete_btn.setObjectName("delete_btn")
        self.frame_7 = QtWidgets.QFrame(self.frame_5)
        self.frame_7.setGeometry(QtCore.QRect(149, 218, 28, 28))
        self.frame_7.setStyleSheet("background-image: url(:/images/Images/pin1.png);\n"
                                   "background-color: transparent;")
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/images/Images/journal.png"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab, icon4, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.line_3 = QtWidgets.QFrame(self.tab_3)
        self.line_3.setGeometry(QtCore.QRect(0, 0, 1312, 2))
        self.line_3.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                  "")
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.performance_frame = QtWidgets.QFrame(self.tab_3)
        self.performance_frame.setGeometry(QtCore.QRect(30, 158, 1087, 529))
        self.performance_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.performance_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.performance_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.performance_frame.setObjectName("performance_frame")
        self.frame_23 = QtWidgets.QFrame(self.tab_3)
        self.frame_23.setGeometry(QtCore.QRect(30, 120, 271, 35))
        self.frame_23.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_23.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_23.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_23.setObjectName("frame_23")
        self.max_gain_performance = QtWidgets.QLabel(self.frame_23)
        self.max_gain_performance.setGeometry(QtCore.QRect(140, 0, 111, 35))
        self.max_gain_performance.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                "color: rgb(0, 132, 0);\n"
                                                "background: transparent;")
        self.max_gain_performance.setObjectName("max_gain_performance")
        self.label_48 = QtWidgets.QLabel(self.frame_23)
        self.label_48.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_48.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_48.setObjectName("label_48")
        self.frame_24 = QtWidgets.QFrame(self.tab_3)
        self.frame_24.setGeometry(QtCore.QRect(303, 120, 266, 35))
        self.frame_24.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_24.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_24.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_24.setObjectName("frame_24")
        self.min_gain_performance = QtWidgets.QLabel(self.frame_24)
        self.min_gain_performance.setGeometry(QtCore.QRect(140, 0, 111, 35))
        self.min_gain_performance.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                "color: rgb(0, 132, 0);\n"
                                                "background: transparent;")
        self.min_gain_performance.setObjectName("min_gain_performance")
        self.label_50 = QtWidgets.QLabel(self.frame_24)
        self.label_50.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_50.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_50.setObjectName("label_50")
        self.frame_25 = QtWidgets.QFrame(self.tab_3)
        self.frame_25.setGeometry(QtCore.QRect(573, 120, 266, 35))
        self.frame_25.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_25.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_25.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_25.setObjectName("frame_25")
        self.max_loss_performance = QtWidgets.QLabel(self.frame_25)
        self.max_loss_performance.setGeometry(QtCore.QRect(140, 0, 111, 35))
        self.max_loss_performance.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                "color: rgb(191, 0, 0);\n"
                                                "background: transparent;")
        self.max_loss_performance.setObjectName("max_loss_performance")
        self.label_52 = QtWidgets.QLabel(self.frame_25)
        self.label_52.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_52.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_52.setObjectName("label_52")
        self.frame_26 = QtWidgets.QFrame(self.tab_3)
        self.frame_26.setGeometry(QtCore.QRect(842, 120, 275, 35))
        self.frame_26.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_26.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_26.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_26.setObjectName("frame_26")
        self.min_loss_performance = QtWidgets.QLabel(self.frame_26)
        self.min_loss_performance.setGeometry(QtCore.QRect(150, 0, 111, 35))
        self.min_loss_performance.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                "color: rgb(191, 0, 0);\n"
                                                "background: transparent;")
        self.min_loss_performance.setObjectName("min_loss_performance")
        self.label_54 = QtWidgets.QLabel(self.frame_26)
        self.label_54.setGeometry(QtCore.QRect(10, 0, 91, 35))
        self.label_54.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_54.setObjectName("label_54")
        self.frame_31 = QtWidgets.QFrame(self.tab_3)
        self.frame_31.setGeometry(QtCore.QRect(390, 690, 372, 35))
        self.frame_31.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_31.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_31.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_31.setObjectName("frame_31")
        self.label_59 = QtWidgets.QLabel(self.frame_31)
        self.label_59.setGeometry(QtCore.QRect(20, 0, 91, 31))
        self.label_59.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_59.setObjectName("label_59")
        self.preformance_total_loss_label = QtWidgets.QLabel(self.frame_31)
        self.preformance_total_loss_label.setGeometry(QtCore.QRect(240, 0, 121, 31))
        self.preformance_total_loss_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                        "color: rgb(191, 0, 0);\n"
                                                        "\n"
                                                        "background: transparent;")
        self.preformance_total_loss_label.setObjectName("preformance_total_loss_label")
        self.frame_32 = QtWidgets.QFrame(self.tab_3)
        self.frame_32.setGeometry(QtCore.QRect(30, 690, 361, 35))
        self.frame_32.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_32.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_32.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_32.setObjectName("frame_32")
        self.label_58 = QtWidgets.QLabel(self.frame_32)
        self.label_58.setGeometry(QtCore.QRect(20, 0, 81, 31))
        self.label_58.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_58.setObjectName("label_58")
        self.preformance_total_wins_label = QtWidgets.QLabel(self.frame_32)
        self.preformance_total_wins_label.setGeometry(QtCore.QRect(230, 0, 121, 31))
        self.preformance_total_wins_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                        "color: rgb(0, 132, 0);\n"
                                                        "background: transparent;")
        self.preformance_total_wins_label.setObjectName("preformance_total_wins_label")
        self.frame_30 = QtWidgets.QFrame(self.tab_3)
        self.frame_30.setGeometry(QtCore.QRect(766, 690, 351, 35))
        self.frame_30.setStyleSheet("background: rgb(0, 0, 0);")
        self.frame_30.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_30.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_30.setObjectName("frame_30")
        self.label_56 = QtWidgets.QLabel(self.frame_30)
        self.label_56.setGeometry(QtCore.QRect(20, 0, 81, 31))
        self.label_56.setStyleSheet("font: 11pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_56.setObjectName("label_56")
        self.preformance_pure_profit_label = QtWidgets.QLabel(self.frame_30)
        self.preformance_pure_profit_label.setGeometry(QtCore.QRect(220, 0, 121, 31))
        self.preformance_pure_profit_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                         "color: rgb(0, 132, 0);\n"
                                                         "background: transparent;")
        self.preformance_pure_profit_label.setObjectName("preformance_pure_profit_label")
        self.listWidget_preformance = QtWidgets.QListWidget(self.tab_3)
        self.listWidget_preformance.setGeometry(QtCore.QRect(1118, 154, 161, 534))
        self.listWidget_preformance.setStyleSheet("* {\n"
                                                  "    show-decoration-selected: 1;\n"
                                                  "    selection-color: white;\n"
                                                  "    selection-background-color: rgb(132,88, 0);\n"
                                                  "    font: 11pt \"Bahnschrift\";\n"
                                                  "    color: rgb(255, 255, 255);\n"
                                                  "    background-color: rgb(0, 0, 0);\n"
                                                  "\n"
                                                  "    \n"
                                                  "}\n"
                                                  "\n"
                                                  "QListView::item:selected:active:hover{\n"
                                                  "    background-color:rgb(211, 211, 211); \n"
                                                  "    color: black;\n"
                                                  "}\n"
                                                  "QListView::item:selected:active:!hover{\n"
                                                  "     background-color: rgb(211, 211, 211); \n"
                                                  "   \n"
                                                  "    color: rgb(0, 0, 0);\n"
                                                  "\n"
                                                  "}\n"
                                                  "QListView::item:selected:!active{\n"
                                                  "    background-color:rgb(163, 163, 163); \n"
                                                  "   \n"
                                                  "    color: rgb(0, 0, 0);\n"
                                                  "}\n"
                                                  "QListView::item:!selected:hover{\n"
                                                  "   background-color:rgb(0, 0, 0); \n"
                                                  "    background-color: rgb(125, 83, 0);\n"
                                                  "    color: rgb(255, 255, 255);\n"
                                                  "}\n"
                                                  "\n"
                                                  "QScrollBar:vertical {              \n"
                                                  "  border: none;\n"
                                                  "  background:rgb(0, 0, 0);\n"
                                                  "  width:8px;\n"
                                                  "  margin: 0px 0px 0px 0px;\n"
                                                  "        }\n"
                                                  "QScrollBar::handle:vertical {\n"
                                                  "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                                  "stop:0.820896 rgba(200, 117, 17, 255), stop:1 "
                                                  "rgba(255, 255, 255, 255));\n"
                                                  "            min-height: 0px;\n"
                                                  "        }\n"
                                                  "QScrollBar::add-line:vertical {\n"
                                                  "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                                  "            stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                                  "stop:1 rgb(32, 47, 130));\n"
                                                  "\n"
                                                  "            height: 0px;\n"
                                                  "            subcontrol-position: bottom;\n"
                                                  "            subcontrol-origin: margin;\n"
                                                  "        }\n"
                                                  "QScrollBar::sub-line:vertical {\n"
                                                  "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                                  "            stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                                  "stop:1 rgb(32, 47, 130));\n"
                                                  "            height: 0 px;\n"
                                                  "            subcontrol-position: top;\n"
                                                  "            subcontrol-origin: margin;\n"
                                                  "        }\n"
                                                  "\n"
                                                  "QScrollBar::down-arrow:vertical {\n"
                                                  "                        image:url(:/images/Images/S.png);\n"
                                                  "                        height: 40px; \n"
                                                  "                        width: 40px                              \n"
                                                  "                      }\n"
                                                  "")
        self.listWidget_preformance.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget_preformance.setFrameShadow(QtWidgets.QFrame.Plain)
        self.listWidget_preformance.setLineWidth(1)
        self.listWidget_preformance.setIconSize(QtCore.QSize(0, 0))
        self.listWidget_preformance.setTextElideMode(QtCore.Qt.ElideNone)
        self.listWidget_preformance.setMovement(QtWidgets.QListView.Static)
        self.listWidget_preformance.setProperty("isWrapping", False)
        self.listWidget_preformance.setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget_preformance.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget_preformance.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget_preformance.setModelColumn(0)
        self.listWidget_preformance.setUniformItemSizes(False)
        self.listWidget_preformance.setBatchSize(100)
        self.listWidget_preformance.setWordWrap(True)
        self.listWidget_preformance.setSelectionRectVisible(True)
        self.listWidget_preformance.setItemAlignment(QtCore.Qt.AlignHCenter)
        self.listWidget_preformance.setObjectName("listWidget_preformance")
        item = QtWidgets.QListWidgetItem()
        self.listWidget_preformance.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_preformance.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_preformance.addItem(item)
        self.line_15 = QtWidgets.QFrame(self.tab_3)
        self.line_15.setGeometry(QtCore.QRect(763, 690, 2, 35))
        self.line_15.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_15.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_15.setLineWidth(0)
        self.line_15.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_15.setObjectName("line_15")
        self.line_30 = QtWidgets.QFrame(self.tab_3)
        self.line_30.setGeometry(QtCore.QRect(390, 690, 2, 35))
        self.line_30.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_30.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_30.setLineWidth(0)
        self.line_30.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_30.setObjectName("line_30")
        self.line_31 = QtWidgets.QFrame(self.tab_3)
        self.line_31.setGeometry(QtCore.QRect(300, 120, 2, 35))
        self.line_31.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_31.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_31.setLineWidth(0)
        self.line_31.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_31.setObjectName("line_31")
        self.line_32 = QtWidgets.QFrame(self.tab_3)
        self.line_32.setGeometry(QtCore.QRect(570, 120, 2, 35))
        self.line_32.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_32.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_32.setLineWidth(0)
        self.line_32.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_32.setObjectName("line_32")
        self.line_33 = QtWidgets.QFrame(self.tab_3)
        self.line_33.setGeometry(QtCore.QRect(840, 120, 2, 35))
        self.line_33.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_33.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_33.setLineWidth(0)
        self.line_33.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_33.setObjectName("line_33")
        self.note_date_2 = QtWidgets.QLabel(self.tab_3)
        self.note_date_2.setGeometry(QtCore.QRect(1118, 120, 161, 33))
        self.note_date_2.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                       "font: 10pt \"Bahnschrift\";\n"
                                       "")
        self.note_date_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.note_date_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.note_date_2.setLineWidth(2)
        self.note_date_2.setAlignment(QtCore.Qt.AlignCenter)
        self.note_date_2.setObjectName("note_date_2")
        self.line_34 = QtWidgets.QFrame(self.tab_3)
        self.line_34.setGeometry(QtCore.QRect(1117, 157, 2, 530))
        self.line_34.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_34.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_34.setLineWidth(0)
        self.line_34.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_34.setObjectName("line_34")
        self.line_36 = QtWidgets.QFrame(self.tab_3)
        self.line_36.setGeometry(QtCore.QRect(30, 688, 1250, 2))
        self.line_36.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_36.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_36.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_36.setObjectName("line_36")
        self.line_37 = QtWidgets.QFrame(self.tab_3)
        self.line_37.setGeometry(QtCore.QRect(30, 154, 1249, 2))
        self.line_37.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);\n"
                                   "")
        self.line_37.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_37.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_37.setObjectName("line_37")
        self.line_35 = QtWidgets.QFrame(self.tab_3)
        self.line_35.setGeometry(QtCore.QRect(1117, 120, 2, 34))
        self.line_35.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_35.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_35.setLineWidth(0)
        self.line_35.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_35.setObjectName("line_35")
        self.line_38 = QtWidgets.QFrame(self.tab_3)
        self.line_38.setGeometry(QtCore.QRect(1117, 690, 2, 35))
        self.line_38.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_38.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_38.setLineWidth(0)
        self.line_38.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_38.setObjectName("line_38")
        self.note_date_3 = QtWidgets.QLabel(self.tab_3)
        self.note_date_3.setGeometry(QtCore.QRect(1120, 690, 159, 35))
        self.note_date_3.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                       "font: 10pt \"Bahnschrift\";\n"
                                       "")
        self.note_date_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.note_date_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.note_date_3.setLineWidth(2)
        self.note_date_3.setText("")
        self.note_date_3.setAlignment(QtCore.Qt.AlignCenter)
        self.note_date_3.setObjectName("note_date_3")
        self.label_64 = QtWidgets.QLabel(self.tab_3)
        self.label_64.setGeometry(QtCore.QRect(30, 10, 1251, 101))
        self.label_64.setStyleSheet("background: transparent;\n"
                                    "font: 13pt \"Bahnschrift\";\n"
                                    "color: rgb(0, 0, 0);")
        self.label_64.setAlignment(QtCore.Qt.AlignCenter)
        self.label_64.setObjectName("label_64")
        self.line_28 = QtWidgets.QFrame(self.tab_3)
        self.line_28.setGeometry(QtCore.QRect(1310, 0, 3, 856))
        self.line_28.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_28.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_28.setObjectName("line_28")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/images/Images/graph.png"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.tab_3, icon5, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.line_4 = QtWidgets.QFrame(self.tab_2)
        self.line_4.setGeometry(QtCore.QRect(0, 0, 1313, 2))
        self.line_4.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.note_TextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.note_TextEdit.setGeometry(QtCore.QRect(330, 60, 951, 791))
        self.note_TextEdit.setAutoFillBackground(False)
        self.note_TextEdit.setStyleSheet("font: 12pt \"Bahnschrift\";\n"
                                         "color: rgb(255, 255, 255);\n"
                                         "\n"
                                         "background: transparent;\n"
                                         "")
        self.note_TextEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.note_TextEdit.setFrameShadow(QtWidgets.QFrame.Raised)
        self.note_TextEdit.setLineWidth(0)
        self.note_TextEdit.setTabChangesFocus(False)
        self.note_TextEdit.setOverwriteMode(False)
        self.note_TextEdit.setBackgroundVisible(False)
        self.note_TextEdit.setObjectName("note_TextEdit")
        self.listWidget_Note = QtWidgets.QListWidget(self.tab_2)
        self.listWidget_Note.setGeometry(QtCore.QRect(10, 125, 271, 731))
        self.listWidget_Note.setStyleSheet("QListView {\n"
                                           "    show-decoration-selected: 1;\n"
                                           "    selection-color: white;\n"
                                           "    selection-background-color: rgb(132,88, 0);\n"
                                           "    font: 11pt \"Bahnschrift\";\n"
                                           "    color: rgb(255, 255, 255);\n"
                                           "    background: transparent;\n"
                                           "  \n"
                                           "}\n"
                                           "\n"
                                           "QListView::item:selected:active:hover{\n"
                                           "    background-color:rgb(211, 211, 211); \n"
                                           "    color: black;\n"
                                           "}\n"
                                           "QListView::item:selected:active:!hover{\n"
                                           "     background-color: rgb(211, 211, 211); \n"
                                           "   \n"
                                           "    color: rgb(0, 0, 0);\n"
                                           "\n"
                                           "}\n"
                                           "QListView::item:selected:!active{\n"
                                           "    background-color:rgb(224, 219, 219);\n"
                                           "    color: rgb(0, 0, 0);\n"
                                           "  \n"
                                           "}\n"
                                           "QListView::item:!selected:hover{\n"
                                           "   background-color:rgb(0, 0, 0); \n"
                                           "   background: qlineargradient(spread:pad, x1:0.423, y1:0.625, "
                                           "x2:0.99005, y2:0.188, stop:0 rgba(124, 119, 119, 255), stop:1 "
                                           "rgba(255, 255, 255, 255));\n"
                                           "    color: rgb(255, 255, 255);\n"
                                           "    color: rgb(0, 0, 0);\n"
                                           "}\n"
                                           "\n"
                                           "QScrollBar:vertical {              \n"
                                           "  border: none;\n"
                                           "  background:rgb(0, 0, 0);\n"
                                           "  width:8px;\n"
                                           "  margin: 0px 0px 0px 0px;\n"
                                           "        }\n"
                                           "QScrollBar::handle:vertical {\n"
                                           "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
                                           "stop:0.820896 rgba(200, 117, 17, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                           "            min-height: 0px;\n"
                                           "        }\n"
                                           "QScrollBar::add-line:vertical {\n"
                                           "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                           "            stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                           "stop:1 rgb(32, 47, 130));\n"
                                           "\n"
                                           "            height: 0px;\n"
                                           "            subcontrol-position: bottom;\n"
                                           "            subcontrol-origin: margin;\n"
                                           "        }\n"
                                           "QScrollBar::sub-line:vertical {\n"
                                           "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                           "            stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  "
                                           "stop:1 rgb(32, 47, 130));\n"
                                           "            height: 0 px;\n"
                                           "            subcontrol-position: top;\n"
                                           "            subcontrol-origin: margin;\n"
                                           "        }\n"
                                           "\n"
                                           "QScrollBar::down-arrow:vertical {\n"
                                           "                        /*image:url(:/images/Images/open-label.png);*/\n"
                                           "                        height: 40px; \n"
                                           "                        width: 40px                              \n"
                                           "                      }\n"
                                           "\n"
                                           "")
        self.listWidget_Note.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget_Note.setFrameShadow(QtWidgets.QFrame.Plain)
        self.listWidget_Note.setLineWidth(1)
        self.listWidget_Note.setIconSize(QtCore.QSize(0, 0))
        self.listWidget_Note.setTextElideMode(QtCore.Qt.ElideNone)
        self.listWidget_Note.setMovement(QtWidgets.QListView.Static)
        self.listWidget_Note.setProperty("isWrapping", False)
        self.listWidget_Note.setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget_Note.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget_Note.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget_Note.setModelColumn(0)
        self.listWidget_Note.setUniformItemSizes(False)
        self.listWidget_Note.setWordWrap(True)
        self.listWidget_Note.setSelectionRectVisible(True)
        self.listWidget_Note.setObjectName("listWidget_Note")
        item = QtWidgets.QListWidgetItem()
        self.listWidget_Note.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_Note.addItem(item)
        self.line_5 = QtWidgets.QFrame(self.tab_2)
        self.line_5.setGeometry(QtCore.QRect(292, 0, 5, 860))
        self.line_5.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_5.setLineWidth(1)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.note_btn_add = QtWidgets.QPushButton(self.tab_2)
        self.note_btn_add.setGeometry(QtCore.QRect(260, 22, 28, 28))
        self.note_btn_add.setStyleSheet("\n"
                                        "\n"
                                        "*{\n"
                                        "border-radius:10px;\n"
                                        "background-image: url(:/images/Images/add.png);\n"
                                        "background-color: transparent ;\n"
                                        "\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "background-color: rgb(55,55,55);\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton{\n"
                                        "border: 1px solid   transparent;\n"
                                        "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                        "}\n"
                                        "\n"
                                        "\n"
                                        "QPushButton:pressed \n"
                                        "{\n"
                                        " border: 2px inset     rgb(255, 255, 255);\n"
                                        "background-color: #333;\n"
                                        "}")
        self.note_btn_add.setText("")
        self.note_btn_add.setObjectName("note_btn_add")
        self.note_input_add = QtWidgets.QLineEdit(self.tab_2)
        self.note_input_add.setGeometry(QtCore.QRect(20, 20, 231, 31))
        self.note_input_add.setStyleSheet("*{\n"
                                          "font: 75 12pt \"MS Shell Dlg 2\";\n"
                                          "color: rgb(255, 255, 255);\n"
                                          "border-radius:15px;\n"
                                          "background-color: rgb(0, 0, 0);\n"
                                          "}\n"
                                          "")
        self.note_input_add.setText("")
        self.note_input_add.setAlignment(QtCore.Qt.AlignCenter)
        self.note_input_add.setObjectName("note_input_add")
        self.note_input_search = QtWidgets.QLineEdit(self.tab_2)
        self.note_input_search.setGeometry(QtCore.QRect(20, 70, 231, 31))
        self.note_input_search.setStyleSheet("*{\n"
                                             "font: 75 12pt \"MS Shell Dlg 2\";\n"
                                             "color: rgb(255, 255, 255);\n"
                                             "border-radius:15px;\n"
                                             "background-color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "")
        self.note_input_search.setText("")
        self.note_input_search.setAlignment(QtCore.Qt.AlignCenter)
        self.note_input_search.setObjectName("note_input_search")
        self.line_6 = QtWidgets.QFrame(self.tab_2)
        self.line_6.setGeometry(QtCore.QRect(0, 120, 292, 2))
        self.line_6.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.note_btn_search = QtWidgets.QPushButton(self.tab_2)
        self.note_btn_search.setGeometry(QtCore.QRect(260, 72, 28, 28))
        self.note_btn_search.setStyleSheet("\n"
                                           "\n"
                                           "*{\n"
                                           "border-radius:10px;\n"
                                           "\n"
                                           "background-image:url(:/images/Images/search.png);\n"
                                           "background-color: transparent ;\n"
                                           "\n"
                                           "\n"
                                           "\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton:hover{\n"
                                           "background-color: rgb(55, 55, 55);\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton{\n"
                                           "border: 1px solid   transparent;\n"
                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                           "}\n"
                                           "\n"
                                           "\n"
                                           "QPushButton:pressed \n"
                                           "{\n"
                                           " border: 2px inset     rgb(255, 255, 255);\n"
                                           "background-color: #333;\n"
                                           "}")
        self.note_btn_search.setText("")
        self.note_btn_search.setObjectName("note_btn_search")
        self.frame = QtWidgets.QFrame(self.tab_2)
        self.frame.setGeometry(QtCore.QRect(309, 10, 991, 41))
        self.frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                 "\n"
                                 "border-radius:20px;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.note_date = QtWidgets.QLabel(self.frame)
        self.note_date.setGeometry(QtCore.QRect(770, 0, 221, 41))
        self.note_date.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                     "border-radius:20px;")
        self.note_date.setFrameShape(QtWidgets.QFrame.Panel)
        self.note_date.setFrameShadow(QtWidgets.QFrame.Raised)
        self.note_date.setLineWidth(2)
        self.note_date.setAlignment(QtCore.Qt.AlignCenter)
        self.note_date.setObjectName("note_date")
        self.note_title = QtWidgets.QLabel(self.frame)
        self.note_title.setGeometry(QtCore.QRect(0, 0, 661, 41))
        self.note_title.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                      "border-radius:20px;\n"
                                      "")
        self.note_title.setFrameShape(QtWidgets.QFrame.Panel)
        self.note_title.setFrameShadow(QtWidgets.QFrame.Raised)
        self.note_title.setLineWidth(2)
        self.note_title.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.note_title.setIndent(10)
        self.note_title.setObjectName("note_title")
        self.note_btn_delete = QtWidgets.QPushButton(self.frame)
        self.note_btn_delete.setGeometry(QtCore.QRect(730, 0, 31, 41))
        self.note_btn_delete.setStyleSheet("\n"
                                           "*{\n"
                                           "border-radius:10px;\n"
                                           "background-color: transparent ;\n"
                                           "\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton:hover{\n"
                                           "background-color: rgb(55, 55, 55);\n"
                                           "}\n"
                                           "\n"
                                           "QPushButton{\n"
                                           "border: 1px solid   transparent;\n"
                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                           "}\n"
                                           "\n"
                                           "\n"
                                           "QPushButton:pressed \n"
                                           "{\n"
                                           " border: 2px inset     rgb(255, 255, 255);\n"
                                           "background-color: #333;\n"
                                           "}")
        self.note_btn_delete.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/images/Images/icons8-delete-file-26.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.note_btn_delete.setIcon(icon6)
        self.note_btn_delete.setFlat(True)
        self.note_btn_delete.setObjectName("note_btn_delete")
        self.note_btn_save = QtWidgets.QPushButton(self.frame)
        self.note_btn_save.setGeometry(QtCore.QRect(680, 0, 31, 41))
        self.note_btn_save.setStyleSheet("\n"
                                         "\n"
                                         "*{\n"
                                         "border-radius:10px;\n"
                                         "background-color: transparent ;\n"
                                         "\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "background-color: rgb(55, 55, 55);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton{\n"
                                         "border: 1px solid  transparent;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:pressed \n"
                                         "{\n"
                                         " border: 2px inset    rgb(255, 255, 255);\n"
                                         "background-color: #333;\n"
                                         "}")
        self.note_btn_save.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/images/Images/saveb.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.note_btn_save.setIcon(icon7)
        self.note_btn_save.setFlat(True)
        self.note_btn_save.setObjectName("note_btn_save")
        self.line_27 = QtWidgets.QFrame(self.tab_2)
        self.line_27.setGeometry(QtCore.QRect(1310, 0, 3, 856))
        self.line_27.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_27.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_27.setObjectName("line_27")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/images/Images/note.png"), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        icon8.addPixmap(QtGui.QPixmap(":/images/Images/note.png"), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self.tabWidget.addTab(self.tab_2, icon8, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.line_13 = QtWidgets.QFrame(self.tab_4)
        self.line_13.setGeometry(QtCore.QRect(0, 0, 1313, 2))
        self.line_13.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_13.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_13.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_13.setObjectName("line_13")
        self.toolBox = QtWidgets.QToolBox(self.tab_4)
        self.toolBox.setGeometry(QtCore.QRect(2, 3, 1307, 852))
        self.toolBox.setStyleSheet("*{\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "    \n"
                                   "font: 75 12pt \"Bahnschrift\";\n"
                                   "border-width: 0px;\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "QToolBox::tab:selected {\n"
                                   "background: qlineargradient(spread:pad, x1:0.423, y1:0.625, x2:0.99005, "
                                   "y2:0.188, stop:0 rgba(124, 119, 119, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                   "color: rgb(0, 0, 0);\n"
                                   "}\n"
                                   "\n"
                                   "QToolBox::tab{\n"
                                   "background: rgb(88,88, 88);\n"
                                   "\n"
                                   "}")
        self.toolBox.setObjectName("toolBox")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setGeometry(QtCore.QRect(0, 0, 1307, 774))
        self.page_3.setObjectName("page_3")
        self.historical_data_graph_frame = QtWidgets.QFrame(self.page_3)
        self.historical_data_graph_frame.setGeometry(QtCore.QRect(40, 140, 1058, 561))
        self.historical_data_graph_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.historical_data_graph_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.historical_data_graph_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.historical_data_graph_frame.setObjectName("historical_data_graph_frame")
        self.comboBox1_historical_data = QtWidgets.QComboBox(self.page_3)
        self.comboBox1_historical_data.setGeometry(QtCore.QRect(1100, 50, 161, 22))
        self.comboBox1_historical_data.setStyleSheet(
            "color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.373134 rgba(255, 255, 255, 255));\n"
            "\n"
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.097, "
            "stop:0.771144 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
            "color: rgb(255, 255, 255);\n"
            "background-color: rgb(0, 0, 0);\n"
            "font: 11pt \"Bahnschrift\";")
        self.comboBox1_historical_data.setObjectName("comboBox1_historical_data")
        self.comboBox1_historical_data.addItem("")
        self.comboBox1_historical_data.addItem("")
        self.comboBox1_historical_data.addItem("")
        self.label_18 = QtWidgets.QLabel(self.page_3)
        self.label_18.setGeometry(QtCore.QRect(40, 110, 1058, 31))
        self.label_18.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                    "font: 11pt \"Bahnschrift\";")
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.historical_data_year_label = QtWidgets.QLabel(self.page_3)
        self.historical_data_year_label.setGeometry(QtCore.QRect(40, 80, 91, 35))
        self.historical_data_year_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                                      "color: rgb(255, 255, 255);\n"
                                                      "font: 14pt \"Bahnschrift\";\n"
                                                      "border-radius:8px;")
        self.historical_data_year_label.setAlignment(QtCore.Qt.AlignCenter)
        self.historical_data_year_label.setObjectName("historical_data_year_label")
        self.listWidget_btc_historical_data = QtWidgets.QListWidget(self.page_3)
        self.listWidget_btc_historical_data.setGeometry(QtCore.QRect(1100, 110, 161, 591))
        self.listWidget_btc_historical_data.setStyleSheet("QListView {\n"
                                                          "   show-decoration-selected: 1;\n"
                                                          "selection-color: white;\n"
                                                          "    selection-background-color: rgb(132,88, 0);\n"
                                                          "font: 11pt \"Bahnschrift\";\n"
                                                          "color: rgb(255, 255, 255);\n"
                                                          "background: rgb(0, 0, 0);\n"
                                                          "    \n"
                                                          "}\n"
                                                          "\n"
                                                          "QListView::item:selected:active:hover{\n"
                                                          "    background-color:rgb(211, 211, 211); \n"
                                                          "    color: black;\n"
                                                          "}\n"
                                                          "QListView::item:selected:active:!hover{\n"
                                                          "     background-color: rgb(211, 211, 211); \n"
                                                          "   \n"
                                                          "    color: rgb(0, 0, 0);\n"
                                                          "}\n"
                                                          "QListView::item:selected:!active{\n"
                                                          "    background-color:rgb(163, 163, 163); \n"
                                                          "   \n"
                                                          "    color: rgb(0, 0, 0);\n"
                                                          "}\n"
                                                          "QListView::item:!selected:hover{ \n"
                                                          " background-color:rgb(198, 132, 0); \n"
                                                          "  color: rgb(255, 255, 255);\n"
                                                          " color: rgb(0, 0, 0);\n"
                                                          "}\n"
                                                          "\n"
                                                          "QScrollBar:vertical {              \n"
                                                          "  border: none;\n"
                                                          "  background:rgb(0, 0, 0);\n"
                                                          "  width:8px;\n"
                                                          "  margin: 0px 0px 0px 0px;\n"
                                                          "        }\n"
                                                          "QScrollBar::handle:vertical {\n"
                                                          "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.820896 rgba(200, 117, 17, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                                          "            min-height: 0px;\n"
                                                          "        }\n"
                                                          "QScrollBar::add-line:vertical {\n"
                                                          "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                                          "            stop: 0 rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));\n"
                                                          "\n"
                                                          "            height: 0px;\n"
                                                          "            subcontrol-position: bottom;\n"
                                                          "            subcontrol-origin: margin;\n"
                                                          "        }\n"
                                                          "QScrollBar::sub-line:vertical {\n"
                                                          "            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n"
                                                          "            stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));\n"
                                                          "            height: 0 px;\n"
                                                          "            subcontrol-position: top;\n"
                                                          "            subcontrol-origin: margin;\n"
                                                          "        }\n"
                                                          "\n"
                                                          "QScrollBar::down-arrow:vertical {\n"
                                                          "                        /*image:url(:/images/Images/open-label.png);*/\n"
                                                          "                        height: 40px; \n"
                                                          "                        width: 40px                              \n"
                                                          "                      }\n"
                                                          "\n"
                                                          "")
        self.listWidget_btc_historical_data.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.listWidget_btc_historical_data.setFrameShadow(QtWidgets.QFrame.Plain)
        self.listWidget_btc_historical_data.setLineWidth(1)
        self.listWidget_btc_historical_data.setIconSize(QtCore.QSize(0, 0))
        self.listWidget_btc_historical_data.setTextElideMode(QtCore.Qt.ElideNone)
        self.listWidget_btc_historical_data.setMovement(QtWidgets.QListView.Static)
        self.listWidget_btc_historical_data.setProperty("isWrapping", False)
        self.listWidget_btc_historical_data.setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget_btc_historical_data.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget_btc_historical_data.setViewMode(QtWidgets.QListView.ListMode)
        self.listWidget_btc_historical_data.setModelColumn(0)
        self.listWidget_btc_historical_data.setUniformItemSizes(False)
        self.listWidget_btc_historical_data.setWordWrap(True)
        self.listWidget_btc_historical_data.setSelectionRectVisible(True)
        self.listWidget_btc_historical_data.setObjectName("listWidget_btc_historical_data")
        item = QtWidgets.QListWidgetItem()
        self.listWidget_btc_historical_data.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_btc_historical_data.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_btc_historical_data.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.listWidget_btc_historical_data.addItem(item)
        self.line_39 = QtWidgets.QFrame(self.page_3)
        self.line_39.setGeometry(QtCore.QRect(1100, 110, 2, 591))
        self.line_39.setStyleSheet("\n"
                                   "background-color: rgb(184, 184, 0);")
        self.line_39.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line_39.setLineWidth(0)
        self.line_39.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_39.setObjectName("line_39")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/images/Images/icons8-candlestick-chart-16.png"), QtGui.QIcon.Normal,
                        QtGui.QIcon.On)
        self.toolBox.addItem(self.page_3, icon9, "")
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setGeometry(QtCore.QRect(0, 0, 1307, 774))
        self.page_4.setObjectName("page_4")
        self.stackedWidget = QtWidgets.QStackedWidget(self.page_4)
        self.stackedWidget.setGeometry(QtCore.QRect(20, 0, 1251, 751))
        self.stackedWidget.setStyleSheet("*{\n"
                                         "color: rgb(255, 255, 255);\n"
                                         "background: transparent;\n"
                                         "    \n"
                                         "}\n"
                                         "\n"
                                         "")
        self.stackedWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.stackedWidget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.BH_jan_frame = QtWidgets.QFrame(self.page_2)
        self.BH_jan_frame.setGeometry(QtCore.QRect(10, 80, 291, 191))
        self.BH_jan_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_jan_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_jan_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_jan_frame.setObjectName("BH_jan_frame")
        self.BH_may_frame = QtWidgets.QFrame(self.page_2)
        self.BH_may_frame.setGeometry(QtCore.QRect(10, 310, 291, 191))
        self.BH_may_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_may_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_may_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_may_frame.setObjectName("BH_may_frame")
        self.BH_sep_frame = QtWidgets.QFrame(self.page_2)
        self.BH_sep_frame.setGeometry(QtCore.QRect(10, 550, 291, 191))
        self.BH_sep_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_sep_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_sep_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_sep_frame.setObjectName("BH_sep_frame")
        self.BH_feb_frame = QtWidgets.QFrame(self.page_2)
        self.BH_feb_frame.setGeometry(QtCore.QRect(320, 80, 291, 191))
        self.BH_feb_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_feb_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_feb_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_feb_frame.setObjectName("BH_feb_frame")
        self.BH_mar_frame = QtWidgets.QFrame(self.page_2)
        self.BH_mar_frame.setGeometry(QtCore.QRect(630, 80, 291, 191))
        self.BH_mar_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_mar_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_mar_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_mar_frame.setObjectName("BH_mar_frame")
        self.BH_june_frame = QtWidgets.QFrame(self.page_2)
        self.BH_june_frame.setGeometry(QtCore.QRect(320, 310, 291, 191))
        self.BH_june_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                         "border-radius:8px;")
        self.BH_june_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_june_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_june_frame.setObjectName("BH_june_frame")
        self.BH_july_frame = QtWidgets.QFrame(self.page_2)
        self.BH_july_frame.setGeometry(QtCore.QRect(630, 310, 291, 191))
        self.BH_july_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                         "border-radius:8px;")
        self.BH_july_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_july_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_july_frame.setObjectName("BH_july_frame")
        self.BH_oct_frame = QtWidgets.QFrame(self.page_2)
        self.BH_oct_frame.setGeometry(QtCore.QRect(320, 550, 291, 191))
        self.BH_oct_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_oct_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_oct_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_oct_frame.setObjectName("BH_oct_frame")
        self.BH_nov_frame = QtWidgets.QFrame(self.page_2)
        self.BH_nov_frame.setGeometry(QtCore.QRect(630, 550, 291, 191))
        self.BH_nov_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_nov_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_nov_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_nov_frame.setObjectName("BH_nov_frame")
        self.BH_apr_frame = QtWidgets.QFrame(self.page_2)
        self.BH_apr_frame.setGeometry(QtCore.QRect(940, 80, 291, 191))
        self.BH_apr_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_apr_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_apr_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_apr_frame.setObjectName("BH_apr_frame")
        self.BH_aug_frame = QtWidgets.QFrame(self.page_2)
        self.BH_aug_frame.setGeometry(QtCore.QRect(940, 310, 291, 191))
        self.BH_aug_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_aug_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_aug_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_aug_frame.setObjectName("BH_aug_frame")
        self.BH_dec_frame = QtWidgets.QFrame(self.page_2)
        self.BH_dec_frame.setGeometry(QtCore.QRect(940, 550, 291, 191))
        self.BH_dec_frame.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "border-radius:8px;")
        self.BH_dec_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.BH_dec_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.BH_dec_frame.setObjectName("BH_dec_frame")
        self.BH_jan_label = QtWidgets.QLabel(self.page_2)
        self.BH_jan_label.setGeometry(QtCore.QRect(10, 54, 131, 36))
        self.BH_jan_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_jan_label.setObjectName("BH_jan_label")
        self.BH_feb_label = QtWidgets.QLabel(self.page_2)
        self.BH_feb_label.setGeometry(QtCore.QRect(320, 54, 131, 36))
        self.BH_feb_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_feb_label.setObjectName("BH_feb_label")
        self.BH_mar_label = QtWidgets.QLabel(self.page_2)
        self.BH_mar_label.setGeometry(QtCore.QRect(630, 54, 131, 36))
        self.BH_mar_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_mar_label.setObjectName("BH_mar_label")
        self.BH_apr_label = QtWidgets.QLabel(self.page_2)
        self.BH_apr_label.setGeometry(QtCore.QRect(940, 54, 131, 36))
        self.BH_apr_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_apr_label.setObjectName("BH_apr_label")
        self.BH_may_label = QtWidgets.QLabel(self.page_2)
        self.BH_may_label.setGeometry(QtCore.QRect(10, 284, 131, 36))
        self.BH_may_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_may_label.setObjectName("BH_may_label")
        self.BH_june_label = QtWidgets.QLabel(self.page_2)
        self.BH_june_label.setGeometry(QtCore.QRect(320, 284, 131, 36))
        self.BH_june_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                         "color: rgb(255, 255, 255);\n"
                                         "font: 10pt \"Bahnschrift\";\n"
                                         "border-radius:8px;")
        self.BH_june_label.setObjectName("BH_june_label")
        self.BH_july_label = QtWidgets.QLabel(self.page_2)
        self.BH_july_label.setGeometry(QtCore.QRect(630, 284, 131, 36))
        self.BH_july_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                         "color: rgb(255, 255, 255);\n"
                                         "font: 10pt \"Bahnschrift\";\n"
                                         "border-radius:8px;")
        self.BH_july_label.setObjectName("BH_july_label")
        self.BH_aug_label = QtWidgets.QLabel(self.page_2)
        self.BH_aug_label.setGeometry(QtCore.QRect(940, 284, 131, 36))
        self.BH_aug_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_aug_label.setObjectName("BH_aug_label")
        self.BH_sep_label = QtWidgets.QLabel(self.page_2)
        self.BH_sep_label.setGeometry(QtCore.QRect(10, 524, 131, 36))
        self.BH_sep_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_sep_label.setObjectName("BH_sep_label")
        self.BH_oct_label = QtWidgets.QLabel(self.page_2)
        self.BH_oct_label.setGeometry(QtCore.QRect(320, 524, 131, 36))
        self.BH_oct_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_oct_label.setObjectName("BH_oct_label")
        self.BH_nov_label = QtWidgets.QLabel(self.page_2)
        self.BH_nov_label.setGeometry(QtCore.QRect(630, 524, 131, 36))
        self.BH_nov_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_nov_label.setObjectName("BH_nov_label")
        self.BH_dec_label = QtWidgets.QLabel(self.page_2)
        self.BH_dec_label.setGeometry(QtCore.QRect(940, 524, 131, 36))
        self.BH_dec_label.setStyleSheet("background-color: rgb(0, 0, 0);\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "font: 10pt \"Bahnschrift\";\n"
                                        "border-radius:8px;")
        self.BH_dec_label.setObjectName("BH_dec_label")
        self.comboBox2_historical_data = QtWidgets.QComboBox(self.page_2)
        self.comboBox2_historical_data.setGeometry(QtCore.QRect(1076, 8, 111, 21))
        self.comboBox2_historical_data.setStyleSheet(
            "color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.373134 rgba(255, 255, 255, 255));\n"
            "\n"
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
            "y2:0.097, stop:0.771144 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
            "color: rgb(255, 255, 255);\n"
            "background-color: rgb(0, 0, 0);\n"
            "font: 11pt \"Bahnschrift\";")
        self.comboBox2_historical_data.setObjectName("comboBox2_historical_data")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.comboBox2_historical_data.addItem("")
        self.label_76 = QtWidgets.QLabel(self.page_2)
        self.label_76.setGeometry(QtCore.QRect(1020, 0, 41, 31))
        self.label_76.setStyleSheet("background: transparent;\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_76.setObjectName("label_76")
        self.stackedWidget.addWidget(self.page_2)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/images/Images/icons8-active-directory-26 (1).png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.toolBox.addItem(self.page_4, icon10, "")
        self.line_26 = QtWidgets.QFrame(self.tab_4)
        self.line_26.setGeometry(QtCore.QRect(1310, 0, 3, 856))
        self.line_26.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_26.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_26.setObjectName("line_26")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/images/Images/icons8-candlestick-chart-26.png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.tabWidget.addTab(self.tab_4, icon11, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.about_btn = QtWidgets.QPushButton(self.tab_5)
        self.about_btn.setGeometry(QtCore.QRect(470, 10, 91, 31))
        self.about_btn.setStyleSheet("\n"
                                     "\n"
                                     "*{\n"
                                     "color:rgb(1, 1, 1);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton{\n"
                                     "border: 1px solid rgb(255, 170, 0);\n"
                                     "background:  rgb(140, 140, 140);\n"
                                     "border-radius:10px;\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                     "}\n"
                                     "\n"
                                     "\n"
                                     "QPushButton:hover{\n"
                                     "\n"
                                     "    color: rgb(255, 255, 255);\n"
                                     "background-color: rgb(83, 83, 83);\n"
                                     "background:qlineargradient(spread:pad, x1:0.443, y1:0.670545, x2:0, y2:0.801, stop:0 rgba(0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n"
                                     "border-radius:10px;\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:pressed \n"
                                     "{\n"
                                     " border: 2px inset    rgb(255, 170, 0);\n"
                                     "background-color: #333;\n"
                                     "}")
        self.about_btn.setObjectName("about_btn")
        self.import_btn = QtWidgets.QPushButton(self.tab_5)
        self.import_btn.setGeometry(QtCore.QRect(20, 160, 101, 31))
        self.import_btn.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "\n"
                                      "    \n"
                                      "background-color: rgb(100, 100, 100);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(90, 90, 90);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(66, 66, 66);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/images/Images/icons8-data-backup-26 (1).png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.import_btn.setIcon(icon12)
        self.import_btn.setObjectName("import_btn")
        self.progressBar_download = QtWidgets.QProgressBar(self.tab_5)
        self.progressBar_download.setGeometry(QtCore.QRect(130, 80, 301, 31))
        self.progressBar_download.setStyleSheet("*{font: 9pt \"MV Boli\";\n"
                                                "color: rgb(255, 255, 255);}\n"
                                                "\n"
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
                                                "    background-color:rgb(222, 148, 0);\n"
                                                "    width: 10px;\n"
                                                "    margin:1px;\n"
                                                "}\n"
                                                "\n"
                                                "")
        self.progressBar_download.setProperty("value", 20)
        self.progressBar_download.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar_download.setTextVisible(True)
        self.progressBar_download.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar_download.setInvertedAppearance(False)
        self.progressBar_download.setObjectName("progressBar_download")
        self.label_61 = QtWidgets.QLabel(self.tab_5)
        self.label_61.setGeometry(QtCore.QRect(20, 30, 291, 21))
        self.label_61.setStyleSheet("background: transparent;")
        self.label_61.setObjectName("label_61")
        self.download_btn = QtWidgets.QPushButton(self.tab_5)
        self.download_btn.setGeometry(QtCore.QRect(20, 80, 101, 31))
        self.download_btn.setStyleSheet("*{\n"
                                        "color: rgb(211, 211, 211);\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "\n"
                                        "    \n"
                                        "background-color: rgb(100, 100, 100);\n"
                                        "\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton{\n"
                                        "border: 1px solid  #333;\n"
                                        "background:  rgb(90, 90, 90);\n"
                                        "border-radius:10px;\n"
                                        "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                        "}\n"
                                        "\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "\n"
                                        "color: rgb(225, 255, 255);\n"
                                        "    background-color: rgb(66, 66, 66);\n"
                                        "border-radius:10px;\n"
                                        "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed \n"
                                        "{\n"
                                        " border: 2px inset   rgb(225, 225, 255);\n"
                                        "background-color: #333;\n"
                                        "}")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/images/Images/icons8-download-26.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.download_btn.setIcon(icon13)
        self.download_btn.setObjectName("download_btn")
        self.progressBar_import = QtWidgets.QProgressBar(self.tab_5)
        self.progressBar_import.setGeometry(QtCore.QRect(130, 160, 301, 31))
        self.progressBar_import.setStyleSheet("*{font: 9pt \"MV Boli\";\n"
                                              "color: rgb(255, 255, 255);}\n"
                                              "\n"
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
                                              "    background-color:rgb(222, 148, 0);\n"
                                              "    width: 10px;\n"
                                              "    margin:1px;\n"
                                              "}\n"
                                              "\n"
                                              "")
        self.progressBar_import.setProperty("value", 20)
        self.progressBar_import.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar_import.setTextVisible(True)
        self.progressBar_import.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar_import.setInvertedAppearance(False)
        self.progressBar_import.setObjectName("progressBar_import")
        self.notify_input = QtWidgets.QLineEdit(self.tab_5)
        self.notify_input.setGeometry(QtCore.QRect(140, 275, 131, 21))
        self.notify_input.setStyleSheet("\n"
                                        "QLineEdit{\n"
                                        "border-radius:10px;\n"
                                        "background-color: rgb(240, 240, 240);\n"
                                        "    color: rgb(0, 0, 0);\n"
                                        "}")
        self.notify_input.setAlignment(QtCore.Qt.AlignCenter)
        self.notify_input.setObjectName("notify_input")
        self.notify_btn = QtWidgets.QPushButton(self.tab_5)
        self.notify_btn.setGeometry(QtCore.QRect(20, 270, 101, 31))
        self.notify_btn.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "\n"
                                      "    \n"
                                      "background-color: rgb(100, 100, 100);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(90, 90, 90);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(66, 66, 66);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(":/images/Images/icons8-notification-26.png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.notify_btn.setIcon(icon14)
        self.notify_btn.setObjectName("notify_btn")
        self.line_14 = QtWidgets.QFrame(self.tab_5)
        self.line_14.setGeometry(QtCore.QRect(0, 0, 1313, 2))
        self.line_14.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_14.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_14.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_14.setObjectName("line_14")
        self.line_16 = QtWidgets.QFrame(self.tab_5)
        self.line_16.setGeometry(QtCore.QRect(569, 0, 3, 327))
        self.line_16.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_16.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_16.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_16.setObjectName("line_16")
        self.resut_output_0 = QtWidgets.QLabel(self.tab_5)
        self.resut_output_0.setGeometry(QtCore.QRect(600, 23, 691, 51))
        self.resut_output_0.setStyleSheet("\n"
                                          "\n"
                                          "background-color: rgba(150, 150, 150,100);\n"
                                          "font: 12pt \"Sylfaen\";\n"
                                          "\n"
                                          "color: rgb(255, 170, 0);\n"
                                          "\n"
                                          "")
        self.resut_output_0.setFrameShape(QtWidgets.QFrame.Box)
        self.resut_output_0.setFrameShadow(QtWidgets.QFrame.Raised)
        self.resut_output_0.setLineWidth(1)
        self.resut_output_0.setAlignment(QtCore.Qt.AlignCenter)
        self.resut_output_0.setWordWrap(True)
        self.resut_output_0.setObjectName("resut_output_0")
        self.radioButton_ordersize = QtWidgets.QRadioButton(self.tab_5)
        self.radioButton_ordersize.setGeometry(QtCore.QRect(610, 150, 121, 21))
        self.radioButton_ordersize.setStyleSheet("background: transparent;\n"
                                                 "font: 10pt \"Bahnschrift\";")
        self.radioButton_ordersize.setObjectName("radioButton_ordersize")
        self.radioButton_risk = QtWidgets.QRadioButton(self.tab_5)
        self.radioButton_risk.setGeometry(QtCore.QRect(770, 150, 111, 21))
        self.radioButton_risk.setStyleSheet("background: transparent;\n"
                                            "font: 10pt \"Bahnschrift\";")
        self.radioButton_risk.setObjectName("radioButton_risk")
        self.radioButton_stop = QtWidgets.QRadioButton(self.tab_5)
        self.radioButton_stop.setGeometry(QtCore.QRect(910, 150, 95, 21))
        self.radioButton_stop.setStyleSheet("background: transparent;\n"
                                            "font: 10pt \"Bahnschrift\";")
        self.radioButton_stop.setObjectName("radioButton_stop")
        self.input_entry = QtWidgets.QLineEdit(self.tab_5)
        self.input_entry.setGeometry(QtCore.QRect(710, 220, 201, 21))
        self.input_entry.setStyleSheet("\n"
                                       "QLineEdit{\n"
                                       "border-radius:10px;\n"
                                       "background-color: rgb(240, 240, 240);\n"
                                       "    color: rgb(0, 0, 0);\n"
                                       "}")
        self.input_entry.setText("")
        self.input_entry.setAlignment(QtCore.Qt.AlignCenter)
        self.input_entry.setObjectName("input_entry")
        self.input_ordersize = QtWidgets.QLineEdit(self.tab_5)
        self.input_ordersize.setGeometry(QtCore.QRect(710, 270, 201, 21))
        self.input_ordersize.setStyleSheet("\n"
                                           "QLineEdit{\n"
                                           "border-radius:10px;\n"
                                           "background-color: rgb(240, 240, 240);\n"
                                           "    color: rgb(0, 0, 0);\n"
                                           "}")
        self.input_ordersize.setText("")
        self.input_ordersize.setAlignment(QtCore.Qt.AlignCenter)
        self.input_ordersize.setObjectName("input_ordersize")
        self.input_risk_right = QtWidgets.QLineEdit(self.tab_5)
        self.input_risk_right.setGeometry(QtCore.QRect(1030, 220, 201, 21))
        self.input_risk_right.setStyleSheet("\n"
                                            "QLineEdit{\n"
                                            "border-radius:10px;\n"
                                            "background-color: rgb(240, 240, 240);\n"
                                            "    color: rgb(0, 0, 0);\n"
                                            "}")
        self.input_risk_right.setText("")
        self.input_risk_right.setAlignment(QtCore.Qt.AlignCenter)
        self.input_risk_right.setObjectName("input_risk_right")
        self.input_stop = QtWidgets.QLineEdit(self.tab_5)
        self.input_stop.setGeometry(QtCore.QRect(1030, 270, 201, 21))
        self.input_stop.setStyleSheet("\n"
                                      "QLineEdit{\n"
                                      "border-radius:10px;\n"
                                      "background-color: rgb(240, 240, 240);\n"
                                      "    color: rgb(0, 0, 0);\n"
                                      "}")
        self.input_stop.setText("")
        self.input_stop.setAlignment(QtCore.Qt.AlignCenter)
        self.input_stop.setObjectName("input_stop")
        self.label_82 = QtWidgets.QLabel(self.tab_5)
        self.label_82.setGeometry(QtCore.QRect(610, 220, 55, 21))
        self.label_82.setStyleSheet("background: transparent;\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_82.setObjectName("label_82")
        self.label_83 = QtWidgets.QLabel(self.tab_5)
        self.label_83.setGeometry(QtCore.QRect(610, 270, 81, 21))
        self.label_83.setStyleSheet("background: transparent;\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_83.setObjectName("label_83")
        self.label_84 = QtWidgets.QLabel(self.tab_5)
        self.label_84.setGeometry(QtCore.QRect(950, 220, 55, 21))
        self.label_84.setStyleSheet("background: transparent;\n"
                                    "\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_84.setObjectName("label_84")
        self.label_85 = QtWidgets.QLabel(self.tab_5)
        self.label_85.setGeometry(QtCore.QRect(950, 270, 55, 21))
        self.label_85.setStyleSheet("background: transparent;\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_85.setObjectName("label_85")
        self.Calc_btn_1 = QtWidgets.QPushButton(self.tab_5)
        self.Calc_btn_1.setGeometry(QtCore.QRect(871, 337, 141, 31))
        self.Calc_btn_1.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "\n"
                                      "    \n"
                                      "background-color: rgb(100, 100, 100);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(90, 90, 90);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(66, 66, 66);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        icon15 = QtGui.QIcon()
        icon15.addPixmap(QtGui.QPixmap(":/images/Images/icons8-calculator-26.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Calc_btn_1.setIcon(icon15)
        self.Calc_btn_1.setObjectName("Calc_btn_1")
        self.convert_input = QtWidgets.QLineEdit(self.tab_5)
        self.convert_input.setGeometry(QtCore.QRect(710, 786, 201, 21))
        self.convert_input.setStyleSheet("\n"
                                         "QLineEdit{\n"
                                         "border-radius:10px;\n"
                                         "background-color: rgb(240, 240, 240);\n"
                                         "    color: rgb(0, 0, 0);\n"
                                         "}")
        self.convert_input.setText("")
        self.convert_input.setAlignment(QtCore.Qt.AlignCenter)
        self.convert_input.setObjectName("convert_input")
        self.radioButton_Riskpercentage_left = QtWidgets.QRadioButton(self.tab_5)
        self.radioButton_Riskpercentage_left.setGeometry(QtCore.QRect(610, 590, 149, 20))
        self.radioButton_Riskpercentage_left.setStyleSheet("background: transparent;\n"
                                                           "font: 10pt \"Bahnschrift\";")
        self.radioButton_Riskpercentage_left.setObjectName("radioButton_Riskpercentage_left")
        self.Radiobtn_Risksato_left = QtWidgets.QRadioButton(self.tab_5)
        self.Radiobtn_Risksato_left.setGeometry(QtCore.QRect(770, 590, 131, 20))
        self.Radiobtn_Risksato_left.setStyleSheet("background: transparent;\n"
                                                  "font: 10pt \"Bahnschrift\";")
        self.Radiobtn_Risksato_left.setObjectName("Radiobtn_Risksato_left")
        self.label_80 = QtWidgets.QLabel(self.tab_5)
        self.label_80.setGeometry(QtCore.QRect(610, 650, 41, 21))
        self.label_80.setStyleSheet("background: transparent;\n"
                                    "\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_80.setObjectName("label_80")
        self.label_81 = QtWidgets.QLabel(self.tab_5)
        self.label_81.setGeometry(QtCore.QRect(950, 650, 51, 21))
        self.label_81.setStyleSheet("background: transparent;\n"
                                    "\n"
                                    "font: 12pt \"Bahnschrift\";")
        self.label_81.setObjectName("label_81")
        self.input_Calc_Risk_left = QtWidgets.QLineEdit(self.tab_5)
        self.input_Calc_Risk_left.setGeometry(QtCore.QRect(710, 650, 201, 21))
        self.input_Calc_Risk_left.setStyleSheet("\n"
                                                "QLineEdit{\n"
                                                "border-radius:10px;\n"
                                                "background-color: rgb(240, 240, 240);\n"
                                                "    color: rgb(0, 0, 0);\n"
                                                "}")
        self.input_Calc_Risk_left.setText("")
        self.input_Calc_Risk_left.setAlignment(QtCore.Qt.AlignCenter)
        self.input_Calc_Risk_left.setObjectName("input_Calc_Risk_left")
        self.input_Calc_Profit_left = QtWidgets.QLineEdit(self.tab_5)
        self.input_Calc_Profit_left.setGeometry(QtCore.QRect(1030, 650, 201, 21))
        self.input_Calc_Profit_left.setStyleSheet("\n"
                                                  "QLineEdit{\n"
                                                  "border-radius:10px;\n"
                                                  "background-color: rgb(240, 240, 240);\n"
                                                  "    color: rgb(0, 0, 0);\n"
                                                  "}")
        self.input_Calc_Profit_left.setText("")
        self.input_Calc_Profit_left.setAlignment(QtCore.Qt.AlignCenter)
        self.input_Calc_Profit_left.setObjectName("input_Calc_Profit_left")
        self.label_86 = QtWidgets.QLabel(self.tab_5)
        self.label_86.setGeometry(QtCore.QRect(20, 220, 261, 21))
        self.label_86.setStyleSheet("background: transparent;")
        self.label_86.setObjectName("label_86")
        self.pushButton_10 = QtWidgets.QPushButton(self.tab_5)
        self.pushButton_10.setEnabled(False)
        self.pushButton_10.setGeometry(QtCore.QRect(270, 271, 31, 31))
        self.pushButton_10.setAutoFillBackground(False)
        self.pushButton_10.setStyleSheet("background-image: url(:/images/Images/S.png);\n"
                                         "\n"
                                         "background-color: transparent;")
        self.pushButton_10.setText("")
        self.pushButton_10.setCheckable(False)
        self.pushButton_10.setChecked(False)
        self.pushButton_10.setFlat(True)
        self.pushButton_10.setObjectName("pushButton_10")
        self.line_17 = QtWidgets.QFrame(self.tab_5)
        self.line_17.setGeometry(QtCore.QRect(593, 351, 271, 3))
        self.line_17.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_17.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_17.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_17.setObjectName("line_17")
        self.line_18 = QtWidgets.QFrame(self.tab_5)
        self.line_18.setGeometry(QtCore.QRect(1018, 351, 296, 3))
        self.line_18.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_18.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_18.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_18.setObjectName("line_18")
        self.line_19 = QtWidgets.QFrame(self.tab_5)
        self.line_19.setGeometry(QtCore.QRect(1310, 0, 3, 856))
        self.line_19.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_19.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_19.setObjectName("line_19")
        self.label_3 = QtWidgets.QLabel(self.tab_5)
        self.label_3.setGeometry(QtCore.QRect(600, 420, 461, 31))
        self.label_3.setStyleSheet("background-color: transparent;\n"
                                   "font: 12pt \"Sylfaen\";\n"
                                   "\n"
                                   "\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "\n"
                                   "")
        self.label_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_3.setLineWidth(1)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.tab_5)
        self.label_2.setGeometry(QtCore.QRect(600, 470, 431, 31))
        self.label_2.setStyleSheet("background-color: transparent;\n"
                                   "font: 12pt \"Sylfaen\";\n"
                                   "\n"
                                   "\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "\n"
                                   "")
        self.label_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label_2.setLineWidth(1)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.tab_5)
        self.label.setGeometry(QtCore.QRect(600, 520, 461, 31))
        self.label.setStyleSheet("background-color: transparent;\n"
                                 "font: 12pt \"Sylfaen\";\n"
                                 "\n"
                                 "\n"
                                 "color: rgb(255, 255, 255);\n"
                                 "\n"
                                 "")
        self.label.setFrameShape(QtWidgets.QFrame.Panel)
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label.setLineWidth(1)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.resut_output_1 = QtWidgets.QLabel(self.tab_5)
        self.resut_output_1.setGeometry(QtCore.QRect(1120, 420, 171, 31))
        self.resut_output_1.setStyleSheet("\n"
                                          "\n"
                                          "background-color: rgba(150, 150, 150,100);\n"
                                          "font: 12pt \"Sylfaen\";\n"
                                          "\n"
                                          "color: rgb(255, 170, 0);\n"
                                          "\n"
                                          "\n"
                                          "")
        self.resut_output_1.setFrameShape(QtWidgets.QFrame.Box)
        self.resut_output_1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.resut_output_1.setLineWidth(1)
        self.resut_output_1.setAlignment(QtCore.Qt.AlignCenter)
        self.resut_output_1.setWordWrap(True)
        self.resut_output_1.setObjectName("resut_output_1")
        self.resut_output_2 = QtWidgets.QLabel(self.tab_5)
        self.resut_output_2.setGeometry(QtCore.QRect(1120, 470, 171, 31))
        self.resut_output_2.setStyleSheet("\n"
                                          "\n"
                                          "background-color: rgba(150, 150, 150,100);\n"
                                          "font: 12pt \"Sylfaen\";\n"
                                          "\n"
                                          "color: rgb(255, 170, 0);\n"
                                          "\n"
                                          "")
        self.resut_output_2.setFrameShape(QtWidgets.QFrame.Box)
        self.resut_output_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.resut_output_2.setLineWidth(1)
        self.resut_output_2.setAlignment(QtCore.Qt.AlignCenter)
        self.resut_output_2.setWordWrap(True)
        self.resut_output_2.setObjectName("resut_output_2")
        self.resut_output_3 = QtWidgets.QLabel(self.tab_5)
        self.resut_output_3.setGeometry(QtCore.QRect(1120, 520, 171, 31))
        self.resut_output_3.setStyleSheet("\n"
                                          "\n"
                                          "background-color: rgba(150, 150, 150,100);\n"
                                          "font: 12pt \"Sylfaen\";\n"
                                          "\n"
                                          "color: rgb(255, 170, 0);\n"
                                          "\n"
                                          "")
        self.resut_output_3.setFrameShape(QtWidgets.QFrame.Box)
        self.resut_output_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.resut_output_3.setLineWidth(1)
        self.resut_output_3.setAlignment(QtCore.Qt.AlignCenter)
        self.resut_output_3.setWordWrap(True)
        self.resut_output_3.setObjectName("resut_output_3")
        self.Calc_btn_2 = QtWidgets.QPushButton(self.tab_5)
        self.Calc_btn_2.setGeometry(QtCore.QRect(871, 716, 141, 31))
        self.Calc_btn_2.setStyleSheet("*{\n"
                                      "color: rgb(211, 211, 211);\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "\n"
                                      "    \n"
                                      "background-color: rgb(100, 100, 100);\n"
                                      "\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton{\n"
                                      "border: 1px solid  #333;\n"
                                      "background:  rgb(90, 90, 90);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "\n"
                                      "QPushButton:hover{\n"
                                      "\n"
                                      "color: rgb(225, 255, 255);\n"
                                      "    background-color: rgb(66, 66, 66);\n"
                                      "border-radius:10px;\n"
                                      "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                      "}\n"
                                      "\n"
                                      "QPushButton:pressed \n"
                                      "{\n"
                                      " border: 2px inset   rgb(225, 225, 255);\n"
                                      "background-color: #333;\n"
                                      "}")
        self.Calc_btn_2.setIcon(icon15)
        self.Calc_btn_2.setObjectName("Calc_btn_2")
        self.line_20 = QtWidgets.QFrame(self.tab_5)
        self.line_20.setGeometry(QtCore.QRect(570, 374, 3, 483))
        self.line_20.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_20.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_20.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_20.setObjectName("line_20")
        self.line_21 = QtWidgets.QFrame(self.tab_5)
        self.line_21.setGeometry(QtCore.QRect(570, 730, 292, 3))
        self.line_21.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_21.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_21.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_21.setObjectName("line_21")
        self.line_22 = QtWidgets.QFrame(self.tab_5)
        self.line_22.setGeometry(QtCore.QRect(1020, 730, 292, 3))
        self.line_22.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_22.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_22.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_22.setObjectName("line_22")
        self.convert_output = QtWidgets.QLabel(self.tab_5)
        self.convert_output.setGeometry(QtCore.QRect(1010, 781, 251, 31))
        self.convert_output.setStyleSheet("\n"
                                          "\n"
                                          "background-color: rgba(150, 150, 150,100);\n"
                                          "font: 12pt \"Sylfaen\";\n"
                                          "\n"
                                          "color: rgb(255, 170, 0);\n"
                                          "\n"
                                          "")
        self.convert_output.setFrameShape(QtWidgets.QFrame.Box)
        self.convert_output.setFrameShadow(QtWidgets.QFrame.Raised)
        self.convert_output.setLineWidth(1)
        self.convert_output.setAlignment(QtCore.Qt.AlignCenter)
        self.convert_output.setWordWrap(True)
        self.convert_output.setObjectName("convert_output")
        self.label_87 = QtWidgets.QLabel(self.tab_5)
        self.label_87.setGeometry(QtCore.QRect(610, 784, 101, 21))
        self.label_87.setStyleSheet("background: transparent;")
        self.label_87.setObjectName("label_87")
        self.pushButton_12 = QtWidgets.QPushButton(self.tab_5)
        self.pushButton_12.setEnabled(False)
        self.pushButton_12.setGeometry(QtCore.QRect(540, 320, 61, 61))
        self.pushButton_12.setAutoFillBackground(False)
        self.pushButton_12.setStyleSheet("background-image: url(:/images/Images/icons8-fibonacci-circles-60.png);\n"
                                         "background-color: transparent;\n"
                                         "")
        self.pushButton_12.setText("")
        self.pushButton_12.setCheckable(False)
        self.pushButton_12.setChecked(False)
        self.pushButton_12.setFlat(True)
        self.pushButton_12.setObjectName("pushButton_12")
        self.label_62 = QtWidgets.QLabel(self.tab_5)
        self.label_62.setGeometry(QtCore.QRect(20, 360, 291, 31))
        self.label_62.setStyleSheet("background: transparent;")
        self.label_62.setObjectName("label_62")
        self.export_btn_2 = QtWidgets.QPushButton(self.tab_5)
        self.export_btn_2.setEnabled(True)
        self.export_btn_2.setGeometry(QtCore.QRect(230, 446, 111, 31))
        self.export_btn_2.setStyleSheet("*{\n"
                                        "color: rgb(211, 211, 211);\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "color: rgb(255, 255, 255);\n"
                                        "\n"
                                        "    \n"
                                        "background-color: rgb(100, 100, 100);\n"
                                        "\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton{\n"
                                        "border: 1px solid  #333;\n"
                                        "background:  rgb(90, 90, 90);\n"
                                        "border-radius:10px;\n"
                                        "font: 75 9pt \"MS Shell Dlg 2\";\n"
                                        "}\n"
                                        "\n"
                                        "\n"
                                        "QPushButton:hover{\n"
                                        "\n"
                                        "color: rgb(225, 255, 255);\n"
                                        "    background-color: rgb(66, 66, 66);\n"
                                        "border-radius:10px;\n"
                                        "font: 75 8pt \"MS Shell Dlg 2\";\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:pressed \n"
                                        "{\n"
                                        " border: 2px inset   rgb(225, 225, 255);\n"
                                        "background-color: #333;\n"
                                        "}")
        icon16 = QtGui.QIcon()
        icon16.addPixmap(QtGui.QPixmap(":/images/Images/icons8-download-from-the-cloud-100.png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.export_btn_2.setIcon(icon16)
        self.export_btn_2.setObjectName("export_btn_2")
        self.label_20 = QtWidgets.QLabel(self.tab_5)
        self.label_20.setGeometry(QtCore.QRect(20, 400, 331, 51))
        self.label_20.setStyleSheet("background: transparent;")
        self.label_20.setObjectName("label_20")
        self.line_23 = QtWidgets.QFrame(self.tab_5)
        self.line_23.setGeometry(QtCore.QRect(0, 351, 547, 3))
        self.line_23.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_23.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_23.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_23.setObjectName("line_23")
        self.line_24 = QtWidgets.QFrame(self.tab_5)
        self.line_24.setGeometry(QtCore.QRect(0, 460, 221, 3))
        self.line_24.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_24.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_24.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_24.setObjectName("line_24")
        self.line_25 = QtWidgets.QFrame(self.tab_5)
        self.line_25.setGeometry(QtCore.QRect(349, 460, 221, 3))
        self.line_25.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line_25.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_25.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_25.setObjectName("line_25")
        self.comboBox_backup = QtWidgets.QComboBox(self.tab_5)
        self.comboBox_backup.setGeometry(QtCore.QRect(450, 84, 91, 22))
        self.comboBox_backup.setStyleSheet(
            "color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.373134 rgba(255, 255, 255, 255));\n"
            "\n"
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:1 rgba(198, 132, 0, "
            "255));\n "
            "\n"
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.977, stop:0.761194 rgba("
            "204, 110, 0, 255), stop:0.99005 rgba(255, 255, 255, 255));\n "
            "\n"
            "color: rgb(0, 0, 0);\n"
            "background-color: rgba(150, 150, 150,100);\n"
            "font: 11pt \"Bahnschrift\";")
        self.comboBox_backup.setObjectName("comboBox_backup")
        self.comboBox_backup.addItem("")
        self.comboBox_backup.addItem("")
        self.comboBox_backup.addItem("")
        self.checkBox = QtWidgets.QCheckBox(self.tab_5)
        self.checkBox.setGeometry(QtCore.QRect(770, 100, 121, 20))
        self.checkBox.setStyleSheet("background: transparent;\n"
                                    "font: 10pt \"Bahnschrift\";")
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.tab_5)
        self.checkBox_2.setGeometry(QtCore.QRect(610, 100, 161, 20))
        self.checkBox_2.setStyleSheet("background: transparent;\n"
                                      "font: 10pt \"Bahnschrift\";")
        self.checkBox_2.setObjectName("checkBox_2")
        self.tabWidget.addTab(self.tab_5, icon15, "")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(281, 0, 5, 888))
        self.line.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.down_bar_label = QtWidgets.QLabel(Form)
        self.down_bar_label.setGeometry(QtCore.QRect(0, 888, 1599, 25))
        self.down_bar_label.setStyleSheet("background:  rgb(51, 51, 51);")
        self.down_bar_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.down_bar_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.down_bar_label.setLineWidth(1)
        self.down_bar_label.setMidLineWidth(0)
        self.down_bar_label.setIndent(20)
        self.down_bar_label.setObjectName("down_bar_label")
        self.frame_4 = QtWidgets.QFrame(Form)
        self.frame_4.setGeometry(QtCore.QRect(0, 0, 281, 888))
        self.frame_4.setStyleSheet("*{background-image: url(:/images/Images/profile_bg.png);\n"
                                   ";\n"
                                   "    background-image: url(:/images/Images/profile_bg.png);\n"
                                   "    \n"
                                   "    \n"
                                   "    background-image: url(:/images/Images/BG.png);\n"
                                   "\n"
                                   "}\n"
                                   "\n"
                                   "\n"
                                   "QLabel {\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "background: transparent;\n"
                                   "}\n"
                                   "")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.win_rate_win = QtWidgets.QToolButton(self.frame_4)
        self.win_rate_win.setGeometry(QtCore.QRect(93, 48, 111, 111))
        self.win_rate_win.setStyleSheet("border-radius:55px;\n"
                                        "background: rgb(203, 135, 0);\n"
                                        "background-color: rgb(255,215,0);\n"
                                        "\n"
                                        "")
        self.win_rate_win.setText("")
        self.win_rate_win.setObjectName("win_rate_win")
        self.image_label = QtWidgets.QToolButton(self.frame_4)
        self.image_label.setEnabled(True)
        self.image_label.setGeometry(QtCore.QRect(98, 53, 101, 101))
        self.image_label.setMouseTracking(False)
        self.image_label.setTabletTracking(False)
        self.image_label.setAcceptDrops(False)
        self.image_label.setAutoFillBackground(False)
        # ------------
        image_format = self.pre_profile()

        if len(image_format) != 0:
            image = image_format.split("\\")[1]
            image_url = f"background-image: url(Images/{image});"
        else:
            image_url = "background-image: url(:/images/Images/Avatar.png);"

        # ------------
        self.image_label.setStyleSheet("border-radius:50px;\n"
                                       "\n"
                                       "background-color: rgb(10, 10, 10);\n"
                                       "\n"
                                       f"{image_url}"
                                       "background-repeat: no-repeat; "
                                       "background-position: center;"
                                       )
        self.image_label.setText("")
        self.image_label.setAutoRaise(False)
        self.image_label.setArrowType(QtCore.Qt.NoArrow)
        self.image_label.setObjectName("image_label")
        self.label_10 = QtWidgets.QLabel(self.frame_4)
        self.label_10.setGeometry(QtCore.QRect(200, 210, 71, 21))
        self.label_10.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.label_8 = QtWidgets.QLabel(self.frame_4)
        self.label_8.setGeometry(QtCore.QRect(100, 209, 81, 21))
        self.label_8.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "background: transparent;")
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        self.label_7.setGeometry(QtCore.QRect(10, 210, 81, 21))
        self.label_7.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                   "color: rgb(255, 255, 255);\n"
                                   "background: transparent;")
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.rate_label = QtWidgets.QLabel(self.frame_4)
        self.rate_label.setGeometry(QtCore.QRect(190, 240, 81, 31))
        self.rate_label.setStyleSheet("color: rgb(0, 153, 0);\n"
                                      "font: 63 14pt \"Segoe UI Semibold\";")
        self.rate_label.setAlignment(QtCore.Qt.AlignCenter)
        self.rate_label.setObjectName("rate_label")
        self.win_label = QtWidgets.QLabel(self.frame_4)
        self.win_label.setGeometry(QtCore.QRect(99, 240, 81, 31))
        self.win_label.setStyleSheet("color: rgb(0, 153, 0);\n"
                                     "font: 63 14pt \"Segoe UI Semibold\";\n"
                                     "\n"
                                     "background:transparent;")
        self.win_label.setAlignment(QtCore.Qt.AlignCenter)
        self.win_label.setObjectName("win_label")
        self.losses_label = QtWidgets.QLabel(self.frame_4)
        self.losses_label.setGeometry(QtCore.QRect(10, 240, 81, 31))
        self.losses_label.setStyleSheet("color: rgb(199, 0, 0);\n"
                                        "font: 63 14pt \"Segoe UI Semibold\";")
        self.losses_label.setAlignment(QtCore.Qt.AlignCenter)
        self.losses_label.setObjectName("losses_label")
        self.name_label = QtWidgets.QLabel(self.frame_4)
        self.name_label.setGeometry(QtCore.QRect(10, 170, 271, 31))
        self.name_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.name_label.setAutoFillBackground(False)
        self.name_label.setStyleSheet("font: 12pt \"Bahnschrift\";\n"
                                      "color: rgb(255, 255, 255);\n"
                                      "\n"
                                      "")
        self.name_label.setInputMethodHints(QtCore.Qt.ImhNoTextHandles)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setIndent(0)
        self.name_label.setOpenExternalLinks(False)
        self.name_label.setObjectName("name_label")
        self.line_7 = QtWidgets.QFrame(self.frame_4)
        self.line_7.setGeometry(QtCore.QRect(90, 210, 3, 61))
        self.line_7.setStyleSheet("background-color: rgb(71, 71, 71);")
        self.line_7.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.line_8 = QtWidgets.QFrame(self.frame_4)
        self.line_8.setGeometry(QtCore.QRect(184, 210, 3, 61))
        self.line_8.setStyleSheet("background-color: rgb(71, 71, 71);")
        self.line_8.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.frame_2 = QtWidgets.QFrame(self.frame_4)
        self.frame_2.setGeometry(QtCore.QRect(1, 660, 279, 51))
        self.frame_2.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                   "")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.profile_pure_profit_label = QtWidgets.QLabel(self.frame_2)
        self.profile_pure_profit_label.setGeometry(QtCore.QRect(130, 0, 141, 51))
        self.profile_pure_profit_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                     "\n"
                                                     "\n"
                                                     "\n"
                                                     "color: rgb(0, 132, 0);\n"
                                                     "background: transparent;")
        self.profile_pure_profit_label.setAlignment(QtCore.Qt.AlignCenter)
        self.profile_pure_profit_label.setObjectName("profile_pure_profit_label")
        self.label_21 = QtWidgets.QLabel(self.frame_2)
        self.label_21.setGeometry(QtCore.QRect(20, 0, 91, 51))
        self.label_21.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_21.setObjectName("label_21")
        self.frame_3 = QtWidgets.QFrame(self.frame_4)
        self.frame_3.setGeometry(QtCore.QRect(1, 720, 279, 51))
        self.frame_3.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                   "")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.profile_total_wins_label = QtWidgets.QLabel(self.frame_3)
        self.profile_total_wins_label.setGeometry(QtCore.QRect(130, 0, 141, 51))
        self.profile_total_wins_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                    "color: rgb(0, 132, 0);\n"
                                                    "background: transparent;")
        self.profile_total_wins_label.setAlignment(QtCore.Qt.AlignCenter)
        self.profile_total_wins_label.setObjectName("profile_total_wins_label")
        self.label_22 = QtWidgets.QLabel(self.frame_3)
        self.label_22.setGeometry(QtCore.QRect(20, 0, 81, 51))
        self.label_22.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_22.setObjectName("label_22")
        self.frame_6 = QtWidgets.QFrame(self.frame_4)
        self.frame_6.setGeometry(QtCore.QRect(1, 780, 279, 51))
        self.frame_6.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                   "")
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.label_23 = QtWidgets.QLabel(self.frame_6)
        self.label_23.setGeometry(QtCore.QRect(20, 0, 91, 51))
        self.label_23.setStyleSheet("font: 10pt \"Bahnschrift\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "background: transparent;")
        self.label_23.setObjectName("label_23")
        self.profile_total_losses_label = QtWidgets.QLabel(self.frame_6)
        self.profile_total_losses_label.setGeometry(QtCore.QRect(130, 0, 141, 51))
        self.profile_total_losses_label.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                                      "color: rgb(191, 0, 0);\n"
                                                      "\n"
                                                      "background: transparent;")
        self.profile_total_losses_label.setAlignment(QtCore.Qt.AlignCenter)
        self.profile_total_losses_label.setObjectName("profile_total_losses_label")
        self.frame_16 = QtWidgets.QFrame(self.frame_4)
        self.frame_16.setGeometry(QtCore.QRect(1, 370, 279, 51))
        self.frame_16.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                    "")
        self.frame_16.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_16.setObjectName("frame_16")
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_16)
        self.pushButton_7.setEnabled(False)
        self.pushButton_7.setGeometry(QtCore.QRect(20, 10, 28, 28))
        self.pushButton_7.setAutoFillBackground(False)
        self.pushButton_7.setStyleSheet("background-image:url(:/images/Images/ww.png);\n"
                                        "\n"
                                        "background-color: transparent;\n"
                                        "")
        self.pushButton_7.setText("")
        self.pushButton_7.setCheckable(False)
        self.pushButton_7.setChecked(False)
        self.pushButton_7.setFlat(True)
        self.pushButton_7.setObjectName("pushButton_7")
        self.wallet_sato_label = QtWidgets.QLabel(self.frame_16)
        self.wallet_sato_label.setGeometry(QtCore.QRect(120, 10, 151, 31))
        self.wallet_sato_label.setStyleSheet("\n"
                                             "font: 10pt \"HoloLens MDL2 Assets\";\n"
                                             "background: transparent;")
        self.wallet_sato_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallet_sato_label.setObjectName("wallet_sato_label")
        self.frame_17 = QtWidgets.QFrame(self.frame_4)
        self.frame_17.setGeometry(QtCore.QRect(1, 440, 279, 51))
        self.frame_17.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                    "")
        self.frame_17.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_17.setObjectName("frame_17")
        self.pushButton_8 = QtWidgets.QPushButton(self.frame_17)
        self.pushButton_8.setEnabled(False)
        self.pushButton_8.setGeometry(QtCore.QRect(20, 10, 28, 28))
        self.pushButton_8.setAutoFillBackground(False)
        self.pushButton_8.setStyleSheet("background-image:url(:/images/Images/bb.png);\n"
                                        "\n"
                                        "background-color: transparent;")
        self.pushButton_8.setText("")
        self.pushButton_8.setCheckable(False)
        self.pushButton_8.setChecked(False)
        self.pushButton_8.setFlat(True)
        self.pushButton_8.setObjectName("pushButton_8")
        self.wallet_btc_label = QtWidgets.QLabel(self.frame_17)
        self.wallet_btc_label.setGeometry(QtCore.QRect(120, 10, 151, 31))
        self.wallet_btc_label.setStyleSheet("\n"
                                            "font: 10pt \"HoloLens MDL2 Assets\";\n"
                                            "background: transparent;")
        self.wallet_btc_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallet_btc_label.setObjectName("wallet_btc_label")
        self.frame_18 = QtWidgets.QFrame(self.frame_4)
        self.frame_18.setGeometry(QtCore.QRect(1, 510, 279, 51))
        self.frame_18.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                    "")
        self.frame_18.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_18.setObjectName("frame_18")
        self.pushButton_9 = QtWidgets.QPushButton(self.frame_18)
        self.pushButton_9.setEnabled(False)
        self.pushButton_9.setGeometry(QtCore.QRect(20, 10, 28, 28))
        self.pushButton_9.setAutoFillBackground(False)
        self.pushButton_9.setStyleSheet("background-image:url(:/images/Images/ss.png);\n"
                                        "\n"
                                        "background-color: transparent;")
        self.pushButton_9.setText("")
        self.pushButton_9.setCheckable(False)
        self.pushButton_9.setChecked(False)
        self.pushButton_9.setFlat(True)
        self.pushButton_9.setObjectName("pushButton_9")
        self.wallet_S_label = QtWidgets.QLabel(self.frame_18)
        self.wallet_S_label.setGeometry(QtCore.QRect(120, 10, 151, 31))
        self.wallet_S_label.setStyleSheet("\n"
                                          "font: 10pt \"HoloLens MDL2 Assets\";\n"
                                          "background: transparent;")
        self.wallet_S_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallet_S_label.setObjectName("wallet_S_label")
        self.frame_19 = QtWidgets.QFrame(self.frame_4)
        self.frame_19.setGeometry(QtCore.QRect(1, 580, 279, 51))
        self.frame_19.setStyleSheet("background: rgba(0, 0, 0, 100);\n"
                                    "")
        self.frame_19.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_19.setObjectName("frame_19")
        self.pushButton_11 = QtWidgets.QPushButton(self.frame_19)
        self.pushButton_11.setEnabled(False)
        self.pushButton_11.setGeometry(QtCore.QRect(20, 10, 28, 28))
        self.pushButton_11.setAutoFillBackground(False)
        self.pushButton_11.setStyleSheet("background-image:url(:/images/Images/ss.png);\n"
                                         "\n"
                                         "background-color: transparent;")
        self.pushButton_11.setText("")
        self.pushButton_11.setCheckable(False)
        self.pushButton_11.setChecked(False)
        self.pushButton_11.setFlat(True)
        self.pushButton_11.setObjectName("pushButton_11")
        self.wallet_SS_label = QtWidgets.QLabel(self.frame_19)
        self.wallet_SS_label.setGeometry(QtCore.QRect(90, 16, 121, 21))
        self.wallet_SS_label.setStyleSheet("\n"
                                           "font: 10pt \"HoloLens MDL2 Assets\";\n"
                                           "background: transparent;")
        self.wallet_SS_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.wallet_SS_label.setObjectName("wallet_SS_label")
        self.comboBox_currency = QtWidgets.QComboBox(self.frame_19)
        self.comboBox_currency.setGeometry(QtCore.QRect(220, 16, 61, 22))
        self.comboBox_currency.setStyleSheet(
            "color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0.373134 rgba(255, 255, 255, 255));\n"
            "\n"
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.097, stop:0.771144 rgba("
            "0, 0, 0, 255), stop:1 rgba(255, 255, 255, 255));\n "
            "color: rgb(211, 211, 211);\n"
            "background:transparent;\n"
            "font: 11pt \"Bahnschrift\";")
        self.comboBox_currency.setObjectName("comboBox_currency")
        self.comboBox_currency.addItem("")
        self.comboBox_currency.addItem("")
        self.comboBox_currency.addItem("")
        self.comboBox_currency.addItem("")
        self.comboBox_currency.currentIndexChanged.connect(self.currency_combo)
        # =========================

        self.frame_22 = QtWidgets.QFrame(self.frame_4)
        self.frame_22.setGeometry(QtCore.QRect(1, 300, 279, 51))
        self.frame_22.setStyleSheet("background: rgba(0, 0, 0,150);\n"
                                    "")
        self.frame_22.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_22.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_22.setObjectName("frame_22")
        self.label_11 = QtWidgets.QLabel(self.frame_22)
        self.label_11.setGeometry(QtCore.QRect(10, 10, 71, 31))
        self.label_11.setStyleSheet("font: 75 10pt \"Bahnschrift\";\n"
                                    "background: transparent;")
        self.label_11.setObjectName("label_11")
        self.btc_price = QtWidgets.QLabel(self.frame_22)
        self.btc_price.setGeometry(QtCore.QRect(120, 10, 151, 31))
        self.btc_price.setStyleSheet("font: bold 11pt \"Courier\";\n"
                                     "background: transparent;\n"
                                     "color: rgb(0, 132, 0);")
        self.btc_price.setAlignment(QtCore.Qt.AlignCenter)
        self.btc_price.setObjectName("btc_price")
        self.image_btn = QtWidgets.QPushButton(self.frame_4)
        self.image_btn.setGeometry(QtCore.QRect(180, 146, 31, 21))
        self.image_btn.setStyleSheet("*{\n"
                                     "background: transparent ;\n"
                                     "border-radius:10px;\n"
                                     "\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:hover{\n"
                                     "background-color: rgb(0, 0, 0);\n"
                                     "border: 1px solid  rgb(0,0,0);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton{\n"
                                     "border: 1px solid  transparent;\n"
                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                     "}\n"
                                     "\n"
                                     "\n"
                                     "QPushButton:pressed \n"
                                     "{\n"
                                     " border: 2px inset    rgb(203, 135, 0);\n"
                                     "background-color: #333;\n"
                                     "}")
        self.image_btn.setText("")
        icon17 = QtGui.QIcon()
        icon17.addPixmap(QtGui.QPixmap(":/images/Images/icons8-google-images-50 (1).png"), QtGui.QIcon.Normal,
                         QtGui.QIcon.On)
        self.image_btn.setIcon(icon17)
        self.image_btn.setObjectName("image_btn")
        self.image_btn.clicked.connect(self.profile)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        # ----------------------------------------
        threading.Thread(target=lambda: Thread.every(10, self.update)).start()
        self.table()
        self.currency_combo_init()
        self.opentrade_init()

        # =========================================

    def currency_combo_init(self):
        _translate = QtCore.QCoreApplication.translate
        _btc_ = old_btc_price
        now = datetime.datetime.now()
        currency_price = 0
        try:
            if Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                value = eval(Extract(f"Prevalues_{identity}").get_by_id("currency_api")[1])
                currency_price = value["currency_Price"]
                currency_ = value["currency"]
                time_pass = value["time"]
                pass_ = True if time_pass != now.day else False
                a = 0
                b = 1
                cc = 2
                d = 3
                if currency_ == "SGD":
                    a = 0
                    b = 1
                    cc = 2
                    d = 3
                if currency_ == "CAD":
                    a = 1
                    b = 0
                    cc = 2
                    d = 3
                if currency_ == "EUR":
                    a = 1
                    b = 2
                    cc = 0
                    d = 3
                if currency_ == "MAD":
                    a = 3
                    b = 1
                    cc = 2
                    d = 0
                self.comboBox_currency.setItemText(a, _translate("Form", "SGD"))
                self.comboBox_currency.setItemText(b, _translate("Form", "CAD"))
                self.comboBox_currency.setItemText(cc, _translate("Form", "EUR"))
                self.comboBox_currency.setItemText(d, _translate("Form", "MAD"))
            else:
                pass_ = True
                self.comboBox_currency.setItemText(0, _translate("Form", "SGD"))
                self.comboBox_currency.setItemText(1, _translate("Form", "CAD"))
                self.comboBox_currency.setItemText(2, _translate("Form", "EUR"))
                self.comboBox_currency.setItemText(3, _translate("Form", "MAD"))

            currency_price = API.currency_exchange(self.comboBox_currency.currentText()) if pass_ else \
                currency_price

            if _btc_ is not None:
                Table(f"Prevalues_{identity}").create()
                if Extract(f"Prevalues_{identity}").check_cell("Wallet"):
                    input_wallet = Extract(f"Prevalues_{identity}").get_by_id("Wallet")

                    input_wallet = input_wallet[1]

                    xusd = round(((float(input_wallet) * 0.00000001) * _btc_), 1)
                    usd = str(f"{int(xusd):,d}") + "." + str(round(abs(xusd - int(xusd)), 1)).split(".")[1]

                    xcurrency = round(float(currency_price) * xusd, 1)
                    currency = str(f"{int(xcurrency):,d}") + "." + \
                               str(round(abs(xcurrency - int(xcurrency)), 1)).split(".")[1]

                    btc_ = round((float(input_wallet) * 0.00000001), 5)

                    self.wallet_sato_label.setText(_translate("Form", f"{int(input_wallet):,d} sat"))
                    self.wallet_btc_label.setText(_translate("Form", f"{btc_} ₿"))
                    self.wallet_S_label.setText(
                        _translate("Form", f"{self.zero_remover(usd)} $"))
                    self.wallet_SS_label.setText(_translate("Form", f"{self.zero_remover(currency)}"))
                else:
                    self.wallet_sato_label.setText(_translate("Form", "0 sat"))
                    self.wallet_btc_label.setText(_translate("Form", "0 ₿"))
                    self.wallet_S_label.setText(_translate("Form", "0 $"))
                    self.wallet_SS_label.setText(_translate("Form", "0"))

                if pass_:
                    data = {"currency_Price": currency_price,
                            "currency": self.comboBox_currency.currentText(), "time": now.day}

                    if not Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                        Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).insert()
                    else:
                        Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).update()

        except Exception as e:
            print("currency_combo_init ", e)

    def currency_combo(self):
        _translate = QtCore.QCoreApplication.translate
        _btc_ = old_btc_price
        now = datetime.datetime.now()
        try:
            currency_price = API.currency_exchange(self.comboBox_currency.currentText())

            if _btc_ is not None:
                Table(f"Prevalues_{identity}").create()
                if Extract(f"Prevalues_{identity}").check_cell("Wallet"):
                    input_wallet = Extract(f"Prevalues_{identity}").get_by_id("Wallet")

                    input_wallet = input_wallet[1]

                    xusd = round(((float(input_wallet) * 0.00000001) * _btc_), 1)

                    xcurrency = round(float(currency_price) * xusd, 1)
                    currency = str(f"{int(xcurrency):,d}") + "." + \
                               str(round(abs(xcurrency - int(xcurrency)), 1)).split(".")[1]

                    self.wallet_SS_label.setText(_translate("Form", f"{self.zero_remover(currency)}"))

                    data = {"currency_Price": currency_price,
                            "currency": self.comboBox_currency.currentText(), "time": now.day}

                    if not Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                        Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).insert()
                    else:
                        Pre_values(f"Prevalues_{identity}", "currency_api", str(data)).update()

                self.table()
            else:
                pass
        except Exception as e:
            print("currency_combo ", e)

    def pre_profile(self):
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk("Images"):
            for file in f:
                if 'user_image' in file:
                    files.append(os.path.join(r, file))
        return files[0] if len(files) != 0 else []

    def profile(self):
        global identity
        try:
            file_path = QFileDialog.getOpenFileName(None, 'Select Your Backup image:', expanduser("~"))[0]
            print(file_path)
            base_width = 100
            img = Image.open(file_path)
            w_percent = (base_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            re_image = img.resize((base_width, h_size), Image.ANTIALIAS)
            image_format = img.format
            re_image.save(f'Images/user_image.{image_format}')

            self.image_label.setStyleSheet("border-radius:50px;\n"
                                           "\n"
                                           "background-color: rgb(150, 150, 150);\n"
                                           f"background-image: url(Images/user_image.{image_format});\n"
                                           "background-repeat: no-repeat; "
                                           "background-position: center;"
                                           "")
        except AttributeError as e:
            print("profile ", e)
        except Exception as e:
            print("profile ", e)

    def table(self):
        btc_ = old_btc_price
        if btc_ is not None:
            pass
        else:
            btc_ = 0
        try:
            if not Table(f"Journal_{identity}").check:  # f'Journal_{identity}'
                journal_data = []
                pass
            else:
                journal_data = Extract(f"Journal_{identity}").fetchall()

            # ===========================================
            _translate = QtCore.QCoreApplication.translate
            self.TABLE_Widget.setSortingEnabled(True)
            item = self.TABLE_Widget.horizontalHeaderItem(0)
            item.setText(_translate("Form", "ID"))
            item = self.TABLE_Widget.horizontalHeaderItem(1)
            item.setText(_translate("Form", "DATE"))
            item = self.TABLE_Widget.horizontalHeaderItem(2)
            item.setText(_translate("Form", "AMOUNT"))
            item = self.TABLE_Widget.horizontalHeaderItem(3)
            item.setText(_translate("Form", "ENTRY"))
            item = self.TABLE_Widget.horizontalHeaderItem(4)
            item.setText(_translate("Form", "EXIT"))
            item = self.TABLE_Widget.horizontalHeaderItem(5)
            item.setText(_translate("Form", "RESULT"))
            __sortingEnabled = self.TABLE_Widget.isSortingEnabled()
            self.TABLE_Widget.setSortingEnabled(False)
            self.TABLE_Widget.setRowCount(len(journal_data))

            # =======================================
            if Extract(f"Prevalues_{identity}").check_cell("currency_api"):
                value = eval(Extract(f"Prevalues_{identity}").get_by_id("currency_api")[1])
                currency_price = value["currency_Price"]
                currency_s = value["currency"]
            else:
                try:
                    currency_price = API.currency_exchange("SGD")
                    currency_s = "SGD"
                except Exception:
                    currency_price = 0
                    currency_s = 0
                    msg = QMessageBox()
                    msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("conix Error")
                    msg.setInformativeText('Something wrong restart your program and try again.')
                    msg.setWindowTitle("wifi-Error")
                    msg.exec_()
            k = 0
            for i in range(len(journal_data)):
                result = float(journal_data[(len(journal_data) - 1) - k][7])

                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.TABLE_Widget.setItem(i, 0, item)
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.TABLE_Widget.setItem(i, 1, item)
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.TABLE_Widget.setItem(i, 2, item)
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.TABLE_Widget.setItem(i, 3, item)
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.TABLE_Widget.setItem(i, 4, item)
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                font = QtGui.QFont()
                font.setPointSize(13)
                item.setFont(font)
                self.TABLE_Widget.setItem(i, 5, item)
                # ===========================
                item = self.TABLE_Widget.item(i, 0)
                item.setText(_translate("MyAPP", f"{journal_data[(len(journal_data) - 1) - k][0]}"))
                item = self.TABLE_Widget.item(i, 1)
                item.setText(_translate("MyAPP", f"{journal_data[(len(journal_data) - 1) - k][3]}"))
                item = self.TABLE_Widget.item(i, 2)
                item.setText(_translate("MyAPP",
                                        f"{journal_data[(len(journal_data) - 1) - k][4]} $"))
                item = self.TABLE_Widget.item(i, 3)
                item.setText(_translate("MyAPP",
                                        f"{self.zero_remover(journal_data[(len(journal_data) - 1) - k][5])} $"))
                item = self.TABLE_Widget.item(i, 4)
                item.setText(_translate("MyAPP",
                                        f"{self.zero_remover(journal_data[(len(journal_data) - 1) - k][6])} $"))
                item = self.TABLE_Widget.item(i, 5)
                xusd = round(result * btc_, 1)
                usd = str(f"{int(xusd):,d}") + "." + str(round(abs(xusd - int(xusd)), 1)).split(".")[1]
                curr = round(float(currency_price) * xusd, 1)
                currency = str(f"{int(curr):,d}") + "." + \
                           str(round(abs(curr - int(curr)), 1)).split(".")[1]
                item.setText(
                    _translate("MyAPP",
                               f"{round(result, 5)}₿ ➨ "
                               f"{self.zero_remover(usd)} $ "
                               f"| {self.zero_remover(currency)}"
                               f" {currency_s}"))
                # ===========================
                if result >= 0:
                    brush = QtGui.QBrush(QtGui.QColor(3, 100, 64))
                else:
                    brush = QtGui.QBrush(QtGui.QColor(139, 0, 0))
                brush.setStyle(QtCore.Qt.NoBrush)
                item.setForeground(brush)
                k += 1
            self.TABLE_Widget.setSortingEnabled(__sortingEnabled)
            self.TABLE_Widget.sortItems(1, QtCore.Qt.DescendingOrder)
        except Exception as e:
            print("table", e)
            pass

    def open_trade_combo(self):
        _translate = QtCore.QCoreApplication.translate
        if self.checkBox_opentrade.isChecked():
            self.input_exit_BS.setReadOnly(True)
            self.input_exit_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setStyleSheet("*{\n"
                                             "font: 75 12pt \"Bahnschrift\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background: rgb(100, 100, 100);\n"
                                             "}")

            frame_state = "background-image: url(Images/open-sign-black.png);"
            self.Trade_state_frame.setStyleSheet(f"{frame_state}"
                                                 "background-color: transparent;")

            color = "background: rgb(100, 100, 100);"

            self.frame_12.setStyleSheet(color)
            self.frame_13.setStyleSheet(color)
            self.frame_14.setStyleSheet(color)

        else:
            self.input_exit_BS.setReadOnly(False)
            self.input_exit_BS.setText(_translate("MyAPP", ""))
            self.input_exit_BS.setStyleSheet("*{\n"
                                             "font: 75 12pt \"Bahnschrift\";\n"
                                             "color: rgb(0, 0, 0);\n"
                                             "}\n"
                                             "QLineEdit{\n"
                                             "border-radius:8px;\n"
                                             "background: rgb(240, 240, 240);\n"
                                             "}")
            self.Trade_state_frame.setStyleSheet("background-image: url(:/images/Images/close_sign.png);\n"
                                                 "background-color: transparent;")

            color = "background: rgb(0, 0, 0);"

            self.frame_12.setStyleSheet(color)
            self.frame_13.setStyleSheet(color)
            self.frame_14.setStyleSheet(color)

    def calc_openTradeBUY(self):  # open the trade buy calculator
        _translate = QtCore.QCoreApplication.translate
        if self.checkBox_opentrade.isChecked():
            try:
                amount = float(self.input_amount_BS_3.text())
                entry = float(self.input_entry_BS.text())

                self.checkBox_opentrade.setEnabled(False)
                date = datetime.date.today()
                month = date.month
                day = date.day
                year = date.year

                open_data = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])

                state_ = open_data["state"]

                if state_ == "closed":

                    data = {"date": date, "amount": amount,
                            "entry": entry, "state": "BUY"}

                    Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()
                    data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                    Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                elif state_ == "BUY":

                    date_str_ = open_data["date"]
                    amount_ = float(open_data["amount"])
                    entry_ = float(open_data["entry"])
                    x_amount = amount_ + amount
                    x_entry = ((amount_ * entry_) + (amount * entry)) / x_amount

                    data = {"date": date_str_, "amount": x_amount,

                            "entry": round(x_entry, 1), "state": "BUY"}

                    Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                elif state_ == "SELL":

                    date_str_ = open_data["date"]
                    amount_ = float(open_data["amount"])
                    entry_ = float(open_data["entry"])
                    x_amount = amount_ - amount

                    if x_amount > 0:

                        data = {"date": date_str_, "amount": x_amount,

                                "entry": entry_, "state": "SELL"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()

                    elif x_amount < 0:

                        data = {"date": date, "amount": abs(x_amount),

                                "entry": entry, "state": "BUY"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": date_str_, "amount": amount_, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()

                    elif x_amount == 0:

                        data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()
                        self.checkBox_opentrade.setChecked(False)
                        self.checkBox_opentrade.setEnabled(True)
                        self.input_exit_BS.setReadOnly(False)

                        data = {"date": 0, "amount": 0, "entry": 0, "state": "closed"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                state = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])["state"]

                if state != "closed":

                    open_data_ = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])

                    amount = open_data_["amount"]
                    entry = open_data_["entry"]
                    date = open_data_["date"]

                    color = "background: rgb(191, 0, 0);" if state == "SELL" else \
                        "background: rgb(0, 132, 0);"

                    self.trade_date.setText(_translate("Form", f"{date}"))
                    self.frame_12.setStyleSheet(color)
                    self.trade_amount.setText(_translate("Form", f"{amount}$"))
                    self.frame_13.setStyleSheet(color)
                    self.trade_entry.setText(_translate("Form", f"{entry}$"))
                    self.frame_14.setStyleSheet(color)

                    frame_state = "background-image: url(:/images/Images/open_sign_sell.png);" if \
                        state == "SELL" else "background-image: url(:/images/Images/open_sign_buy.png);\n"

                    self.Trade_state_frame.setStyleSheet(f"{frame_state}"
                                                         "background-color: transparent;")

                    self.down_bar_label.setText(_translate("Form",
                                                           f"Data Storage Size : {file_size('database.db')}           "
                                                           f"     "
                                                           f"                  Trade open since : {date}              "
                                                           f"     "
                                                           f"                        "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           f"              {current_time()} "))

                else:
                    color = "background: rgb(0, 0, 0);"

                    self.trade_date.setText(_translate("Form", ""))
                    self.frame_12.setStyleSheet(color)
                    self.trade_amount.setText(_translate("Form", ""))
                    self.frame_13.setStyleSheet(color)
                    self.trade_entry.setText(_translate("Form", ""))
                    self.frame_14.setStyleSheet(color)
                    self.Trade_state_frame.setStyleSheet("background-image: url(:/images/Images/close_sign.png);\n"
                                                         "background-color: transparent;")

                    self.down_bar_label.setText(_translate("Form",
                                                           f"Data Storage Size : {file_size('database.db')}      "
                                                           f"          "
                                                           f"                  Trade closed :                      "
                                                           f"        "
                                                           f"                        "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           f"                   {current_time()} "))

                self.input_amount_BS_3.setText(_translate("MyAPP", ""))
                self.input_entry_BS.setText(_translate("MyAPP", ""))

            except Exception as e:
                print("open buy ", e)
        else:
            self.journal_buy()
            self.table()

    def calc_openTradeSELL(self):
        _translate = QtCore.QCoreApplication.translate
        if self.checkBox_opentrade.isChecked():
            try:
                amount = float(self.input_amount_BS_3.text())
                entry = float(self.input_entry_BS.text())

                self.checkBox_opentrade.setEnabled(False)
                date = datetime.date.today()
                month = date.month
                day = date.day
                year = date.year

                open_data = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])

                state_ = open_data["state"]

                if state_ == "closed":

                    data = {"date": date, "amount": amount,
                            "entry": entry, "state": "SELL"}

                    Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()
                    data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}
                    Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                elif state_ == "SELL":

                    date_str_ = open_data["date"]
                    amount_ = float(open_data["amount"])
                    entry_ = float(open_data["entry"])
                    x_amount = amount_ + amount
                    x_entry = ((amount_ * entry_) + (amount * entry)) / x_amount

                    data = {"date": date_str_, "amount": x_amount,

                            "entry": round(x_entry, 1), "state": "SELL"}

                    Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                elif state_ == "BUY":

                    date_str_ = open_data["date"]
                    amount_ = float(open_data["amount"])
                    entry_ = float(open_data["entry"])
                    x_amount = amount_ - amount

                    if x_amount > 0:

                        data = {"date": date_str_, "amount": x_amount,

                                "entry": entry_, "state": "BUY"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()

                    elif x_amount < 0:

                        data = {"date": date, "amount": abs(x_amount),

                                "entry": entry, "state": "SELL"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": date_str_, "amount": amount_, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()

                    elif x_amount == 0:

                        data_ = {"date": date_str_, "amount": amount, "entry": entry_, "exit": entry}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                        self.journal_sell()
                        self.table()
                        self.checkBox_opentrade.setChecked(False)
                        self.checkBox_opentrade.setEnabled(True)
                        self.input_exit_BS.setReadOnly(False)

                        data = {"date": 0, "amount": 0, "entry": 0, "state": "closed"}

                        Pre_values(f"Prevalues_{identity}", "opentrade", str(data)).update()

                        data_ = {"date": 0, "amount": 0, "entry": 0, "exit": 0}

                        Pre_values(f"Prevalues_{identity}", "opentradeplus", str(data_)).update()

                state = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])["state"]

                if state != "closed":

                    open_data_ = eval(Extract(f"Prevalues_{identity}").get_by_id("opentrade")[1])

                    amount = open_data_["amount"]
                    entry = open_data_["entry"]
                    date = open_data_["date"]

                    color = "background: rgb(191, 0, 0);" if state == "SELL" else \
                        "background: rgb(0, 132, 0);"

                    self.trade_date.setText(_translate("Form", f"{date}"))
                    self.frame_12.setStyleSheet(color)
                    self.trade_amount.setText(_translate("Form", f"{amount}$"))
                    self.frame_13.setStyleSheet(color)
                    self.trade_entry.setText(_translate("Form", f"{entry}$"))
                    self.frame_14.setStyleSheet(color)
                    frame_state = "background-image: url(:/images/Images/open_sign_sell.png);" if \
                        state == "SELL" else "background-image: url(:/images/Images/open_sign_buy.png);\n"

                    self.Trade_state_frame.setStyleSheet(f"{frame_state}"
                                                         "background-color: transparent;")

                    self.down_bar_label.setText(_translate("Form",
                                                           f"Data Storage Size : {file_size('database.db')}         "
                                                           f"       "
                                                           f"                  Trade open since : {date}             "
                                                           f"      "
                                                           f"                        "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           f"              {current_time()} "))

                else:
                    color = "background: rgb(0, 0, 0);"

                    self.trade_date.setText(_translate("Form", ""))
                    self.frame_12.setStyleSheet(color)
                    self.trade_amount.setText(_translate("Form", ""))
                    self.frame_13.setStyleSheet(color)
                    self.trade_entry.setText(_translate("Form", ""))
                    self.frame_14.setStyleSheet(color)
                    self.Trade_state_frame.setStyleSheet("background-image: url(:/images/Images/close_sign.png);\n"
                                                         "background-color: transparent;")

                    self.down_bar_label.setText(_translate("Form",
                                                           f"Data Storage Size : {file_size('database.db')}      "
                                                           f"          "
                                                           f"                  Trade closed :                     "
                                                           f"         "
                                                           f"                        "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           "                         "
                                                           "                                                    "
                                                           f"                   {current_time()} "))

                self.input_amount_BS_3.setText(_translate("MyAPP", ""))
                self.input_entry_BS.setText(_translate("MyAPP", ""))

            except Exception as e:
                print("open sell ", e)
        else:
            self.journal_sell()
            self.table()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "BitHunter"))
        # =============================================
        self.max_gain_1_label.setText(_translate("Form", "+0.12304₿"))
        self.label_31.setText(_translate("Form", "MAX Gain"))
        self.min_gain_1_label.setText(_translate("Form", "+0.12304₿"))
        self.label_34.setText(_translate("Form", "MIN Gain"))
        self.max_loss_1_label.setText(_translate("Form", "+0.12304₿"))
        self.label_36.setText(_translate("Form", "MAX Loss"))
        self.min_loss_1_label.setText(_translate("Form", "+0.12304₿"))
        self.label_38.setText(_translate("Form", "MIN Loss"))
        self.btn_SELL.setText(_translate("Form", "▼ SELL"))
        self.btn_BUY.setText(_translate("Form", "▲ BUY"))
        self.label_44.setText(_translate("Form", "Entry"))
        self.label_42.setText(_translate("Form", "Amount"))
        self.label_40.setText(_translate("Form", "Date"))
        self.input_delete.setPlaceholderText(_translate("Form", "ID "))
        self.label_16.setText(_translate("Form", " Delete:"))
        self.input_wallet_balance.setPlaceholderText(_translate("Form", "Sat"))
        self.label_39.setText(_translate("Form", "Wallet "))
        self.input_modify.setPlaceholderText(_translate("Form", "ID/Amount/Entry/Exit"))
        self.label_15.setText(_translate("Form", "Modify"))
        self.label_32.setText(_translate("Form", "Amount"))
        self.label_45.setText(_translate("Form", "Entry"))
        self.label_46.setText(_translate("Form", "Exit"))
        self.checkBox_opentrade.setText(_translate("Form", "Open Trade"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "TRADING  JOURNAL "))
        self.max_gain_performance.setText(_translate("Form", "+0.12304₿"))
        self.label_48.setText(_translate("Form", "MAX Gain"))
        self.min_gain_performance.setText(_translate("Form", "+0.12304₿"))
        self.label_50.setText(_translate("Form", "MIN Gain"))
        self.max_loss_performance.setText(_translate("Form", "+0.12304₿"))
        self.label_52.setText(_translate("Form", "MAX Loss"))
        self.min_loss_performance.setText(_translate("Form", "+0.12304₿"))
        self.label_54.setText(_translate("Form", "MIN Loss"))
        self.label_59.setText(_translate("Form", "Total Losses"))
        self.preformance_total_loss_label.setText(_translate("Form", "+0.12304₿"))
        self.label_58.setText(_translate("Form", "Total Wins"))
        self.preformance_total_wins_label.setText(_translate("Form", "+0.12304₿"))
        self.label_56.setText(_translate("Form", "Pure Profit"))
        self.preformance_pure_profit_label.setText(_translate("Form", "+0.10304₿"))
        self.listWidget_preformance.setSortingEnabled(False)
        __sortingEnabled = self.listWidget_preformance.isSortingEnabled()
        self.listWidget_preformance.setSortingEnabled(False)
        item = self.listWidget_preformance.item(0)
        item.setText(_translate("Form", "VIEW ALL"))
        item = self.listWidget_preformance.item(1)
        item.setText(_translate("Form", "9-17-2019"))
        item = self.listWidget_preformance.item(2)
        item.setText(_translate("Form", "9-16-2019"))
        self.listWidget_preformance.setSortingEnabled(__sortingEnabled)
        self.note_date_2.setText(_translate("Form", "SELECT MONTH"))
        self.label_64.setText(_translate("Form", "TRADE  PERFORMANCE  GRAPH"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "PERFORMANCE GRAPH"))
        self.note_TextEdit.setPlainText(
            _translate("Form", "We will notify you after the price of BTC reaches 11,000 USD.\n"
                               "rgb(203, 135, 0);\n"
                               "CSS alpha transparency method (doesn\'t work in Internet Explorer 8): #div{"
                               "background-color:rgba(255,0,0,0.5);} Use a transparent PNG image according to your "
                               "choice as background. Use the following CSS code snippet to create a cross-browser "
                               "alpha-transparent background. Here is an example with #000000 @ 0.4% opacity .Sep 24, "
                               "2"))
        self.listWidget_Note.setSortingEnabled(True)
        __sortingEnabled = self.listWidget_Note.isSortingEnabled()
        self.listWidget_Note.setSortingEnabled(False)
        item = self.listWidget_Note.item(0)
        item.setText(_translate("Form",
                                "New World :  We will notify you after the price of BTC reaches 11,000 USD.  "
                                "14/09/2019   4:00 AM"))
        item = self.listWidget_Note.item(1)
        item.setText(_translate("Form",
                                "New World :  We will notify you after the price of BTC reaches 11,000 USD.  "
                                "14/09/2019   4:00 AM"))
        self.listWidget_Note.setSortingEnabled(__sortingEnabled)
        self.note_input_add.setPlaceholderText(_translate("Form", "Title"))
        self.note_input_search.setPlaceholderText(_translate("Form", "Search"))
        self.note_date.setText(_translate("Form", "14-09-2019        4:00 AM"))
        self.note_title.setText(_translate("Form", "   # NEW WORLD"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "BUSINESS NOTE"))
        self.comboBox1_historical_data.setItemText(0, _translate("Form", "  MONTH"))
        self.comboBox1_historical_data.setItemText(1, _translate("Form", "  WEEK"))
        self.comboBox1_historical_data.setItemText(2, _translate("Form", "  DAY"))
        self.label_18.setText(_translate("Form", "9-16-2019"))
        self.historical_data_year_label.setText(_translate("Form", "2019"))
        __sortingEnabled = self.listWidget_btc_historical_data.isSortingEnabled()
        self.listWidget_btc_historical_data.setSortingEnabled(False)
        item = self.listWidget_btc_historical_data.item(0)
        item.setText(_translate("Form", "ALL HISTORY"))
        item = self.listWidget_btc_historical_data.item(1)
        item.setText(_translate("Form", "9-17-2019"))
        item = self.listWidget_btc_historical_data.item(2)
        item.setText(_translate("Form", "9-16-2019"))
        item = self.listWidget_btc_historical_data.item(3)
        item.setText(_translate("Form", "9-15-2019"))
        self.listWidget_btc_historical_data.setSortingEnabled(__sortingEnabled)
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_3), _translate("Form", "GENERAL GRAPH"))

        self.BH_jan_label.setText(_translate("Form", "Janurary  2011"))
        self.BH_feb_label.setText(_translate("Form", "February  2011"))
        self.BH_mar_label.setText(_translate("Form", "March  2011"))
        self.BH_apr_label.setText(_translate("Form", "April  2011"))
        self.BH_may_label.setText(_translate("Form", "May  2011"))
        self.BH_june_label.setText(_translate("Form", "June  2011"))
        self.BH_july_label.setText(_translate("Form", "July  2011"))
        self.BH_aug_label.setText(_translate("Form", "August  2011"))
        self.BH_sep_label.setText(_translate("Form", "September  2011"))
        self.BH_oct_label.setText(_translate("Form", "October  2011"))
        self.BH_nov_label.setText(_translate("Form", "November  2011"))
        self.BH_dec_label.setText(_translate("Form", "December  2011"))
        self.comboBox2_historical_data.setItemText(0, _translate("Form", "2010"))
        self.comboBox2_historical_data.setItemText(1, _translate("Form", "2011"))
        self.comboBox2_historical_data.setItemText(2, _translate("Form", "2012"))
        self.comboBox2_historical_data.setItemText(3, _translate("Form", "2013"))
        self.comboBox2_historical_data.setItemText(4, _translate("Form", "2014"))
        self.comboBox2_historical_data.setItemText(5, _translate("Form", "2015"))
        self.comboBox2_historical_data.setItemText(6, _translate("Form", "2016"))
        self.comboBox2_historical_data.setItemText(7, _translate("Form", "2017"))
        self.comboBox2_historical_data.setItemText(8, _translate("Form", "2018"))
        self.comboBox2_historical_data.setItemText(9, _translate("Form", "2019"))
        self.label_76.setText(_translate("Form", "Year :"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_4), _translate("Form", "MULTI GRAPH"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4),
                                  _translate("Form", "BTC HISTORICAL DATA ANALYSIS"))
        self.about_btn.setText(_translate("Form", "About Me"))
        self.import_btn.setText(_translate("Form", "Import"))
        self.progressBar_download.setFormat(_translate("Form", "%p%"))
        self.label_61.setText(_translate("Form", "Download & Import backup data."))
        self.download_btn.setText(_translate("Form", "Download "))
        self.progressBar_import.setFormat(_translate("Form", "%p%"))
        self.notify_input.setText(_translate("Form", "45343"))
        self.notify_btn.setText(_translate("Form", "Notify me"))
        self.resut_output_0.setText(_translate("Form", "The Order size: 27617.42$"))
        self.radioButton_ordersize.setText(_translate("Form", "Order Size"))
        self.radioButton_risk.setText(_translate("Form", "The Risk"))
        self.radioButton_stop.setText(_translate("Form", "The Stop"))
        self.label_82.setText(_translate("Form", "Entry"))
        self.label_83.setText(_translate("Form", "Order size"))
        self.label_84.setText(_translate("Form", "Risk"))
        self.label_85.setText(_translate("Form", "Stop"))
        self.Calc_btn_1.setText(_translate("Form", "CALCULATE"))
        self.radioButton_Riskpercentage_left.setText(_translate("Form", "Risk in Percentage"))
        self.Radiobtn_Risksato_left.setText(_translate("Form", "Risk in Satochi"))
        self.label_80.setText(_translate("Form", "Risk"))
        self.label_81.setText(_translate("Form", "Profit"))
        self.label_86.setText(_translate("Form", "BTC price notification."))
        self.label_3.setText(_translate("Form", "The new profit in your wallet balance."))
        self.label_2.setText(_translate("Form", "The new value of your wallet balance."))
        self.label.setText(_translate("Form", "The profit percentage of your wallet balance."))
        self.resut_output_1.setText(_translate("Form", "564566"))
        self.resut_output_2.setText(_translate("Form", "564566"))
        self.resut_output_3.setText(_translate("Form", "564566"))
        self.Calc_btn_2.setText(_translate("Form", "CALCULATE"))
        self.convert_output.setText(_translate("Form", "122,445,374 SATO"))
        self.label_87.setText(_translate("Form", "BTC To Sato"))
        self.label_62.setText(_translate("Form", "Download BTC Historical Data online."))
        self.export_btn_2.setText(_translate("Form", "Download "))
        self.label_20.setText(_translate("Form",
                                         "<html><head/><body><p><span style=\" font-size:10pt;\">We Update BTC "
                                         "Historical Data From </span><a "
                                         "href=\"https://finance.yahoo.com/quote/BTC-USD/history/\"><span style=\" "
                                         "font-size:10pt; text-decoration: underline; "
                                         "color:#0000ff;\">Here</span></a><span style=\" "
                                         "font-size:10pt;\">.</span></p></body></html>"))
        self.comboBox_backup.setItemText(0, _translate("Form", "HTML"))
        self.comboBox_backup.setItemText(1, _translate("Form", "TXT"))
        self.comboBox_backup.setItemText(2, _translate("Form", "JSON"))
        self.checkBox.setText(_translate("Form", "Risk in Satochi"))
        self.checkBox_2.setText(_translate("Form", "Risk in Percentage"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("Form", "Calculator      Features"))
        self.label_10.setText(_translate("Form", "Rate"))
        self.label_8.setText(_translate("Form", "Wins"))
        self.label_7.setText(_translate("Form", "losses"))
        self.rate_label.setText(_translate("Form", "+75%"))
        self.win_label.setText(_translate("Form", "75"))
        self.losses_label.setText(_translate("Form", "12"))
        self.name_label.setText(_translate("Form", "ISAAC FROST"))
        self.profile_pure_profit_label.setText(_translate("Form", "+0.10304₿"))
        self.label_21.setText(_translate("Form", "Pure Profit"))
        self.profile_total_wins_label.setText(_translate("Form", "+0.12304₿"))
        self.label_22.setText(_translate("Form", "Total Wins"))
        self.label_23.setText(_translate("Form", "Total Losses"))
        self.profile_total_losses_label.setText(_translate("Form", "+0.12304₿"))
        self.label_11.setText(_translate("Form", "BTC PRICE"))
        self.btc_price.setText(_translate("Form", f"{API.btc()[0].split('.')[0]}$"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
