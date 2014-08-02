import os, sys, subprocess, inspect, platform, argparse, mimetypes
from PyQt4 import QtCore, QtGui

if platform.system() == 'Darwin':
    onionshare_gui_dir = os.path.dirname(__file__)
else:
    onionshare_gui_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

try:
    import onionshare
except ImportError:
    sys.path.append(os.path.abspath(onionshare_gui_dir+"/.."))
    import onionshare
from onionshare import translated

class Application(QtGui.QApplication):
    def __init__(self):
        platform = onionshare.get_platform()
        if platform == 'Tails' or platform == 'Linux':
            self.setAttribute(QtCore.Qt.AA_X11InitThreads, True)

        QtGui.QApplication.__init__(self, sys.argv)

class FileList(QtGui.QListWidget):
    files_dropped = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(FileList, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QtCore.QSize(32, 32))

        self.filenames = []

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
            size = onionshare.human_readable_filesize(fileinfo.size())

            item = QtGui.QListWidgetItem('{0} ({1})'.format(basename, size))
            item.setIcon(icon)
            item.setToolTip(QtCore.QString(size))
            self.addItem(item)

class FileSelection(QtGui.QVBoxLayout):
    def __init__(self):
        super(FileSelection, self).__init__()

        # file list
        self.file_list = FileList()
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
        self.update()

        # add the widgets
        self.addWidget(self.file_list)
        self.addLayout(button_layout)

    def update(self):
        # delete button should be disabled if item isn't selected
        current_item = self.file_list.currentItem()
        if not current_item:
            self.delete_button.setEnabled(False)
        else:
            self.delete_button.setEnabled(True)

        # file list should have a background image if empty
        if len(self.file_list.filenames) == 0:
            self.file_list.setStyleSheet('background: url(drop_files.png) no-repeat center center')
        else:
            self.file_list.setStyleSheet('')

    def add_file(self):
        filename = QtGui.QFileDialog.getOpenFileName(caption=translated('choose_file'), options=QtGui.QFileDialog.ReadOnly)
        if filename:
            self.file_list.add_file(str(filename))
        self.update()

    def delete_file(self):
        current_row = self.file_list.currentRow()
        self.file_list.filenames.pop(current_row)
        self.file_list.takeItem(current_row)
        self.update()

class OnionShareGui(QtGui.QWidget):
    def __init__(self):
        global onionshare_gui_dir
        super(OnionShareGui, self).__init__()
        self.window_icon = QtGui.QIcon("{0}/onionshare-icon.png".format(onionshare_gui_dir))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('OnionShare')
        self.setWindowIcon(self.window_icon)

        # file selection
        file_selection = FileSelection()

        # main layout
        self.layout = QtGui.QHBoxLayout()
        self.layout.addLayout(file_selection)
        self.setLayout(self.layout)
        self.show()

    def alert(self, msg, icon=QtGui.QMessageBox.NoIcon):
        dialog = QtGui.QMessageBox()
        dialog.setWindowTitle("OnionShare")
        dialog.setWindowIcon(self.window_icon)
        dialog.setText(msg)
        dialog.setIcon(icon)
        dialog.exec_()

    def select_file(self, strings, filename=None):
        # get filename, either from argument or file chooser dialog
        if not filename:
            args = {}
            if onionshare.get_platform() == 'Tails':
                args['directory'] = '/home/amnesia'

            filename = QtGui.QFileDialog.getOpenFileName(caption=translated('choose_file'), options=QtGui.QFileDialog.ReadOnly, **args)
            if not filename:
                return False, False

            filename = str(filename)

        # validate filename
        if not os.path.isfile(filename):
            alert(translated("not_a_file").format(filename), QtGui.QMessageBox.Warning)
            return False, False

        filename = os.path.abspath(filename)
        basename = os.path.basename(filename)
        return filename, basename

def main():
    onionshare.strings = onionshare.load_strings()

    # start the Qt app
    app = Application()

    # check for root in Tails
    if onionshare.get_platform() == 'Tails' and not onionshare.is_root():
        subprocess.call(['/usr/bin/gksudo']+sys.argv)
        return

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-only', action='store_true', dest='local_only', help='Do not attempt to use tor: for development only')
    parser.add_argument('--stay-open', action='store_true', dest='stay_open', help='Keep hidden service running after download has finished')
    parser.add_argument('--debug', action='store_true', dest='debug', help='Log errors to disk')
    parser.add_argument('filename', nargs='?', help='File to share')
    args = parser.parse_args()

    filename = args.filename
    local_only = bool(args.local_only)
    stay_open = bool(args.stay_open)
    debug = bool(args.debug)

    onionshare.set_stay_open(stay_open)

    # try starting hidden service
    onionshare_port = onionshare.choose_port()
    local_host = "127.0.0.1:{0}".format(onionshare_port)
    if not local_only:
        try:
            onion_host = onionshare.start_hidden_service(onionshare_port)
        except onionshare.NoTor as e:
            alert(e.args[0], QtGui.QMessageBox.Warning)
            return
    onionshare.tails_open_port(onionshare_port)

    # clean up when app quits
    def shutdown():
        onionshare.tails_close_port(onionshare_port)
    app.connect(app, QtCore.SIGNAL("aboutToQuit()"), shutdown)

    # launch the window
    gui = OnionShareGui()

    # all done
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
