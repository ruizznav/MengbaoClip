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
├── make_shortcuts.vbs       # 快捷方式辅助
├── .gitignore
└── README.md
```

## 📝 更新日志

### v3.0 (2026-05-08)

#### ✨ 新增功能
- ⏰ **时间显示** - 每条记录显示复制时间（月/日 时:分）
- 🖼️ **查看完整** - 图片右键可查看原图
- 📝 **备注增强** - 有备注的图片显示 📷+备注，文本显示 📄+备注
- 💾 **数据路径** - 默认存储路径改为 D:\Installation path\MengbaoClip

#### 🐛 Bug 修复
- 修复双击复制只复制标题不复制全文的问题
- 修复分类筛选显示混乱的问题
- 修复图片在不同分类下缩略图大小不一致的问题
- 修复复制文件时显示文件路径的问题（跳过非图片文件）
- 修复 QQ 等应用复制图片不显示的问题
- 修复加/删备注后图片不立即刷新的问题
- 修复文本查看完整版闪退的问题
- 修复设置页作者信息丢失的问题
- 修复热键响应不灵敏的问题（检测频率加快 + 修饰键宽松）
- 修复任务栏点击无法最小化的问题
- 统一右键菜单命名

#### 🎨 UI 优化
- 界面名称统一为「萌宝剪贴板」
- 左上角标题改为「萌宝剪贴板 v3」
- 状态栏按钮改名：「置顶」→「屏幕置顶」、「自启」→「开机自启」
- 设置页使用说明精简为 2 行
- 每条记录显示复制时间
- 有备注的条目显示对应图标（📷图片/📄文本）+ 备注

#### ❌ 移除
- 移除文本查看完整版功能（文本双击复制即可查看全文）
- 移除文件路径在剪贴板中的显示（复制文件时不记录）
- 移除右键菜单中的「复制图片」冗余项
- 主窗口标题改为「萌宝剪贴板 v3」

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
