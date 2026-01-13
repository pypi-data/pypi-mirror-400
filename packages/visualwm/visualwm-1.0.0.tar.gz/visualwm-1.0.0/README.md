# VisualWM - 泄密警示明水印SDK

一个功能强大的Python SDK，用于在图片、视频、文本、文档等多种载体中嵌入和提取泄密警示明水印。

## 功能特性

### 1. 多载体嵌入适配
- **图片**: PNG、JPG、JPEG、BMP、TIFF、WEBP
- **视频**: MP4、AVI、MOV、MKV、WMV、FLV、WEBM（支持多核并行加速）
- **文档**: 
  - Word (.docx) - Office 2007及以上
  - PDF 
  - Excel (.xlsx) - Office 2007及以上
- **文本**: 纯文本、HTML、Markdown

> ⚠️ **注意**: 不支持老版本Office格式（.doc, .xls），如需处理请先转换为新格式

### 2. 溯源信息完整嵌入
- 用户姓名、工号
- 设备编号、IP、MAC地址
- 时间戳
- 自定义扩展信息

### 3. 明水印样式定制
- 字体、颜色、透明度
- 位置（平铺、角落、居中）
- 旋转角度
- 高风险警示模式

### 4. 动态信息实时更新
- 自动获取当前时间
- 自动获取设备信息（IP、MAC）
- 支持自定义动态数据

### 5. 防篡改机制
- 内置校验码生成与验证
- 篡改检测与告警

### 6. 水印信息提取
- 从载体中提取水印文本
- OCR识别支持
- 校验码验证

## 安装

```bash
pip install visualwm
```

或从源码安装：

```bash
git clone https://github.com/example/visualwm.git
cd visualwm
pip install -e .
```

## 快速开始

### 图片水印

```python
from visualwm import ImageWatermark, WatermarkInfo, WatermarkStyle

# 创建水印信息
info = WatermarkInfo(
    username="张三",
    employee_id="EMP001",
    device_id="DEV-2024-001",
    auto_fill=True  # 自动填充IP、MAC、时间戳
)

# 创建水印样式
style = WatermarkStyle(
    font_size=24,
    color=(128, 128, 128),
    opacity=0.5,
    rotation=45,
    pattern="tile"  # 平铺模式
)

# 添加水印
wm = ImageWatermark()
wm.embed("input.jpg", "output.jpg", info, style)

# 提取水印信息
extracted_info = wm.extract("output.jpg")
print(extracted_info)
```

### 视频水印

```python
from visualwm import VideoWatermark, WatermarkInfo, WatermarkStyle

info = WatermarkInfo(username="李四", employee_id="EMP002", auto_fill=True)
style = WatermarkStyle(font_size=20, opacity=0.3, position="bottom_right")

wm = VideoWatermark()
wm.embed("input.mp4", "output.mp4", info, style)
```

### 文本水印

```python
from visualwm import TextWatermark, WatermarkInfo

info = WatermarkInfo(username="王五", employee_id="EMP003", auto_fill=True)

wm = TextWatermark()
# 生成带水印的文本
watermarked_text = wm.embed("这是需要添加水印的文本内容", info)
print(watermarked_text)
```

### 高风险警示模式

```python
from visualwm import ImageWatermark, WatermarkInfo, WatermarkStyle, RiskLevel

style = WatermarkStyle.high_risk_preset()  # 使用高风险预设样式
# 或自定义高风险样式
style = WatermarkStyle(
    font_size=32,
    color=(255, 0, 0),  # 红色
    opacity=0.7,
    bold=True,
    prefix="【机密】"
)

wm = ImageWatermark()
wm.embed("secret_doc.png", "output.png", info, style)
```

## API文档

### WatermarkInfo - 水印信息类

| 参数 | 类型 | 说明 |
|------|------|------|
| username | str | 用户姓名 |
| employee_id | str | 工号 |
| device_id | str | 设备编号 |
| ip_address | str | IP地址（auto_fill时自动获取） |
| mac_address | str | MAC地址（auto_fill时自动获取） |
| timestamp | str | 时间戳（auto_fill时自动获取） |
| custom_data | dict | 自定义扩展数据 |
| auto_fill | bool | 是否自动填充动态信息 |

### WatermarkStyle - 水印样式类

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| font_name | str | "SimHei" | 字体名称 |
| font_size | int | 24 | 字体大小 |
| color | tuple | (128,128,128) | RGB颜色 |
| opacity | float | 0.5 | 透明度(0-1) |
| rotation | int | 45 | 旋转角度 |
| position | str | "tile" | 位置模式 |
| bold | bool | False | 是否加粗 |
| prefix | str | "" | 前缀文字 |

### 位置模式

- `tile`: 平铺整个载体
- `center`: 居中显示
- `top_left`: 左上角
- `top_right`: 右上角
- `bottom_left`: 左下角
- `bottom_right`: 右下角

## 许可证

MIT License
