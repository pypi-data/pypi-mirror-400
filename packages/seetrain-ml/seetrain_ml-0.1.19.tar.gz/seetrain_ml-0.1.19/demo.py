import time
import random

import seetrain


if __name__ == "__main__":
    seetrain.init(
        config={
            "learning_rate": 0.02,
            "architecture": "CNN",
            "dataset": "CIFAR-100",
            "epochs": 10
        }
    )
    
    seetrain.log({
        "Preview/image": seetrain.Image(data_or_path="/Users/CHENXI/Downloads/a2132178a29d78676e78e2692fad1fc25cc80c9a28d7-MzqehH_fw658.webp"),
        "Preview/video":  seetrain.Video(data_or_path="/Users/CHENXI/Downloads/IMG_3010.MOV"),
        "Preview/audio": seetrain.Audio(data_or_path="/Users/CHENXI/Downloads/云埔四路6.m4a", sample_rate=44100, caption="测试音频")
        },
        step=1)
    
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