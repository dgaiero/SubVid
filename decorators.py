import functools

def _statusBarDecorator(message):
   def statusBarDecorator(func):
      @functools.wraps(func)
      def statusBarMessage_wrapper(self, *args, **kwargs):
         self.statusbar.showMessage(message)
         func(self)
         self.statusbar.clearMessage()
      return statusBarMessage_wrapper
   return statusBarDecorator


def _checkFileExists(func):
   @functools.wraps(func)
   def checkFileExists_wrapper(self):
      filesNotFoundList = self.checkFilesExist()
      if (filesNotFoundList != []):
         self.file_not_found.set_data(filesNotFoundList)
         self.file_not_found.show()
      else:
         func(self)
   return checkFileExists_wrapper

def _refreshPreview(func):
   @functools.wraps(func)
   def refreshPreview_wrapper(self):
      func(self)
      self.setPreviewPicture()
   return refreshPreview_wrapper
