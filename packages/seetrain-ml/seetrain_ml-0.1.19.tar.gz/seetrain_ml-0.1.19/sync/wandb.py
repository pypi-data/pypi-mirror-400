#!/usr/bin/env python
# -*- coding: utf-8 -*-

from seetrain.data import data as seetrain_data
from seetrain.data.modules import Image
from seetrain.log import seetrainlog


def _extract_args(args, kwargs, param_names):
    """
    从args和kwargs中提取参数值的通用函数
    
    Args:
        args: 位置参数元组
        kwargs: 关键字参数字典
        param_names: 参数名称列表
    
    Returns:
        tuple: 按param_names顺序返回提取的参数值
    """
    values = []
    for i, name in enumerate(param_names):
        if len(args) > i:
            values.append(args[i])
        else:
            values.append(kwargs.get(name, None))
    return tuple(values)


def sync_wandb(wandb_run: bool = True):
    """
    同步 wandb 与 SeeTrain，将 wandb 的调用自动同步到 SeeTrain
    
    Args:
        wandb_run: 如果此参数设置为False，则不会将数据上传到wandb，等同于设置wandb.init(mode="offline")
    
    Example:
    ```python
    import wandb
    import random
    import seetrain
    
    seetrain.sync_wandb()
    
    wandb.init(
        project="test",
        config={"a": 1, "b": 2},
        name="test",
    )
    
    epochs = 10
    offset = random.random() / 5
    for epoch in range(2, epochs):
        acc = 1 - 2 ** -epoch - random.random() / epoch - offset
        loss = 2 ** -epoch + random.random() / epoch + offset
        
        wandb.log({"acc": acc, "loss": loss}, step=epoch)
    ```
    """
    try:
        import wandb
        from wandb import sdk as wandb_sdk
    except ImportError:
        raise ImportError("please install wandb first, command: `pip install wandb`")
    
    original_init = wandb.init
    original_log = wandb_sdk.wandb_run.Run.log
    original_finish = wandb_sdk.wandb_run.Run.finish
    original_config_update = wandb_sdk.wandb_config.Config.update
    
    def patched_init(*args, **kwargs):
        entity, project, dir, id, name, notes, tags, config, config_exclude_keys, reinit = _extract_args(
            args, kwargs, ['entity', 'project', 'dir', 'id', 'name', 'notes', 'tags', 'config', 'config_exclude_keys', 'reinit']
        )
        
        if wandb_run is False:
            kwargs["mode"] = "offline"
        
        run = original_init(*args, **kwargs)
        
        import seetrain.data.data as data_module
        import os
        wandb_dir = None
        
        if run:
            if hasattr(run, 'dir') and run.dir:
                wandb_dir = run.dir
            elif hasattr(run, 'settings') and hasattr(run.settings, 'run_dir') and run.settings.run_dir:
                wandb_dir = run.settings.run_dir
            elif hasattr(run, 'settings') and hasattr(run.settings, 'files_dir') and run.settings.files_dir:
                wandb_dir = run.settings.files_dir
        
        if not wandb_dir and dir:
            wandb_dir = dir
        
        if wandb_dir:
            wandb_dir = os.path.abspath(wandb_dir)
            seetrainlog.info(f"Using wandb directory: {wandb_dir}")
        
        if not data_module._initialized:
            seetrain_data.init(config=config, dir=wandb_dir)
        else:
            if config:
                seetrain_data.update_config(config)
            if wandb_dir:
                seetrain_data.init(config=None, dir=wandb_dir)
        
        return run

    def patched_config_update(self, *args, **kwargs):
        d, _ = _extract_args(args, kwargs, ['d', 'allow_val_change'])
        
        if d is not None:
            seetrain_data.update_config(d)
        return original_config_update(self, *args, **kwargs)

    def patched_log(self, *args, **kwargs):
        data, step, commit, sync = _extract_args(args, kwargs, ['data', 'step', 'commit', 'sync'])
        
        if data is None:
            return original_log(self, *args, **kwargs)
        
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, (int, float, bool, str)):
                processed_data[key] = value
            elif hasattr(value, '__class__') and value.__class__.__name__ == 'Image' and hasattr(value, 'image'):
                try:
                    if value.image is not None:
                        import numpy as np
                        img_array = np.array(value.image)
                        caption = getattr(value, '_caption', None)
                        seetrain_image = Image(img_array, caption=caption)
                        processed_data[key] = seetrain_image
                    else:
                        if hasattr(value, '_image') and value._image is not None:
                            import numpy as np
                            img_array = np.array(value._image)
                            caption = getattr(value, '_caption', None)
                            seetrain_image = Image(img_array, caption=caption)
                            processed_data[key] = seetrain_image
                except Exception as e:
                    seetrainlog.warning(f"Failed to convert wandb.Image for key '{key}': {e}")
                    continue
            elif isinstance(value, list) and value and hasattr(value[0], '__class__') and value[0].__class__.__name__ == 'Image':
                try:
                    import numpy as np
                    seetrain_images = []
                    for v in value:
                        if hasattr(v, 'image') and v.image is not None:
                            img_array = np.array(v.image)
                            caption = getattr(v, '_caption', None)
                            seetrain_images.append(Image(img_array, caption=caption))
                        elif hasattr(v, '_image') and v._image is not None:
                            img_array = np.array(v._image)
                            caption = getattr(v, '_caption', None)
                            seetrain_images.append(Image(img_array, caption=caption))
                    if seetrain_images:
                        processed_data[key] = seetrain_images
                except Exception as e:
                    seetrainlog.warning(f"Failed to convert wandb.Image list for key '{key}': {e}")
                    continue
        
        if processed_data:
            seetrain_data.log(processed_data, step=step, print_to_console=False)
        
        return original_log(self, *args, **kwargs)
    
    def patched_finish(*args, **kwargs):
        seetrain_data.finish()
        return original_finish(*args, **kwargs)

    wandb.init = patched_init
    wandb_sdk.wandb_run.Run.log = patched_log
    wandb_sdk.wandb_run.Run.finish = patched_finish
    wandb_sdk.wandb_config.Config.update = patched_config_update

