# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'image_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImageViewer(object):
    def setupUi(self, ImageViewer):
        ImageViewer.setObjectName("ImageViewer")
        ImageViewer.setWindowModality(QtCore.Qt.NonModal)
        ImageViewer.resize(960, 540)
        ImageViewer.setIconSize(QtCore.QSize(20, 20))
        self.centralwidget = QtWidgets.QWidget(ImageViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.preview_graphic = QtWidgets.QGraphicsView(self.centralwidget)
        self.preview_graphic.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.preview_graphic.setObjectName("preview_graphic")
        self.gridLayout.addWidget(self.preview_graphic, 0, 0, 1, 1)
        ImageViewer.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(ImageViewer)
        self.statusbar.setEnabled(False)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        ImageViewer.setStatusBar(self.statusbar)

        self.retranslateUi(ImageViewer)
        QtCore.QMetaObject.connectSlotsByName(ImageViewer)

    def retranslateUi(self, ImageViewer):
        _translate = QtCore.QCoreApplication.translate
        ImageViewer.setWindowTitle(_translate("ImageViewer", "Image Viewer"))
