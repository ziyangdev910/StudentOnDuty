from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                            QGroupBox, QDialog, QFontComboBox, QGridLayout)

from PyQt6.QtGui import QIcon, QFont
import os
import sys
import winreg
import datetime

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
        self.main_window.group_label.setFont(new_font)
    
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

    def init_ui(self):
        self.setWindowTitle("设置")
        main_layout = QVBoxLayout()
        
        # 1. 学生名单设置组
        students_group = QGroupBox("学生名单设置")
        students_layout = QHBoxLayout()
        
        # 左侧：全体学生名单
        left_layout = QVBoxLayout()
        self.students_edit = QTextEdit()
        self.students_edit.setPlaceholderText("请输入全体学生名单，每行一个名字")
        self.students_edit.setText("\n".join(self.main_window.settings["students"]))
        self.students_edit.textChanged.connect(self.on_students_changed)
        left_layout.addWidget(QLabel("全体学生名单："))
        left_layout.addWidget(self.students_edit)
        
        # 右侧：班干部名单
        right_layout = QVBoxLayout()
        self.cadres_edit = QTextEdit()
        self.cadres_edit.setPlaceholderText("请输入值周生名单，每行一个名字")
        self.cadres_edit.setText("\n".join(self.main_window.settings.get("cadres", [])))
        self.cadres_edit.textChanged.connect(self.on_students_changed)
        right_layout.addWidget(QLabel("值周生名单："))
        right_layout.addWidget(self.cadres_edit)
        
        # 将左右布局添加到主布局
        students_layout.addLayout(left_layout)
        students_layout.addLayout(right_layout)
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
        
        # 添加小组设置
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("值周小组总数："))
        self.total_groups_spin = QSpinBox()
        self.total_groups_spin.setRange(1, 20)
        self.total_groups_spin.setValue(self.main_window.settings["total_groups"])
        group_layout.addWidget(self.total_groups_spin)
        
        group_layout.addWidget(QLabel("当前值周小组："))
        self.current_group_combo = QComboBox()
        self.update_group_combo()
        group_layout.addWidget(self.current_group_combo)
        
        duty_layout.addLayout(weekly_layout)
        duty_layout.addLayout(daily_layout)
        duty_layout.addLayout(group_layout)
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
        
        # connections
        self.opacity_spin.valueChanged.connect(self.apply_window_changes)
        self.size_spin.valueChanged.connect(self.apply_window_changes)
        self.font_combo.currentFontChanged.connect(self.apply_window_changes)
        self.font_spin.valueChanged.connect(self.apply_window_changes)
        self.always_on_top_check.toggled.connect(self.apply_window_changes)
        self.total_groups_spin.valueChanged.connect(self.update_group_combo)

        # 4. 跳过日期设置
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
        
        # 5. 开机自启动设置
        self.autostart_check = QCheckBox("开机自动启动")
        self.autostart_check.setChecked(self.main_window.settings["autostart"])
        main_layout.addWidget(self.autostart_check)
        
        # 6. 保存按钮
        save_button = QPushButton("保存设置")
        save_button.clicked.connect(self.save_settings)
        main_layout.addWidget(save_button)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 更新下拉框
        self.update_combo_boxes()
        self.update_group_combo()
        
        # 设置窗口大小
        self.resize(400, 600)

    def update_group_combo(self):
        """更新小组下拉框"""
        self.current_group_combo.clear()
        total_groups = self.total_groups_spin.value()
        groups = [f"第{i}组" for i in range(1, total_groups + 1)]
        self.current_group_combo.addItems(groups)
        
        current_group = self.main_window.settings["current_group"]
        if 1 <= current_group <= total_groups:
            self.current_group_combo.setCurrentIndex(current_group - 1)

    def update_combo_boxes(self):
        day_students = self.students_edit.toPlainText().split("\n")
        day_students = [s.strip() for s in day_students if s.strip()]
        week_students = self.cadres_edit.toPlainText().split("\n")
        week_students = [s.strip() for s in week_students if s.strip()]

        self.daily_combo.clear()
        self.weekly_combo.clear()
        
        if day_students:
            self.daily_combo.addItems(day_students)
            
            if self.main_window.settings["current_daily"] in day_students:
                self.daily_combo.setCurrentText(self.main_window.settings["current_daily"])
        
        if week_students:
            self.weekly_combo.addItems(week_students)
            
            if self.main_window.settings["current_weekly"] in week_students:
                self.weekly_combo.setCurrentText(self.main_window.settings["current_weekly"])
        
        # self.update_group_combo()

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
        self.main_window.settings["students"] = students
        
        # 保存班干部名单
        cadres = self.cadres_edit.toPlainText().split("\n")
        cadres = [s.strip() for s in cadres if s.strip()]
        self.main_window.settings["cadres"] = cadres
        
        # 处理学生名单的更新
        if students:  # 如果有学生
            new_weekly = self.weekly_combo.currentText()
            new_daily = self.daily_combo.currentText()
                
            if new_weekly:
                self.main_window.settings["current_weekly"] = new_weekly
                self.main_window.weekly_label.setText(f"值周：{new_weekly}")
                
            if new_daily:
                self.main_window.settings["current_daily"] = new_daily
                self.main_window.daily_label.setText(f"值日：{new_daily}")
        
        # 保存小组设置
        self.main_window.settings["total_groups"] = self.total_groups_spin.value()

        # 直接保存当前选择的小组值
        current_group = self.current_group_combo.currentIndex() + 1
        self.main_window.settings["current_group"] = current_group
        self.main_window.group_label.setText(f"小组：第{current_group}组")
        
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
        self.main_window.update_font()
        
        # 更新最后保存日期为今天，避免自动更新覆盖
        self.main_window.settings["last_update"] = str(datetime.date.today())
        
        # 保存跳过日期设置
        self.main_window.settings["skip_days"] = [day for day, check in zip(["周一", "周二", "周三", "周四", "周五", "周六", "周日"], self.skip_checks) if check.isChecked()]
        
        # 保存所有设置到文件
        self.main_window.save_settings()

        # 设置开机自动启动
        self.set_autostart(self.main_window.settings["autostart"])
        
        # 刷新设置页面的内容
        self.update_combo_boxes()
        self.update_group_combo()
        
        # 隐藏窗口
        self.hide()

    def closeEvent(self, event):
        """重写关闭事件"""
        self.hide()  # 隐藏窗口
        event.ignore()  # 忽略关闭事件，防止窗口被销毁
