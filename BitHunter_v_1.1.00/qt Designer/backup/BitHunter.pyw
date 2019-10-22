# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!

import onetimepad
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import hashlib
import threading
import time
from PyQt5.QtWidgets import QMessageBox


def hash_password(password):  # password hash
    return hashlib.sha256(password.encode()).hexdigest()


key = "8bd305eff112e6a5289f4d0c43b412d06a7285d7c23510fb87d156703b06dcb6"  # the key to encrypt and decrypt
# the username / Gmail / password (for sending it via Gmail if the user forget)

conn_sign = sqlite3.connect('pre_database.db', check_same_thread=False)
c_sign = conn_sign.cursor()
lock = threading.Lock()

"""Database management"""


class Table:

    def __init__(self, name):
        self.name = name

    def create_table(self):
        c_sign.execute(f"""CREATE TABLE {self.name}(
        id INTEGER PRIMARY KEY,
        data STRING
        )""")

    def drop_table(self):
        sql = f"DROP TABLE {self.name}"
        c_sign.execute(sql)

    def check_table(self):
        try:
            c_sign.execute(f"select * from '{self.name}'")
            return True
        except sqlite3.Error:
            return False

    def shift_table(self):
        InsertData(1, 'processed_data_' + str(int(self.name.split('_')[2]) + 1), 'table_shift').update_data()


class InsertData:

    def __init__(self, _id_, _data_, name):
        self._id_ = _id_
        self._data_ = _data_
        self.name = name

    def insert_data(self):
        with conn_sign:
            c_sign.execute(f"INSERT INTO {self.name} VALUES (:id, :data)",
                           {'id': self._id_, 'data': self._data_})

    def update_data(self):
        try:
            lock.acquire(True)
            with conn_sign:
                c_sign.execute(f"""UPDATE {self.name} SET data = :data WHERE id = :id""",
                               {'id': self._id_, 'data': self._data_})

        except sqlite3.Error:
            print("sqlite3.Error in update")
            pass
        except sqlite3.ProgrammingError:
            pass
        finally:
            lock.release()


class ExtractData:

    def __init__(self, _id_, name):
        self._id_ = _id_
        self.name = name

    def get_data(self):
        try:
            lock.acquire(True)
            c_sign.execute(f"SELECT * FROM {self.name} WHERE id= :id", {'id': self._id_})
            return c_sign.fetchall()
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def get_(self, data):
        try:
            lock.acquire(True)
            c_sign.execute(f"SELECT * FROM {self.name} WHERE data= :data", {'data': data})
            return c_sign.fetchall()
        except sqlite3.Error:
            pass
        finally:
            lock.release()

    def check_data(self, data):
        if str(ExtractData(self._id_, self.name).get_(data)) != '[]':
            return True

        else:
            return False

    def delete(self):
        with conn_sign:
            c_sign.execute(f"DELETE from {self.name} WHERE id = :id",
                           {'id': self._id_})


def xquit():  # helps to break the while loop for the update in the mainwindow
    if not Table('close').check_table():
        Table('close').create_table()
        data = 1
        InsertData(1, str(data), 'close').insert_data()
    else:
        data = 1
        InsertData(1, str(data), 'close').update_data()


class Ui_log_window(object):

    def setupUi(self, log_window):
        log_window.setObjectName("log_window")

        log_window.resize(391, 641)
        log_window.setFixedSize(391, 641)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/log/Images/MainWinTite.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        log_window.setWindowIcon(icon)
        log_window.setLayoutDirection(QtCore.Qt.LeftToRight)
        log_window.setAutoFillBackground(False)
        log_window.setStyleSheet("*{background-image: url(:/background/Images/bgi.png);}\n"
                                 "\n"
                                 "QFrame{\n"
                                 "background: rgba(211, 211, 211,0.9);\n"
                                 "\n"
                                 " border-radius:15px\n"
                                 "}\n"
                                 "\n"
                                 "QPushButton{\n"
                                 "color: rgb(255, 255, 255);\n"
                                 "background: #333;\n"
                                 "border-radius:10px;\n"
                                 "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                 "}\n"
                                 "\n"
                                 "\n"
                                 "QPushButton:hover{\n"
                                 "color: rgb(225, 150, 0);\n"
                                 "    background-color: rgb(0, 0, 0);\n"
                                 "border-radius:10px;\n"
                                 "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                 "}\n"
                                 "\n"
                                 "QToolButton{\n"
                                 "background: rgb(211, 211, 211);\n"
                                 "border-radius:55px 20px 20px 55px;\n"
                                 "}\n"
                                 "QLabel{\n"
                                 "background:transparent;\n"
                                 "    color: rgb(0, 0, 0);\n"
                                 " font: 75 12pt \"MS Shell Dlg 2\";\n"
                                 "}\n"
                                 "\n"
                                 "QLineEdit{\n"
                                 "color: rgb(0, 0, 0);\n"
                                 "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                 "background:transparent;\n"
                                 "border-radius:10px;\n"
                                 "border:none;\n"
                                 "border-bottom: 1px solid #717072 ;\n"
                                 "}\n"
                                 "\n"
                                 "QRadioButton{\n"
                                 "background:transparent;\n"
                                 "color: #d3d3d3;\n"
                                 " \n"
                                 "    font: 8pt \"Yu Gothic\";\n"
                                 "}")
        self.frame_2 = QtWidgets.QFrame(log_window)
        self.frame_2.setGeometry(QtCore.QRect(36, 106, 321, 441))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.btn_sighnin = QtWidgets.QPushButton(self.frame_2)
        self.btn_sighnin.setGeometry(QtCore.QRect(40, 360, 241, 31))
        self.btn_sighnin.setObjectName("btn_sighnin")
        self.btn_sighnin.setStyleSheet("*{\n"
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

        self.btn_sighnin.clicked.connect(self.sign_in)

        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(70, 60, 221, 41))
        self.label_2.setObjectName("label_2")

        self.input_signin_username = QtWidgets.QLineEdit(self.frame_2)
        self.input_signin_username.setGeometry(QtCore.QRect(40, 140, 241, 31))
        self.input_signin_username.setStyleSheet("")
        self.input_signin_username.setText("")
        self.input_signin_username.setObjectName("input_signin_username")
        self.input_signin_password = QtWidgets.QLineEdit(self.frame_2)
        self.input_signin_password.setGeometry(QtCore.QRect(40, 220, 241, 31))
        self.input_signin_password.setStyleSheet("")
        self.input_signin_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_signin_password.setObjectName("input_signin_password")
        self.check_remember_me = QtWidgets.QRadioButton(self.frame_2)
        self.check_remember_me.setGeometry(QtCore.QRect(40, 320, 121, 21))
        self.check_remember_me.setStyleSheet("color: rgb(0, 0, 0);")
        self.check_remember_me.setObjectName("check_remember_me")
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(40, 100, 91, 41))
        self.label_3.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";color: rgb(0, 0, 0);")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(40, 180, 211, 41))
        self.label_4.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";color: rgb(0, 0, 0);")
        self.label_4.setObjectName("label_4")

        self.btn_sighnin_2 = QtWidgets.QPushButton(self.frame_2)
        self.btn_sighnin_2.setGeometry(QtCore.QRect(57, 400, 71, 31))
        self.btn_sighnin_2.setStyleSheet("\n"
                                         "\n"
                                         "QPushButton{\n"
                                         "color:rgb(51, 51, 51);\n"
                                         "background: transparent;\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "color: rgb(225, 150, 0);\n"
                                         "    background-color: transparent;\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:pressed \n"
                                         "{\n"
                                         " border: 2px inset   rgb(225, 150, 0);\n"
                                         "background-color: #333;\n"
                                         "}")
        self.btn_sighnin_2.setObjectName("btn_sighnin_2")

        self.btn_sighnin_2.clicked.connect(self.register)

        self.btn_sighnin_3 = QtWidgets.QPushButton(self.frame_2)
        self.btn_sighnin_3.setGeometry(QtCore.QRect(190, 400, 71, 31))
        self.btn_sighnin_3.setStyleSheet("\n"
                                         "\n"
                                         "QPushButton{\n"
                                         "color:rgb(51, 51, 51);\n"
                                         "background: transparent;\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "color: rgb(225, 150, 0);\n"
                                         "    background-color: transparent;\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:pressed \n"
                                         "{\n"
                                         " border: 2px inset   rgb(225, 150, 0);\n"
                                         "background-color: #333;\n"
                                         "}")
        self.btn_sighnin_3.setObjectName("btn_sighnin_3")
        self.btn_sighnin_3.clicked.connect(self.forget)

        self.line = QtWidgets.QFrame(self.frame_2)
        self.line.setGeometry(QtCore.QRect(156, 400, 3, 30))
        self.line.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.input_signin_password_2 = QtWidgets.QLineEdit(self.frame_2)
        self.input_signin_password_2.setGeometry(QtCore.QRect(40, 270, 241, 31))
        self.input_signin_password_2.setStyleSheet("QLineEdit{\n"
                                                   "color: rgb(0, 0, 0);\n"
                                                   "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                   "background:transparent;\n"
                                                   "border-radius:10px;\n"
                                                   "border:none;\n"
                                                   "border-bottom: 0px solid #717072 ;\n"
                                                   "}\n")
        self.input_signin_password_2.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.input_signin_password_2.setReadOnly(True)
        self.input_signin_password_2.setObjectName("input_signin_password_2")
        self.toolButton = QtWidgets.QToolButton(log_window)
        self.toolButton.setGeometry(QtCore.QRect(140, 50, 111, 111))
        self.toolButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/log/Images/male avatar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toolButton.setIcon(icon1)
        self.toolButton.setIconSize(QtCore.QSize(90, 90))
        self.toolButton.setObjectName("toolButton")

        self.retranslateUi(log_window)
        QtCore.QMetaObject.connectSlotsByName(log_window)
        # ------------------------
        self.check()
        app.aboutToQuit.connect(self.quit)  # break the loop when the window closed

    def quit(self):
        data = 0
        InsertData(1, str(data), 'close').update_data()

    def sign_in(self):
        # ----------------------------
        try:
            if self.input_signin_username.text() != "":

                if Table('last_re').check_table():
                    value = ExtractData(1, "last_re").get_data()[0][1]
                else:
                    value = 0

                    # ----------------------------
                _translate = QtCore.QCoreApplication.translate

                self.input_signin_password_2.setStyleSheet("QLineEdit{\n"
                                                           "color: rgb(0, 0, 0);\n"
                                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                           "background:transparent;\n"
                                                           "border-radius:10px;\n"
                                                           "border:none;\n"
                                                           "border-bottom: 0px solid #717072 ;\n"
                                                           "}\n")
                self.input_signin_password_2.setReadOnly(True)
                self.input_signin_password_2.setPlaceholderText(_translate("log_window", ""))

                encrypt_username = onetimepad.encrypt(str(self.input_signin_username.text()), key)

                data = {"username": encrypt_username,
                        "password": hash_password(str(self.input_signin_password.text()))}
                x = 0
                if str(self.input_signin_password_2.text()) != "" and value == 1:

                    try:

                        if str(self.input_signin_password_2.text()).split("@")[1] != "gmail.com":
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Information)
                            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
                            msg.setText("Gmail required!")
                            msg.setInformativeText('the program only support Gmail')
                            msg.setWindowTitle("Email Error")
                            msg.exec_()
                            self.input_signin_password_2.setReadOnly(False)
                        else:
                            encrypt_email = onetimepad.encrypt(str(self.input_signin_password_2.text()), key)
                            e_data = {"email": encrypt_email,
                                      "check": self.check_remember_me.isChecked()}

                            encrypt_pass = onetimepad.encrypt(str(self.input_signin_password.text()), key)

                            user_forget_data = {"username": encrypt_username}
                            pass_forget_data = {"password": encrypt_pass}

                            if not Table('sigh_in').check_table():
                                Table('sigh_in').create_table()
                                Table('email').create_table()
                                Table('user_forget').create_table()
                                Table('pass_forget').create_table()

                                InsertData(1, str(data), 'sigh_in').insert_data()
                                InsertData(1, str(pass_forget_data), 'pass_forget').insert_data()
                                InsertData(1, str(user_forget_data), 'user_forget').insert_data()
                                InsertData(1, str(e_data), 'email').insert_data()

                            else:

                                c_sign.execute("select * from 'sigh_in'")
                                count = c_sign.fetchall()

                                if not ExtractData(0, "sigh_in").check_data(str(data)) and \
                                        not ExtractData(0, "user_forget").check_data(str(user_forget_data)):

                                    InsertData(len(count) + 1, str(pass_forget_data), 'pass_forget').insert_data()
                                    InsertData(len(count) + 1, str(user_forget_data), 'user_forget').insert_data()
                                    InsertData(len(count) + 1, str(data), 'sigh_in').insert_data()
                                    InsertData(len(count) + 1, str(e_data), 'email').insert_data()
                                else:
                                    msg = QMessageBox()
                                    msg.setIcon(QMessageBox.Critical)
                                    msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
                                    msg.setText("Account-Error")
                                    msg.setInformativeText('The Username Already Exist!')
                                    msg.setWindowTitle("Error")
                                    msg.exec_()
                            self.input_signin_password_2.setText("")
                    except Exception:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setText("Gmail required!")
                        msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
                        msg.setInformativeText('enter the correct Gmail')
                        msg.setWindowTitle("Email Error")
                        msg.exec_()
                        x = 1
                        self.register()
                        pass
                else:

                    if ExtractData(0, "sigh_in").check_data(str(data)):
                        s_data = {"username": str(encrypt_username),
                                  "password": hash_password(str(self.input_signin_password.text())),
                                  "check": str(eval(ExtractData(int(ExtractData(0, 'sigh_in').get_(str(data))[0][0]),
                                                                'email').get_data()[0][1])['check'])}
                        if not Table('log_save').check_table():
                            Table('log_save').create_table()
                            InsertData(1, str(s_data), 'log_save').insert_data()

                        elif not ExtractData(1, 'log_save').get_data():

                            InsertData(1, str(s_data), 'log_save').insert_data()
                        else:

                            InsertData(1, str(s_data), 'log_save').update_data()

                        if self.check_remember_me.isChecked() or not self.check_remember_me.isChecked():
                            e_data = {
                                "email": str(eval(ExtractData(int(ExtractData(0, 'sigh_in').get_(str(data))[0][0]),
                                                              'email').get_data()[0][1])['email']),
                                "check": self.check_remember_me.isChecked()}
                            InsertData(int(ExtractData(0, 'sigh_in').get_(str(data))[0][0]), str(e_data),
                                       'email').update_data()

                        self.launcher()

                    else:
                        self.input_signin_password_2.setText(" The Account Does Not Exist!")
                        self.input_signin_password_2.setStyleSheet("color: rgb(255, 0, 0);"
                                                                   "border-bottom: 0px solid #717072 ;\n")
                if x == 0:
                    datax = 0
                else:
                    datax = 1
                if not Table('last_re').check_table():
                    Table('last_re').create_table()
                    InsertData(1, str(datax), 'last_re').insert_data()
                else:
                    InsertData(1, str(datax), 'last_re').update_data()
                x = 0
            else:

                self.input_signin_password.setStyleSheet("QLineEdit{\n"
                                                         "color: rgb(0, 0, 0);\n"
                                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                         "background:transparent;\n"
                                                         "border-radius:10px;\n"
                                                         "border:none;\n"
                                                         "border-bottom: 1px solid #717072 ;\n"
                                                         "}\n")
                self.input_signin_password_2.setStyleSheet("QLineEdit{\n"
                                                           "color: rgb(0, 0, 0);\n"
                                                           "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                           "background:transparent;\n"
                                                           "border-radius:10px;\n"
                                                           "border:none;\n"
                                                           "border-bottom: 0px solid #717072 ;\n"
                                                           "}\n")
                _translate = QtCore.QCoreApplication.translate
                self.input_signin_password.setReadOnly(False)
                self.label_4.setText(_translate("log_window", "Password"))
                self.input_signin_password.setPlaceholderText(_translate("log_window", "Password"))
                self.input_signin_password_2.setReadOnly(True)
                self.input_signin_password_2.setPlaceholderText(_translate("log_window", ""))
        except Exception:
            pass

    def register(self):
        try:
            self.input_signin_password.setStyleSheet("QLineEdit{\n"
                                                     "color: rgb(0, 0, 0);\n"
                                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                     "background:transparent;\n"
                                                     "border-radius:10px;\n"
                                                     "border:none;\n"
                                                     "border-bottom: 1px solid #717072 ;\n"
                                                     "}\n")
            _translate = QtCore.QCoreApplication.translate
            self.input_signin_password.setReadOnly(False)
            self.label_4.setText(_translate("log_window", "Password"))
            self.input_signin_password.setPlaceholderText(_translate("log_window", "Password"))
            self.label_2.setText(_translate("log_window", "    Register HERE"))

            self.input_signin_password_2.setStyleSheet("QLineEdit{\n"
                                                       "color: rgb(0, 0, 0);\n"
                                                       "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                       "background:transparent;\n"
                                                       "border-radius:10px;\n"
                                                       "border:none;\n"
                                                       "border-bottom: 1px solid #717072 ;\n"
                                                       "}\n")
            self.input_signin_password_2.setReadOnly(False)
            self.input_signin_password_2.setPlaceholderText(_translate("log_window", "Gmail"))
            self.input_signin_password_2.setText("")
            self.input_signin_password.setText("")
            self.input_signin_username.setText("")
            # --------------------
            data = 1
            if not Table('last_re').check_table():
                Table('last_re').create_table()
                InsertData(1, str(data), 'last_re').insert_data()
            else:
                InsertData(1, str(data), 'last_re').update_data()
        except Exception:
            pass
        # ------------------

    def forget(self):
        _translate = QtCore.QCoreApplication.translate
        try:
            self.input_signin_password_2.setStyleSheet("QLineEdit{\n"
                                                       "color: rgb(0, 0, 0);\n"
                                                       "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                       "background:transparent;\n"
                                                       "border-radius:10px;\n"
                                                       "border:none;\n"
                                                       "border-bottom: 0px solid #717072 ;\n"
                                                       "}\n")
            self.input_signin_password_2.setPlaceholderText(_translate("log_window", ""))
            self.input_signin_password.setStyleSheet("QLineEdit{\n"
                                                     "color: rgb(0, 0, 0);\n"
                                                     "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                     "background:transparent;\n"
                                                     "border-radius:10px;\n"
                                                     "border:none;\n"
                                                     "border-bottom: 0px solid #717072 ;\n"
                                                     "}\n")
            self.input_signin_password.setReadOnly(True)
            self.input_signin_password.setPlaceholderText(_translate("log_window", ""))
            self.input_signin_password.setText("")
            self.input_signin_password_2.setText("")

            if str(self.input_signin_username.text()) == "":
                self.label_4.setText(_translate("log_window", "Enter Your Username"))
                self.btn_sighnin_3.setText(_translate("log_window", "Submit"))
                self.input_signin_password_2.setText("")

            else:
                encrypt_username = onetimepad.encrypt(str(self.input_signin_username.text()), key)

                user_forget_data = {"username": encrypt_username}
                id_ = ExtractData(0, 'user_forget').get_(str(user_forget_data))[0][0]

                password = eval(ExtractData(id_, 'pass_forget').get_data()[0][1])["password"]

                decrypt = onetimepad.decrypt(password, key)
                email = onetimepad.decrypt(eval(ExtractData(id_, 'email').get_data()[0][1])["email"], key)
                # --------------------
                import smtplib

                text = f"Hello {onetimepad.decrypt(encrypt_username, key)}!\nThis is your Password: {decrypt}\n\n" \
                    f"\nThank you for using BitHunter Journal."
                subject = "Bitcoin Trading Journal"

                content = 'Subject: {}\n\n{}'.format(subject, text)

                mail = smtplib.SMTP("smtp.gmail.com", 587)
                mail.ehlo()
                mail.starttls()

                mail.login("larbisahili95@gmail.com", "iloverobots1905")  # use a Gmail to send the user their password

                mail.sendmail("larbisahili95@gmail.com", f"{email}", content)

                mail.close()

                # --------------------
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
                msg.setText("DONE!")
                msg.setInformativeText(f'we sent your password to this Gmail Address:\n{email}')
                msg.setWindowTitle("Check Your Mail")
                msg.exec_()

                self.btn_sighnin_3.setText(_translate("log_window", "Forget"))
                self.input_signin_password.setStyleSheet("QLineEdit{\n"
                                                         "color: rgb(0, 0, 0);\n"
                                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                                         "background:transparent;\n"
                                                         "border-radius:10px;\n"
                                                         "border:none;\n"
                                                         "border-bottom: 1px solid #717072 ;\n"
                                                         "}\n")
                self.input_signin_password.setReadOnly(False)
                self.input_signin_password.setPlaceholderText(_translate("log_window", "Password"))

        except Exception:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Username_Error")
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.ico'))
            msg.setInformativeText('username not found')
            msg.setWindowTitle("Oops!")
            msg.exec_()
            self.input_signin_username.setText(_translate("log_window", ""))

    def launcher(self):  # launch the mainwindow and hide
        from MainWindow import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui.setupUi(self.MainWindow)
        self.ui.graph()
        self.MainWindow.show()
        time.sleep(2)
        log_window.close()

    def check(self):

        if Table("log_save").check_table():
            check = eval(ExtractData(1, "log_save").get_data()[0][1])["check"]
            if check == "True":
                self.check_remember_me.setChecked(True)
                _translate = QtCore.QCoreApplication.translate
                username = eval(ExtractData(1, "log_save").get_data()[0][1])["username"]

                user_forget_data = {"username": str(username)}
                id_ = ExtractData(0, 'user_forget').get_(str(user_forget_data))[0][0]

                password = eval(ExtractData(id_, 'pass_forget').get_data()[0][1])["password"]

                decrypt = onetimepad.decrypt(password, key)
                self.input_signin_username.setText(_translate("log_window", f"{onetimepad.decrypt(username, key)}"))
                self.input_signin_password.setText(_translate("log_window", f"{decrypt}"))

    def retranslateUi(self, log_window):
        _translate = QtCore.QCoreApplication.translate
        log_window.setWindowTitle(_translate("log_window", "BitHunter Journal-log in"))
        self.btn_sighnin.setText(_translate("log_window", "Sign In"))
        self.label_2.setText(_translate("log_window", "Login to your Account"))
        self.input_signin_username.setPlaceholderText(_translate("log_window", "Username"))
        self.input_signin_password.setPlaceholderText(_translate("log_window", "Password"))
        self.check_remember_me.setText(_translate("log_window", "Remember me"))
        self.label_3.setText(_translate("log_window", "Username"))
        self.label_4.setText(_translate("log_window", "Password"))
        self.btn_sighnin_2.setText(_translate("log_window", "Register"))
        self.btn_sighnin_3.setText(_translate("log_window", "Forget"))


import pictures_rc

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    log_window = QtWidgets.QWidget()
    ui = Ui_log_window()
    ui.setupUi(log_window)
    log_window.show()
    sys.exit(app.exec_())
