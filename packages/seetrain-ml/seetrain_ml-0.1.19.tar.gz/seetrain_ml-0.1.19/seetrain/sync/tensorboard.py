#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
from typing import Any, Dict, List

from ..data import data as seetrain_data
from ..data.modules import Image, Text
from ..log import seetrainlog


def _extract_args(args: tuple, kwargs: Dict[str, Any], param_names: List[str]) -> tuple:
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


def _create_patched_methods(SummaryWriter, logdir_extractor, types=None):
    """
    创建patched方法的工厂函数

    Args:
        SummaryWriter: SummaryWriter类
        logdir_extractor: 提取logdir的函数
        types: 要同步的数据类型列表，如 ['scalar', 'scalars', 'image', 'text']。
               None 表示同步所有类型。

    Returns:
        tuple: (patched_init, patched_add_scalar, patched_add_image, patched_close)
    """
    types_set = set(types) if types is not None else None

    original_init = SummaryWriter.__init__
    original_add_scalar = SummaryWriter.add_scalar
    original_add_scalars = SummaryWriter.add_scalars
    original_add_image = SummaryWriter.add_image
    original_add_text = SummaryWriter.add_text
    original_close = SummaryWriter.close

    def patched_init(self, *args, **kwargs):
        tb_logdir = logdir_extractor(args, kwargs)

        tb_config = {
            'tensorboard_logdir': tb_logdir,
        }

        if not seetrain_data._initialized:
            seetrain_data.init(config=tb_config, dir=tb_logdir)
        else:
            seetrain_data.update_config(tb_config)
            if tb_logdir:
                import os
                os.environ["LOG_FILE"] = os.path.join(os.path.abspath(tb_logdir), "seetrain.log")

        return original_init(self, *args, **kwargs)

    @functools.wraps(original_add_scalar)
    def patched_add_scalar(self, *args, **kwargs):
        if types_set is not None and 'scalar' not in types_set:
            return original_add_scalar(self, *args, **kwargs)
        tag, scalar_value, global_step = _extract_args(
            args, kwargs, ['tag', 'scalar_value', 'global_step']
        )

        data = {tag: scalar_value}
        seetrain_data.log(data=data, step=int(global_step), print_to_console=False)

        return original_add_scalar(self, *args, **kwargs)

    @functools.wraps(original_add_scalars)
    def patched_add_scalars(self, *args, **kwargs):
        if types_set is not None and 'scalars' not in types_set:
            return original_add_scalars(self, *args, **kwargs)
        tag, scalar_value_dict, global_step = _extract_args(
            args, kwargs, ['tag', 'scalar_value_dict', 'global_step']
        )
        data = {}
        for dict_tag, value in scalar_value_dict.items():
            data[f"{tag}/{dict_tag}"] = value
        seetrain_data.log(data=data, step=int(global_step), print_to_console=False)
        return original_add_scalars(self, *args, **kwargs)

    @functools.wraps(original_add_image)
    def patched_add_image(self, *args, **kwargs):
        if types_set is not None and 'image' not in types_set:
            return original_add_image(self, *args, **kwargs)
        import numpy as np

        tag, img_tensor, global_step, dataformats = _extract_args(
            args, kwargs, ['tag', 'img_tensor', 'global_step', 'dataformats']
        )
        dataformats = dataformats or 'CHW'

        if hasattr(img_tensor, 'cpu'):
            img_tensor = img_tensor.cpu()
        if hasattr(img_tensor, 'numpy'):
            img_tensor = img_tensor.numpy()

        if dataformats == 'CHW':
            img_tensor = np.transpose(img_tensor, (1, 2, 0))
        elif dataformats == 'NCHW':
            if img_tensor.ndim == 4:
                img_tensor = img_tensor[0]
            img_tensor = np.transpose(img_tensor, (1, 2, 0))
        elif dataformats == 'HW':
            img_tensor = np.expand_dims(img_tensor, axis=-1)
        elif dataformats == 'HWC':
            pass

        data = {tag: Image(img_tensor)}
        seetrain_data.log(data=data, step=int(global_step), print_to_console=False)

        return original_add_image(self, *args, **kwargs)

    @functools.wraps(original_add_text)
    def patched_add_text(self, *args, **kwargs):
        if types_set is not None and 'text' not in types_set:
            return original_add_text(self, *args, **kwargs)
        tag, text_string, global_step = _extract_args(
            args, kwargs, ['tag', 'text_string', 'global_step']
        )
        data = {tag: Text(text_string)}
        seetrain_data.log(data=data, step=int(global_step), print_to_console=False)
        return original_add_text(self, *args, **kwargs)

    def patched_close(self):
        original_close(self)
        seetrain_data.finish()

    return patched_init, patched_add_scalar, patched_add_scalars, patched_add_image, patched_add_text, patched_close


def _apply_patches(SummaryWriter, patched_methods):
    """
    应用monkey patch到SummaryWriter类
    
    Args:
        SummaryWriter: SummaryWriter类
        patched_methods: (patched_init, patched_add_scalar, patched_add_image, patched_close)
    """
    patched_init, patched_add_scalar, patched_add_scalars, patched_add_image, patched_add_text, patched_close = patched_methods
    
    SummaryWriter.__init__ = patched_init
    SummaryWriter.add_scalar = patched_add_scalar
    SummaryWriter.add_scalars = patched_add_scalars
    SummaryWriter.add_image = patched_add_image
    SummaryWriter.add_text = patched_add_text
    SummaryWriter.close = patched_close


def _sync_tensorboard_generic(import_func, logdir_extractor, types=None):
    """
    通用的tensorboard同步函数

    Args:
        import_func: 导入SummaryWriter的函数
        logdir_extractor: 提取logdir的函数
        types: 要同步的数据类型列表，如 ['scalar', 'scalars', 'image', 'text']。
               None 表示同步所有类型。
    """
    try:
        SummaryWriter = import_func()
    except ImportError as e:
        raise ImportError(f"Import failed: {e}")

    patched_methods = _create_patched_methods(SummaryWriter, logdir_extractor, types)
    _apply_patches(SummaryWriter, patched_methods)


def sync_tensorboardX(types=None):
    """
    同步tensorboardX到seetrain

    from tensorboardX import SummaryWriter
    import numpy as np
    import seetrain

    seetrain.sync_tensorboardX()

    seetrain.sync_tensorboardX(types=['scalar', 'scalars'])

    writer = SummaryWriter('runs/example')

    for i in range(100):
        scalar_value = np.random.rand()
        writer.add_scalar('random_scalar', scalar_value, i)

    writer.close()

    Args:
        types: 要同步的数据类型列表，可选值: 'scalar', 'scalars', 'image', 'text'。
               None 表示同步所有类型。
    """
    def import_tensorboardx():
        from tensorboardX import SummaryWriter
        return SummaryWriter

    def extract_logdir_tensorboardx(args, kwargs):
        logdir, _, _, _, _, _, _, log_dir, _ = _extract_args(
            args, kwargs,
            ['logdir', 'comment', 'purge_step', 'max_queue', 'flush_secs',
             'filename_suffix', 'write_to_disk', 'log_dir', 'comet_config']
        )
        return logdir or log_dir

    _sync_tensorboard_generic(import_tensorboardx, extract_logdir_tensorboardx, types)


def sync_tensorboard_torch(types=None):
    """
    同步torch自带的tensorboard到seetrain

    from torch.utils.tensorboard import SummaryWriter
    import numpy as np
    import seetrain

    seetrain.sync_tensorboard_torch()

    seetrain.sync_tensorboard_torch(types=['scalar', 'scalars'])

    writer = SummaryWriter('runs/example')

    for i in range(100):
        scalar_value = np.random.rand()
        writer.add_scalar('random_scalar', scalar_value, i)

    writer.close()

    Args:
        types: 要同步的数据类型列表，可选值: 'scalar', 'scalars', 'image', 'text'。
               None 表示同步所有类型。
    """
    def import_torch_tensorboard():
        from torch.utils.tensorboard import SummaryWriter
        return SummaryWriter

    def extract_logdir_torch(args, kwargs):
        logdir, _ = _extract_args(args, kwargs, ['log_dir', 'comment'])
        return logdir

    _sync_tensorboard_generic(import_torch_tensorboard, extract_logdir_torch, types)

