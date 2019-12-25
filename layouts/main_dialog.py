# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        MainWindow.setEnabled(True)
        MainWindow.resize(1000, 500)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(578, 357))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 500))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        font.setKerning(True)
        MainWindow.setFont(font)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        MainWindow.setDockNestingEnabled(False)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.sound_track_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.sound_track_label.setFont(font)
        self.sound_track_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sound_track_label.setObjectName("sound_track_label")
        self.gridLayout.addWidget(self.sound_track_label, 1, 0, 1, 1)
        self.source_time_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.source_time_label.setFont(font)
        self.source_time_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.source_time_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.source_time_label.setObjectName("source_time_label")
        self.gridLayout.addWidget(self.source_time_label, 0, 0, 1, 1)
        self.sound_track_button = QtWidgets.QPushButton(self.centralwidget)
        self.sound_track_button.setObjectName("sound_track_button")
        self.gridLayout.addWidget(self.sound_track_button, 1, 2, 1, 1)
        self.source_time_tb = QtWidgets.QLineEdit(self.centralwidget)
        self.source_time_tb.setEnabled(False)
        self.source_time_tb.setInputMethodHints(QtCore.Qt.ImhNone)
        self.source_time_tb.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.source_time_tb.setObjectName("source_time_tb")
        self.gridLayout.addWidget(self.source_time_tb, 0, 1, 1, 1)
        self.sound_track_tb = QtWidgets.QLineEdit(self.centralwidget)
        self.sound_track_tb.setEnabled(False)
        self.sound_track_tb.setObjectName("sound_track_tb")
        self.gridLayout.addWidget(self.sound_track_tb, 1, 1, 1, 1)
        self.source_time_button = QtWidgets.QPushButton(self.centralwidget)
        self.source_time_button.setObjectName("source_time_button")
        self.gridLayout.addWidget(self.source_time_button, 0, 2, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frame_preview = QtWidgets.QVBoxLayout()
        self.frame_preview.setObjectName("frame_preview")
        self.preview_graphic = QtWidgets.QGraphicsView(self.centralwidget)
        self.preview_graphic.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.preview_graphic.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_graphic.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_graphic.setObjectName("preview_graphic")
        self.frame_preview.addWidget(self.preview_graphic)
        self.frame_controls = QtWidgets.QHBoxLayout()
        self.frame_controls.setObjectName("frame_controls")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.frame_controls.addItem(spacerItem)
        self.frame_previous_button = QtWidgets.QPushButton(self.centralwidget)
        self.frame_previous_button.setObjectName("frame_previous_button")
        self.frame_controls.addWidget(self.frame_previous_button)
        self.refresh_button = QtWidgets.QPushButton(self.centralwidget)
        self.refresh_button.setObjectName("refresh_button")
        self.frame_controls.addWidget(self.refresh_button)
        self.frame_next_button = QtWidgets.QPushButton(self.centralwidget)
        self.frame_next_button.setObjectName("frame_next_button")
        self.frame_controls.addWidget(self.frame_next_button)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.frame_controls.addItem(spacerItem1)
        self.frame_preview.addLayout(self.frame_controls)
        self.horizontalLayout_2.addLayout(self.frame_preview)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.font_choice_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.font_choice_label.setFont(font)
        self.font_choice_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.font_choice_label.setObjectName("font_choice_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.font_choice_label)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.font_tb = QtWidgets.QLineEdit(self.centralwidget)
        self.font_tb.setEnabled(False)
        self.font_tb.setObjectName("font_tb")
        self.horizontalLayout_4.addWidget(self.font_tb)
        self.font_button = QtWidgets.QPushButton(self.centralwidget)
        self.font_button.setObjectName("font_button")
        self.horizontalLayout_4.addWidget(self.font_button)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.formLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.font_size_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.font_size_label.setFont(font)
        self.font_size_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.font_size_label.setObjectName("font_size_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.font_size_label)
        self.font_size_tb = QtWidgets.QSpinBox(self.centralwidget)
        self.font_size_tb.setMinimumSize(QtCore.QSize(70, 0))
        self.font_size_tb.setMinimum(1)
        self.font_size_tb.setMaximum(10000)
        self.font_size_tb.setSingleStep(1)
        self.font_size_tb.setObjectName("font_size_tb")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.font_size_tb)
        self.horizontalLayout.addLayout(self.formLayout_2)
        self.red_layout_2 = QtWidgets.QFormLayout()
        self.red_layout_2.setObjectName("red_layout_2")
        self.red_label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.red_label_2.setFont(font)
        self.red_label_2.setObjectName("red_label_2")
        self.red_layout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.red_label_2)
        self.red_spin_box_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.red_spin_box_2.setMaximum(255)
        self.red_spin_box_2.setObjectName("red_spin_box_2")
        self.red_layout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.red_spin_box_2)
        self.horizontalLayout.addLayout(self.red_layout_2)
        self.green_layout = QtWidgets.QFormLayout()
        self.green_layout.setObjectName("green_layout")
        self.green_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.green_label.setFont(font)
        self.green_label.setObjectName("green_label")
        self.green_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.green_label)
        self.green_spin_box = QtWidgets.QSpinBox(self.centralwidget)
        self.green_spin_box.setMaximum(255)
        self.green_spin_box.setObjectName("green_spin_box")
        self.green_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.green_spin_box)
        self.horizontalLayout.addLayout(self.green_layout)
        self.blue_layout = QtWidgets.QFormLayout()
        self.blue_layout.setObjectName("blue_layout")
        self.blue_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.blue_label.setFont(font)
        self.blue_label.setObjectName("blue_label")
        self.blue_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.blue_label)
        self.blue_spin_box = QtWidgets.QSpinBox(self.centralwidget)
        self.blue_spin_box.setMaximum(255)
        self.blue_spin_box.setObjectName("blue_spin_box")
        self.blue_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.blue_spin_box)
        self.horizontalLayout.addLayout(self.blue_layout)
        self.fps_layout = QtWidgets.QFormLayout()
        self.fps_layout.setObjectName("fps_layout")
        self.fps_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.fps_label.setFont(font)
        self.fps_label.setObjectName("fps_label")
        self.fps_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.fps_label)
        self.fps_options = QtWidgets.QComboBox(self.centralwidget)
        self.fps_options.setObjectName("fps_options")
        self.fps_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.fps_options)
        self.horizontalLayout.addLayout(self.fps_layout)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.background_preview = QtWidgets.QGraphicsView(self.centralwidget)
        self.background_preview.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.background_preview.setInputMethodHints(QtCore.Qt.ImhNone)
        self.background_preview.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.background_preview.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.background_preview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.background_preview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.background_preview.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.background_preview.setObjectName("background_preview")
        self.verticalLayout_2.addWidget(self.background_preview)
        self.background_button = QtWidgets.QPushButton(self.centralwidget)
        self.background_button.setObjectName("background_button")
        self.verticalLayout_2.addWidget(self.background_button)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.video_location_button = QtWidgets.QPushButton(self.centralwidget)
        self.video_location_button.setObjectName("video_location_button")
        self.gridLayout_2.addWidget(self.video_location_button, 0, 2, 1, 1)
        self.video_location_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.video_location_label.setFont(font)
        self.video_location_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.video_location_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.video_location_label.setObjectName("video_location_label")
        self.gridLayout_2.addWidget(self.video_location_label, 0, 0, 1, 1)
        self.video_location_tb = QtWidgets.QLineEdit(self.centralwidget)
        self.video_location_tb.setEnabled(False)
        self.video_location_tb.setObjectName("video_location_tb")
        self.gridLayout_2.addWidget(self.video_location_tb, 0, 1, 1, 1)
        self.generate_video_button = QtWidgets.QPushButton(self.centralwidget)
        self.generate_video_button.setObjectName("generate_video_button")
        self.gridLayout_2.addWidget(self.generate_video_button, 0, 3, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.video_generation_progress = QtWidgets.QProgressBar(self.centralwidget)
        self.video_generation_progress.setEnabled(True)
        self.video_generation_progress.setProperty("value", 0)
        self.video_generation_progress.setInvertedAppearance(False)
        self.video_generation_progress.setObjectName("video_generation_progress")
        self.verticalLayout_3.addWidget(self.video_generation_progress)
        self.gridLayout_4.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 20))
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setEnabled(True)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("open")
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionSave)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SubVideo"))
        self.sound_track_label.setText(_translate("MainWindow", "Sound Track:"))
        self.source_time_label.setText(_translate("MainWindow", "Source Time:"))
        self.sound_track_button.setToolTip(_translate("MainWindow", "Browse Soundtrack (Ctrl+T)"))
        self.sound_track_button.setStatusTip(_translate("MainWindow", "Browse for sound track file"))
        self.sound_track_button.setText(_translate("MainWindow", "Browse"))
        self.sound_track_button.setShortcut(_translate("MainWindow", "Ctrl+T"))
        self.source_time_button.setToolTip(_translate("MainWindow", "Browse Source Time File (Ctrl+E)"))
        self.source_time_button.setStatusTip(_translate("MainWindow", "Browse for frame text and timecode file"))
        self.source_time_button.setText(_translate("MainWindow", "Browse"))
        self.source_time_button.setShortcut(_translate("MainWindow", "Ctrl+E"))
        self.preview_graphic.setStatusTip(_translate("MainWindow", "Preview window for each frame"))
        self.frame_previous_button.setToolTip(_translate("MainWindow", "Show previous frame (p)"))
        self.frame_previous_button.setStatusTip(_translate("MainWindow", "Show previous frame"))
        self.frame_previous_button.setText(_translate("MainWindow", "Previous"))
        self.frame_previous_button.setShortcut(_translate("MainWindow", "P"))
        self.refresh_button.setToolTip(_translate("MainWindow", "Refresh Preview (Ctrl+R)"))
        self.refresh_button.setStatusTip(_translate("MainWindow", "Refresh frame preview window"))
        self.refresh_button.setText(_translate("MainWindow", "↻ Refresh"))
        self.refresh_button.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.frame_next_button.setToolTip(_translate("MainWindow", "Show next frame (n)"))
        self.frame_next_button.setStatusTip(_translate("MainWindow", "Show next frame"))
        self.frame_next_button.setText(_translate("MainWindow", "Next"))
        self.frame_next_button.setShortcut(_translate("MainWindow", "N"))
        self.font_choice_label.setText(_translate("MainWindow", "Font:"))
        self.font_button.setToolTip(_translate("MainWindow", "Browse for font file (Ctrl+F)"))
        self.font_button.setStatusTip(_translate("MainWindow", "Browse for font file"))
        self.font_button.setText(_translate("MainWindow", "Browse"))
        self.font_button.setShortcut(_translate("MainWindow", "Ctrl+F"))
        self.font_size_label.setText(_translate("MainWindow", "Font Size:"))
        self.font_size_tb.setStatusTip(_translate("MainWindow", "Set font size"))
        self.red_label_2.setText(_translate("MainWindow", "R"))
        self.red_spin_box_2.setStatusTip(_translate("MainWindow", "Set font red value"))
        self.green_label.setText(_translate("MainWindow", "G"))
        self.green_spin_box.setStatusTip(_translate("MainWindow", "Set font green value"))
        self.blue_label.setText(_translate("MainWindow", "B"))
        self.blue_spin_box.setStatusTip(_translate("MainWindow", "Set font blue value"))
        self.fps_label.setText(_translate("MainWindow", "FPS"))
        self.fps_options.setStatusTip(_translate("MainWindow", "Set output video frame rate"))
        self.background_preview.setStatusTip(_translate("MainWindow", "Preview window showing the background frame"))
        self.background_button.setToolTip(_translate("MainWindow", "Browse for background frame (Ctrl+B)"))
        self.background_button.setStatusTip(_translate("MainWindow", "Browse for background frame"))
        self.background_button.setText(_translate("MainWindow", "Select Background Frame"))
        self.background_button.setShortcut(_translate("MainWindow", "Ctrl+B"))
        self.video_location_button.setToolTip(_translate("MainWindow", "Browse for output file location (Ctrl+L)"))
        self.video_location_button.setStatusTip(_translate("MainWindow", "Browse for output video location"))
        self.video_location_button.setText(_translate("MainWindow", "Browse"))
        self.video_location_button.setShortcut(_translate("MainWindow", "Ctrl+L"))
        self.video_location_label.setText(_translate("MainWindow", "Save As:"))
        self.generate_video_button.setToolTip(_translate("MainWindow", "Generate Video (Ctrl+Return)"))
        self.generate_video_button.setStatusTip(_translate("MainWindow", "Generate video"))
        self.generate_video_button.setText(_translate("MainWindow", "Generate Video"))
        self.generate_video_button.setShortcut(_translate("MainWindow", "Ctrl+Return"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionAbout.setShortcut(_translate("MainWindow", "Ctrl+A"))
