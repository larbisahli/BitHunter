# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(899, 379)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon/Images/MainWinTite.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        Form.setStyleSheet("background-color: rgb(63, 0, 191);\n"
                           "background-color: rgb(36, 0, 108);")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(30, 40, 201, 201))
        self.frame.setAutoFillBackground(False)
        self.frame.setStyleSheet("\n"
                                 "background-image: url(:/icon/Images/picabout.png);\n"
                                 "\n"
                                 "border-radius: 100px;\n"
                                 "")
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(3)
        self.frame.setObjectName("frame")
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setGeometry(QtCore.QRect(270, 20, 601, 350))
        self.frame_2.setStyleSheet("font: 12pt \"Bahnschrift\";\n"
                                   "color: rgb(211, 211, 211);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_2.setLineWidth(0)
        self.frame_2.setObjectName("frame_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(10, 10, 381, 41))
        self.label.setStyleSheet("font: 20pt \"Bahnschrift\";\n"
                                 "color: rgb(255, 255, 255);")
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 541, 101))
        self.label_2.setScaledContents(False)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        self.label_4.setGeometry(QtCore.QRect(10, 160, 511, 31))
        self.label_4.setObjectName("label_4")
        self.textEdit = QtWidgets.QTextEdit(self.frame_2)
        self.textEdit.setGeometry(QtCore.QRect(10, 260, 591, 61))
        self.textEdit.setStyleSheet(
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:1 rgba(103, 0, 0, 255));")
        self.textEdit.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit.setReadOnly(True)
        self.textEdit.setOverwriteMode(False)
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(self.frame_2)
        self.textEdit_2.setGeometry(QtCore.QRect(10, 210, 591, 61))
        self.textEdit_2.setStyleSheet(
            "selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:1 rgba(103, 0, 0, 255));")
        self.textEdit_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.textEdit_2.setFrameShadow(QtWidgets.QFrame.Plain)
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setOverwriteMode(False)
        self.textEdit_2.setObjectName("textEdit_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "About BitHunter"))
        self.label.setText(_translate("Form", "Bitcoin Hunter Journal v1.1.00"))
        self.label_2.setText(_translate("Form",
                                        "Lightweight trading journal desktop application with multiple features "
                                        "including import and export of dataset, automated charting and analyzing of "
                                        "data, and live Bitcoin, Ethereum, Litecoin prices."))
        self.label_4.setText(_translate("Form", "Copyright of Larbi Sahli. ALL Rights Reserved."))
        self.textEdit.setHtml(_translate("Form",
                                         "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" "
                                         "\"http://www.w3.org/TR/REC-html40/strict.dtd\">\n "
                                         "<html><head><meta name=\"qrichtext\" content=\"1\" /><style "
                                         "type=\"text/css\">\n "
                                         "p, li { white-space: pre-wrap; }\n"
                                         "</style></head><body style=\" font-family:\'Bahnschrift\'; font-size:12pt; "
                                         "font-weight:400; font-style:normal;\">\n "
                                         "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; "
                                         "margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" "
                                         "font-family:\'MS Shell Dlg 2\'; font-size:9pt; color:#d4d4d4;\">Want to "
                                         "help? Make a Donation: </span><span style=\" font-family:\'MS Shell Dlg "
                                         "2\'; font-size:9pt; color:#e29300;\">BTC</span><span style=\" "
                                         "font-family:\'MS Shell Dlg 2\'; font-size:9pt; color:#d4d4d4;\"> "
                                         "-</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:9pt;\"> "
                                         "</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:9pt; "
                                         "color:#ffffff;\">1MkivnZjnK2HpDwWY9dH9VkEaGe8TZttRD</span></p></body></html"
                                         ">"))
        self.textEdit_2.setHtml(_translate("Form",
                                           "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" "
                                           "\"http://www.w3.org/TR/REC-html40/strict.dtd\">\n "
                                           "<html><head><meta name=\"qrichtext\" content=\"1\" /><style "
                                           "type=\"text/css\">\n "
                                           "p, li { white-space: pre-wrap; }\n"
                                           "</style></head><body style=\" font-family:\'Bahnschrift\'; "
                                           "font-size:12pt; font-weight:400; font-style:normal;\">\n "
                                           "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; "
                                           "margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" "
                                           "font-family:\'MS Shell Dlg 2\'; font-size:11pt; "
                                           "color:#ffffff;\">Github:</span><span style=\" font-family:\'MS Shell Dlg "
                                           "2\'; font-size:11pt; color:#d3d3d3;\"> "
                                           "https://github.com/Larbi-Sahli</span></p></body></html>"))


import mainW_rc

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
