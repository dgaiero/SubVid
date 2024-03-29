import datetime
import functools
import time
import json
import os
import re
import subprocess
import sys
import webbrowser
from uuid import uuid4

import cv2
import numpy
import PyQt5.QtGui as QtGui
import qdarkstyle
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSettings, QThread, QUrl
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent, QKeySequence
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QShortcut, QStyle
from recently_opened import RecentlyOpened

import constants
import layouts.file_not_found
import layouts.image_viewer
import layouts.license
import layouts.main_dialog
import layouts.search_ffmpeg_executable
import layouts_helper
from AppParameters import Settings
from decorators import _checkFileExists, _statusBarDecorator, _refreshPreview
from draw_background import convert_to_qt, draw_frame
from GenerateVideo import GenerateVideo
from Lyrics import Lyrics, MalFormedDataException
from version import Version

processes = set([])

ALL_KEYS_DISABLED = 0
NEXT_KEY_ENABLED = 1
PREVIOUS_KEY_ENABLED = 2
ALL_KEYS_ENABLED = 3

SETTINGS_THEME = 'settings/theme'
SETTINGS_THEME_CUSTOM = 'settings/themeCustom'


def theme_set(theme): return layouts_helper.Theme(theme, theme)


class MainDialog(QtWidgets.QMainWindow, layouts.main_dialog.Ui_MainWindow):

    previewClicked = QtCore.pyqtSignal(QtCore.QPoint)
    imageChanged = QtCore.pyqtSignal(object)

    def __init__(self, app, uuid, parent=None):
        super(MainDialog, self).__init__(parent)
        layouts_helper.configure_default_params(self)
        self.app = app
        self.uuid = uuid
        self.settings: Settings = Settings(
            constants.ORGANIZATION_NAME, constants.APPLICATION_NAME)
        self.appSettings = QSettings()
        self.ffmpeg_config = FfmpegConfig()
        processes.add(self.ffmpeg_config)
        self.fileOpenDialogDirectory = os.path.expanduser('~')
        self.bindLicenseActions()
        self.source_time_button.clicked.connect(self.getSourceTime)
        self.sound_track_button.clicked.connect(self.getSoundTrack)
        self.font_button.clicked.connect(self.getParamFont)
        self.font_size_tb.valueChanged.connect(self.setFontSize)
        self.red_spin_box_2.valueChanged.connect(self.changeFontPickerRed)
        self.green_spin_box.valueChanged.connect(self.changeFontPickerGreen)
        self.blue_spin_box.valueChanged.connect(self.changeFontPickerBlue)

        self.red_spin_box_text_box.valueChanged.connect(self.changeBackgroundPickerRed)
        self.green_spin_box_text_box.valueChanged.connect(self.changeBackgroundPickerGreen)
        self.blue_spin_box_text_box.valueChanged.connect(
            self.changeBackgroundPickerBlue)
        self.show_bounding_box.clicked.connect(self.toggleBoundingBox)

        self.background_button.clicked.connect(self.getBackgroundImage)
        self.generate_video_button.clicked.connect(self._generateVideo)
        self.refresh_button.clicked.connect(self.refreshVideo)
        self.video_location_button.clicked.connect(self.getVideoOutputLocation)
        self.frame_next_button.clicked.connect(self.showNextFrame)
        self.frame_previous_button.clicked.connect(self.showPreviousFrame)
        self.source_time_tb.textChanged.connect(self.updateSourceTimeTextBox)
        self.sound_track_tb.textChanged.connect(self.updateSoundTrackTextBox)
        self.font_tb.textChanged.connect(self.updateFontTextBox)
        self.video_location_tb.textChanged.connect(
            self.updateVideoLocationTextBox)
        self.theme_actions = {}
        self.themes = (list(map(theme_set, QtWidgets.QStyleFactory.keys())) +
                       [layouts_helper.Theme("Dark Style", qdarkstyle.load_stylesheet_pyqt5(), True)])

        self.videoThread: QThread = GenerateVideo()
        self.videoThread.update.connect(self.updateProgress)
        self.videoThread.text.connect(self.updateVideoGenerationStatusText)
        self.videoThread.image.connect(self.updatePreviewWindowVG)
        self.videoThread.success.connect(self.generationSuccessCheck)
        self.videoThread.finished.connect(self.cleanupVideoGeneration)

        self.actionOpen.triggered.connect(self.openConfig)
        self.actionOpen.setIcon(
            self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.actionSave_As.triggered.connect(self.saveAsConfig)
        self.actionSave.triggered.connect(self.saveConfig)
        self.actionSave.setIcon(
            self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.actionNew.triggered.connect(self.newWindow)
        self.actionNew.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))

        self.recently_opened = RecentlyOpened(self)
        self.recently_opened.buildRecentlyOpenedDict()
        self.recently_opened.build_dropdown()
        self.actionExit.triggered.connect(self.close)

        self.align_text_top_radial.toggled.connect(self.setTextPosition)
        self.align_text_center_radial.toggled.connect(self.setTextPosition)
        self.align_text_bottom_radial.toggled.connect(self.setTextPosition)

        self.reset_preview_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.reset_preview_button.clicked.connect(self.resetPreview)

        self.skip_to_end_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.skip_to_end_button.clicked.connect(self.skipToEnd)

        self.player = QMediaPlayer()

        self.isMuted = False
        self.mute_preview_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_preview_button.clicked.connect(self.checkPreviewMute)

        self.isPlayingPreview = False
        self.play_preview_button.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_preview_button.clicked.connect(self.playPreview)

        self.background_preview.setRenderHint(
            QtGui.QPainter.SmoothPixmapTransform)
        self.preview_graphic.setRenderHint(
            QtGui.QPainter.SmoothPixmapTransform)

        self.actionClear_all_settings.triggered.connect(self.appSettings.clear)

        self.text_align_left.setDisabled(True)
        self.text_align_center.setDisabled(True)
        self.text_align_right.setDisabled(True)

        self.text_x_pos.valueChanged.connect(self.update_text_x_pos)
        self.text_y_pos.valueChanged.connect(self.update_text_y_pos)

        self.currentFrame = 0

        self.actionConfigure_FFMPEG_location.triggered.connect(
            self.showFFMPEGConfigureDialog)
        self.checkFFMPEGVersion(onStart=True)
        self.setThemeOptions()
        self.setTheme()
        # self.actionTheme.triggered.connect(self.changeTheme)

        self.updateColors()

        self.preview_dialog = ImageViewer(self)
        processes.add(self.preview_dialog)
        self.previewClicked.connect(self.bindLargePreviewActions)

        self.checkFramePosition()
        self.preview_frame_buffer = list()

        timer100ms = QtCore.QTimer(self)
        timer100ms.timeout.connect(self.runUpdateEvents100ms)
        timer100ms.start(100)  # 100 ms refesh rate

        self.file_not_found = FileNotFound(self)
        processes.add(self.file_not_found)

    def checkFFMPEGVersion(self, onStart=False):
        version = self.ffmpeg_config.verifyFFMPEG(self.appSettings.value(
            constants.FFMPEG_LOCATION, 'ffmpeg', type='QStringList')[0])
        if not(version):
            self.ffmpeg_config.show()

    def showFFMPEGConfigureDialog(self):
        self.ffmpeg_config.appSettings = self.appSettings
        self.ffmpeg_config.show()

    def setTheme(self):
        current_theme = self.appSettings.value(
            SETTINGS_THEME, 'Fusion', type='QStringList')
        custom_theme = self.appSettings.value(
            SETTINGS_THEME_CUSTOM, False, type=bool)
        current_theme = current_theme[0]
        if custom_theme:
            self.app.setStyleSheet(
                self.theme_actions[current_theme]['theme'].func)
        else:
            self.app.setStyle(QtWidgets.QApplication.setStyle(current_theme))
            self.app.setStyleSheet("")
        self.theme_actions[current_theme]['action'].setChecked(True)

    def changeTheme(self, name, func, customStyle):
        if customStyle:
            self.app.setStyleSheet(func)
        else:
            self.app.setStyle(QtWidgets.QApplication.setStyle(func))
            self.app.setStyleSheet("")
        self.appSettings.setValue(SETTINGS_THEME, name)
        self.appSettings.setValue(SETTINGS_THEME_CUSTOM, customStyle)

    def setThemeOptions(self):
        group = QtWidgets.QActionGroup(self.menuTheme)
        for theme in self.themes:
            action: QtWidgets.QAction = self.menuTheme.addAction(
                f"{theme.name}")
            action.setCheckable(True)
            action.triggered.connect(
                functools.partial(self.changeTheme, theme.name, theme.func, theme.customTheme))
            group.addAction(action)
            self.theme_actions[theme.name] = {'action': action, 'theme': theme}
        group.setExclusive(True)

    @_statusBarDecorator("Open Configuration File")
    def openConfig(self):
        filters = 'SubVid Configuration File (*.svp);;\
      All Files (*.*)'
        fname = QFileDialog.getOpenFileName(self, 'Select SubVid Configuration File',
                                            self.fileOpenDialogDirectory, filters)
        if fname[0] == '' or fname is None:
            return
        self.recently_opened.admitNewItem(os.path.normpath(fname[0]))
        self.readConfigFile(fname[0])

    def readConfigFile(self, fname):
        with open(fname, 'r') as handle:
            try:
                settings = json.load(handle)
            except json.decoder.JSONDecodeError:
                layouts_helper.show_dialog_non_informative_text(self, "Error",
                                                                f"Failed to open {fname[0]}",
                                                                f"Ensure that <b>{os.path.basename(fname[0])}</b> is formatted correctly and not corrupted.",
                                                                buttons=QtWidgets.QMessageBox.Ok,
                                                                icon=QtWidgets.QMessageBox.Critical)
                return
        self.settings.saveFile = fname
        self.settings.loadFromConfig(**settings)
        filesNotFoundList = self.checkFilesExist()
        if (filesNotFoundList != []):
            self.file_not_found.set_data(filesNotFoundList)
            self.file_not_found.show()
        else:
            self.loadConfigurationToUI(settings)

    def loadConfigurationToUI(self, settings):
        self.updateTextBoxFromSettings()
        if self.settings.background_frame != '':
            self.resizeBackgroundImage()
        if self.settings.source_time != '':
            self.readSourceTimeData()
        self.font_size_tb.setValue(self.settings.font_size)
        self.red_spin_box_2.setValue(self.settings.text_color[0])
        self.green_spin_box.setValue(self.settings.text_color[1])
        self.blue_spin_box.setValue(self.settings.text_color[2])
        self.text_color_preview.setStyleSheet(
            f"background-color: rgb({self.settings.text_color[0]}, \
                {self.settings.text_color[1]}, \
                {self.settings.text_color[2]});")

        self.red_spin_box_text_box.setValue(self.settings.background_color[0])
        self.green_spin_box_text_box.setValue(self.settings.background_color[1])
        self.blue_spin_box_text_box.setValue(self.settings.background_color[2])

        self.text_x_pos.setValue(self.settings.text_offset[0])
        self.text_y_pos.setValue(self.settings.text_offset[1])
        self.text_box_color_preview.setStyleSheet(
            f"background-color: rgb({self.settings.background_color[0]}, \
                {self.settings.background_color[1]}, \
                {self.settings.background_color[2]});")
        self.show_bounding_box.setChecked(self.settings.show_background_frame)
        if (self.settings.text_position in ['top', 'center', 'bottom']):
            radial: QtWidgets.QRadioButton = getattr(
                self, f'align_text_{self.settings.text_position}_radial')
            radial.setChecked(True)
        self.refreshVideo()

    def checkFilesExist(self):
        filesToCheckList = ["source_time",
                            "sound_track", "font", "background_frame"]
        filesNotFoundList = []
        for file in filesToCheckList:
            if self.settings.checkFileExists(file) is False:
                filesNotFoundList.append(
                    [file, self.settings.getFileName(file), eval(f"self.settings.{file}")])
        return filesNotFoundList

    @_statusBarDecorator("Save Configuration File")
    def saveAsConfig(self):
        filters = 'SubVid Configuration File (*.svp)'
        fname = QFileDialog.getSaveFileName(self, 'Save As',
                                            self.fileOpenDialogDirectory, filters)
        if (fname[0] == ''):
            return
        self.saveConfigFile(fname[0])
        self.settings.saveFile = fname[0]

    def saveConfig(self):
        if self.settings.saveFile is None:
            return self.saveAsConfig()
        self.saveConfigFile(self.settings.saveFile)

    def saveConfigFile(self, fname):
        with open(fname, 'w') as handle:
            json.dump(self.settings.configData(), handle)

    def runUpdateEvents100ms(self):
        self.generate_video_button.setEnabled(self.settings.canGenerate())
        self.refresh_button.setEnabled(self.settings.canPreview())
        self.checkFramePosition()
        self.setTitle()

    def setTitle(self):
        if self.settings.saveFile is not None:
            self.setWindowTitle(f"SubVideo ({self.settings.saveFile})")

    def resetPreview(self):
        if (self.isPlayingPreview == True) or self.settings.videoInProgress or (self.settings.canPreview() == False):
            return
        self.settings.frameNumber = 0
        self.refreshVideo()

    def skipToEnd(self):
        if (self.isPlayingPreview == True) or self.settings.videoInProgress or (self.settings.canPreview() == False):
            return
        self.settings.frameNumber = len(self.settings.frameTextList) - 1
        self.refreshVideo()

    def resizeEvent(self, event):
        self.resizeBackgroundImage()
        self.resizePreview()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def showEvent(self, event):
        self.resizeBackgroundImage()
        self.resizePreview()
        QtWidgets.QMainWindow.showEvent(self, event)

    def closeEvent(self, event):
        closeAccept = True
        if (self.saveDataSame()) == False:
            ret = self.showSaveQuitDialog()
            if (ret == QtWidgets.QMessageBox.Save):
                self.saveConfig()
            elif (ret == QtWidgets.QMessageBox.Cancel):
                closeAccept = False
                event.ignore()
        if closeAccept:
            self.preview_dialog.close()
            self.close()
            del self.app._windows[self.uuid]
            QtWidgets.QMainWindow.closeEvent(self, event)

    def showSaveQuitDialog(self):
        filename = os.path.basename(self.settings.saveFile)

        msg = QtWidgets.QMessageBox(self)
        msg.setText(
            f'Do you want to save the changes you made to "{filename}"\nIf you don\'t save, your changes will be lost')
        msg.setWindowTitle('Unsaved Changes')
        msg.setStandardButtons(QtWidgets.QMessageBox.Save)
        save_as_button = msg.addButton("Save As", QtWidgets.QMessageBox.ActionRole)
        save_as_button.clicked.connect(self.saveAsConfig)
        msg.addButton("Don't Save", QtWidgets.QMessageBox.RejectRole)
        msg.addButton(QtWidgets.QMessageBox.Cancel)
        return msg.exec_()

    def mousePressEvent(self, event):
        if self.preview_graphic.underMouse():
            self.previewClicked.emit(QtCore.QPoint(event.pos()))
        QtWidgets.QMainWindow.mousePressEvent(self, event)

    def saveDataSame(self) -> bool:
        if (self.settings.saveFile is None):
            return
        currentData = self.settings.configData()
        saveData = json.loads(open(self.settings.saveFile, 'r').read())
        return currentData == saveData

    def newWindow(self):
        self.app.newWindow()

    @_checkFileExists
    def refreshVideo(self):
        self.setPreviewPicture()

    def updateSourceTimeTextBox(self):
        self.settings.source_time = self.source_time_tb.text()
        if os.path.exists(self.settings.source_time):
            self.readSourceTimeData()

    def updateSoundTrackTextBox(self):
        self.settings.sound_track = self.sound_track_tb.text()

    def updateFontTextBox(self):
        self.settings.font = os.path.normpath(self.font_tb.text())

    def updateVideoLocationTextBox(self):
        self.settings.output_location = os.path.normpath(
            self.video_location_tb.text())
    
    @_refreshPreview
    def toggleBoundingBox(self):
        if self.show_bounding_box.isChecked():
            self.settings.show_background_frame = True
        else:
            self.settings.show_background_frame = False

    def checkPreviewMute(self):
        if self.isMuted == True:
            self.isMuted = False
            self.mute_preview_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaVolume))
            self.player.setMuted(False)
        else:
            self.isMuted = True
            self.mute_preview_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
            self.player.setMuted(True)

    def playPreview(self):
        if self.isPlayingPreview == True:
            self.settings.frameNumber = self.currentFrame
            self.isPlayingPreview = False
            self.timer_next_frame.stop()
            self.player.pause()
            self.play_preview_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            self.play_preview_button.setToolTip(
                QCoreApplication.translate("MainWindow", "Play Preview (Shift+P)"))
            self.play_preview_button.setStatusTip(
                QCoreApplication.translate("MainWindow", "Play Preview"))
            self.checkFramePosition()
            self.video_generation_progress.setValue(0)
        else:
            self.isPlayingPreview = True
            self.checkFramePosition()
            self.video_generation_progress.setValue(self.settings.frameNumber)
            start_frame = self.settings.frameTextList[self.settings.frameNumber]

            self.play_preview_button.setDisabled(True)
            for idx, _ in enumerate(self.settings.frameTextList):
                if idx < self.settings.frameNumber:
                    continue
                self.updateProgress()
                pilImg = draw_frame(
                    self.settings, self.settings.frameTextList[idx].line)
                self.preview_frame_buffer[idx] = convert_to_qt(pilImg)
            self.video_generation_progress.setValue(0)
            self.video_generation_progress.setValue(self.settings.frameNumber)
            self.play_preview_button.setDisabled(False)

            num_seconds = (start_frame.start.frames)*1.0/(self.settings.framerate)
            song_uri = QUrl.fromLocalFile(self.settings.sound_track)
            content = QMediaContent(song_uri)
            self.player.setMedia(content)
            self.player.setPosition(num_seconds*1000)
            self.player.play()
            self.play_preview_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
            self.play_preview_button.setToolTip(
                QCoreApplication.translate("MainWindow", "Pause Preview (Shift+P)"))
            self.play_preview_button.setStatusTip(
                QCoreApplication.translate("MainWindow", "Pause Preview"))
            self._playPreview()

    def _playPreview(self):
        if self.isPlayingPreview is False:
            self.timer_next_frame.stop()
            return
        if self.settings.frameNumber == len(self.settings.frameTextList):
            self.isPlayingPreview = False
            self.play_preview_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
            self.checkFramePosition()
            return
        # self.setPreviewPicture()
        self.updateProgress()
        self.settings.preview_frame = self.preview_frame_buffer[self.settings.frameNumber]
        self.resizePreview()
        current_frame = self.settings.frameTextList[self.settings.frameNumber]
        num_seconds = (current_frame.num_frames)*1.0/(self.settings.framerate)
        self.timer_next_frame = QtCore.QTimer(self)
        self.timer_next_frame.setSingleShot(True)
        self.timer_next_frame.timeout.connect(self.previewShowNextFrame)
        self.timer_next_frame.start(num_seconds*1000)

    def previewShowNextFrame(self):
        self.settings.frameNumber += 1
        self._playPreview()

    def updateTextBoxFromSettings(self):
        self.source_time_tb.setText(self.settings.source_time)
        self.sound_track_tb.setText(self.settings.sound_track)
        self.font_tb.setText(self.settings.font)
        self.video_location_tb.setText(self.settings.output_location)

    def checkFramePosition(self):
        if (self.isPlayingPreview == True):
            self.frame_previous_button.setEnabled(False)
            self.reset_preview_button.setEnabled(False)
            self.skip_to_end_button.setEnabled(False)
            self.frame_next_button.setEnabled(False)
            return ALL_KEYS_DISABLED
        if (self.settings.videoInProgress or (self.settings.canPreview() == False)):
            self.frame_previous_button.setEnabled(False)
            self.frame_next_button.setEnabled(False)
            self.play_preview_button.setEnabled(False)
            self.reset_preview_button.setEnabled(False)
            self.skip_to_end_button.setEnabled(False)
            return ALL_KEYS_DISABLED
        self.play_preview_button.setEnabled(True)
        enabled = ALL_KEYS_DISABLED
        if self.settings.frameNumber == 0:
            self.frame_previous_button.setEnabled(False)
            self.reset_preview_button.setEnabled(False)
        else:
            self.frame_previous_button.setEnabled(True)
            self.reset_preview_button.setEnabled(True)
            enabled |= PREVIOUS_KEY_ENABLED
        if self.settings.frameNumber == len(self.settings.frameTextList) - 1:
            self.skip_to_end_button.setEnabled(False)
            self.frame_next_button.setEnabled(False)
        else:
            self.skip_to_end_button.setEnabled(True)
            self.frame_next_button.setEnabled(True)
            enabled |= NEXT_KEY_ENABLED
        return enabled


    @_refreshPreview
    def setTextPosition(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            self.settings.text_position = radio_button.text().lower()

    @_checkFileExists
    def showPreviousFrame(self):
        if ((self.checkFramePosition() & PREVIOUS_KEY_ENABLED) >= 1):
            self.settings.frameNumber -= 1
            self.statusbar.showMessage(
                f"Showing frame {self.settings.frameNumber + 1}", msecs=1000)
            self.setPreviewPicture()

    @_checkFileExists
    def showNextFrame(self):
        if ((self.checkFramePosition() & NEXT_KEY_ENABLED) >= 1):
            self.settings.frameNumber += 1
            self.statusbar.showMessage(
                f"Showing frame {self.settings.frameNumber + 1}", msecs=1000)
            self.setPreviewPicture()

    def setPreviewPicture(self):
        self.currentFrame = self.settings.frameNumber
        if ((self.checkFramePosition() >= 1) | self.isPlayingPreview):
            pilImg = draw_frame(
                self.settings, self.settings.frameTextList[self.settings.frameNumber].line)
            self.settings.preview_frame = convert_to_qt(pilImg)
            self.resizePreview()

    @_checkFileExists
    def _generateVideo(self):
        # self.appSettings.setValue(constants.FFMPEG_LOCATION, 'ffmpeg')
        self.checkFFMPEGVersion()
        self.generate_video_status_label = QtWidgets.QLabel()
        self.statusbar.addPermanentWidget(
            self.generate_video_status_label, 100)
        self.toggleButtoms(False, True)
        self.toggleTextBoxes(False)

        self.videoThread.settings = self.settings
        self.videoThread.start()

    def toggleButtoms(self, tstatus, video_in_progress_status):
        self.source_time_button.setEnabled(tstatus)
        self.sound_track_button.setEnabled(tstatus)
        self.font_button.setEnabled(tstatus)
        self.font_size_tb.setEnabled(tstatus)
        self.red_spin_box_2.setEnabled(tstatus)
        self.green_spin_box.setEnabled(tstatus)
        self.blue_spin_box.setEnabled(tstatus)
        self.background_button.setEnabled(tstatus)
        self.video_location_button.setEnabled(tstatus)
        self.actionOpen.setEnabled(tstatus)
        self.settings.videoInProgress = video_in_progress_status

    def toggleTextBoxes(self, tstatus):
        self.source_time_tb.setEnabled(tstatus)
        self.sound_track_tb.setEnabled(tstatus)
        self.font_tb.setEnabled(tstatus)
        self.video_location_tb.setEnabled(tstatus)

    def updateVideoGenerationStatusText(self, text):
        self.generate_video_status_label.setText(text)

    def updateProgress(self):
        self.video_generation_progress.setValue(
            self.video_generation_progress.value() + 1)

    def updatePreviewWindowVG(self, pilImg):
        self.settings.preview_frame = convert_to_qt(pilImg)
        self.resizePreview()

    def generationSuccessCheck(self, check):
        if check == False:
            layouts_helper.show_dialog_non_informative_text(self, "Error",
                                                            f"Video Generation Failure",
                                                            "",
                                                            buttons=QtWidgets.QMessageBox.Ok,
                                                            icon=QtWidgets.QMessageBox.Critical)
        else:
            QtWidgets.QApplication.beep()
            layouts_helper.show_dialog_non_informative_text(self, "Done",
                                                            f"Video file located at <br /><code>{self.settings.output_location}</code>",
                                                            "",
                                                            buttons=QtWidgets.QMessageBox.Ok,
                                                            icon=QtWidgets.QMessageBox.NoIcon)

    def cleanupVideoGeneration(self):
        self.statusbar.removeWidget(self.generate_video_status_label)
        self.toggleButtoms(True, False)
        self.toggleTextBoxes(True)
        self.video_generation_progress.setValue(0)

    @_statusBarDecorator("Browse for Source Time Spreadsheet")
    def getSourceTime(self):
        fname = self.settings.getSourceTime(self, self.fileOpenDialogDirectory)[0]
        self.processSourceTimeData(fname)

    def processSourceTimeData(self, fname):
        if fname != '':
            self.settings.source_time = os.path.normpath(fname)
            self.fileOpenDialogDirectory = os.path.dirname(
                self.settings.source_time)
            self.source_time_tb.setText(self.settings.source_time)
            self.readSourceTimeData()

    @_statusBarDecorator("Reading source time data")
    def readSourceTimeData(self):
        frameText = Lyrics(self.settings.source_time,
                           str(self.settings.framerate))
        frameText.importData()
        try:
            frameText.readData()
            self.settings.frameTextList = frameText.timecode_frames
            self.video_generation_progress.setMaximum(
                len(self.settings.frameTextList) + 1)
            self.preview_frame_buffer = [None]*len(self.settings.frameTextList)
        except ValueError as e:
            layouts_helper.show_dialog_non_informative_text(
                self, "Error", f"<b>Value Error:</b> {str(e)}", "", buttons=QtWidgets.QMessageBox.Ok)
        except MalFormedDataException as e:
            extended_text = f"{e.message}\nActual Headers: {', '.join(e.actual_headers)}"
            layouts_helper.show_dialog_detailed_text(
                self, "Error", f"Error: {e.message}", "Informative Text", extended_text)
        

    @_statusBarDecorator("Browse for a font")
    def getParamFont(self):
        fname = self.settings.getParamFont(self, self.fileOpenDialogDirectory)[0]
        self.processParamFont(fname)

    def processParamFont(self, fname):
        if fname != '':
            self.settings.font = os.path.normpath(fname)
            self.fileOpenDialogDirectory = os.path.dirname(
                self.settings.sound_track)
            self.font_tb.setText(self.settings.font)

    @_refreshPreview
    def setFontSize(self):
        self.settings.font_size = self.font_size_tb.value()

    @_refreshPreview
    def update_text_x_pos(self):
        self.settings.text_offset[0] = self.text_x_pos.value()

    @_refreshPreview
    def update_text_y_pos(self):
        self.settings.text_offset[1] = self.text_y_pos.value()

    @_refreshPreview
    def changeFontPickerRed(self):
        self.settings.text_color[0] = self.red_spin_box_2.value()
        self.updateColors()

    @_refreshPreview
    def changeFontPickerGreen(self):
        self.settings.text_color[1] = self.green_spin_box.value()
        self.updateColors()

    @_refreshPreview
    def changeFontPickerBlue(self):
        self.settings.text_color[2] = self.blue_spin_box.value()
        self.updateColors()

    @_refreshPreview
    def changeBackgroundPickerRed(self):
        self.settings.background_color[0] = self.red_spin_box_text_box.value()
        self.updateColors()

    @_refreshPreview
    def changeBackgroundPickerGreen(self):
        self.settings.background_color[1] = self.green_spin_box_text_box.value()
        self.updateColors()

    @_refreshPreview
    def changeBackgroundPickerBlue(self):
        self.settings.background_color[2] = self.blue_spin_box_text_box.value()
        self.updateColors()

    def updateColors(self):
        self.text_color_preview.setStyleSheet(
            f"background-color: rgb({self.settings.text_color[0]}, \
       {self.settings.text_color[1]}, \
       {self.settings.text_color[2]});")

        self.text_box_color_preview.setStyleSheet(
            f"background-color: rgb({self.settings.background_color[0]}, \
       {self.settings.background_color[1]}, \
       {self.settings.background_color[2]});")

    @_statusBarDecorator("Browse for soundtrack")
    def getSoundTrack(self):
        fname = self.settings.getSoundTrack(self, self.fileOpenDialogDirectory)[0]
        self.processSoundTrack(fname)

    def processSoundTrack(self, fname):
        if fname != '':
            self.settings.sound_track = os.path.normpath(fname)
            self.fileOpenDialogDirectory = os.path.dirname(
                self.settings.sound_track)
            self.sound_track_tb.setText(self.settings.sound_track)

    @_statusBarDecorator("Browse for output video location")
    def getVideoOutputLocation(self):
        filters = 'MP4 File (*.mp4)'
        fname = QFileDialog.getSaveFileName(self, 'Save As', self.fileOpenDialogDirectory,
                                            filters)
        if fname[0] != '':
            self.settings.output_location = os.path.normpath(fname[0])
            self.fileOpenDialogDirectory = os.path.dirname(
                self.settings.sound_track)
            self.video_location_tb.setText(self.settings.output_location)

    @_statusBarDecorator("Browse for background image")
    def getBackgroundImage(self):
        fname = self.settings.getBackgroundImage(
            self, self.fileOpenDialogDirectory)[0]
        self.processBackgroundImage(fname)

    def processBackgroundImage(self, fname):
        if fname != '':
            self.settings.background_frame = os.path.normpath(fname)
            self.fileOpenDialogDirectory = os.path.dirname(
                self.settings.background_frame)
            self.resizeBackgroundImage()

    def resizeBackgroundImage(self):
        scene = QGraphicsScene()
        pixmap = QtGui.QPixmap(self.settings.background_frame)
        scene.addPixmap(pixmap)
        scale_factor = self.background_preview.width()/scene.width()
        self.background_preview.scale(scale_factor, scale_factor)
        self.background_preview.fitInView(
            scene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
        self.background_preview.setScene(scene)

    def resizePreview(self):
        scene = QGraphicsScene()
        pixmap = QtGui.QPixmap(self.settings.preview_frame)
        scene.addPixmap(pixmap)
        scale_factor = self.preview_graphic.width()/scene.width()
        self.preview_graphic.scale(scale_factor, scale_factor)
        self.preview_graphic.fitInView(
            scene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
        self.preview_graphic.setScene(scene)
        self.preview_dialog.qScene = scene
        self.preview_dialog.resizePreview()
        if self.settings.canPreview():
            self.preview_dialog.setWindowTitle(
                f"Scene Viewer: Frame {self.settings.frameNumber + 1}")
        # Emit to signal here with QGraphicsScene

    def bindLicenseActions(self):
        self.actionAbout.triggered.connect(self.app.license_view_dialog.show)

    def bindLargePreviewActions(self):
        self.preview_dialog.show()


class LicenseWindow(QtWidgets.QDialog, layouts.license.Ui_Dialog):
    def __init__(self, parent=None):
        super(LicenseWindow, self).__init__(parent)
        layouts_helper.configure_default_params(self)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.version = Version()
        self.version.read_file()
        self.viewLicenseOnlineButton.clicked.connect(self.viewLicense)
        self.viewAddendumOnlineButton.clicked.connect(self.viewAddendum)
        license_text = open(layouts_helper.resource_path('LICENSE.LGPL')).read()
        addendum_text = open(layouts_helper.resource_path('COPYING.LESSER')).read()
        self.license_url = 'https://raw.githubusercontent.com/dgaiero/SubVid/master/LICENSE.LGPL'
        self.addendum_url = 'https://raw.githubusercontent.com/dgaiero/SubVid/master/COPYING.LESSER'
        self.licenseText.setPlainText(license_text)
        self.addendumText.setPlainText(addendum_text)
        id = QFontDatabase.addApplicationFont(":/fonts/FiraCode-Regular.ttf")
        _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
        _font = QFont(_fontstr, 8)
        self.licenseText.setFont(_font)
        self.addendumText.setFont(_font)
        self.versionText.setText(f'Version: {self.version}')
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Dialog", f"<html><head/><body><h1 style=\" margin-top:18px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:xx-large; font-weight:600;\">Copyright &copy; Dominic Gaiero {datetime.datetime.now().year}</span></h1><p>Developed and Designed by Dominic Gaiero This program is licensed under the GNU General Public License v3.0. This license is shown below and is generated from the online version. For an online version, click the button below.</p></body></html>"))


    def viewLicense(self):
        title = "View License"
        message = f"You are about to open the license in your default webrowser. Do you want to continue?"
        choice = QtWidgets.QMessageBox.question(self, title,
                                                message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            webbrowser.open_new_tab(self.license_url)

    def viewAddendum(self):
        title = "View Addendum"
        message = f"You are about to open the addendum in your default webrowser. Do you want to continue?"
        choice = QtWidgets.QMessageBox.question(self, title,
                                                message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            webbrowser.open_new_tab(self.addendum_url)

class ImageViewer(QtWidgets.QMainWindow, layouts.image_viewer.Ui_ImageViewer):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        layouts_helper.configure_default_params(self)
        self.qScene = QGraphicsScene()
        self.MainWindow: MainDialog = parent

        nextShortcut = QShortcut(QKeySequence('Ctrl+N'), self)
        nextShortcut.activated.connect(self.MainWindow.showNextFrame)

        nextShortcut2 = QShortcut(QKeySequence('N'), self)
        nextShortcut2.activated.connect(self.MainWindow.showNextFrame)

        prevShortcut = QShortcut(QKeySequence('Ctrl+P'), self)
        prevShortcut.activated.connect(self.MainWindow.showPreviousFrame)

        prevShortcut2 = QShortcut(QKeySequence('P'), self)
        prevShortcut2.activated.connect(self.MainWindow.showPreviousFrame)

        refreshShortcut = QShortcut(QKeySequence('Ctrl+R'), self)
        refreshShortcut.activated.connect(self.MainWindow.refreshVideo)

        refreshShortcut2 = QShortcut(QKeySequence('R'), self)
        refreshShortcut2.activated.connect(self.MainWindow.refreshVideo)

        fullScreenShortcut = QShortcut(QKeySequence('Ctrl+F'), self)
        fullScreenShortcut.activated.connect(self.toggleFullScreen)

        fullScreenShortcut2 = QShortcut(QKeySequence('F'), self)
        fullScreenShortcut2.activated.connect(self.toggleFullScreen)

        playPausePreviewShortcut = QShortcut(QKeySequence('Space'), self)
        playPausePreviewShortcut.activated.connect(self.MainWindow.playPreview)

        skipToBeginningShortcut = QShortcut(QKeySequence('Ctrl+B'), self)
        skipToBeginningShortcut.activated.connect(self.MainWindow.resetPreview)

        skipToBeginningShortcut2 = QShortcut(QKeySequence('B'), self)
        skipToBeginningShortcut2.activated.connect(self.MainWindow.resetPreview)

        skipToEndShortcut = QShortcut(QKeySequence('Ctrl+E'), self)
        skipToEndShortcut.activated.connect(self.MainWindow.skipToEnd)

        skipToEndShortcut2 = QShortcut(QKeySequence('E'), self)
        skipToEndShortcut2.activated.connect(self.MainWindow.skipToEnd)

        muteShortcut = QShortcut(QKeySequence('Ctrl+M'), self)
        muteShortcut.activated.connect(self.MainWindow.checkPreviewMute)

        muteShortcut2 = QShortcut(QKeySequence('M'), self)
        muteShortcut2.activated.connect(self.MainWindow.checkPreviewMute)

        self.preview_graphic.setRenderHint(
            QtGui.QPainter.SmoothPixmapTransform)

    def resizePreview(self):
        scale_factor = self.preview_graphic.width()/self.qScene.width()
        self.preview_graphic.scale(scale_factor, scale_factor)
        self.preview_graphic.fitInView(
            self.qScene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
        self.preview_graphic.setScene(self.qScene)

    def showEvent(self, event):
        self.resizePreview()
        QtWidgets.QMainWindow.showEvent(self, event)

    def resizeEvent(self, event):
        self.resizePreview()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def keyPressEvent(self, event):
        pressEvent: QKeyEvent = event
        if (pressEvent.key() == QtCore.Qt.Key_Escape):
            self.hide()
        QtWidgets.QMainWindow.keyPressEvent(self, event)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def mouseDoubleClickEvent(self, event):
        self.toggleFullScreen()
        QtWidgets.QMainWindow.mouseDoubleClickEvent(self, event)


class FileNotFound(QtWidgets.QMainWindow, layouts.file_not_found.Ui_FileNotFound):
    def __init__(self, parent=None):
        super(FileNotFound, self).__init__(parent)
        layouts_helper.configure_default_params(self)
        self.MainWindow: MainDialog = parent
        self.closeButton.clicked.connect(self.close)
        self.file_locator_view.setColumnCount(3)
        self.configure_headers()

        self.file_locator_view.cellClicked.connect(self.actionRow)
        self.file_locator_view.cellDoubleClicked.connect(self.locateFile)

        self.locateButton.setEnabled(False)
        self.clearFileButton.setEnabled(False)

        self.locateButton.clicked.connect(self.locateFile)
        self.clearFileButton.clicked.connect(self.initalizeFileValue)

    def actionRow(self):
        self.currentRow = self.file_locator_view.currentRow()
        self.currentItemUsedIn = self.file_locator_view.item(
            self.currentRow, 0).text()
        self.currentItemFileName = self.file_locator_view.item(
            self.currentRow, 1).text()
        self.currentItemFilePath = self.file_locator_view.item(
            self.currentRow, 2).text()

        self.locateButton.setEnabled(True)
        self.clearFileButton.setEnabled(True)

    def locateFileProc(self, findFileFunc, mainWindowProc):
        ret = findFileFunc[0]
        if os.path.isfile(ret):
            mainWindowProc(ret)
            self.removeRow(self.currentRow)

    def locateFile(self):
        if self.currentItemUsedIn == "source_time":
            self.locateFileProc(self.MainWindow.settings.getSourceTime(
                self, self.currentItemFilePath), self.MainWindow.processSourceTimeData)
        elif self.currentItemUsedIn == "sound_track":
            self.locateFileProc(self.MainWindow.settings.getSoundTrack(
                self, self.currentItemFilePath), self.MainWindow.processSoundTrack)
        elif self.currentItemUsedIn == "font":
            self.locateFileProc(self.MainWindow.settings.getParamFont(
                self, self.currentItemFilePath, True), self.MainWindow.processParamFont)
        elif self.currentItemUsedIn == "background_frame":
            self.locateFileProc(self.MainWindow.settings.getBackgroundImage(
                self, self.currentItemFilePath), self.MainWindow.processBackgroundImage)

    def removeRow(self, row: int):
        self.file_locator_view.removeRow(row)
        if self.file_locator_view.rowCount() == 0:
            self.hide()
            self.MainWindow.loadConfigurationToUI(self.MainWindow.settings)

    def initalizeFileValue(self):
        self.MainWindow.settings.initLine(self.currentItemUsedIn)
        self.removeRow(self.currentRow)

    def closeEvent(self, event):
        self.MainWindow.close()
        QtWidgets.QMainWindow.closeEvent(self, event)

    def configure_headers(self):
        column_labels = ["Description", "File Name", "File Path"]
        self.file_locator_view.setHorizontalHeaderLabels(column_labels)
        self.file_locator_view.horizontalHeader()

    def set_data(self, data: list):
        self.file_locator_view.setRowCount(0)
        for row in data:
            inx = data.index(row)
            self.file_locator_view.insertRow(inx)
            for i in range(len(row)):
                self.file_locator_view.setItem(
                    inx, i, QtWidgets.QTableWidgetItem(str(row[i])))


class FfmpegConfig(QtWidgets.QDialog, layouts.search_ffmpeg_executable.Ui_FfmpegExecDialog):
    def __init__(self, parent=None):
        super(FfmpegConfig, self).__init__(parent)
        layouts_helper.configure_default_params(self)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint |
                            QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        # self.MainWindow: MainDialog = parent
        self.ffmpeg_found = False
        self.verify = False
        self.save_button.setEnabled(self.ffmpeg_found)
        self.ffmpeg_version = '0.0.0'
        self.appSettings = QSettings()
        self.openLocation = ''
        self.ffmpeg_location = self.appSettings.value(
            constants.FFMPEG_LOCATION, 'ffmpeg', type='QStringList')[0]

        self.ffmpeg_exec_button.clicked.connect(self.getNewFFMPEG)
        self.ffmpeg_exec_tb.setText(self.ffmpeg_location)
        self.ffmpeg_exec_tb.textChanged.connect(
            functools.partial(self.save_button.setEnabled, False))
        self.cancel_button.clicked.connect(self.close)
        self.save_button.clicked.connect(self.saveSettings)
        self.verify_button.clicked.connect(self.checkFFMPEGVersion)
        self.checkFFMPEGVersion()
        if self.ffmpeg_found == False:
            self.show()

    def closeEvent(self, event):
        if not(self.ffmpeg_found):
            sys.exit()
        else:
            self.cancel_button.setEnabled(True)
            self.setWindowFlag(
                QtCore.Qt.WindowCloseButtonHint, True)
            QtWidgets.QDialog.closeEvent(self, event)

    def saveSettings(self):
        if self.ffmpeg_found == True:
            self.appSettings.setValue(
                constants.FFMPEG_LOCATION, self.ffmpeg_location)
        self.close()

    def getNewFFMPEG(self):
        ffmpeg_location = self.getExecutable(self, self.openLocation)[0]
        if ffmpeg_location == '':
            return
        self.ffmpeg_exec_tb.setText(ffmpeg_location)
        self.checkFFMPEGVersion()

    def checkFFMPEGVersion(self):
        version_number = None
        if self.ffmpeg_exec_tb.text() != '':
            version_number = self.verifyFFMPEG(self.ffmpeg_exec_tb.text())
        if version_number is None:
            self.ffmpeg_version_label.setText("Invalid FFMPEG Version")
        else:
            self.ffmpeg_location = self.ffmpeg_exec_tb.text()
            self.ffmpeg_version_label.setText(
                f"Found FFMPEG version {version_number}")
            self.ffmpeg_found = True
            self.save_button.setEnabled(self.ffmpeg_found)

    def verifyFFMPEG(self, ffmpeg_location):
        if not(self.ffmpeg_found):
            self.cancel_button.setText('Exit')
            self.cancel_button.clicked.connect(sys.exit)
            self.cancel_button.setEnabled(True)
        try:
            spc = subprocess.check_output([ffmpeg_location, '-version'])
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError:
            return None
        version = re.findall(r"ffmpeg version\s(.+)\sCopyright",
                             spc.decode(sys.stdout.encoding))
        if version:
            return version[0].strip()
        return None

    def getExecutable(self, parent, openLocation):
        filters = 'All Executable Files (*.exe)'
        fname = QFileDialog.getOpenFileName(parent, 'Select FFMPEG Executable File', openLocation,
                                            filters)
        return fname
