# fire_detector —— 火灾/烟雾检测包

**Fire Detector** 是一个专为工业安全、智慧城市及野外监控场景设计的轻量级 Python 深度学习工具包。它集成了先进的目标检测与视频追踪算法，旨在为开发者提供开箱即用、高效精准的火灾与烟雾识别能力。

无论是对静态图像的快速筛查，还是对监控视频流的实时预警，本工具包都能通过简洁统一的 API 轻松实现。

⭐️ **核心亮点**:
*   **轻量高效**: 专为边缘计算优化的轻量化模型，在 CPU 环境下也能流畅运行。
*   **功能全面**: 涵盖图像分类、目标检测及视频多目标追踪 (MOT)。
*   **简单易用**: 无需繁琐配置，一行代码即可加载模型并开始推理。

---

⭐️ **主入口 (Main Entry)**

本文档仅包含项目简介。详细文档请查阅 [docs/](docs/) 目录：

- 📥 [安装与环境 (Install)](docs/INSTALL.md)
- 🚀 [快速开始 (Quick Start)](docs/QUICKSTART.md)
- 📖 [API 文档 (API Reference)](docs/API.md)
- 🧠 [模型说明 (Models)](docs/MODELS.md)
- 🏋️ [训练指南 (Training)](docs/TRAINING.md)
- ❓ [常见问题 (FAQ)](docs/FAQ.md)

### 📂 项目结构 (Project Structure)

```text
fire-detector/
├── fire_detector/       # 📦 核心源码包
│   ├── models/          #    ├── 预训练模型权重 (.pt/.pth)
│   ├── YoloDetector.py  #    ├── YOLOv8 目标检测封装
│   ├── yolo_track.py    #    ├── 视频追踪模块 (ByteTrack)
│   ├── image_detect.py  #    ├── 静态图像分类 (ResNet)
│   ├── video_detect.py  #    ├── 视频逐帧检测统计
│   ├── modules.py       #    ├── 轻量化网络模块定义
│   └── ...
├── tools/               # 工具脚本 (评测、转换等)
├── docs/                # 📚 详细文档目录
├── examples/            # 💡 示例代码
├── trainer/             # 🏋️ 模型训练脚本
└── setup.py             # ⚙️ 安装配置文件
```

---

## 功能特性

- **YOLOv8 目标检测**: 同时检测火焰与烟雾位置 (基于轻量化 YOLOv8)
- **视频追踪**: 基于 YOLOv8 + ByteTrack 的实时目标追踪
- **图像/视频分类**: 基于 ResNet18 (FP16) 的快速二分类筛查
- **开箱即用**: 内置预训练模型权重，安装即用

## 快速预览

![Demo Tracking](assets/demo_tracking.gif)
![Track Demo](assets/track_demo.gif)

```python
from fire_detector import FireDetector

# 初始化 (自动加载内置模型)
detector = FireDetector()

# 1. 检测图片
results = detector.detect_yolo("assets/test.jpg")
print(results)

# 2. 追踪视频
detector.track_video("assets/test_video.mp4", show=True)
```

## 导出与部署

- **ResNet18**: 提供 ONNX 部署文件，位于包内 [fire_resnet18_fp16.onnx](file:///d:/liuyi/projiect/test/fire_detector/models/fire_resnet18_fp16.onnx)。适合在 CPU 环境高性能部署。
- **YOLOv8**: 不随包提供 ONNX 导出文件，以减少包体积；在 CPU 上的加速收益有限。默认使用 [light_yolov8_flame.pt](file:///d:/liuyi/projiect/test/fire_detector/models/light_yolov8_flame.pt)。
- **性能对比 (CPU)**:
  - ResNet18: PyTorch 89 FPS → ONNX 244 FPS（约 2.7× 速度提升）
  - YOLOv8 (Light): PyTorch 22 FPS ↔ ONNX 20 FPS（提升不明显）

## 更新日志 (Changelog)

### [1.0.3] - 2026-01-07
- 🗑️ 移除：不再随包提供 YOLOv8 的 ONNX 导出及模型文件，以减少包体积；默认保留 PyTorch 权重 [light_yolov8_flame.pt](file:///d:/liuyi/projiect/test/fire_detector/models/light_yolov8_flame.pt)
- ✨ 新增：保留并推荐使用 ResNet18 的 ONNX 部署文件 [fire_resnet18_fp16.onnx](file:///d:/liuyi/projiect/test/fire_detector/models/fire_resnet18_fp16.onnx)（CPU 上显著加速）
- ⚡ 优化：更新导出脚本 [export_models.py](file:///d:/liuyi/projiect/test/tools/export_models.py) 仅导出 ResNet18 到 ONNX
- 📚 文档：更新 README、MODELS、INSTALL、FAQ、TRAINING，补充 CPU 基准结果与部署说明
- 📊 基准：CPU 上 ResNet18 ONNX ≈ 244 FPS、PyTorch ≈ 89 FPS；YOLOv8 (Light) ONNX 与 PyTorch 差异不大
- 🛰 GUI：YOLOv8 追踪支持实时统计显示（帧数/FPS/检测数），状态栏动态更新
- 🔁 API：`FireDetector.track_video` 新增 `progress_callback(frames, fps, det_cnt)`，支持流式追踪与进度上报
- 🎛️ 参数：GUI 默认阈值与主分支对齐（conf=0.25，iou=0.5），可在界面调节
- 🧭 路径：优先使用主包 `path_utils.resolve_model_path` 解析内置模型路径，支持自定义覆盖
- 🧹 清理：GUI 中移除主分支废弃的旧视频脚本，统一使用主入口与YOLO GUI

### [1.0.2] - 2025-12-25
- ✨ **新增**: `detect_yolo` 接口支持 `output_path` 参数，可直接保存检测结果图片。
- ✨ **新增**: 集成 YOLOv8 + ByteTrack 视频追踪模块
- ⚡ **优化**: 默认模型切换为轻量级版本，保持了相近的检测性能。
- ⚡ **优化**: 改进轻量化 YOLO 训练脚本 (FasterNet 模块劫持)
- ⚡ **优化**: 将resnet18模型转换为FP16格式，准确率不变以减少模型体积
- 🗑️ **移除**: 删除了 `full` (yolov8s) 模型，统一使用轻量化 `light` 模型以减小包体积。
- 🗑️ **移除**: 删除了过时的 CNN+LSTM 及二阶段检测模块
---

© 2025 Fire Detector Project.
