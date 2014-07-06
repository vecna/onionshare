# Building OnionShare

## GNU/Linux

Start by getting a copy of the source code:

```sh
git clone https://github.com/micahflee/onionshare.git
cd onionshare
```

*For .deb-based distros (like Debian, Ubuntu, Linux Mint):*

Note that python-stem appears in Debian wheezy and newer (so by extension Tails 1.1 and newer), and it appears in Ubuntu 13.10 and newer. Older versions of Debian and Ubuntu aren't supported.

```sh
sudo apt-get install -y build-essential fakeroot python-all python-stdeb python-flask python-stem python-qt4
./build_deb.sh
sudo dpkg -i deb_dist/onionshare_*.deb
```

*For .rpm-based distros (Red Hat, Fedora, CentOS):*

```sh
sudo yum install -y rpm-build python-flask python-stem pyqt4
./build_rpm.sh
sudo yum install -y dist/onionshare-*.rpm
```

## Mac OS X

Set up your development environment:

* Install Xcode from the Mac App Store.
* Go to http://qt-project.org/downloads and download and install the latest Qt5 for Mac.
* If you don't already have pip, install it with `sudo easy_install pip`.
* Install virtualenv with `sudo pip install virtualenv`.
* Go to http://www.riverbankcomputing.co.uk/software/sip/download and download the latest SIP for Mac (I downloaded `sip-4.16.2.tar.gz`).
* Go to http://www.riverbankcomputing.co.uk/software/pyqt/download5 and download the latest PyQt5 for Mac (I downloaded `PyQt-gpl-5.3.1.tar.gz`).

After installing Qt5, make sure its bin directory is added to your path:

```sh
echo export PATH=\$PATH:~/Qt/5.3/clang_64/bin >> ~/.profile
source ~/.profile
```

Now compile SIP:

```sh
cd ~/Downloads/
tar -xvf sip-4.16.2.tar.gz
cd sip-4.16.2
python configure.py
make
sudo make install

# make sip available in path too
echo export PATH=\$PATH:/System/Library/Frameworks/Python.framework/Versions/2.7/bin/ >> ~/.profile
source ~/.profile
```

Now compile PyQt5:

```sh
cd ~/Downloads/
tar -xvf PyQt-gpl-5.3.1.tar.gz
cd PyQt-gpl-5.3.1
python configure.py
# type "yes" to accept the license
make
sudo make install
```

Now make sure python can find PyQt5 on your system:
```sh
echo export PYTHONPATH=\$PYTHONPATH:/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages >> ~/.profile
source ~/.profile
```

Now get the source code and set up the virtualenv:

```sh
git clone https://github.com/micahflee/onionshare.git
cd onionshare
virtualenv env
. env/bin/activate
pip install flask stem pyinstaller itsdangerous
```

Each time you start work:

```sh
. env/bin/activate
```

To build the .app:

```sh
pyinstaller -w -y setup/onionshare-osx.spec
```

Now you should have `dist/OnionShare.app`.

To build a .dmg (this script builds the .app for you):

```sh
./build_dmg.sh
```

Now you should have `dist/OnionShare.dmg`.

## Windows

The first time you're setting up your dev environment:

* Download and install the latest python 2.7 from https://www.python.org/downloads/ -- make sure you install the 32-bit version.
* Right click on Computer, go to Properties. Click "Advanced system settings". Click Environment Variables. Under "System variables" double-click on Path to edit it. Add `;C:\Python27;C:\Python27\Scripts` to the end. Now you can just type `python` to run python scripts in the command prompt.
* Go to https://pip.pypa.io/en/latest/installing.html. Right-click on `get-pip.py` and Save Link As, and save it to your home folder.
* Open `cmd.exe` as an administrator. Type: `python get-pip.py`. Now you can use `pip` to install packages.
* Open a command prompt and type: `pip install flask stem pyinstaller`
* Go to http://www.riverbankcomputing.com/software/pyqt/download and download the latest PyQt4 for Windows for python 2.7, 32-bit (I downloaded `PyQt4-4.11-gpl-Py2.7-Qt4.8.6-x32.exe`), then install it.
* Go to http://sourceforge.net/projects/pywin32/ and download and install the latest 32-bit pywin32 binary for python 2.7. I downloaded `pywin32-219.win32-py2.7.exe`.
* Download and install the [Microsoft Visual C++ 2008 Redistributable Package (x86)](http://www.microsoft.com/en-us/download/details.aspx?id=29).

To make a .exe:

* Open a command prompt, cd into the onionshare directory, and type: `pyinstaller -y setup\onionshare-win.spec`. Inside the `dist` folder there will be a folder called `onionshare` with `onionshare.exe` in it.

If you want to build the installer:

* Go to http://nsis.sourceforge.net/Download and download the latest NSIS. I downloaded `nsis-3.0b0-setup.exe`.
* Right click on Computer, go to Properties. Click "Advanced system settings". Click Environment Variables. Under "System variables" double-click on Path to edit it. Add `;C:\Program Files (x86)\NSIS` to the end. Now you can just type `makensisw [script]` to build an installer.

To build the installer:

* Open a command prompt, cd to the onionshare directory, and type:

`build_exe.bat`

A NSIS window will pop up, and once it's done you will have `dist\OnionShare_Setup.exe`.

## Tests

OnionShare includes [nose](https://nose.readthedocs.org/en/latest/) unit tests. First,

```sh
sudo pip install nose
```

To run the tests:

```sh
nosetests test
```
