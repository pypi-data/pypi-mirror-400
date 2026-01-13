# 🚀 ArchLiner

<p align="center">
<pre align="center">
    ___                __    __    _                   
   /   |  _____ _____ / /_  / /   (_)____   ___   _____ 
  / /| | / ___// ___// __ \/ /   / // __ \ / _ \ / ___/ 
 / ___ |/ /   / /__ / / / / /___/ // / / //  __// /     
/_/  |_/_/    \___//_/ /_/_____/_//_/ /_/ \___//_/      
>> Streamlined Application Launcher for Arch Linux & XFCE
</pre>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OS-Arch%20Linux-blue?logo=arch-linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Desktop-XFCE-orange?logo=xfce&logoColor=white" />
  <img src="https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

---

**ArchLiner** 是一款专为 Arch Linux 用户（尤其是 XFCE 桌面环境）打造的轻量级、全能型启动器。它遵循 **KISS (Keep It Simple, Stupid)** 原则，完美弥补了原生启动器在终端交互、别名支持和文件搜索上的不足。

## ✨ 特性 (Features)

- 🔍 **智能程序索引**：深度解析 `.desktop` 文件，支持显示系统图标和友好名称，而非冷冰冰的二进制文件名。
- 🐚 **Shell 别名支持**：自动从你的 `bash` 或 `zsh` 配置文件中读取 `alias`，让你的快捷指令触手可及。
- 📂 **全盘闪电搜索**：集成 `plocate` 引擎，输入 `/` 或 `~` 即可在毫秒内定位全系统文件。
- 💻 **智能终端唤起**：自动识别指令类型。需要参数的复杂命令？自动打开终端并保持开启，方便查看输出。
- 🧮 **安全计算器**：内置沙箱化的数学表达式解析逻辑，输入即得结果，回车即刻复制。
- 🎨 **现代 UI 体验**：基于 PySide6 (Qt6) 开发，拥有 Nord 风格的深色配色和流畅的动态响应。

## 🛠 安装 (Installation)

### 1. 安装系统依赖
为了确保所有功能正常运行，你需要安装以下工具：
```bash
sudo pacman -S plocate xclip
# 更新文件索引数据库
sudo updatedb
```

### 2. 通过 PyPI 安装

```bash
pip install archliner
```

## ⌨️ 快速上手 (Quick Start)

### 配置快捷键

为了获得类似 macOS Spotlight 的体验，建议在 XFCE 中绑定 `Super + Space` (Command + Space)：

1. 打开 **设置 -> 键盘 -> 应用程序快捷键**。
2. 点击 **添加**。
3. 命令输入：`archliner`。
4. 按下 `Super + Space` 完成绑定。

### 使用技巧

* **启动程序**：直接输入 `firefox` 或 `浏览器`。
* **运行命令**：输入 `ping google.com`，它会自动弹出终端。
* **搜索文件**：输入 `/etc/pacman` 快速查看配置文件。
* **数学运算**：直接输入 `(512*2)/8`。

## 🏗 技术架构 (Architecture)

ArchLiner 采用了模块化的设计，确保启动速度和扩展性：

## 📝 路线图 (Roadmap)

* [ ] 增加常用文件的颜色标记
* [ ] 支持通过 `yay`/`pacman` 直接搜索软件库
* [ ] 增加简单的单位换算功能 (如 XXX)

## 📄 开源协议 (License)

本项目采用 [MIT License](./LICENSE) 开源。

---

**💡 提示**：如果你觉得好用，请给一个 ⭐️ Star！欢迎提交 Pull Request 来完善它。