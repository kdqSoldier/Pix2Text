import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QHBoxLayout, QFileDialog
from PyQt6.QtGui import QPixmap, QImage, QClipboard
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pix2text import Pix2Text
from concurrent.futures import ProcessPoolExecutor

class ImageRecognitionWorker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, image_path, p2t):
        super().__init__()
        self.image_path = image_path
        self.p2t = p2t

    def run(self):
        # 执行公式识别
        result = self.p2t.recognize_formula(self.image_path)
        self.result_signal.emit(result)

class ImageRecognitionApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("图片公式识别")
        self.setGeometry(100, 100, 800, 600)

        self.p2t = Pix2Text.from_config()

        self.layout = QVBoxLayout()

        # 图片显示框
        self.image_label = QLabel("图片显示框")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # 结果文本框
        self.result_text = QTextEdit(self)
        self.result_text.setPlaceholderText("识别结果将在这里显示")
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.paste_button = QPushButton("粘贴图片")
        self.paste_button.clicked.connect(self.paste_image)
        button_layout.addWidget(self.paste_button)

        self.load_button = QPushButton("加载图片")
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)

        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

    def paste_image(self):
        # 获取剪贴板内容并检查是否为图片
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        if mime_data.hasImage():
            # 获取剪贴板中的图片
            image = clipboard.pixmap()
            self.display_image_from_pixmap(image)

            # 将 pixmap 转换为图片文件并保存
            temp_file = 'temp_image.png'
            image.save(temp_file)

            # 使用后台线程进行识别
            self.recognize_formula_from_file(temp_file)
        else:
            self.result_text.setText("剪贴板中没有图片。")

    def load_image(self):
        # 通过文件选择对话框加载图片
        file, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.bmp *.jpeg)")
        if file:
            self.display_image(file)
            self.recognize_formula(file)

    def display_image(self, img_fp):
        # 显示从文件加载的图片
        pixmap = QPixmap(img_fp)
        self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.AspectRatioMode.KeepAspectRatio))

    def display_image_from_pixmap(self, pixmap):
        # 显示从剪贴板获取的图片
        self.image_label.setPixmap(pixmap.scaled(600, 400, Qt.AspectRatioMode.KeepAspectRatio))

    def recognize_formula(self, img_fp):
        # 使用多核加速识别
        def process_recognition():
            outs = self.p2t.recognize_formula(img_fp)
            self.result_text.setText(outs)

        # 在新的线程中执行识别过程
        executor = ProcessPoolExecutor()
        executor.submit(process_recognition)

    def recognize_formula_from_file(self, image_path):
        # 使用后台线程执行识别
        self.worker = ImageRecognitionWorker(image_path, self.p2t)
        self.worker.result_signal.connect(self.update_result)
        self.worker.start()

    def update_result(self, result):
        # 更新文本框显示识别结果
        self.result_text.setText(result)

    def keyPressEvent(self, event):
        # 实现 Ctrl + V 粘贴快捷键功能
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_V:
            self.paste_image()
        super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageRecognitionApp()
    window.show()
    sys.exit(app.exec())
