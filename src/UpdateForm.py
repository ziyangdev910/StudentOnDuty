import sys
import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton, QLabel, QMessageBox, QApplication
from PyQt6.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    progress_update = pyqtSignal(int)

    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path

    def run(self):
        response = requests.get(self.url, stream=True, verify=False)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(self.file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                downloaded_size += len(data)
                progress = int((downloaded_size / total_size) * 100)
                self.progress_update.emit(progress)

class DownloadWidget(QWidget):
    url = ""
    file_path = ""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def __init__(self, url, file_path):
        super().__init__()
        self.url = url
        self.file_path = file_path
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.label = QLabel('下载进度:', self)
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.layout.addWidget(self.progress_bar)

        self.button = QPushButton('开始下载', self)
        self.button.clicked.connect(self.start_download)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.setWindowTitle('文件下载进度条')
        self.setGeometry(300, 300, 300, 100)
        
        self.okbutton = QPushButton('取消', self)
        self.okbutton.clicked.connect(self.hide)
        self.layout.addWidget(self.okbutton)

    def start_download(self):
        if self.url == "" or self.file_path == "":
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle('错误')
            msg_box.setText('空的url或文件路径')
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
            return
        self.download_thread = DownloadThread(self.url, self.file_path)
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.start()
        self.button.setEnabled(False)
        print(self.url)

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.label.setText('下载完成!')

'''
if __name__ == '__main__':
    app = QApplication(sys.argv)
    r = requests.get("https://api.github.com/repos/ziyangdev910/StudentOnDuty/releases/latest",verify=False)
    import json
    data = json.loads(r.text)
    durl = data["assets"][0]["browser_download_url"]
    widget = DownloadWidget(url=durl, file_path=durl.split("/")[-1])
    widget.show()
    sys.exit(app.exec())
'''


