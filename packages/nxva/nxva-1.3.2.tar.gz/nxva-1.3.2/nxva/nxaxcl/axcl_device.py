#!/usr/bin/env python
# -*- coding:utf-8 -*-
import numpy as np
import axcl
from axcl.rt.axcl_rt_type import *

class AxclDevice:
    """
    AXCL 設備與資源管理器
    """
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.context = None # Base Context
        self._init_device()

    def _init_device(self):
        # 1. 獲取設備列表
        devices, ret = axcl.rt.get_device_list()
        if ret != axcl.AXCL_SUCC or not devices:
            raise RuntimeError("No AXCL devices found.")
        
        if self.device_id not in devices:
            print(f"[Device] ID {self.device_id} not found, using {devices[0]}")
            self.device_id = devices[0]

        # 2. 設置設備
        ret = axcl.rt.set_device(self.device_id)
        if ret != axcl.AXCL_SUCC:
            raise RuntimeError(f"set_device failed: 0x{ret&0xFFFFFFFF:x}")

        # 3. 創建 Base Context
        self.context, ret = axcl.rt.create_context(self.device_id)
        if ret != axcl.AXCL_SUCC:
            raise RuntimeError(f"create_context failed: 0x{ret&0xFFFFFFFF:x}")
        
        # 4. 綁定到當前線程 (Main Thread)
        self.bind_to_current_thread()
        
        # print(f"[Device] Device {self.device_id} initialized and context created.")

    def bind_to_current_thread(self):
        """
        將 Base Context 設置為當前線程的當前 Context。
        讓當前線程可以使用關聯的 Device 資源。
        任何新線程在使用 AXCL API 前都必須調用此方法。
        """
        if self.context:
            ret = axcl.rt.set_current_context(self.context)
            if ret != axcl.AXCL_SUCC:
                raise RuntimeError(f"set_current_context failed for thread: 0x{ret&0xFFFFFFFF:x}")

    def malloc(self, size: int):
        dev_ptr, ret = axcl.rt.malloc(size, AXCL_MEM_MALLOC_NORMAL_ONLY)
        if ret != 0:
            raise RuntimeError(f"Device malloc failed ({size} bytes): {ret}")
        return dev_ptr

    def free(self, dev_ptr):
        if dev_ptr:
            axcl.rt.free(dev_ptr)

    def memcpy_h2d(self, dev_ptr, host_data: np.ndarray):
        host_data = np.ascontiguousarray(host_data)
        src = int(host_data.ctypes.data)
        size = host_data.nbytes
        ret = axcl.rt.memcpy(dev_ptr, src, size, AXCL_MEMCPY_HOST_TO_DEVICE)
        if ret != 0:
            raise RuntimeError(f"Memcpy H2D failed: {ret}")

    def memcpy_d2h(self, dev_ptr, size: int) -> bytes:
        host_buffer = np.empty(size, dtype=np.uint8)
        dst = int(host_buffer.ctypes.data)
        ret = axcl.rt.memcpy(dst, dev_ptr, size, AXCL_MEMCPY_DEVICE_TO_HOST)
        if ret != 0:
            raise RuntimeError(f"Memcpy D2H failed: {ret}")
        return host_buffer.tobytes()
    
    def memcpy_d2d(self, dst_dev_ptr, src_dev_ptr, size: int):
        """
        Copy memory from device to device (device-to-device transfer).
        This is much faster than D2H + H2D for large buffers like KV cache.
        
        Args:
            dst_dev_ptr: Destination device pointer
            src_dev_ptr: Source device pointer
            size: Size in bytes to copy
        """
        ret = axcl.rt.memcpy(dst_dev_ptr, src_dev_ptr, size, AXCL_MEMCPY_DEVICE_TO_DEVICE)
        if ret != 0:
            raise RuntimeError(f"Memcpy D2D failed: {ret}")
        
    def free_resource(self):
        """
        [修復] 釋放 Device 資源，不管當前線程綁定的是什麼 Context
        核心思路：在回收時，不管當前線程綁定的是什麼 Context，直接銷毀所有需要銷毀的資源
        """
        if not self.context:
            return
        
        # 嘗試綁定到當前線程，但即使失敗也繼續銷毀
        # 這樣可以避免 Context ID 不匹配的問題
        try:
            ret = axcl.rt.set_current_context(self.context)
            if ret != axcl.AXCL_SUCC:
                # 綁定失敗也繼續，因為我們要強制銷毀
                pass
        except Exception:
            # 忽略綁定錯誤，繼續銷毀
            pass
        
        # 直接銷毀 Context，不管當前線程綁定的是什麼
        try:
            ret = axcl.rt.destroy_context(self.context)
            if ret != axcl.AXCL_SUCC:
                # 即使銷毀失敗也繼續，避免程序崩潰
                pass
        except Exception:
            # 忽略銷毀錯誤，繼續清理
            pass
        
        self.context = None
        
        # 重置設備
        try:
            axcl.rt.reset_device(self.device_id)
        except Exception:
            # 忽略重置錯誤
            pass