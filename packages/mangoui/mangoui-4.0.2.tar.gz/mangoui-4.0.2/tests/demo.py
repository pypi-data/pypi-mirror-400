from PySide6.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout, QWidget

# 定义两套主题
light_theme = {
    "primary_100": "#d4eaf7",
    "text_100": "#1d1c1c",
    "border": "1px solid #cccbc8",
    "border_radius": "7px",
    "font": {
        "title_size": 11,
    }
}

dark_theme = {
    "primary_100": "#2d2d2d",
    "text_100": "#ffffff",
    "border": "1px solid #3b3b3b",
    "border_radius": "7px",
    "font": {
        "title_size": 11,
    }
}


# 生成 QSS 样式
def generate_qss(theme):
    return f"""
        QPushButton {{
            background-color: {theme["primary_100"]};
            color: {theme["text_100"]};
            border: {theme["border"]};
            border-radius: {theme["border_radius"]};
        }}
        QLabel {{
            color: {theme["text_100"]};
            font-size: {theme["font"]["title_size"]}pt;
        }}
    """


# 切换主题
def apply_theme(theme):
    qss_style = generate_qss(theme)
    QApplication.instance().setStyleSheet(qss_style)


# 主窗口
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        button = QPushButton("切换主题")
        button.clicked.connect(self.toggle_theme)
        layout.addWidget(button)

        label = QLabel("这是一个标签")
        layout.addWidget(label)

        self.setLayout(layout)

    def toggle_theme(self):
        current_theme = dark_theme if QApplication.instance().styleSheet() == generate_qss(light_theme) else light_theme
        apply_theme(current_theme)


# 运行应用程序
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    apply_theme(light_theme)  # 初始主题
    window.show()
    app.exec()
