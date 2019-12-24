from tablib import Dataset
from binaryornot.check import is_binary
import datetime

class Line():
   def __init__(self, start, end, line):
      self.start = datetime.datetime.strptime(start, '%H:%M:%S:%f').time()
      self.end = datetime.datetime.strptime(end, '%H:%M:%S:%f').time()
      self.start = datetime.datetime.combine(datetime.date(1, 1, 1), self.start)
      self.end = datetime.datetime.combine(datetime.date(1, 1, 1), self.end)
      self.delta = self.start - self.end
      self.line = line
      # print(f"{self.line} - {self.delta} ({self.start} - {self.end})")

class Timecode():
   def __init__(self, source):
      self.source = source
      self.timecode_frames = []
   
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
         except KeyError:
            raise MalFormedDataException(self.tbData.headers)
         print(f"{start} - {end} - {name}")
         tLine = Line(start,end,name)
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