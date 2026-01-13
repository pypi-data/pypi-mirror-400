#!/usr/bin/env python
# -*- coding:utf-8 -*-
import threading
import time
import numpy as np
from typing import List

# 導入其他模組
from .axcl_system import AxclSystem
from .axcl_device import AxclDevice
from .axcl_model import AxclModel
from axcl.rt.axcl_rt_engine import *

class AxclInfer:
    """
    AXCL 高層推論器 - 支援多線程
    """
    _engine_initialized = False

    def __init__(self, model_path: str, device_id: int = 1, vnpu_mode: int = 0):
        # 1. 系統與設備初始化
        AxclSystem.init()
        self.device = AxclDevice(device_id)

        # 2. Engine 初始化 (全局一次)
        if not AxclInfer._engine_initialized:
            # 確保 Engine Init 時，當前線程有綁定 Context
            self.device.bind_to_current_thread()
            ret = engine_init(vnpu_mode)
            if ret != 0:
                raise RuntimeError(f"engine_init failed: {ret}")
            AxclInfer._engine_initialized = True

        # 3. 載入模型
        self.model = AxclModel(model_path)
        
        # 4. 線程本地存儲
        self._tls = threading.local()

    def _prepare_thread_resources(self):
        """
        為當前線程準備資源。
        [重要] 必須先將當前線程綁定到 Device Context
        """
        if hasattr(self._tls, 'ready') and self._tls.ready:
            return

        # thread_id = threading.get_ident()
        # print(f"[Thread {thread_id}] Binding context and preparing resources...")
        # print(f"[Thread {thread_id}] Binding context and preparing resources...")

        # [修復點] 讓子線程綁定 Base Context
        self.device.bind_to_current_thread()

        # 創建 Engine Context 和 IO
        self._tls.ctx = self.model.create_execution_context()
        self._tls.io = self.model.create_io_handle()
        self._tls.in_ptrs = []
        self._tls.out_ptrs = []

        # 分配並綁定輸入 Buffer (H2D)
        for meta in self.model.inputs:
            ptr = self.device.malloc(meta['size'])
            ret = engine_set_input_buffer_by_index(self._tls.io, meta['index'], ptr, meta['size'])
            if ret != 0: raise RuntimeError(f"Set input buffer failed: {ret}")
            self._tls.in_ptrs.append(ptr)

        # 分配並綁定輸出 Buffer (D2H)
        for meta in self.model.outputs:
            ptr = self.device.malloc(meta['size'])
            ret = engine_set_output_buffer_by_index(self._tls.io, meta['index'], ptr, meta['size'])
            if ret != 0: raise RuntimeError(f"Set output buffer failed: {ret}")
            self._tls.out_ptrs.append(ptr)

        self._tls.ready = True

    def __call__(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        # 準備資源 (包含線程綁定)
        self._prepare_thread_resources()

        if len(inputs) != len(self.model.inputs):
            raise ValueError(f"Input mismatch: expected {len(self.model.inputs)}, got {len(inputs)}")

        # Get batch size from first input [B, H, W, C]
        input_data = inputs[0]
        batch_size = input_data.shape[0] if input_data.ndim == 4 else 1
        
        # Process each image in batch
        all_results = []
        for b in range(batch_size):
            single_inputs = [inp[b:b+1] for inp in inputs]
            results = self._infer_single(single_inputs)
            all_results.append(results)
        
        # Concatenate results along batch dimension
        final_results = []
        for out_idx in range(len(all_results[0])):
            stacked = np.concatenate([all_results[b][out_idx] for b in range(batch_size)], axis=0)
            final_results.append(stacked)
        
        return final_results

    def _infer_single(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """Run inference for single batch (batch=1)."""
        # 1. H2D
        for i, data in enumerate(inputs):
            meta = self.model.inputs[i]
            if not data.flags['C_CONTIGUOUS']:
                data = np.ascontiguousarray(data)
            if data.nbytes > meta['size']:
                raise ValueError(f"Input too large for index {i}")
            self.device.memcpy_h2d(self._tls.in_ptrs[i], data)

        # 2. Execute
        ret = engine_execute(self.model.model_id, self._tls.ctx, 0, self._tls.io)
        if ret != 0:
            raise RuntimeError(f"Engine execute failed: {ret}")

        # 3. D2H
        results = []
        for i, meta in enumerate(self.model.outputs):
            raw_bytes = self.device.memcpy_d2h(self._tls.out_ptrs[i], meta['size'])
            dtype = self._get_numpy_dtype(meta['dtype'])
            arr = np.frombuffer(raw_bytes, dtype=dtype).reshape(meta['dims'])
            results.append(arr.copy() if arr.nbytes < 1024 * 1024 else arr)

        return results

    def _get_numpy_dtype(self, type_str):
        mapping = {
            "float32": np.float32, "fp32": np.float32,
            "float16": np.float16, "fp16": np.float16,
            "int8": np.int8, "uint8": np.uint8,
            "int32": np.int32, "int64": np.int64
        }
        return mapping.get(type_str, np.float32)
    
    def get_input_device_ptr(self, index: int):
        """
        Get device pointer for input buffer at given index.
        Useful for device-to-device transfers.
        """
        self._prepare_thread_resources()
        if index < 0 or index >= len(self._tls.in_ptrs):
            raise ValueError(f"Input index {index} out of range")
        return self._tls.in_ptrs[index]
    
    def get_output_device_ptr(self, index: int):
        """
        Get device pointer for output buffer at given index.
        Useful for device-to-device transfers.
        """
        self._prepare_thread_resources()
        if index < 0 or index >= len(self._tls.out_ptrs):
            raise ValueError(f"Output index {index} out of range")
        return self._tls.out_ptrs[index]
    
    def copy_output_to_input_d2d(self, output_index: int, input_index: int):
        """
        Copy output buffer to input buffer using device-to-device transfer.
        This is much faster than D2H + H2D for large buffers like KV cache.
        
        Args:
            output_index: Index of output buffer to copy from
            input_index: Index of input buffer to copy to
        """
        self._prepare_thread_resources()
        if output_index < 0 or output_index >= len(self._tls.out_ptrs):
            raise ValueError(f"Output index {output_index} out of range")
        if input_index < 0 or input_index >= len(self._tls.in_ptrs):
            raise ValueError(f"Input index {input_index} out of range")
        
        # Get sizes
        output_size = self.model.outputs[output_index]['size']
        input_size = self.model.inputs[input_index]['size']
        
        if output_size > input_size:
            raise ValueError(f"Output size {output_size} > input size {input_size}")
        
        # Perform device-to-device copy
        self.device.memcpy_d2d(
            self._tls.in_ptrs[input_index],
            self._tls.out_ptrs[output_index],
            output_size
        )
    
    def run_with_d2d_kv_cache(self, inputs: List[np.ndarray], 
                               kv_cache_input_indices: List[int] = None,
                               kv_cache_output_indices: List[int] = None,
                               copy_outputs: List[bool] = None) -> List[np.ndarray]:
        """
        Optimized run method that supports device-to-device KV cache updates.
        
        Args:
            inputs: List of input numpy arrays
            kv_cache_input_indices: List of input indices that should be updated from previous outputs (D2D)
            kv_cache_output_indices: List of output indices that contain KV cache to copy
            copy_outputs: List of booleans indicating which outputs to copy to host (default: all True)
            
        Returns:
            List of output numpy arrays (only for outputs where copy_outputs[i] is True)
        """
        self._prepare_thread_resources()
        
        if len(inputs) != len(self.model.inputs):
            raise ValueError(f"Input mismatch: expected {len(self.model.inputs)}, got {len(inputs)}")
        
        # Copy KV cache from previous outputs to inputs (D2D)
        if kv_cache_input_indices and kv_cache_output_indices:
            if len(kv_cache_input_indices) != len(kv_cache_output_indices):
                raise ValueError("kv_cache_input_indices and kv_cache_output_indices must have same length")
            for in_idx, out_idx in zip(kv_cache_input_indices, kv_cache_output_indices):
                self.copy_output_to_input_d2d(out_idx, in_idx)
        
        # 1. H2D for non-KV-cache inputs
        for i, data in enumerate(inputs):
            # Skip inputs that were updated via D2D
            if kv_cache_input_indices and i in kv_cache_input_indices:
                continue
            meta = self.model.inputs[i]
            if data.nbytes > meta['size']:
                raise ValueError(f"Input too large for index {i}")
            self.device.memcpy_h2d(self._tls.in_ptrs[i], data)
        
        # 2. Execute
        ret = engine_execute(self.model.model_id, self._tls.ctx, 0, self._tls.io)
        if ret != 0:
            raise RuntimeError(f"Engine execute failed: {ret}")
        
        # 3. D2H (only for outputs that need to be copied)
        if copy_outputs is None:
            copy_outputs = [True] * len(self.model.outputs)
        
        results = []
        for i, meta in enumerate(self.model.outputs):
            if copy_outputs[i]:
                raw_bytes = self.device.memcpy_d2h(self._tls.out_ptrs[i], meta['size'])
                dtype = self._get_numpy_dtype(meta['dtype'])
                arr = np.frombuffer(raw_bytes, dtype=dtype).reshape(meta['dims'])
                results.append(arr.copy())
            else:
                # Return None for outputs that weren't copied
                results.append(None)
        
        return results

    def release(self):
        """清理當前線程資源"""
        if hasattr(self._tls, 'ready') and self._tls.ready:
            # 確保有綁定 context 才能執行 free
            self.device.bind_to_current_thread()
            
            for ptr in self._tls.in_ptrs + self._tls.out_ptrs:
                self.device.free(ptr)
            
            engine_destroy_context(self._tls.ctx)
            engine_destroy_io(self._tls.io)
            self._tls.ready = False

    def close(self):
        """
        [新增] 主線程調用，徹底關閉此實例的資源
        注意：這會卸載模型和清理 Device，請在所有線程結束後調用
        """
        # 1. 卸載模型
        if self.model:
            self.model.unload()
            self.model = None

        # 2. 釋放 Device Base Context
        if self.device:
            self.device.free_resource()
            self.device = None

    @classmethod
    def env_close(cls):
        """全局清理"""
        if cls._engine_initialized:
            engine_finalize()
            cls._engine_initialized = False
        AxclSystem.finalize()

# ==========================================
# 測試代碼 (請將此部分存為 test_threading.py 運行)
# ==========================================
if __name__ == "__main__":
    import threading
    
    MODEL_PATH = "yolov5m_512.axmodel" # 請確保文件存在
    if not os.path.exists(MODEL_PATH):
        print(f"[Error] {MODEL_PATH} not found")
        exit(1)

    # 1. 初始化
    print("初始化模型 (Main Thread)...")
    infer = AxclInfer(MODEL_PATH, device_id=0)

    # 2. 準備數據
    fake_img = np.random.randint(0, 255, (1, 512, 512, 3)).astype(np.uint8)

    # 3. 定義線程工作
    def worker(name, loop_count):
        print(f"[{name}] Start")
        try:
            for i in range(loop_count):
                outputs = infer([fake_img])
                if i % 10 == 0:
                    print(f"[{name}] Iter {i}: Output shape {outputs[0].shape}")
        except Exception as e:
            print(f"[{name}] Error: {e}")
        finally:
            infer.release() # 記得清理線程資源
        print(f"[{name}] Done")

    # 4. 啟動多線程
    ts = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(f"Worker-{i}", 20))
        ts.append(t)
        t.start()

    for t in ts:
        t.join()

    # 5. 全局清理
    AxclInfer.shutdown()
    AxclSystem.finalize()
    print("All done.")