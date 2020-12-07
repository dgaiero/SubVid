import functools
import os
from collections import OrderedDict

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction, QActionGroup

SETTINGS_RECENTLY_OPENED = 'settings/recentlyOpened'

class RecentlyOpened():
    def __init__(self, parent):
        self.parent = parent
        self._items = list()

    def buildRecentlyOpenedDict(self):
        recentlyOpenedList = self.parent.appSettings.value(
            SETTINGS_RECENTLY_OPENED, [], type='QStringList'
        )
        for item in recentlyOpenedList:
            self._admitNewItem(item)

    def build_dropdown(self):
        if len(self._items) == 0:
            self.parent.actionOpenRecent.setDisabled(True)
        else:
            self.parent.actionOpenRecent.setEnabled(True)
            group = QActionGroup(self.parent.actionOpenRecent)
            self.parent.actionOpenRecent.clear()
            for item in self._items[:-6:-1]:
                path = os.path.normpath(item)
                filename = os.path.basename(path)
                action: QAction = self.parent.actionOpenRecent.addAction(
                    f"{filename}"
                )
                action.triggered.connect(
                    functools.partial(self.parent.readConfigFile, path))
                group.addAction(action)
            self.parent.actionOpenRecent.addSeparator()
            action: QAction = self.parent.actionOpenRecent.addAction("Clear List")
            action.triggered.connect(self.clearRecentlyOpened)

    def clearRecentlyOpened(self):
        self._items = list()
        self.setSettings()
        self.build_dropdown()

    def _admitNewItem(self, path):
        self._items.append(path)

    def admitNewItem(self, path):
        self._admitNewItem(path)
        self.setSettings()
        self.build_dropdown()

    def removeItem(self, key):
        self._items.pop()
        self.setSettings()

    def setSettings(self):
        self.parent.appSettings.setValue(
            SETTINGS_RECENTLY_OPENED, list(self._items))
