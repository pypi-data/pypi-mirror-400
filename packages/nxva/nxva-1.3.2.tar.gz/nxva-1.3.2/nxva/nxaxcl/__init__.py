#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
NXAX - AX650 Inference Library
High-level API for AX650 model inference
"""

from .axcl_system import AxclSystem
from .axcl_infer import AxclInfer
from .axcl_model import AxclModel

__all__ = ['AxclSystem', 'AxclInfer', 'AxclModel']

