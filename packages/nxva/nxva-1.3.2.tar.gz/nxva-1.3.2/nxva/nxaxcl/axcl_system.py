#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import threading
import axcl
# from axcl.rt.axcl_rt_engine import engine_deinit # 修復 engine_deinit 引用問題
from axcl.rt.axcl_rt_engine import *


class AxclSystem:
    """
    AXCL 系統級管理
    負責全域的 init 與 finalize
    """
    _initialized = False

    @classmethod
    def init(cls):
        if cls._initialized:
            return
            
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "axcl.json")
        
        # print(f"[System] Initializing AXCL with config: {json_path}")
        ret = axcl.init(json_path if json_path else "")
        if ret != axcl.AXCL_SUCC:
            raise RuntimeError(f"axcl.init failed, code: 0x{ret&0xFFFFFFFF:x}")
        
        cls._initialized = True

    @classmethod
    def finalize(cls):
        if cls._initialized:
            # print("[System] Finalizing AXCL...")
            axcl.finalize()
            cls._initialized = False