import os, inspect, platform
from PyQt4 import QtCore, QtGui
import common

class Controls(QtGui.QVBoxLayout):
    def __init__(self, onionshare, file_selection, parent=None):
        super(Controls, self).__init__(parent)
        self.onionshare = onionshare
        self.file_selection = file_selection
        self.server_running = False

        # buttons
        self.server_button = QtGui.QPushButton('')
        self.server_button.clicked.connect(self.server_toggle)
        self.copy_url_button = QtGui.QPushButton('Copy URL')
        self.copy_url_button.clicked.connect(self.copy_url)

        # add the widgets
        self.addWidget(self.server_button)
        self.addWidget(self.copy_url_button)
        self.update()

    def update(self):
        if self.server_running:
            self.server_button.setEnabled(True)
            self.server_button.setText(QtCore.QString('Stop Server'))
            self.copy_url_button.setEnabled(True)
        else:
            self.server_button.setEnabled(True)
            self.server_button.setText(QtCore.QString('Start Server'))
            self.copy_url_button.setEnabled(False)

    def server_toggle(self):
        if self.server_running:
            self.server_running = False
        else:
            self.server_running = True

        self.update()

    def copy_url(self):
        pass
