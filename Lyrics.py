from tablib import Dataset
from binaryornot.check import is_binary
import datetime
from timecode import Timecode

class Line():
   def __init__(self, start, end, line, fps):
      self.start = Timecode(fps,start)
      self.end = Timecode(fps, end)
      self.delta: Timecode = self.end - self.start
      self.num_frames = self.delta.frames
      # print(self.delta)
      # print(type(self.delta))
      # print(self.delta.total_seconds())
      # print(type(self.delta.total_seconds()))
      self.line = line.split("\\n")
      # print(f"{'; '.join(self.line):50s} - {self.delta} ({self.num_frames}) ({self.start} - {self.end})")

class Lyrics():
   def __init__(self, source, fps):
      self.source = source
      self.timecode_frames = []
      self.fps = fps
   
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
            if name == None:
               name = ''
         except KeyError:
            raise MalFormedDataException(self.tbData.headers)
         # print(f"({start} - {end}) - {name}")
         tLine = Line(start,end,name, self.fps)
         self.timecode_frames.append(tLine)


class MalFormedDataException(Exception):
   def __init__(self, headers):
      super().__init__("Data formatted incorrectly")
      self.message = "Required Headers: Name, Start, End"
      self.actual_headers = headers

if __name__ == "__main__":
   test = Timecode('song_markers.xlsx')
   test.importData()
   test.readData()
