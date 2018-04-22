#! python3
from pytube import YouTube
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import *
import os
import sys


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('YouDownload')
        self.setFixedSize(475, 325)
        # Fonts
        title_font = QtGui.QFont('Times', 24, QtGui.QFont.Bold)
        label_font = QtGui.QFont('Times', 8, QtGui.QFont.Bold)
        # Main title
        self.title = QtWidgets.QLabel("YouDownload")
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignBottom)
        # Play button image
        self.play_button = QtWidgets.QLabel()
        self.play_button.setPixmap(QtGui.QPixmap('playbutton.png'))

        title_frame = QtWidgets.QHBoxLayout()
        title_frame.addWidget(self.title)
        title_frame.addStretch()
        title_frame.addWidget(self.play_button)
        title_frame.addStretch()

        #Entry box for youtube link
        self.video_link_entry = QtWidgets.QLineEdit()
        self.video_entry_text = QtWidgets.QLabel('Video Link:')
        self.video_entry_text.setFont(label_font)

        # Frame for youtube link entry
        video_link_frame = QtWidgets.QHBoxLayout()
        video_link_frame.addWidget(self.video_entry_text)
        video_link_frame.addWidget(self.video_link_entry)
        video_link_frame.insertSpacing(2,50)

        # Edit Title
        self.title_label = QtWidgets.QLabel('Filename:')
        self.title_label.setAlignment(Qt.AlignRight)
        self.title_label.setFont(label_font)
        self.title_entry = QtWidgets.QLineEdit()

        #video title frame
        vid_title_frm = QtWidgets.QHBoxLayout()
        vid_title_frm.addWidget(self.title_label)
        vid_title_frm.addWidget(self.title_entry)
        vid_title_frm.insertSpacing(2,50)

        # Check boxes frame
        self.audio_only_cb = QtWidgets.QCheckBox('Audio Only')
        chkbox_frm = QtWidgets.QHBoxLayout()
        chkbox_frm.addWidget(self.audio_only_cb)
        chkbox_frm.addStretch()

        # Download / Change dir buttons
        self.changedir_button = QtWidgets.QPushButton("Change Dir")
        self.changedir_button.clicked.connect(self.change_save_path)
        self.download_button = QtWidgets.QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        button_frm = QtWidgets.QHBoxLayout()
        button_frm.addWidget(self.download_button)
        button_frm.addWidget(self.changedir_button)
        button_frm.addStretch()

        # Download thread
        self.downloader = Downloader(self)
        self.downloader.processSignal.connect(self.update_progressbar)


        # Save destination
        self.path_label = QtWidgets.QLabel("Download Destination:")
        self.path_label.setFont(label_font)
        self.path_var = os.path.expanduser('~')
        self.path_destination = QtWidgets.QLabel()
        self.path_destination.setText(self.path_var)

        # Save path frame
        save_path_frame = QtWidgets.QHBoxLayout()
        save_path_frame.addWidget(self.path_label)
        save_path_frame.addWidget(self.path_destination)
        save_path_frame.addStretch()

        # progress bar
        self.progress = QtWidgets.QProgressBar()

        # Main layout of window
        main_window_frame = QtWidgets.QVBoxLayout()
        main_window_frame.addLayout(title_frame)
        main_window_frame.insertSpacing(1, 15)
        main_window_frame.addLayout(video_link_frame)
        main_window_frame.addLayout(vid_title_frm)
        main_window_frame.addLayout(chkbox_frm)
        main_window_frame.addLayout(save_path_frame)
        main_window_frame.addLayout(button_frm)
        main_window_frame.addWidget(self.progress)

        self.setLayout(main_window_frame)
        self.show()

    def change_save_path(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.path_destination.setText(file)

    def download(self):
        if self.audio_only_cb.isChecked():
            self.downloader.download_video(self.video_link_entry.text(), self.path_destination.text(), audio_only=1, file_name=self.title_entry.text())
        else:
            self.downloader.download_video(self.video_link_entry.text(), self.path_destination.text(), file_name=self.title_entry.text())

    def update_progressbar(self, percentage):
        self.progress.setValue(percentage)
        if int(percentage) == 100:
            self.completed()

    def completed(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle("Completed")
        msg.setText('Video Downloaded successfully')
        msg.exec_()




class Downloader(QThread):

    processSignal = pyqtSignal(float)

    def __init__(self, parent=None):
        super(Downloader, self).__init__(parent=parent)
        self.path = None
        self.url = None
        self.video = None
        self.stream = None
        self.audio_only = None

    def download_video(self, url, path, audio_only=0, file_name=None):
        self.path = path
        self.url = url
        self.audio_only = audio_only
        self.file_name = file_name

        self.start()

    def run(self):
        self.video = YouTube(self.url)
        self.video.register_on_progress_callback(self.return_progress)
        if self.audio_only == 1:
            self.stream = self.video.streams.filter(only_audio=True).first()
        else:
            self.stream = self.video.streams.first()
        self.stream.download(self.path, self.file_name)

    def return_progress(self, stream, chunk, file_handle, bytes_remaining):
        percentage = (1 - bytes_remaining / self.stream.filesize) * 100
        self.processSignal.emit(percentage)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
app.exit(app.exec_())