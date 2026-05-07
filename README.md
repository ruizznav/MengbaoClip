# 萌宝剪贴板 🐾

一个基于 PyQt6 的 Windows 剪贴板管理工具，可爱又好用！

## ✨ 功能

- 📋 **剪贴板历史** - 自动记录复制的内容
- 🔍 **实时搜索** - 快速找到历史记录
- ⭐ **星标收藏** - 重要的内容标记起来
- 📝 **备注功能** - 给条目加备注名
- 📂 **分类管理** - 自定义分类，拖拽排序
- 📷 **图片支持** - 自动保存图片，缩略图预览
- 🔍 **OCR 识别** - 图片转文字（需安装 Tesseract）
- 📄 **富文本保留** - 复制格式文字，粘贴时保留样式
- 🗑️ **回收站** - 删除可恢复，彻底删除不残留
- 🎨 **多种主题** - 经典粉、奶蓝、暖橙、浅绿、梦幻紫
- 🖥️ **系统托盘** - 后台常驻，热键呼出
- 🔄 **数据备份** - 导出/导入/恢复
- ⚡ **开机自启** - 开机自动启动

## 🚀 快速开始

### 方法一：直接运行源码

```bash
pip install PyQt6 pillow pytesseract
python clipboard_single.py
```

### 方法二：打包成 exe

```bash
pip install PyInstaller
python -m PyInstaller --clean --onefile --windowed --noconsole --name "ClipboardManager" --distpath "dist_release" --add-data "icon_r.png;." clipboard_single.py
```

### 方法三：一键安装

双击 `install.bat`，自动打包 + 安装到电脑。

### OCR 识别（可选）

如需图片文字识别功能：
1. 安装 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki)（勾选简体中文）
2. `pip install pytesseract pillow`

## 📦 项目结构

```
├── clipboard_single.py      # 主程序（单文件）
├── icon_r.png               # 应用图标
├── install.bat              # 安装脚本
├── uninstall.bat            # 卸载脚本
├── build_final.bat          # 打包脚本
├── .gitignore
└── README.md
```

## 🔧 技术栈

- Python 3.13
- PyQt6
- Pillow (图片处理)
- PyInstaller (打包)
- pytesseract (OCR，可选)

## 👤 作者

- Ruizz
- Q 1367014277

## 📄 开源协议

MIT
