import sys
import os
#import winreg  # Windows注册表操作
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QSystemTrayIcon, QMenu,  QVBoxLayout, QMessageBox, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import json

from SettingsDialog import *
from UpdateForm import *

VERSION = "V1.1.28"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 加载设置
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        # 这个base_path在真实情况下，指向的是主程序同目录下的_internal文件夹
        # 所以，Tray.png应该放在_internal文件夹下，而非主程序目录下！！！
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
        layout.setSpacing(5)  # 设置标签间距为7像素
        
        # 创建标签并设置大小策略
        self.weekly_label = QLabel()
        self.daily_label = QLabel()
        self.group_label = QLabel()
        
        # 设置标签大小策略，使其可以垂直扩展
        for label in [self.weekly_label, self.daily_label, self.group_label]:
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setMinimumHeight(50)  # 设置最小高度
            
        # 设置布局拉伸因子
        layout.addWidget(self.weekly_label, stretch=1)
        layout.addWidget(self.daily_label, stretch=1)
        layout.addWidget(self.group_label, stretch=1)
        
        # 设置字体
        self.update_font()
        
        # 设置对齐方式
        self.weekly_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.daily_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 设置样式
        self.weekly_label.setStyleSheet("color: black;")
        self.daily_label.setStyleSheet("color: black;")
        self.group_label.setStyleSheet("color: black;")
        
        layout.addWidget(self.weekly_label)
        layout.addWidget(self.daily_label)
        layout.addWidget(self.group_label)

    def setup_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(self.base_path, "img/Tray.png")))
        self.tray_icon.setToolTip("StudentOnDuty " + VERSION)
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
        # self.tray_menu.addSeparator()
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
        
        # 添加其他选项
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
        # self.context_menu.addSeparator()
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
        self.group_label.setFont(self.font)

    def load_settings(self):
        # 定义默认设置
        default_settings = {
            "students": [],
            "cadres": [],  # 班干部名单
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
            "skip_days": [],  # 添加跳过日期设置
            "total_groups": 6,  # 值周小组总数
            "current_group": 1,  # 当前值周小组
        }
        
        try:
            with open(os.path.join(self.base_path, "settings.json"), "r", encoding="utf-8") as f:
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
            self.group_label.setText("小组：第1组")
            return
            
        today = datetime.date.today()
        
        # 将周几转换为中文表示
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        current_day = weekdays[today.weekday()]
        
        # 如果当前日期在跳过列表中，则不更新
        if not current_day in self.settings.get("skip_days", []):  
            # 更新值周生（每周一更新，仅从班干部中循环）
            if today.weekday() == 0 or not self.settings["current_weekly"]:
                if self.settings["cadres"]:  # 如果有班干部名单
                    weekly_index = self.settings["cadres"].index(self.settings["current_weekly"]) if self.settings["current_weekly"] in self.settings["cadres"] else -1
                    weekly_index = (weekly_index + 1) % len(self.settings["cadres"])
                    self.settings["current_weekly"] = self.settings["cadres"][weekly_index]
                else:  # 如果没有班干部名单，从全体学生中循环
                    weekly_index = self.settings["students"].index(self.settings["current_weekly"]) if self.settings["current_weekly"] else -1
                    weekly_index = (weekly_index + 1) % len(self.settings["students"])
                    self.settings["current_weekly"] = self.settings["students"][weekly_index]
                
                # 更新值周小组（每周一更新）
                self.settings["current_group"] = (self.settings["current_group"] % self.settings["total_groups"]) + 1
                
            # 更新值日生（每天更新，从全体学生中循环）
            if str(today) != self.settings["last_update"]:
                daily_index = self.settings["students"].index(self.settings["current_daily"]) if self.settings["current_daily"] else -1
                daily_index = (daily_index + 1) % len(self.settings["students"])
                self.settings["current_daily"] = self.settings["students"][daily_index]
                self.settings["last_update"] = str(today)
        
        # 更新显示
        self.weekly_label.setText(f"值周：{self.settings['current_weekly']}")
        self.daily_label.setText(f"值日：{self.settings['current_daily']}")
        self.group_label.setText(f"小组：第{self.settings['current_group']}组")
        
        # 确保使用正确的字体
        self.update_font()
        
        # 保存更新后的设置
        self.save_settings()

    def save_settings(self):
        with open(os.path.join(self.base_path, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def update_window_geometry(self):
        """更新窗口几何形状"""
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * self.settings["window_size_ratio"])
        height = int(screen.height() * self.settings["window_size_ratio"])
        self.resize(width, height)
        
        # 更新标签高度
        label_height = int(height / 3) - 20  # 减去间距
        for label in [self.weekly_label, self.daily_label, self.group_label]:
            label.setMinimumHeight(label_height)
        
        # 只在没有保存位置时设置默认位置
        if "window_pos" not in self.settings:
            self.move(screen.width() - width, 0)

    def update_window_flags(self):
        """更新窗口标志"""
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        
        # 添加置顶/置底标志
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags |= Qt.WindowType.WindowStaysOnBottomHint
        
        # 添加穿透标志
        if self.settings.get("click_through", False):
            flags |= Qt.WindowType.WindowTransparentForInput
        else:
            flags &= ~Qt.WindowType.WindowTransparentForInput
        
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # try:
    #     with open('VERSION', 'r', encoding='utf-8') as f:
    #         VERSION = f.read()
    # except Exception as e:
    #     msg_box = QMessageBox()
    #     msg_box.setIcon(QMessageBox.Icon.Critical)
    #     msg_box.setWindowTitle('错误')
    #     msg_box.setText('未找到VERSION')
    #     msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    #     msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
    #     VERSION = "V1.1.0"
    window = MainWindow()
    window.show()
    sys.exit(app.exec())