import datetime
import re

from binaryornot.check import is_binary
from tablib import Dataset
from timecode import Timecode


class Line():
    def __init__(self, start, end, line, fps):
        self.start = Timecode(fps, start)
        self.end = Timecode(fps, end)
        self.delta: Timecode = self.end - self.start
        self.num_frames = self.delta.frames
        if line == '':
            self.line = [line]
        else:
            self.line = re.split(r'\\n|\\N', line)


class Lyrics():
    def __init__(self, source, fps):
        self.source = source
        self.timecode_frames = []
        self.fps = fps
        self.tbData = None

    def importData(self):
        read_type = 'r'
        if (is_binary(self.source)):
            read_type = 'rb'
        self.tbData = Dataset().load(open(self.source, read_type).read())

    def readData(self):
        for i in range(len(self.tbData)):
            try:
                start = self.tbData['Start'][i]
                end = self.tbData['End'][i]
                name = self.tbData['Name'][i]
                if name is None:
                    name = ''
            except KeyError:
                raise MalFormedDataException(self.tbData.headers)
            tLine = Line(start, end, name, self.fps)
            self.timecode_frames.append(tLine)


class MalFormedDataException(Exception):
    def __init__(self, headers):
        super().__init__("Data formatted incorrectly")
        self.message = "Required Headers: Name, Start, End"
        self.actual_headers = headers
