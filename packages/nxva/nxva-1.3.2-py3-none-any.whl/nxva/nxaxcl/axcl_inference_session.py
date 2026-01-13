#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
AXCL Inference Session
"""

import numpy as np
from typing import Optional, Dict, List

from .axcl_infer import AxclInfer
from axcl.rt.axcl_rt_engine import engine_execute


class AxclInferenceSession:
    """
    Inference session using nxaxcl instead of axengine.
    This class provides a compatible interface with axengine.InferenceSession.
    """
    _infer_instances = {}  # Track instances for cleanup
    
    def __init__(self, model_path: str, device_id: int = 1):
        """
        Initialize inference session with model file.
        
        Args:
            model_path: Path to the .axmodel file
            device_id: Device ID to use (default: 1)
        """
        # Use nxaxcl.AxclInfer for inference with device_id=1
        self.infer = AxclInfer(model_path, device_id=device_id, vnpu_mode=0)
        
        # Store instance for cleanup tracking
        if model_path not in AxclInferenceSession._infer_instances:
            AxclInferenceSession._infer_instances[model_path] = []
        AxclInferenceSession._infer_instances[model_path].append(self)
        
        # Get input metadata from the model
        self.input_meta = []
        self.output_meta = []
        self._parse_io_info()
    
    def _parse_io_info(self):
        """Parse IO info to get input/output metadata from AxclInfer's model."""
        # Get input/output information from the model
        for inp in self.infer.model.inputs:
            self.input_meta.append({
                'index': inp['index'],
                'name': inp['name'],
                'dims': inp['dims'],
                'dtype': inp['dtype'],
                'size': inp['size']
            })
        
        for out in self.infer.model.outputs:
            self.output_meta.append({
                'index': out['index'],
                'name': out['name'],
                'dims': out['dims'],
                'dtype': out['dtype'],
                'size': out['size']
            })
    
    def _dtype_str_to_numpy(self, dtype_str: str) -> np.dtype:
        """Convert dtype string to numpy dtype."""
        dtype_map = {
            'uint8': np.uint8,
            'uint16': np.uint16,
            'uint32': np.uint32,
            'int8': np.int8,
            'int16': np.int16,
            'int32': np.int32,
            'int64': np.int64,
            'fp16': np.float16,
            'fp32': np.float32,
            'fp64': np.float64,
            'float32': np.float32,
            'float16': np.float16,
        }
        return dtype_map.get(dtype_str, np.float32)
    
    def run(self, output_names: Optional[list] = None, input_feed: Optional[Dict[str, np.ndarray]] = None) -> tuple:
        """
        Run inference.
        
        Args:
            output_names: Optional list of output names (ignored, all outputs returned)
            input_feed: Dictionary mapping input names to numpy arrays
            
        Returns:
            Tuple of output numpy arrays
        """
        if input_feed is None:
            raise ValueError("input_feed is required")
        
        # Convert dictionary input to ordered list based on model input order
        input_list = []
        for meta in self.input_meta:
            input_name = meta['name']
            if input_name in input_feed:
                data = input_feed[input_name]
            else:
                # Fallback: try to get by index if name not found
                # This handles cases where input_feed uses positional keys
                input_keys = list(input_feed.keys())
                if meta['index'] < len(input_keys):
                    data = input_feed[input_keys[meta['index']]]
                else:
                    raise ValueError(f"Input '{input_name}' (index {meta['index']}) not found in input_feed")
            
            # Ensure data is contiguous and correct dtype
            if not isinstance(data, np.ndarray):
                data = np.array(data)
            
            # Convert to appropriate dtype if needed
            numpy_dtype = self._dtype_str_to_numpy(meta['dtype'])
            if data.dtype != numpy_dtype:
                data = data.astype(numpy_dtype)
            
            data = np.ascontiguousarray(data)
            input_list.append(data)
        
        # Run inference using AxclInfer
        outputs = self.infer(input_list)
        
        # Return as tuple to match original interface
        return tuple(outputs)
    
    def copy_output_to_input_d2d(self, output_index: int, input_index: int):
        """
        Copy output buffer to input buffer using device-to-device transfer.
        This is much faster than D2H + H2D for large buffers like KV cache.
        
        Args:
            output_index: Index of output buffer to copy from
            input_index: Index of input buffer to copy to
        """
        return self.infer.copy_output_to_input_d2d(output_index, input_index)
    
    def copy_from_other_session_d2d(self, other_session: 'AxclInferenceSession', 
                                    other_output_index: int, self_input_index: int):
        """
        Copy output from another session to this session's input using device-to-device transfer.
        This is used to transfer data between different models (e.g., encoder -> decoder_main).
        
        Args:
            other_session: The source session (e.g., encoder)
            other_output_index: Output index in the source session
            self_input_index: Input index in this session
        """
        # Get device pointers
        src_ptr = other_session.infer.get_output_device_ptr(other_output_index)
        dst_ptr = self.infer.get_input_device_ptr(self_input_index)
        
        # Get sizes
        src_size = other_session.infer.model.outputs[other_output_index]['size']
        dst_size = self.infer.model.inputs[self_input_index]['size']
        
        if src_size > dst_size:
            raise ValueError(f"Source size {src_size} > destination size {dst_size}")
        
        # Perform D2D copy
        self.infer.device.memcpy_d2d(dst_ptr, src_ptr, src_size)
    
    def run_optimized(self, input_feed: Optional[Dict[str, np.ndarray]] = None,
                     skip_h2d_indices: Optional[List[int]] = None,
                     skip_d2h_indices: Optional[List[int]] = None) -> tuple:
        """
        Optimized run method that allows skipping H2D for certain inputs and D2H for certain outputs.
        This is useful for KV cache optimization where we want to keep data on device.
        
        Args:
            input_feed: Dictionary mapping input names to numpy arrays
            skip_h2d_indices: List of input indices to skip H2D (data already on device via D2D)
            skip_d2h_indices: List of output indices to skip D2H (data not needed on host)
            
        Returns:
            Tuple of output numpy arrays (None for skipped outputs)
        """
        if input_feed is None:
            raise ValueError("input_feed is required")
        
        # Convert dictionary input to ordered list based on model input order
        skip_h2d = skip_h2d_indices if skip_h2d_indices else []
        skip_h2d_set = set(skip_h2d)  # Use set for faster lookup
        
        # Prepare inputs: only process inputs that need H2D
        input_data_map = {}  # Map index -> data for inputs that need H2D
        for input_name, data in input_feed.items():
            # Find the index for this input name
            for meta in self.input_meta:
                if meta['name'] == input_name:
                    input_idx = meta['index']
                    if input_idx not in skip_h2d_set:
                        # Ensure data is contiguous and correct dtype
                        if not isinstance(data, np.ndarray):
                            data = np.array(data)
                        numpy_dtype = self._dtype_str_to_numpy(meta['dtype'])
                        if data.dtype != numpy_dtype:
                            data = data.astype(numpy_dtype)
                        data = np.ascontiguousarray(data)
                        input_data_map[input_idx] = data
                    break
        
        # Use optimized run method
        skip_d2h = skip_d2h_indices if skip_d2h_indices else []
        
        # Prepare inputs: skip H2D for specified indices
        self.infer._prepare_thread_resources()
        
        # H2D for inputs that are not skipped
        for i, meta in enumerate(self.infer.model.inputs):
            if i in skip_h2d_set:
                continue  # Skip H2D, data already on device via D2D
            if i not in input_data_map:
                raise ValueError(f"Input '{meta['name']}' (index {i}) not found in input_feed and not skipped")
            data = input_data_map[i]
            if data.nbytes > meta['size']:
                raise ValueError(f"Input too large for index {i}")
            self.infer.device.memcpy_h2d(self.infer._tls.in_ptrs[i], data)
        
        # Execute
        ret = engine_execute(self.infer.model.model_id, self.infer._tls.ctx, 0, self.infer._tls.io)
        if ret != 0:
            raise RuntimeError(f"Engine execute failed: {ret}")
        
        # D2H for outputs that are not skipped
        results = []
        for i, meta in enumerate(self.infer.model.outputs):
            if i in skip_d2h:
                results.append(None)  # Skip D2H, data stays on device
            else:
                raw_bytes = self.infer.device.memcpy_d2h(self.infer._tls.out_ptrs[i], meta['size'])
                dtype = self.infer._get_numpy_dtype(meta['dtype'])
                arr = np.frombuffer(raw_bytes, dtype=dtype).reshape(meta['dims'])
                # Performance optimization: avoid copy for large arrays
                # The buffer from memcpy_d2h is already a new buffer
                # Only copy small arrays (like logits) to ensure data independence
                if arr.nbytes < 1024 * 1024:  # Only copy if < 1MB
                    results.append(arr.copy())
                else:
                    results.append(arr)
        
        return tuple(results)
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'infer') and self.infer is not None:
                # Release thread resources
                self.infer.release()
        except:
            pass  # Ignore errors during cleanup
    
    @classmethod
    def cleanup_all(cls):
        """Cleanup all inference instances. Call this at program exit."""
        for instances in cls._infer_instances.values():
            for instance in instances:
                try:
                    if hasattr(instance, 'infer') and instance.infer is not None:
                        instance.infer.close()
                except:
                    pass
        
        # Global cleanup
        try:
            AxclInfer.env_close()
        except:
            pass

