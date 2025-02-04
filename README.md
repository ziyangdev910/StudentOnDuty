# StudentOnDuty 班级值周值日生公告牌
### 功能说明
#### 编写初衷 
免除每天把班级值周、值日同学的名字抄写在黑板上的麻烦。本程序通过内嵌于桌面的小窗口，显示值周、值日同学的姓名：每一天将值日生后推一位，每周一将值周生后推一位。
#### 使用方法
1. 右键单击托盘图标，单击“设置”菜单以打开设置界面；
2. 在“学生名单设置”的文本框中逐行填写本班所有参与值周值日排班同学的姓名，并根据实际情况选择当前的值周生和值日生；
3. 根据喜好修改显示姓名的字体和字号，以及窗口大小、窗口透明度，并选择是否开机自动启动；
4. 在显示窗口上右键单击，可以看到“允许拖动”和“窗口穿透”两个选项；在托盘图标上右键单击，也可以看到“允许拖动”和“窗口穿透”两个选项，另有“窗口置顶”选项。
**建议把窗口调整到合适的位置后，先取消勾选“允许拖动”，再勾选“窗口穿透”，最后取消勾选“窗口置顶”，从而实现“桌面内嵌名单”的效果。**

### 调试项目
1. 将项目克隆到本地后，在项目目录下创建虚拟环境env；
2. 在env中安装支持库：`pip install -r requirements.txt`；
3. 在虚拟环境env下运行 `src/StudentOnDuty.py`。

### 打包程序

1. 在虚拟环境env中安装pyinstaller：`pip install pyinstaller`；
2. 切换命令行的工作目录到根目录，在虚拟环境env中运行：
   `pyinstaller StudentOnDuty.spec`
   或者`pyinstaller --noconsole --add-data "src/img/Tray.png;./img/" --add-data "src/img/Tray.ico;./img/" --icon src/img/Tray.ico src/StudentOnDuty.py`
   （其中：图标需要准备2份，1份为png格式，用于程序内的调用，避免出现sRGB相关的问题；另1份为ico格式，用于pyinstaller打包。放于src/img/下）
   将会在 `./dist/StudentOnDuty`目录下生成可执行文件与相关支持文件；
3. 现在可以正常运行程序了。