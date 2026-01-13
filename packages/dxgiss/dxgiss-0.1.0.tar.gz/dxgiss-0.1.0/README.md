# DXGISS Python Wrapper

轻量级的 Windows 屏幕捕获封装，基于本地 `DXGISS.dll`（使用 DXGI）。提供一个简单的 Python 类 `DXGI` 用于设置捕获区域并获取帧作为 `numpy.ndarray`。

## 特性
- 通过 DirectX/DXGI 高效捕获屏幕
- 返回 `numpy` 数组：形状为 `(height, width, channels)`，数据类型为 `uint8`
- 可选保留 Alpha 通道（BGRA）或仅 BGR

## 要求
- Windows（Win32 API + DXGI）
- Python 3.8+
- `numpy`
- 本地 DLL：`DXGISS/DXGISS.dll`（必须随包一起提供）

## 安装
1. 确保 `DXGISS.dll` 位于包资源路径：`DXGISS/DXGISS.dll`
2. 安装 Python 依赖：
```bash
pip install numpy
```
3. 以可编辑模式安装项目（可选）：
```bash
pip install -e .
```

## 使用示例
```python
from dxgiss import DXGI
import numpy as np

# 创建对象：默认自动设置为全屏捕获
cap = DXGI(autoRegion=True, needAlphaChannel=False)

# 捕获一帧
img = cap.capture_frame()  # 返回 shape = (height, width, 3) 或 (height, width, 4)

# 示例：显示信息
print(img.shape, img.dtype)  # e.g. (1080, 1920, 3) uint8

# 释放资源
cap.release()
```

## API（简要）
- `DXGI(autoRegion=True, needAlphaChannel=False)`
  - `autoRegion`: 是否自动设置为全屏（bool）
  - `needAlphaChannel`: 是否保留 Alpha（bol）
- `set_capture_region(x, y, width, height)`
  - 设置捕获区域（像素坐标与尺寸）
- `capture_frame() -> numpy.ndarray`
  - 捕获并返回一帧；通道数由构造参数决定（3 = BGR, 4 = BGRA）
- `release()`
  - 释放底层捕获实例

## 常见问题
- 找不到 DLL：确认 `DXGISS/DXGISS.dll` 路径正确且包含在包资源中。
- 捕获失败：确认运行环境为 Windows 并且有必要的 DXGI 支持；检查是否有权限或显示驱动问题。

## 许可证
请根据项目需要添加合适的许可证文件（例如 `LICENSE`）。
```