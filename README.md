## 调试项目
1. 创建虚拟环境env
2. 在env中安装PyQt6：
   `pip install PyQt6`
   （切换到清华源以加速下载）
4. 保证`Desktop.ico`（图标文件，可自行更换）与`startup.bat`与`StudentOnDuty.py`处于同一目录下
5. 用env运行StudentOnDuty.py
## 打包程序
1. 在env中安装pyinstaller：
   `pip install pyinstaller`
2. 与`StudentOnDuty.py`同一目录下，在env中运行：
   `pyinstaller StudentOnDuty.spec`，
   将会在`dist\StudentOnDuty`目录下生成可执行文件与相关支持文件
3. 将`Desktop.ico`与`startup.bat`复制到`StudentOnDuty.exe`同目录下
4. 完成打包，现在可以正常运行程序了。
