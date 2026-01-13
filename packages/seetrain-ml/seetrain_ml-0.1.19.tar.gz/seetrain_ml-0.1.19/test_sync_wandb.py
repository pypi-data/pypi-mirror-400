#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.environ["TASK_ID"] = "109876543210"
os.environ["PROJECT"] = "act-train"
os.environ["BASE_URL"] = "https://ai-dev.research-pro.sy.cvte.cn/seetrain/api/v1"

import wandb
import seetrain

import random
import time

seetrain.sync_wandb()

wandb.init(
    project="act-train", 
    config={"a": 1, "b": 2}, 
    name="act-train",
    mode="offline")


for step in range(1, 100):
    acc = round(random.uniform(0.8, 1.0), 4)
    loss = round(random.uniform(0.05, 0.3), 4)
    print(f"[step {step}] acc={acc} loss={loss}")
    wandb.log({"acc": acc, "loss": loss}, step=step)
    time.sleep(1)
