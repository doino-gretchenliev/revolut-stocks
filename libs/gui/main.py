import sys
import logging

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from libs.process import process, supported_parsers
from libs.gui.worker import Worker
from libs.gui.signals import LogSignal
from libs.gui.colors import log_colors
from libs.gui.multiselect import CheckableComboBox

TITLE = "NAP Stocks Calculator"


def set_loggers_handler(handler):
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).addHandler(handler)


def set_loggers_level(level):
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(level=level)


class Window(QMainWindow, logging.Handler):
    def __init__(self):
        super(Window, self).__init__()
        self.threadpool = QThreadPool()
        self.log_signal = LogSignal()

        self.setGeometry(50, 50, 600, 600)
        self.setWindowTitle(TITLE)

        self.input_dir = None
        self.output_dir = None

        self.home()

    def get_intput_dir(self):
        self.input_dir = self.open_dialog()
        self.input_box.setText(self.input_dir)
        if self.input_dir is not None and self.output_dir is not None:
            self.calc_button.setEnabled(True)

    def get_output_dir(self):
        self.output_dir = self.open_dialog()
        self.output_box.setText(self.output_dir)
        if self.input_dir is not None and self.output_dir is not None:
            self.calc_button.setEnabled(True)

    def open_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly

        return QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)

    def emit(self, record):
        msg = self.format(record)
        record_color = log_colors[record.levelname]
        html_msg = f'<font color="{record_color}">{msg}</font>'

        self.log_signal.new_message.emit(html_msg)

    def write_log_message(self, msg):
        self.log_widget.appendHtml(msg)

    def home(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        self.input_button = QPushButton("Select input directory")
        self.input_button.clicked.connect(self.get_intput_dir)
        self.input_box = QLineEdit()
        self.input_box.setReadOnly(True)

        self.output_button = QPushButton("Select output directory")
        self.output_button.clicked.connect(self.get_output_dir)
        self.output_box = QLineEdit()
        self.output_box.setReadOnly(True)

        self.parser_combo = CheckableComboBox(self)
        self.parser_combo.addItems(supported_parsers.keys(), next(iter(supported_parsers.keys())))

        self.calc_button = QPushButton("Calculate")
        self.calc_button.setEnabled(False)
        self.calc_button.clicked.connect(self.start_worker)

        self.log_widget = QPlainTextEdit()
        self.log_widget.setStyleSheet("background-color: rgb(30, 30, 30);")
        self.log_widget.setReadOnly(True)
        self.log_widget.moveCursor(QTextCursor.Start)
        self.log_widget.ensureCursorVisible()

        self.debug_check = QCheckBox("Enable verbose log.")
        self.debug_check.stateChanged.connect(self.toggle_debug)

        self.about_link = QLabel()
        self.about_link.setText('Developed by: <a href="https://github.com/doino-gretchenliev/revolut-stocks">Doino Gretchenliev</a>')
        self.about_link.setOpenExternalLinks(True)

        self.log_signal.new_message.connect(self.write_log_message)

        layout.addWidget(self.input_button)
        layout.addWidget(self.input_box)
        layout.addWidget(self.output_button)
        layout.addWidget(self.output_box)
        layout.addWidget(self.parser_combo)
        layout.addWidget(self.calc_button)
        layout.addWidget(self.log_widget)
        layout.addWidget(self.debug_check)
        layout.addWidget(self.about_link)

        self.show()

    def toggle_debug(self, state):
        if state == Qt.Checked:
            set_loggers_level(logging.DEBUG)
        else:
            set_loggers_level(logging.INFO)

    def finished(self):
        self.calc_button.setEnabled(True)

    def error(self, e):
        record_color = log_colors["ERROR"]
        html_msg = f'<font color="{record_color}">{e}</font>'
        self.log_signal.new_message.emit(html_msg)

    def start_worker(self):
        self.calc_button.setEnabled(False)
        self.log_widget.clear()
        worker = Worker(process, self.input_dir, self.output_dir, self.parser_combo.get_selected(), False)
        worker.signals.finished.connect(self.finished)
        worker.signals.error.connect(self.error)
        self.threadpool.start(worker)

    def write(self, m):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    set_loggers_level(logging.INFO)
    set_loggers_handler(window)
    sys.exit(app.exec_())
