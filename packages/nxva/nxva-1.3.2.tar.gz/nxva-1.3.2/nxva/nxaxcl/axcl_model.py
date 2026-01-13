#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from axcl.rt.axcl_rt_engine import *

class AxclModel:
    """
    AXCL 模型封裝
    """
    DTYPE_STR = [
        "none", "int4", "uint4", "int8", "uint8", "int16", "uint16",
        "int32", "uint32", "int64", "uint64", "fp4", "fp8", "fp16",
        "bf16", "fp32", "fp64"
    ]

    def __init__(self, model_path: str):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model_path = model_path
        self.model_id = None
        self.io_info = None
        self.inputs = []
        self.outputs = []
        
        self._load()

    def _load(self):
        self.model_id, ret = engine_load_from_file(self.model_path)
        if ret != 0:
            raise RuntimeError(f"engine_load_from_file failed: {ret}")
        
        self.io_info, ret = engine_get_io_info(self.model_id)
        if ret != 0:
            raise RuntimeError(f"engine_get_io_info failed: {ret}")
        
        self._parse_io_info()
        # print(f"[Model] Loaded {self.model_path} (ID: {self.model_id})")

    def _parse_io_info(self):
        num_inputs = engine_get_num_inputs(self.io_info)
        for i in range(num_inputs):
            name = engine_get_input_name_by_index(self.io_info, i)
            size = engine_get_input_size_by_index(self.io_info, 0, i)
            dims, _ = engine_get_input_dims(self.io_info, 0, i)
            dtype_idx, _ = engine_get_input_data_type(self.io_info, i)
            
            self.inputs.append({
                "index": i, "name": name, "size": size, "dims": dims,
                "dtype": self.DTYPE_STR[dtype_idx]
            })

        num_outputs = engine_get_num_outputs(self.io_info)
        for i in range(num_outputs):
            name = engine_get_output_name_by_index(self.io_info, i)
            size = engine_get_output_size_by_index(self.io_info, 0, i)
            dims, _ = engine_get_output_dims(self.io_info, 0, i)
            dtype_idx, _ = engine_get_output_data_type(self.io_info, i)
            
            self.outputs.append({
                "index": i, "name": name, "size": size, "dims": dims,
                "dtype": self.DTYPE_STR[dtype_idx]
            })

    def create_execution_context(self):
        ctx, ret = engine_create_context(self.model_id)
        if ret != 0:
            raise RuntimeError(f"engine_create_context failed: {ret}")
        return ctx

    def create_io_handle(self):
        io, ret = engine_create_io(self.io_info)
        if ret != 0:
            raise RuntimeError(f"engine_create_io failed: {ret}")
        return io

    def unload(self):
        if self.io_info:
            engine_destroy_io_info(self.io_info)
        if self.model_id is not None:
            engine_unload(self.model_id)