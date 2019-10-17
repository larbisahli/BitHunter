# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'log_in_window.ui'
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
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
import hashlib
import threading
import time
import log_image_rc
from dbManagement import *


# identity = hash_(str(username) + str(password))

# the username / Gmail / password (for sending it via Gmail if the user forget)

def current_time():
    now = datetime.datetime.now()
    current_time_ = datetime.time(hour=now.hour, minute=now.minute).strftime('%I:%M%p').lstrip('0')
    return current_time_


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(310, 585)
        Form.setFixedSize(310, 585)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/log_pic/Images/picabout.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        Form.setWindowIcon(icon)
        Form.setStyleSheet("\n"
                           "\n"
                           "\n"
                           "*{background-image: url(:/log_pic/Images/BG.png);}\n"
                           "\n"
                           "QFrame{\n"
                           "background: rgba(150, 150, 150,0.9);\n"
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
                           "border-radius:55px\n"
                           "}\n"
                           "QLabel{\n"
                           "background:transparent;\n"
                           "    color: rgb(0, 0, 0);\n"
                           " font: 75 12pt \"MS Shell Dlg 2\";\n"
                           "}\n"
                           "\n"
                           "QLineEdit{\n"
                           "color: rgb(0, 0, 0);\n"
                           "font: 75 12pt \"MS Shell Dlg 2\";\n"
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
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(10, 110, 291, 421))
        self.frame_2.setStyleSheet("")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.btn_sighnin = QtWidgets.QPushButton(self.frame_2)
        self.btn_sighnin.setGeometry(QtCore.QRect(126, 330, 141, 31))
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
        self.btn_sighnin.setObjectName("btn_sighnin")
        self.btn_sighnin.clicked.connect(self.sign_in)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(0, 60, 291, 41))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.input_signin_username = QtWidgets.QLineEdit(self.frame_2)
        self.input_signin_username.setGeometry(QtCore.QRect(30, 130, 241, 31))
        self.input_signin_username.setStyleSheet("color: rgb(0, 0, 0);")
        self.input_signin_username.setText("")
        self.input_signin_username.setObjectName("input_signin_username")
        self.input_signin_password = QtWidgets.QLineEdit(self.frame_2)
        self.input_signin_password.setGeometry(QtCore.QRect(30, 210, 241, 31))
        self.input_signin_password.setStyleSheet("color: rgb(0, 0, 0);")
        self.input_signin_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.input_signin_password.setObjectName("input_signin_password")
        self.check_remember_me = QtWidgets.QRadioButton(self.frame_2)
        self.check_remember_me.setEnabled(True)
        self.check_remember_me.setGeometry(QtCore.QRect(30, 280, 121, 21))
        self.check_remember_me.setStyleSheet("color: rgb(0, 0, 0);")
        self.check_remember_me.setChecked(True)
        self.check_remember_me.setObjectName("check_remember_me")
        self.check_remember_me.clicked.connect(lambda: self.check())
        self.label_3 = QtWidgets.QLabel(self.frame_2)
        self.label_3.setGeometry(QtCore.QRect(30, 100, 91, 21))
        self.label_3.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";color: rgb(0, 0, 0);")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(30, 180, 91, 21))
        self.label_4.setStyleSheet("font: 75 10pt \"MS Shell Dlg 2\";color: rgb(0, 0, 0);")
        self.label_4.setObjectName("label_4")
        self.btn_register = QtWidgets.QPushButton(self.frame_2)
        self.btn_register.setGeometry(QtCore.QRect(26, 330, 61, 31))
        self.btn_register.setStyleSheet("*{\n"
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
                                         "background:  rgb(211, 211,211);\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "\n"
                                         "QPushButton:hover{\n"
                                         "\n"
                                         "color: rgb(225, 150, 0);\n"
                                         "    background-color: rgb(55, 55,55);\n"
                                         "border-radius:10px;\n"
                                         "font: 75 10pt \"MS Shell Dlg 2\";\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:pressed \n"
                                         "{\n"
                                         " border: 2px inset   rgb(225, 150, 0);\n"
                                         "background-color: #333;\n"
                                         "}")
        self.btn_register.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/log_pic/Images/add-user-male-52.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_register.setIcon(icon1)
        self.btn_register.setObjectName("btn_register")
        self.btn_register.clicked.connect(self.register)

        self.frame_image = QtWidgets.QToolButton(Form)
        self.frame_image.setGeometry(QtCore.QRect(96, 50, 111, 111))
        self.frame_image.setStyleSheet("border-radius:55px;\n"
                                        "background: rgb(203, 135, 0);\n"
                                        "background-color: rgb(255,215,0);\n"
                                        "\n"
                                        "")
        self.frame_image.setText("")
        self.frame_image.setObjectName("frame_image")
        self.image_frame = QtWidgets.QToolButton(Form)
        self.image_frame.setGeometry(QtCore.QRect(101, 55, 101, 101))
        self.image_frame.setAutoFillBackground(False)
        self.image_frame.setStyleSheet("border-radius:50px;\n"
                                       "\n"
                                       "background-color: rgb(150, 150, 150);\n"
                                       "\n"
                                       "background-image: url(:/log_pic/Images/user_image.png);\n"
                                       "background-image: url(:/log_pic/Images/Avatar.png);")
        self.image_frame.setText("")
        self.image_frame.setObjectName("image_frame")
        self.down_bar_label = QtWidgets.QLabel(Form)
        self.down_bar_label.setGeometry(QtCore.QRect(0, 560, 311, 25))
        self.down_bar_label.setStyleSheet("color:  rgb(211, 211, 211);\n"
                                          "background: rgb(51, 51, 51);\n"
                                          "font: 8pt \"Bahnschrift\";")
        self.down_bar_label.setFrameShape(QtWidgets.QFrame.Panel)
        self.down_bar_label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.down_bar_label.setLineWidth(1)
        self.down_bar_label.setMidLineWidth(0)
        self.down_bar_label.setIndent(10)
        self.down_bar_label.setObjectName("down_bar_label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.check()

    def check(self):
        _translate = QtCore.QCoreApplication.translate
        check = False
        Table("sign").create()
        pre_list_ = Extract("sign").select_column(column="pass")
        len_ = len(pre_list_)
        if len_ != 0:
            check = True
            list_ = Extract("sign").get_by_column(column="pass", cell=pre_list_[len_-1])
        else:
            self.input_signin_username.setText(_translate("Form", ""))
            self.input_signin_password.setText(_translate("Form", ""))
            list_ = []

        if self.check_remember_me.isChecked() and check:
            self.input_signin_username.setText(_translate("Form", f"{decrypt(list_[0])}"))
            self.input_signin_password.setText(_translate("Form", f"{decrypt(list_[1])}"))
        elif not self.check_remember_me.isChecked() and check:
            self.input_signin_username.setText(_translate("Form", ""))
            self.input_signin_password.setText(_translate("Form", ""))

    def register(self):

        username = str(self.input_signin_username.text())
        password = str(self.input_signin_password.text())
        Table("sign").create()
        list_ = Extract("sign").select_column(column="username")
        if len(list_) == 0:
            Sign(password=password, username=username).insert()
        else:
            if not encrypt(username) in list_:
                Sign(password=password, username=username).insert()
            else:
                msg = QMessageBox()
                msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Input Error")
                msg.setInformativeText(
                    "Username already exist")
                msg.setWindowTitle("input-Error")
                msg.exec_()

    def sign_in(self):

        username = str(self.input_signin_username.text())
        password = str(self.input_signin_password.text())
        current_user = {"identity": hash_(username+password)}
        import pickle
        with open("current_access.txt", "wb") as w:
            pickle.dump(current_user, w)
        Table("sign").create()
        list_ = Extract("sign").get_by_column(column="pass", cell=hash_(username))
        if hash_(username) in list_ and list_[1] == encrypt(password):
            from MainWindow import Ui_Form
            self.ui = Ui_Form()
            self.Form = QtWidgets.QWidget()
            self.ui.setupUi(self.Form)
            #self.ui.graph()
            self.Form.show()
            time.sleep(2)
            Form.close()
        else:
            msg = QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('Images\\MainWinTite.png'))
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Input Error")
            msg.setInformativeText(
                "The account does not exist")
            msg.setWindowTitle("input-Error")
            msg.exec_()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Log-in"))
        self.btn_sighnin.setText(_translate("Form", "Sign In"))
        self.label_2.setText(_translate("Form", "Login to your Account"))
        self.input_signin_username.setPlaceholderText(_translate("Form", "Username"))
        self.input_signin_password.setPlaceholderText(_translate("Form", "Password"))
        self.check_remember_me.setText(_translate("Form", "Remember me"))
        self.label_3.setText(_translate("Form", "Username"))
        self.label_4.setText(_translate("Form", "Password"))
        self.down_bar_label.setText(_translate("Form", "BitHunter                                                     "
                                                       "                                 "
                                                       f"             {current_time()}"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
