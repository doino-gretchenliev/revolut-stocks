from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class WorkerSignals(QObject):

    finished = pyqtSignal(object)
    error = pyqtSignal(tuple)


class LogSignal(QObject):

    new_message = pyqtSignal(str)
