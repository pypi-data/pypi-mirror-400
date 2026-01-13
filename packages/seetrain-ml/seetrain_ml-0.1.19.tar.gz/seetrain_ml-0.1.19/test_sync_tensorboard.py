#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.environ["TASK_ID"] = "tensorboard-sync"
os.environ["PROJECT"] = "act-train"
os.environ["BASE_URL"] = "https://ai.research-pro.sy.cvte.cn/seetrain/api/v1"

import numpy as np
import seetrain
import random
import time

try:
    from tensorboardX import SummaryWriter
    seetrain.sync_tensorboardX()
    print("Using tensorboardX")
except ImportError:
    try:
        from torch.utils.tensorboard import SummaryWriter
        seetrain.sync_tensorboard_torch()
        print("Using torch.utils.tensorboard")
    except ImportError:
        print("Error: Please install tensorboardX or torch first")
        print("  Install tensorboardX: pip install tensorboardX")
        print("  Or install torch: pip install torch")
        raise ImportError("Please install tensorboardX or torch first")

writer = SummaryWriter('runs/example')

for step in range(1, 100):
    acc = round(random.uniform(0.8, 1.0), 4)
    loss = round(random.uniform(0.05, 0.3), 4)
    
    writer.add_scalar('acc', acc, step)
    writer.add_scalar('loss', loss, step)
    
    writer.add_scalars('Loss', {'train': loss, 'val': loss * 0.9}, step)
    
    if step % 10 == 0:
        img = np.random.rand(3, 32, 32)
        writer.add_image('sample_image', img, step)
        
        writer.add_text('sample_text', f'Step {step}: acc={acc}, loss={loss}', step)
    
    print(f"[step {step}] acc={acc} loss={loss}")
    time.sleep(1)

writer.close()

