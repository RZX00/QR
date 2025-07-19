# QR码处理工具

一个强大的QR码检测、截取和转换工具集，支持透明背景和SVG转换。

## ✨ 功能特点

- **自动检测** - 智能识别图片中的QR码
- **精确截取** - 按比例保留边距，确保扫码可靠性
- **透明背景** - 自动将白色背景设为透明，适用于任何背景
- **颜色反转** - 将黑色QR码转为白色，适用于深色背景
- **SVG转换** - 生成矢量格式，支持无限缩放
- **批量处理** - 一次处理整个文件夹
- **多种启动方式** - 支持Windows、macOS、Linux

## 🚀 快速开始

### 1. 准备图片
将包含QR码的图片放入 `image` 文件夹

### 2. 一键启动
**Windows**: 双击 `启动QR码处理工具.bat`  
**macOS/Linux**: 运行 `./启动QR码处理工具.sh`  
**通用**: 运行 `python start_qr_tool.py`

### 3. 查看结果
处理完成后，结果保存在 `qr_output` 目录：
- `qr_codes/` - 截取的QR码PNG文件
- `transparent_codes/` - 透明背景版本
- `svg_codes/` - SVG矢量格式

## 🔧 高级使用

### 命令行方式
```bash
# 基础截取
python qr_processor.py image_folder

# 生成透明背景
python qr_processor.py image_folder --transparent

# 转换为SVG
python qr_processor.py image_folder --svg

# 完整处理（推荐）
python qr_processor.py image_folder --transparent --svg

# 自定义参数
python qr_processor.py image_folder -o output_dir -m 0.1 -s 100 --transparent --svg
```

### 参数说明
- `-o, --output` - 输出目录
- `-m, --margin` - 边距比例（默认0.05=5%）
- `-s, --min-size` - 最小QR码尺寸（默认50像素）
- `--transparent` - 生成透明背景
- `--svg` - 转换为SVG格式
- `-q, --quiet` - 静默模式

## 📁 输出结构

```
qr_output/
├── qr_codes/           # 基础截取文件
│   ├── image1_qr.png
│   └── image2_qr.png
├── transparent_codes/  # 透明背景版本
│   ├── image1_qr_transparent.png
│   └── image2_qr_transparent.png
└── svg_codes/          # SVG矢量格式
    ├── image1_qr.svg
    └── image2_qr.svg
```

## ⚙️ 安装要求

### 系统要求
- Python 3.7+
- Windows 10/11、macOS 10.14+、Linux

### 依赖包
自动安装，或手动安装：
```bash
pip install opencv-python pyzbar qrcode[pil]
```

## 📖 使用技巧

### 最佳实践
1. **边距设置**: 5%紧凑，10%适中，15%宽松
2. **图片格式**: 支持JPG、PNG、BMP、TIFF、WEBP
3. **透明背景**: 适用于白底黑码的QR码
4. **SVG格式**: 用于印刷和矢量设计

### 常见问题
**Q: QR码检测不到？**  
A: 确保图片清晰，QR码完整，尺寸不小于50像素

**Q: 透明背景效果不好？**  
A: 调整`--white-threshold`和`--tolerance`参数

**Q: 依赖安装失败？**  
A: 更新pip: `python -m pip install --upgrade pip`

## 🛠️ 工具文件

### 核心工具
- `qr_processor.py` - 主处理工具（推荐使用）
- `qr_extractor.py` - 基础截取工具
- `qr_to_svg.py` - SVG转换工具
- `qr_transparent.py` - 透明背景工具

### 启动脚本
- `启动QR码处理工具.bat` - Windows启动器
- `启动QR码处理工具.sh` - Linux/macOS启动器
- `start_qr_tool.py` - Python启动器
- `快速启动.cmd` - Windows快速启动

## 📝 更新日志

### v2.0.0
- ✅ 重构为统一的本地处理工具
- ✅ 移除Web界面，专注命令行使用
- ✅ 集成所有功能到单一工具
- ✅ 优化透明背景算法
- ✅ 改进批量处理性能

### v1.0.0
- ✅ 基础QR码检测和截取
- ✅ 透明背景处理
- ✅ SVG转换功能
- ✅ Web界面支持

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**💡 提示**: 推荐使用 `python qr_processor.py image --transparent --svg` 获得最佳效果！