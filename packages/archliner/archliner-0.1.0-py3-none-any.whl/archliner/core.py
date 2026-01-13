import sys
import os
import subprocess
import configparser
import re
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLineEdit, QListWidget, QListWidgetItem)
from PySide6.QtGui import QIcon, Qt, QColor, QBrush
from PySide6.QtCore import QSize

class UltimateLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.apps_data = []
        self.load_desktop_files()
        self.load_shell_aliases()
        self.init_ui()
        
    def safe_calculate(self, text):
        # 只允许：数字, +, -, *, /, ., **, (, ), 和空格
        if not re.fullmatch(r"[0-9+\-*/.**\s()]+", text):
            return None
        
        try:
            # 尝试计算。限制 {} 和 [] 进一步防止特殊对象注入
            # 使用 {'__builtins__': {}} 禁用所有内置函数（如 open, __import__ 等）
            result = eval(text, {"__builtins__": {}}, {})
            
            # 结果如果是数字，返回字符串，否则返回 None
            if isinstance(result, (int, float)):
                # 格式化结果：如果是整数则显示整数，否则保留4位小数
                return f"{result:g}" 
        except:
            return None
        return None

    def load_desktop_files(self):
        paths = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
        for path in paths:
            if not os.path.exists(path): continue
            for file in os.listdir(path):
                if file.endswith('.desktop'):
                    try:
                        config = configparser.ConfigParser(interpolation=None)
                        config.read(os.path.join(path, file), encoding='utf-8')
                        if 'Desktop Entry' in config:
                            entry = config['Desktop Entry']
                            if entry.get('NoDisplay') == 'true': continue
                            self.apps_data.append({
                                'name': entry.get('Name', file),
                                'exec': entry.get('Exec', '').split(' %')[0].replace('"', ''),
                                'icon': entry.get('Icon', 'system-run'),
                                'type': 'app'
                            })
                    except: continue

    def load_shell_aliases(self):
        user_shell = os.environ.get("SHELL", "/bin/bash")
        try:
            result = subprocess.run([user_shell, "-i", "-c", "alias"], capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    match = re.match(r'alias (.*)=\'(.*)\'', line)
                    if match:
                        self.apps_data.append({
                            'name': f"Alias: {match.group(1)}",
                            'exec': match.group(2),
                            'icon': 'utilities-terminal',
                            'type': 'alias'
                        })
        except: pass

    def search_files(self, query):
        """使用 plocate 搜索文件"""
        # 如果路径确实存在且以 / 结尾，优先列出该目录下的文件（类似路径补全）
        expanded_path = os.path.expanduser(query)
        if os.path.isdir(expanded_path):
            try:
                # 列出该目录下的前10个文件/文件夹
                return [os.path.join(expanded_path, f) for f in os.listdir(expanded_path)[:10]]
            except:
                pass
                
        # 如果不是目录，则回退到全盘快速搜索
        try:
            # -l 10 限制返回 10 个结果，提高响应速度
            result = subprocess.run(['plocate', '-l', '10', '-i', query], capture_output=True, text=True)
            return result.stdout.splitlines()
        except:
            return []

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(700)
        
        layout = QVBoxLayout(self)
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("搜索程序、别名，或输入 / 搜索文件...")
        self.search_field.setStyleSheet("""
            QLineEdit {
                background-color: #2e3440; color: #eceff4;
                border: 2px solid #81a1c1; border-radius: 12px;
                padding: 18px; font-size: 18px;
            }
        """)
        
        self.result_list = QListWidget()
        self.result_list.setIconSize(QSize(28, 28))
        self.result_list.setStyleSheet("""
            QListWidget {
                background-color: #2e3440; color: #d8dee9;
                border: 2px solid #81a1c1; border-top: none;
                border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;
            }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #4c566a; }
        """)
        self.result_list.hide()
        
        layout.addWidget(self.search_field)
        layout.addWidget(self.result_list)
        self.search_field.textChanged.connect(self.update_list)
        self.search_field.returnPressed.connect(self.execute_selected)
        self.center_on_screen()

    def update_list(self, text):
        self.result_list.clear()
        if not text:
            self.result_list.hide()
            return

        # 1. 尝试安全计算
        calc_result = self.safe_calculate(text)
        if calc_result:
            item = QListWidgetItem(QIcon.fromTheme('accessorries-calculator'), f"= {calc_result}")
            item.setData(Qt.UserRole, f"echo {calc_result} | xclip -selection clipboard") # 逻辑：回车复制结果
            item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, "calc")
            self.result_list.addItem(item)
            self.result_list.show()
            self.adjustSize()
            # 如果是纯数字计算，我们可能不希望它干扰程序搜索，所以这里可以 return 
            # 或者继续往下走显示匹配的程序。

        # 判断是否进入文件搜索模式
        if text.startswith('/') or text.startswith('~'):
            files = self.search_files(text)
            for f in files:
                item = QListWidgetItem(QIcon.fromTheme('document-open'), os.path.basename(f))
                item.setToolTip(f)
                item.setData(Qt.UserRole, f)
                item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, "file")
                self.result_list.addItem(item)
        else:
            # 程序和别名搜索
            matches = [a for a in self.apps_data if text.lower() in a['name'].lower()][:8]
            for app in matches:
                item = QListWidgetItem(QIcon.fromTheme(app['icon'], QIcon.fromTheme('system-run')), app['name'])
                item.setData(Qt.UserRole, app['exec'])
                item.setData(Qt.ItemDataRole.AccessibleDescriptionRole, "app")
                self.result_list.addItem(item)
            if not matches:
                item = QListWidgetItem(QIcon.fromTheme('utilities-terminal'), f"运行原始命令: {text}")
                item.setData(Qt.UserRole, text)
                self.result_list.addItem(item)

        if self.result_list.count() > 0:
            self.result_list.show()
            self.result_list.setCurrentRow(0)
        else:
            self.result_list.hide()
        self.adjustSize()

    def execute_selected(self):
        item = self.result_list.currentItem()
        if not item: return
        
        target = item.data(Qt.UserRole)
        msg_type = item.data(Qt.ItemDataRole.AccessibleDescriptionRole)

        if msg_type == "calc":
            # 计算模式：将结果发送到剪贴板并退出
            # 需要安装 xclip: sudo pacman -S xclip
            subprocess.Popen(target, shell=True)
        if msg_type == "file":
            # 文件模式：使用 xdg-open 调用默认程序打开（如编辑器、播放器）
            subprocess.Popen(['xdg-open', target])
        else:
            # 程序/别名模式：判断是否需要终端
            if " " in self.search_field.text():
                subprocess.Popen(f"xfce4-terminal -e 'bash -ic \"{target}; exec bash\"'", shell=True)
            else:
                subprocess.Popen(target.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        QApplication.quit()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - 700) // 2, screen.height() // 4)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.result_list.setCurrentRow(self.result_list.currentRow() + 1)
        elif event.key() == Qt.Key_Up:
            self.result_list.setCurrentRow(self.result_list.currentRow() - 1)
        elif event.key() == Qt.Key_Escape:
            QApplication.quit()

def main():
    app = QApplication(sys.argv)
    ex = UltimateLauncher()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
