import os, sys, subprocess, inspect, platform, argparse, mimetypes
from PyQt4 import QtCore, QtGui
from file_selection import FileSelection

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

class OnionShareGui(QtGui.QWidget):
    def __init__(self):
        super(OnionShareGui, self).__init__()
        self.window_icon = QtGui.QIcon("{0}/onionshare-icon.png".format(onionshare_gui_dir))
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('OnionShare')
        self.setWindowIcon(self.window_icon)

        # file selection
        file_selection = FileSelection(onionshare)

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
