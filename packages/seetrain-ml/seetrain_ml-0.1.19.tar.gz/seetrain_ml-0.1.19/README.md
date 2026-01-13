# SeeTrain

**SeeTrain** 是一个深度学习实验跟踪和框架集成工具，提供统一的接口来适配各种深度学习框架，实现无缝的实验管理和数据记录。

> **注意**: 本包在 PyPI 上的名称为 `seetrain-ml`，请使用 `pip install seetrain-ml` 进行安装。

## ✨ 特性

- 📊 **统一实验跟踪** - 提供一致的 API 来记录指标、图像、音频、文本等多媒体数据

## 🚀 快速开始

### 安装

```bash
pip install seetrain-ml
```

### 验证安装

```python
import seetrain
print(f"SeeTrain version: {seetrain.__version__}")
print("SeeTrain 安装成功！")
```

### 基本使用

```python
import time
import random
import seetrain

# 初始化实验
seetrain.init(
    config={ # 选填
        "learning_rate": 0.02,
        "architecture": "resnet56",
        "dataset": "fish",
        "epochs": 10  # 建议要填
    }
)


# 记录多媒体类型
seetrain.log({
    "Preview/image": seetrain.Image(data_or_path="fw658.webp"),
    "Preview/video":  seetrain.Video(data_or_path="IMG_3010.MOV"),
    "Preview/audio": seetrain.Audio(data_or_path="6.m4a", sample_rate=44100, caption="测试音频")
    },
    epoch=1)
    
epochs = 10
offset = random.random() / 5
for epoch in range(1, epochs):
    acc = 1 - 2 ** -epoch - random.random() / epoch - offset
    loss = 2 ** -epoch + random.random() / epoch + offset
    # 记录训练指标
    seetrain.log({
        "train/acc": acc, 
        "train/loss": loss,
        "Preview/text": seetrain.Text("Hello, World!")
        }, epoch=epoch)
    time.sleep(1)

seetrain.finish()

```

#### 记录训练指标数据
##### 支持两种调用方式:
- 1.字典方式: log({"loss": 0.5, "acc": 0.95}, epoch=100)
- 2.键值对方式: log("loss", 0.5, epoch=100)
    
##### Args:
- data: 指标数据字典 或 指标名称(字符串)
- value: 指标值 (仅在 data 是字符串时使用)
- step: 训练步数 (可选)
- epoch: 训练轮数 (可选)
- print_to_console: 是否打印到控制台
        
##### Examples:
- 字典方式
    - seetrain.log({"loss": 0.5, "acc": 0.95}, step=100)
    - seetrain.log({"image": Image("path/to/image.jpg")}, step=1)
- 键值对方式
    - seetrain.log("train/loss", 0.5, step=100)
    - seetrain.log("train/acc", 0.95, step=100)

⚠️ 通过 “/” 实现指标分组展示