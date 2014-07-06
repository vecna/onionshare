# import stuff for pyinstaller to find
import os, sys, subprocess, time, hashlib, platform, json, locale, socket, argparse, Queue, inspect, base64, random, functools
import PyQt5.QtCore, PyQt5.QtWidgets, PyQt5.QtWebKitWidgets, PyQt5.QtGui
import stem, stem.control, flask, itsdangerous
import onionshare, onionshare_gui

onionshare_gui.main()
