import sys
import os
import winreg  # Windows注册表操作
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QSystemTrayIcon, 
                            QMenu, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                            QGroupBox, QDialog, QFontComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import datetime
import json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 加载设置
        self.load_settings()
        
        # 创建主窗口组件
        self.setup_ui()
        
        # 创建系统托盘
        self.setup_tray()
        
        # 创建右键菜单
        self.create_context_menu()
        
        # 初始化设置对话框属性
        self.settings_dialog = None
        
        # 初始化状态
        self.draggable = self.settings.get("draggable", False)
        self.drag_position = None
        self.update_click_through(self.settings.get("click_through", False))
        
        # 恢复窗口位置和大小
        self.restore_window_position()
        self.update_window_geometry()
        
        # 更新值日值周生显示
        self.update_duty_students()
        
        # 更新窗口标志
        self.update_window_flags()

    def setup_ui(self):
        """初始化UI组件"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet("background-color: rgba(255, 255, 255, 200);")
        
        # 布局
        layout = QVBoxLayout(self.central_widget)
        
        # 创建标签
        self.weekly_label = QLabel()
        self.daily_label = QLabel()
        
        # 设置字体
        self.update_font()
        
        # 设置对齐方式
        self.weekly_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daily_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.weekly_label)
        layout.addWidget(self.daily_label)

    def setup_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(r"Desktop.ico"))
        self.tray_icon.setToolTip("StudentOnDuty_V1.0.1")
        self.create_tray_menu()  # 创建托盘菜单
        self.tray_icon.show()

    def create_tray_menu(self):
        """创建系统托盘菜单"""
        self.tray_menu = QMenu()
        
        # 添加拖动选项
        self.tray_drag_action = self.tray_menu.addAction("允许拖动")
        self.tray_drag_action.setCheckable(True)
        self.tray_drag_action.setChecked(self.settings.get("draggable", False))
        self.tray_drag_action.triggered.connect(self.toggle_draggable)
        
        # 添加鼠标穿透选项
        self.tray_menu.addSeparator()
        self.tray_click_through_action = self.tray_menu.addAction("鼠标穿透")
        self.tray_click_through_action.setCheckable(True)
        self.tray_click_through_action.setChecked(self.settings.get("click_through", False))
        self.tray_click_through_action.triggered.connect(self.toggle_click_through)
        
        # 添加窗口置顶选项
        self.tray_menu.addSeparator()
        self.tray_always_on_top_action = self.tray_menu.addAction("窗口置顶")
        self.tray_always_on_top_action.setCheckable(True)
        self.tray_always_on_top_action.setChecked(self.settings.get("always_on_top", True))
        self.tray_always_on_top_action.triggered.connect(self.toggle_always_on_top)
        
        # 添加分隔线和其他选项
        self.tray_menu.addSeparator()
        settings_action = self.tray_menu.addAction("设置")
        settings_action.triggered.connect(self.show_settings)
        quit_action = self.tray_menu.addAction("退出")
        quit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(self.tray_menu)

    def create_context_menu(self):
        """初始化右键菜单"""
        self.context_menu = QMenu(self)
        
        # 添加拖动选项
        self.drag_action = self.context_menu.addAction("允许拖动")
        self.drag_action.setCheckable(True)
        self.drag_action.setChecked(self.settings.get("draggable", False))
        self.drag_action.triggered.connect(self.toggle_draggable)
        
        # 添加鼠标穿透选项
        self.context_menu.addSeparator()
        self.click_through_action = self.context_menu.addAction("鼠标穿透")
        self.click_through_action.setCheckable(True)
        self.click_through_action.setChecked(self.settings.get("click_through", False))
        self.click_through_action.triggered.connect(self.toggle_click_through)

    def update_click_through(self, enabled):
        """更新鼠标穿透状态"""
        if not hasattr(self, 'central_widget'):
            return
            
        if enabled:
            # 设置窗口标志为穿透
            self.setWindowFlags(
                self.windowFlags() | 
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.Tool |
                Qt.WindowType.WindowTransparentForInput
            )
            # 设置窗口和中央部件为穿透
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.central_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.weekly_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.daily_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        else:
            # 移除穿透标志
            self.setWindowFlags(
                (self.windowFlags() & ~Qt.WindowType.WindowTransparentForInput) |
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            # 移除穿透属性
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.central_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.weekly_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.daily_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # 重新显示窗口以应用新的标志
        self.show()
        
        # 确保设置被正确保存
        self.settings["click_through"] = enabled
        self.save_settings()

    def update_font(self):
        """更新字体设置"""
        font_family = self.settings.get("font_family", "黑体")
        font_size = self.settings.get("font_size", 30)
        
        self.font = QFont(font_family, font_size)
        self.weekly_label.setFont(self.font)
        self.daily_label.setFont(self.font)

    def load_settings(self):
        # 定义默认设置
        default_settings = {
            "students": [],
            "opacity": 0.60,
            "autostart": False,
            "current_weekly": "",
            "current_daily": "",
            "last_update": "",
            "window_size_ratio": 0.20,
            "font_size": 30,
            "font_family": "黑体",
            "always_on_top": True,
            "draggable": False,
            "click_through": False,  # 添加鼠标穿透设置
            "window_pos": {
                "x": -1,
                "y": -1
            },
        }
        
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                saved_settings = json.load(f)
                self.settings = default_settings | saved_settings
        except FileNotFoundError:
            self.settings = default_settings
        
        self.setWindowOpacity(self.settings["opacity"])

    def show_settings(self):
        """显示设置对话框"""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.show()

    def update_duty_students(self):
        if not self.settings["students"]:
            self.weekly_label.setText("值周：未设置")
            self.daily_label.setText("值日：未设置")
            return
            
        today = datetime.date.today()
        
        # 更新值周生（每周一更新）
        if today.weekday() == 0 or not self.settings["current_weekly"]:
            weekly_index = self.settings["students"].index(self.settings["current_weekly"]) if self.settings["current_weekly"] else -1
            weekly_index = (weekly_index + 1) % len(self.settings["students"])
            self.settings["current_weekly"] = self.settings["students"][weekly_index]
            
        # 更新值日生（每天更新）
        if str(today) != self.settings["last_update"]:
            daily_index = self.settings["students"].index(self.settings["current_daily"]) if self.settings["current_daily"] else -1
            daily_index = (daily_index + 1) % len(self.settings["students"])
            self.settings["current_daily"] = self.settings["students"][daily_index]
            self.settings["last_update"] = str(today)
        
        # 更新显示
        self.weekly_label.setText(f"值周：{self.settings['current_weekly']}")
        self.daily_label.setText(f"值日：{self.settings['current_daily']}")
        
        # 确保使用正确的字体
        self.update_font()
        
        # 保存更新后的设置
        self.save_settings()

    def save_settings(self):
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def update_window_geometry(self):
        """更新窗口几何形状"""
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * self.settings["window_size_ratio"])
        height = int(screen.height() * self.settings["window_size_ratio"])
        self.resize(width, height)
        
        # 只在没有保存位置时设置默认位置
        if "window_pos" not in self.settings:
            self.move(screen.width() - width, 0)

    def update_window_flags(self):
        """更新窗口标志"""
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        
        # 添加置顶标志
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        
        # 添加穿透标志
        if self.settings.get("click_through", False):
            flags |= Qt.WindowType.WindowTransparentForInput
        
        self.setWindowFlags(flags)
        self.show()

    def toggle_draggable(self):
        """切换拖动状态"""
        sender = self.sender()
        is_checked = sender.isChecked()
        
        # 同步两个菜单的状态
        if sender == self.drag_action:
            self.tray_drag_action.setChecked(is_checked)
        else:
            self.drag_action.setChecked(is_checked)
        
        self.draggable = is_checked
        self.settings["draggable"] = is_checked
        self.save_settings()

    def toggle_click_through(self):
        """切换鼠标穿透状态"""
        sender = self.sender()
        is_checked = sender.isChecked()
        
        # 同步两个菜单的状态
        if sender == self.click_through_action:
            self.tray_click_through_action.setChecked(is_checked)
        elif sender == self.tray_click_through_action:
            self.click_through_action.setChecked(is_checked)
        
        # 更新穿透状态前，临时禁用穿透以确保菜单可以正常使用
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        if hasattr(self, 'central_widget'):
            self.central_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.weekly_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self.daily_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # 更新穿透状态
        self.update_click_through(is_checked)
        self.settings["click_through"] = is_checked
        self.save_settings()

    def toggle_always_on_top(self):
        """切换窗口置顶状态"""
        sender = self.sender()
        is_checked = sender.isChecked()
        
        # 同步托盘菜单和设置窗口的状态
        if hasattr(self, 'settings_dialog') and self.settings_dialog:
            self.settings_dialog.always_on_top_check.setChecked(is_checked)
        
        if sender != self.tray_always_on_top_action:
            self.tray_always_on_top_action.setChecked(is_checked)
        
        # 更新设置
        self.settings["always_on_top"] = is_checked
        self.save_settings()
        
        # 应用窗口置顶状态
        self.update_window_flags()

    def contextMenuEvent(self, event):
        """处理右键菜单事件"""
        # 临时禁用穿透以显示菜单
        was_click_through = self.settings.get("click_through", False)
        if was_click_through:
            self.update_click_through()
        
        # 显示菜单
        self.context_menu.exec(event.globalPos())
        
        # 如果之前是穿透状态，恢复穿透
        if was_click_through and self.click_through_action.isChecked():
            self.update_click_through()

    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.draggable:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.draggable:
            # 保存新的窗口位置
            self.settings["window_pos"] = {
                "x": self.pos().x(),
                "y": self.pos().y()
            }
            self.save_settings()
            self.drag_position = None
            event.accept()

    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.draggable and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            # 保存新的窗口位置
            self.settings["window_pos"] = {
                "x": self.pos().x(),
                "y": self.pos().y()
            }
            self.save_settings()
            event.accept()

    def restore_window_position(self):
        """恢复窗口位置"""
        # 获取保存的位置
        window_pos = self.settings.get("window_pos", {})
        x = window_pos.get("x")
        y = window_pos.get("y")
        
        if x is not None and y is not None:
            # 确保位置在屏幕范围内
            screen = QApplication.primaryScreen().geometry()
            x = max(0, min(x, screen.width() - self.width()))
            y = max(0, min(y, screen.height() - self.height()))
            self.move(x, y)
        else:
            # 如果没有保存的位置，使用默认位置
            self.update_window_geometry()

class SettingsDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowTitleHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self.main_window = main_window
        
        # 设置窗口图标
        self.setWindowIcon(QIcon(r"Desktop.ico"))
        
        self.init_ui()

    def on_students_changed(self):
        """Handle updates when student list changes"""
        students = self.students_edit.toPlainText().split("\n")
        students = [s.strip() for s in students if s.strip()]
        self.update_combo_boxes()

    def init_ui(self):
        self.setWindowTitle("设置")
        main_layout = QVBoxLayout()
        
        # 1. 学生名单设置组
        students_group = QGroupBox("学生名单设置")
        students_layout = QVBoxLayout()
        self.students_edit = QTextEdit()
        self.students_edit.setPlaceholderText("请输入学生名单，每行一个名字")
        self.students_edit.setText("\n".join(self.main_window.settings["students"]))
        self.students_edit.textChanged.connect(self.on_students_changed)
        students_layout.addWidget(self.students_edit)
        students_group.setLayout(students_layout)
        main_layout.addWidget(students_group)
        
        # 2. 当前值日值周生设置组
        duty_group = QGroupBox("当前值日值周生")
        duty_layout = QVBoxLayout()
        
        weekly_layout = QHBoxLayout()
        weekly_layout.addWidget(QLabel("当前值周生："))
        self.weekly_combo = QComboBox()
        weekly_layout.addWidget(self.weekly_combo)
        
        daily_layout = QHBoxLayout()
        daily_layout.addWidget(QLabel("当前值日生："))
        self.daily_combo = QComboBox()
        daily_layout.addWidget(self.daily_combo)
        
        duty_layout.addLayout(weekly_layout)
        duty_layout.addLayout(daily_layout)
        duty_group.setLayout(duty_layout)
        main_layout.addWidget(duty_group)
        
        # 3. 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QVBoxLayout()
        
        # 窗口置顶设置
        self.always_on_top_check = QCheckBox("窗口置顶")
        self.always_on_top_check.setChecked(self.main_window.settings.get("always_on_top", True))
        self.always_on_top_check.toggled.connect(self.main_window.toggle_always_on_top)
        window_layout.addWidget(self.always_on_top_check)
        
        # 字体设置
        font_group = QHBoxLayout()
        font_group.addWidget(QLabel("字体："))
        self.font_combo = QFontComboBox()
        current_font = self.main_window.settings.get("font_family", "黑体")
        self.font_combo.setCurrentFont(QFont(current_font))
        font_group.addWidget(self.font_combo)
        
        font_group.addWidget(QLabel("字体大小："))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(10, 100)
        self.font_spin.setValue(self.main_window.settings["font_size"])
        font_group.addWidget(self.font_spin)
        
        window_layout.addLayout(font_group)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度："))
        self.opacity_spin = QDoubleSpinBox()
        self.opacity_spin.setRange(0.1, 1.0)
        self.opacity_spin.setSingleStep(0.1)
        self.opacity_spin.setValue(self.main_window.settings["opacity"])
        opacity_layout.addWidget(self.opacity_spin)
        window_layout.addLayout(opacity_layout)
        
        # 窗口大小设置
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("窗口大小比例："))
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(0.05, 0.5)
        self.size_spin.setSingleStep(0.01)
        self.size_spin.setValue(self.main_window.settings["window_size_ratio"])
        size_layout.addWidget(self.size_spin)
        window_layout.addLayout(size_layout)
        
        window_group.setLayout(window_layout)
        main_layout.addWidget(window_group)
        
        # 4. 开机自启动设置
        self.autostart_check = QCheckBox("开机自动启动")
        self.autostart_check.setChecked(self.main_window.settings["autostart"])
        main_layout.addWidget(self.autostart_check)
        
        # 5. 保存按钮
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(save_button)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 更新下拉框
        self.update_combo_boxes()
        
        # 设置窗口大小
        self.resize(400, 600)

    def update_combo_boxes(self):
        students = self.students_edit.toPlainText().split("\n")
        students = [s.strip() for s in students if s.strip()]
        
        self.weekly_combo.clear()
        self.daily_combo.clear()
        
        if students:
            self.weekly_combo.addItems(students)
            self.daily_combo.addItems(students)
            
            if self.main_window.settings["current_weekly"] in students:
                self.weekly_combo.setCurrentText(self.main_window.settings["current_weekly"])
            if self.main_window.settings["current_daily"] in students:
                self.daily_combo.setCurrentText(self.main_window.settings["current_daily"])

    def set_autostart(self, enable):
        try:
            # 获取程序路径
            app_path = os.path.abspath(sys.argv[0])
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"程序路径不存在: {app_path}")
                
            # 打开注册表项
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Run",
                               0, winreg.KEY_ALL_ACCESS)
            try:
                if enable:
                    # 获取批处理文件路径
                    bat_path = os.path.join(os.path.dirname(app_path), "startup.bat")
                    if not os.path.exists(bat_path):
                        raise FileNotFoundError(f"批处理文件不存在: {bat_path}")
                        
                    # 设置开机启动指向批处理文件
                    winreg.SetValueEx(key, "StudentOnDuty", 0, winreg.REG_SZ, f'"{bat_path}"')
                else:
                    # 删除开机启动项
                    try:
                        winreg.DeleteValue(key, "StudentOnDuty")
                    except FileNotFoundError:
                        pass  # 如果不存在则忽略
            finally:
                winreg.CloseKey(key)
                
        except Exception as e:
            print(f"设置开机启动失败: {str(e)}")
            # 回滚设置
            self.autostart_check.setChecked(not enable)
            self.main_window.settings["autostart"] = not enable

    def save_settings(self):
        # 保存学生名单
        students = self.students_edit.toPlainText().split("\n")
        students = [s.strip() for s in students if s.strip()]
        old_students = self.main_window.settings["students"]
        self.main_window.settings["students"] = students
        
        # 处理学生名单的更新
        if students:  # 如果有学生
            if not old_students:  # 如果是第一次添加学生
                # 设置第一个学生为值日值周生
                first_student = students[0]
                self.main_window.settings["current_weekly"] = first_student
                self.main_window.settings["current_daily"] = first_student
                
                # 更新主界面显示
                self.main_window.weekly_label.setText(f"值周：{first_student}")
                self.main_window.daily_label.setText(f"值日：{first_student}")
                
                # 更新下拉框
                self.weekly_combo.clear()
                self.daily_combo.clear()
                self.weekly_combo.addItems(students)
                self.daily_combo.addItems(students)
                self.weekly_combo.setCurrentText(first_student)
                self.daily_combo.setCurrentText(first_student)
            else:
                # 如果已有学生，使用下拉框的选择
                new_weekly = self.weekly_combo.currentText()
                new_daily = self.daily_combo.currentText()
                
                if new_weekly:
                    self.main_window.settings["current_weekly"] = new_weekly
                    self.main_window.weekly_label.setText(f"值周：{new_weekly}")
                
                if new_daily:
                    self.main_window.settings["current_daily"] = new_daily
                    self.main_window.daily_label.setText(f"值日：{new_daily}")
        
        # 保存窗口设置
        self.main_window.settings["opacity"] = self.opacity_spin.value()
        self.main_window.settings["window_size_ratio"] = self.size_spin.value()
        self.main_window.settings["font_family"] = self.font_combo.currentFont().family()
        self.main_window.settings["font_size"] = self.font_spin.value()
        self.main_window.settings["always_on_top"] = self.always_on_top_check.isChecked()
        self.main_window.settings["autostart"] = self.autostart_check.isChecked()
        
        # 应用窗口设置
        self.main_window.setWindowOpacity(self.opacity_spin.value())
        self.main_window.update_window_flags()
        self.main_window.update_window_geometry()
        
        # 应用字体设置
        new_font = QFont(self.main_window.settings["font_family"])
        new_font.setPointSize(self.main_window.settings["font_size"])
        self.main_window.weekly_label.setFont(new_font)
        self.main_window.daily_label.setFont(new_font)
        
        # 更新今天的日期
        self.main_window.settings["last_update"] = str(datetime.date.today())
        
        # 保存所有设置到文件
        self.main_window.save_settings()

        # 设置开机自动启动
        self.set_autostart(self.main_window.settings["autostart"])
        
        # 刷新设置页面的内容
        self.update_combo_boxes()
        
        # 隐藏窗口
        self.hide()

    def closeEvent(self, event):
        """重写关闭事件"""
        self.hide()  # 隐藏窗口
        event.ignore()  # 忽略关闭事件，防止窗口被销毁

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
