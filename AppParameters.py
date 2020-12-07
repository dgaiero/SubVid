import sys
import os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog


class Settings():
    def __init__(self,
                 source_time='',
                 sound_track='',
                 font='',
                 font_size=1,
                 background_frame='://placeholders//image_assets//background_image_placeholder.jpg',
                 preview_frame='://placeholders//image_assets//export_preview_placeholder.jpg',
                 output_location='',
                 text_color=[0, 0, 0],
                 background_color=[0, 0, 0],
                 show_background_frame=False,
                 text_position='center'):
        self.source_time = source_time
        self.sound_track = sound_track
        self.font = font
        self.font_size = font_size
        self.background_frame = background_frame
        self.preview_frame = preview_frame
        self.output_location = output_location
        self.text_color = text_color
        self.background_color = background_color
        self.show_background_frame = show_background_frame
        self.text_position = text_position
        self.frameNumber = 0
        self.frameTextList = []
        self.framerate = 30
        self.videoInProgress = False
        self.saveFile = None

    def configData(self):
        r_dict = {
            'source_time': self.source_time,
            'sound_track': self.sound_track,
            'font': self.font,
            'font_size': self.font_size,
            'background_frame': self.background_frame,
            'output_location': self.output_location,
            'text_color': self.text_color,
            'background_color': self.background_color,
            'show_background_frame': self.show_background_frame,
            'text_position': self.text_position
        }
        return r_dict

    def checkFileExists(self, parameter):
        parameter = getattr(self, parameter)
        if parameter == '':
            return True
        return os.path.isfile(parameter)

    def getFileName(self, parameter):
        parameter = getattr(self, parameter)
        return os.path.basename(parameter)

    def initLine(self, parameter):
        defaultValue = "''"
        if parameter == 'background_frame':
            defaultValue = '://placeholders//image_assets//background_image_placeholder.jpg'
        exec(f"self.{parameter} = {defaultValue}")

    def loadFromConfig(self,
                       source_time='',
                       sound_track='',
                       font='',
                       font_size='',
                       background_frame='',
                       output_location='',
                       text_color=[0, 0, 0],
                       background_color=[0, 0, 0],
                       show_background_frame=False,
                       text_position='center'):
        self.source_time = source_time
        self.sound_track = sound_track
        self.font = font
        self.font_size = font_size
        self.background_frame = background_frame
        self.output_location = output_location
        self.text_color = text_color
        self.background_color = background_color
        self.show_background_frame = show_background_frame
        self.text_position = text_position

    def canPreview(self):
        if self.videoInProgress:
            return False
        if (self.source_time == '') or\
           (self.sound_track == '') or\
           (self.font == '') or\
           (self.background_frame == '') or\
           (self.background_frame.startswith(':')):
            return False
        return True

    def canGenerate(self):
        if (self.canPreview() == False):
            return False
        else:
            return not(self.output_location == '')

    def getSourceTime(self, parent, openLocation):
        filters = 'All Acceptable Formats (*.xlsx *.xls *.csv *.tsv);;\
         Excel Files (*.xlsx *.xls);;\
         CSV Files (*.csv);;\
         TSV Files (*.tsv);;\
         All Files (*.*)'
        fname = QFileDialog.getOpenFileName(parent, 'Select Timecode File', openLocation,
                                            filters)
        return fname

    def getParamFont(self, parent, openLocation, openLocationOverride=False):
        filters = 'All Acceptable Formats (*.ttf *.otf);;\
         All Files (*.*)'
        file_open_dialog_directory = openLocation
        if not(openLocationOverride):
            if sys.platform == 'win32':
                file_open_dialog_directory = '\\\\localhost\\c$\\windows\\fonts'
            elif sys.platform == 'darwin':
                file_open_dialog_directory = '~/Library/Fonts'
        fname = QFileDialog.getOpenFileName(parent, 'Select Font File', file_open_dialog_directory,
                                            filters)
        return fname

    def getSoundTrack(self, parent, openLocation):
        filters = 'All Acceptable Formats (*.mp3 *.m4a *.wav  *.aac *.aif *.aiff);;\
         All Files (*.*)'
        fname = QFileDialog.getOpenFileName(parent, 'Select Soundtrack File', openLocation,
                                            filters)
        return fname

    def getBackgroundImage(self, parent, openLocation):
        filters = 'Image files (*.jpg *.jpeg *.gif *.png)'
        fname = QFileDialog.getOpenFileName(parent, 'Select Background File', openLocation,
                                            filters)
        return fname
