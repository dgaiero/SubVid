# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_not_found.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FileNotFound(object):
    def setupUi(self, FileNotFound):
        FileNotFound.setObjectName("FileNotFound")
        FileNotFound.setWindowModality(QtCore.Qt.ApplicationModal)
        FileNotFound.resize(855, 429)
        self.centralwidget = QtWidgets.QWidget(FileNotFound)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.headerText = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.headerText.setFont(font)
        self.headerText.setObjectName("headerText")
        self.verticalLayout.addWidget(self.headerText)
        self.descriptionText = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.descriptionText.setFont(font)
        self.descriptionText.setObjectName("descriptionText")
        self.verticalLayout.addWidget(self.descriptionText)
        self.file_locator_view = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.file_locator_view.sizePolicy().hasHeightForWidth())
        self.file_locator_view.setSizePolicy(sizePolicy)
        self.file_locator_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.file_locator_view.setDragEnabled(False)
        self.file_locator_view.setAlternatingRowColors(True)
        self.file_locator_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.file_locator_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.file_locator_view.setShowGrid(False)
        self.file_locator_view.setObjectName("file_locator_view")
        self.file_locator_view.setColumnCount(0)
        self.file_locator_view.setRowCount(0)
        self.file_locator_view.horizontalHeader().setStretchLastSection(True)
        self.file_locator_view.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.file_locator_view)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.locateButton = QtWidgets.QPushButton(self.centralwidget)
        self.locateButton.setObjectName("locateButton")
        self.horizontalLayout.addWidget(self.locateButton)
        self.clearFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.clearFileButton.setObjectName("clearFileButton")
        self.horizontalLayout.addWidget(self.clearFileButton)
        self.closeButton = QtWidgets.QPushButton(self.centralwidget)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        FileNotFound.setCentralWidget(self.centralwidget)

        self.retranslateUi(FileNotFound)
        QtCore.QMetaObject.connectSlotsByName(FileNotFound)

    def retranslateUi(self, FileNotFound):
        _translate = QtCore.QCoreApplication.translate
        FileNotFound.setWindowTitle(_translate("FileNotFound", "File(s) Not Found"))
        self.headerText.setText(_translate("FileNotFound", "The following files could not be found"))
        self.descriptionText.setText(_translate("FileNotFound", "Select a file for more actions"))
        self.file_locator_view.setSortingEnabled(True)
        self.locateButton.setText(_translate("FileNotFound", "Locate"))
        self.clearFileButton.setText(_translate("FileNotFound", "Clear File"))
        self.closeButton.setText(_translate("FileNotFound", "Quit"))
