import os, inspect
from PyQt4 import QtCore, QtGui

onionshare_gui_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

class FileList(QtGui.QListWidget):
    files_dropped = QtCore.pyqtSignal()

    def __init__(self, onionshare, parent=None):
        super(FileList, self).__init__(parent)
        self.onionshare = onionshare
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(32, 32))

        # drag and drop label
        self.drop_label = QtGui.QLabel(QtCore.QString('Drag and drop\nfiles here'), parent=self)
        self.drop_label.setAlignment(QtCore.Qt.AlignCenter)
        self.drop_label.setStyleSheet('background: url({0}/drop_files.png) no-repeat center center; color: #999999;'.format(onionshare_gui_dir))
        self.drop_label.hide()

        self.filenames = []
        self.update()

    def update(self):
        # file list should have a background image if empty
        if len(self.filenames) == 0:
            self.drop_label.show()
        else:
            self.drop_label.hide()

    def resizeEvent(self, event):
        self.drop_label.setGeometry(0, 0, self.width(), self.height())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            valid_files = False
            for url in event.mimeData().urls():
                filename = str(url.toLocalFile())
                if os.path.isfile(filename):
                    valid_files = True
            if valid_files:
                event.setDropAction(QtCore.Qt.CopyAction)
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                filename = str(url.toLocalFile())
                if os.path.isfile(filename):
                    self.add_file(filename)
        else:
            event.ignore()
        self.files_dropped.emit()

    def add_file(self, filename):
        if filename not in self.filenames:
            self.filenames.append(filename)

            basename = os.path.basename(filename)
            fileinfo = QtCore.QFileInfo(filename)
            ip = QtGui.QFileIconProvider()
            icon = ip.icon(fileinfo)
            size = self.onionshare.human_readable_filesize(fileinfo.size())

            item = QtGui.QListWidgetItem('{0} ({1})'.format(basename, size))
            item.setIcon(icon)
            item.setToolTip(QtCore.QString(size))
            self.addItem(item)

class FileSelection(QtGui.QVBoxLayout):
    def __init__(self, onionshare):
        super(FileSelection, self).__init__()
        self.onionshare = onionshare

        # file list
        self.file_list = FileList(onionshare)
        self.file_list.currentItemChanged.connect(self.update)
        self.file_list.files_dropped.connect(self.update)

        # buttons
        self.add_button = QtGui.QPushButton('Add')
        self.add_button.clicked.connect(self.add_file)
        self.delete_button = QtGui.QPushButton('Delete')
        self.delete_button.clicked.connect(self.delete_file)
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        # add the widgets
        self.addWidget(self.file_list)
        self.addLayout(button_layout)

        self.update()

    def update(self):
        # delete button should be disabled if item isn't selected
        current_item = self.file_list.currentItem()
        if not current_item:
            self.delete_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)

        # update the file list
        self.file_list.update()

    def add_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(caption=self.onionshare.translated('choose_file'), options=QtGui.QFileDialog.ReadOnly)
        if filename:
            self.file_list.add_file(str(filename))
        self.update()

    def delete_file(self):
        current_row = self.file_list.currentRow()
        self.file_list.filenames.pop(current_row)
        self.file_list.takeItem(current_row)
        self.update()

