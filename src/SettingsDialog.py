from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                            QGroupBox, QDialog, QFontComboBox, QGridLayout)

from PyQt6.QtGui import QIcon, QFont
import os
import sys
import winreg
import datetime
import json
from UpdateForm import *

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
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.setWindowIcon(QIcon(os.path.join(self.base_path, "img/Tray.png")))      
        self.init_ui()

    # 监听学生名单改变
    def on_students_changed(self):
        students = self.students_edit.toPlainText().split("\n")
        students = [s.strip() for s in students if s.strip()]
        self.update_combo_boxes()

    def apply_window_changes(self):
        # Apply font changes
        new_font = QFont(self.font_combo.currentFont().family())
        new_font.setPointSize(self.font_spin.value())
        self.main_window.weekly_label.setFont(new_font)
        self.main_window.daily_label.setFont(new_font)
    
        # Apply opacity
        self.main_window.setWindowOpacity(self.opacity_spin.value())
    
        # Apply window size
        self.main_window.settings["window_size_ratio"] = self.size_spin.value()
        self.main_window.update_window_geometry()
        
        # Apply window flags (always on top)
        self.main_window.settings["always_on_top"] = self.always_on_top_check.isChecked()
        self.main_window.update_window_flags()
        
        # Update settings dictionary
        self.main_window.settings["font_family"] = self.font_combo.currentFont().family()
        self.main_window.settings["font_size"] = self.font_spin.value()
        self.main_window.settings["opacity"] = self.opacity_spin.value()

    def check_update(self):
        urls = {0:"https://api.github.com/repos/ziyangdev910/StudentOnDuty/releases/latest", 1:""}
        r = requests.get(urls[self.updateSourceComboBox.currentIndex()],verify=False)
        data = json.loads(r.text)
        durl = data["assets"][0]["browser_download_url"]
        widget = DownloadWidget(url=durl, file_path=durl.split("/")[-1])
        widget.show()

    def init_ui(self):
        self.setWindowTitle("设置")
        main_layout = QVBoxLayout()
        
        # 学生名单设置组
        students_group = QGroupBox("学生名单设置")
        students_layout = QVBoxLayout()
        self.students_edit = QTextEdit()
        self.students_edit.setPlaceholderText("请输入学生名单，每行一个名字")
        self.students_edit.setText("\n".join(self.main_window.settings["students"]))
        self.students_edit.textChanged.connect(self.on_students_changed)
        students_layout.addWidget(self.students_edit)
        students_group.setLayout(students_layout)
        main_layout.addWidget(students_group)
        
        # 当前值日值周生设置组
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
        
        # 窗口设置组
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
        
        # connections
        self.opacity_spin.valueChanged.connect(self.apply_window_changes)
        self.size_spin.valueChanged.connect(self.apply_window_changes)
        self.font_combo.currentFontChanged.connect(self.apply_window_changes)
        self.font_spin.valueChanged.connect(self.apply_window_changes)
        self.always_on_top_check.toggled.connect(self.apply_window_changes)


        # 跳过日期设置
        skip_group = QGroupBox("跳过日期设置")
        skip_layout = QGridLayout()
        
        # 周一到周日复选框
        self.skip_checks = []
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(days):
            check = QCheckBox(day)
            check.setChecked(day in self.main_window.settings.get("skip_days", []))
            self.skip_checks.append(check)
            skip_layout.addWidget(check, i // 3, i % 3)  # 3列网格布局
            
        skip_group.setLayout(skip_layout)
        main_layout.addWidget(skip_group)
        
        # 开机自启动设置
        self.autostart_check = QCheckBox("开机自动启动")
        self.autostart_check.setChecked(self.main_window.settings["autostart"])
        main_layout.addWidget(self.autostart_check)
        
        # 检查更新按钮
        update_group = QGroupBox("检查更新")
        update_layout = QHBoxLayout()
        self.checkUpdateButton = QPushButton("检查更新")
        self.checkUpdateButton.clicked.connect(self.check_update)
        update_layout.addWidget(self.checkUpdateButton)
        self.updateSourceComboBox = QComboBox()
        self.updateSourceComboBox.addItem("GitHub")
        #self.updateSourceComboBox.addItem("Gitee")
        self.updateSourceComboBox.setCurrentIndex(0)
        #self.updateSourceComboBox.currentIndexChanged.connect(self.update_update_source)
        update_layout.addWidget(self.updateSourceComboBox)
        update_group.setLayout(update_layout)
        main_layout.addWidget(update_group)
        
        
        # 保存按钮
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
                    # 设置开机启动指向主程序
                    winreg.SetValueEx(key, "StudentOnDuty", 0, winreg.REG_SZ, f'"{app_path}"')
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
        # old_students = self.main_window.settings["students"]
        self.main_window.settings["students"] = students
        
        # 处理学生名单的更新
        if students:  # 如果有学生
            # 下拉框自动更新，则框内必然有学生
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
        self.main_window.settings["skip_days"] = [day for day, check in zip(["周一", "周二", "周三", "周四", "周五", "周六", "周日"], self.skip_checks) if check.isChecked()]
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
