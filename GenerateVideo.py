import os
import subprocess
import tempfile

import cv2
import numpy
from PIL import Image
from PyQt5.QtCore import QSettings, QThread, pyqtSignal

import constants
from AppParameters import Settings
from draw_background import convert_to_qt, draw_frame


class GenerateVideo(QThread):

    text: pyqtSignal = pyqtSignal(object)
    image: pyqtSignal = pyqtSignal(object)
    success: pyqtSignal = pyqtSignal(object)
    update: pyqtSignal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.settings: Settings
        self.appSettings = QSettings()

    # def __del__(self):
    #    self.wait()

    def generateVideo(self):
        tempFile = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tempFile.close()
        pilImg: Image = draw_frame(
            self.settings, self.settings.frameTextList[0].line)
        width, height = pilImg.size
        video: cv2.VideoWriter = cv2.VideoWriter(tempFile.name,
                                                 -1,
                                                 self.settings.framerate,
                                                 (width, height)
                                                 )
        for i in range(len(self.settings.frameTextList)):
            self.text.emit(
                f"Processing: {'/'.join(self.settings.frameTextList[i].line)}")
            pilImg: Image = draw_frame(
                self.settings, self.settings.frameTextList[i].line)
            self.image.emit(pilImg)
            for j in range(self.settings.frameTextList[i].num_frames):
                video.write(cv2.cvtColor(
                    numpy.array(pilImg), cv2.COLOR_RGB2BGR))
            self.update.emit()
        video.release()
        self.text.emit('Writing audio to file')
        ffmpeg_location = self.appSettings.value(
            constants.FFMPEG_LOCATION, 'ffmpeg', type='QStringList')[0]
        vclp = addAudioToVideo(tempFile.name, self.settings.sound_track,
                               self.settings.output_location, ffmpeg_location)
        if vclp != 0:
            self.success.emit(False)
        else:
            self.success.emit(True)
        self.update.emit()
        os.remove(tempFile.name)

    def run(self):
        self.generateVideo()


def addAudioToVideo(video, audio, output, ffmpeg_location):
    spc = subprocess.call([ffmpeg_location, '-y', '-i', video, '-i', audio, '-c:v', 'copy',
                           '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', output])
    return spc
