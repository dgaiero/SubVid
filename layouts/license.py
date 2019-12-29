# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'license.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(765, 485)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(500, 0))
        Dialog.setMaximumSize(QtCore.QSize(780, 505))
        Dialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(300, 84))
        self.label_2.setMaximumSize(QtCore.QSize(300, 84))
        self.label_2.setSizeIncrement(QtCore.QSize(1, 2))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/logoHeaders/image_assets/logo_license_back_small.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.license_view_tab = QtWidgets.QWidget()
        self.license_view_tab.setObjectName("license_view_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.license_view_tab)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.licenseText = QtWidgets.QTextBrowser(self.license_view_tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.licenseText.sizePolicy().hasHeightForWidth())
        self.licenseText.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Courier New")
        self.licenseText.setFont(font)
        self.licenseText.setObjectName("licenseText")
        self.gridLayout_2.addWidget(self.licenseText, 0, 0, 1, 1)
        self.tabWidget.addTab(self.license_view_tab, "")
        self.view_addendum_tab = QtWidgets.QWidget()
        self.view_addendum_tab.setObjectName("view_addendum_tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.view_addendum_tab)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.addendumText = QtWidgets.QTextBrowser(self.view_addendum_tab)
        self.addendumText.setObjectName("addendumText")
        self.gridLayout_3.addWidget(self.addendumText, 0, 0, 1, 1)
        self.tabWidget.addTab(self.view_addendum_tab, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.viewLicenseOnlineButton = QtWidgets.QPushButton(Dialog)
        self.viewLicenseOnlineButton.setObjectName("viewLicenseOnlineButton")
        self.horizontalLayout_2.addWidget(self.viewLicenseOnlineButton)
        self.viewAddendumOnlineButton = QtWidgets.QPushButton(Dialog)
        self.viewAddendumOnlineButton.setObjectName("viewAddendumOnlineButton")
        self.horizontalLayout_2.addWidget(self.viewAddendumOnlineButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About"))
        self.label.setText(_translate("Dialog", "<html><head/><body><h1 style=\" margin-top:18px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:xx-large; font-weight:600;\">Copyright &copy; Dominic Gaiero 2019</span></h1><p>Developed and Designed by Dominic Gaiero This program is licensed under the GNU General Public License v3.0. This license is shown below and is generated from the online version. For an online version, click the button below.</p></body></html>"))
        self.licenseText.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Courier New\'; font-size:8.1pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Fira Code Medium\'; font-size:10pt;\"><br /></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.license_view_tab), _translate("Dialog", "View License"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.view_addendum_tab), _translate("Dialog", "View Addendum"))
        self.viewLicenseOnlineButton.setText(_translate("Dialog", "View License Online"))
        self.viewAddendumOnlineButton.setText(_translate("Dialog", "View Addendum Online"))
import main_images_rc
