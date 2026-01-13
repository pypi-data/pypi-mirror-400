import time
import numpy as np
from functools import partial


class HailoAsyncInference:
    vdevice = None

    def __init__(self, hef_path: str, batch_size : int = 32):
        self.hef_path = hef_path
        self.batch_size = batch_size
        self.timeout_ms = 10000

        self.infer_model = None
        self.configured_infer_model = None

        self.load_model()

    # -------------------------
    # Model / Device lifecycle
    # -------------------------
    def load_model(self):
        from hailo_platform import (
            VDevice,
            HailoSchedulingAlgorithm,
            FormatType,
            HEF
        )
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        params.group_id = "SHARED"

        HailoAsyncInference.vdevice = VDevice(params)
        HailoAsyncInference.vdevice.__enter__()

        hef = HEF(self.hef_path)
        node_info = hef.get_output_vstream_infos()
        self.output_end_node = [info.name for info in node_info]
        del hef; del HEF

        self.infer_model = HailoAsyncInference.vdevice.create_infer_model(self.hef_path)
        self.infer_model.set_batch_size(self.batch_size)

        for name in self.output_end_node:
            self.infer_model.output(name).set_format_type(FormatType.FLOAT32)

        self.configured_infer_model = self.infer_model.configure()
        self.configured_infer_model.__enter__()

    # -------------------------
    # Inference
    # -------------------------
    def __call__(self, input_batch: list):
        """
        input_batch: (B, H, W, C)
        """
        running_tasks = [0]
        collected_buffers = []
        for idx, input_data in enumerate(input_batch):
            bindings = self.configured_infer_model.create_bindings()
            bindings.input().set_buffer(input_data)

            output_buffers = {}
            for name in self.output_end_node:
                buf = np.zeros(self.infer_model.output(name).shape, dtype=np.float32)
                bindings.output(name).set_buffer(buf)
                output_buffers[name] = buf
            self.configured_infer_model.wait_for_async_ready(self.timeout_ms)

            running_tasks[0] += 1
            self.configured_infer_model.run_async(
                [bindings],
                callback=partial(
                    self.callback,
                    output_buffers=output_buffers,
                    running_tasks=running_tasks,
                ),
            )
            collected_buffers.append(output_buffers)
        while running_tasks[0] > 0:
            time.sleep(0.01)
        output = [
            np.stack([np.moveaxis(bufs[name], -1, 0) for bufs in collected_buffers], axis=0) #HWC
            for name in self.output_end_node
        ]
        return output

    def callback(self, completion_info, output_buffers, running_tasks):
        running_tasks[0] -= 1
        if completion_info.exception:
            return

    def close(self):
        self.close_model()
        self.close_device()

    def close_device(self):
        if HailoAsyncInference.vdevice:
            HailoAsyncInference.vdevice.__exit__(None, None, None)

    def close_model(self):
        if self.configured_infer_model:
            self.configured_infer_model.__exit__(None, None, None)

import os
import threading


class HefInference:
    import resource
    # ---- class-level shared state ----
    in_format, out_format = None, None
    interface = None
    target = None
    active_model_id = None
    network_context = None
    infer_pipeline = None
    models_pool = {}
    model_num = 0

    # 串行化所有「切換/推論」操作的鎖
    _lock = threading.RLock()

    # 避免 core dump / 關掉 hailo logger
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.environ["HAILORT_LOGGER_PATH"] = "NONE"

    def __init__(self, weight):
        self.load_model(weight)

    def load_model(self, weight):
        from hailo_platform import (
            VDevice, HEF, HailoStreamInterface, ConfigureParams,
            InputVStreamParams, OutputVStreamParams, FormatType
        )
        # 不需要鎖：只要 pool 是空才會建 VDevice；多執行緒時仍建議加鎖保險
        with HefInference._lock:
            if not HefInference.models_pool:
                HefInference.target = VDevice()

            try:
                self.model_id = HefInference.model_num
                HefInference.model_num += 1

                hef = HEF(weight)
                configure_params = ConfigureParams.create_from_hef(
                    hef, interface=HailoStreamInterface.PCIe
                )
                network_group = HefInference.target.configure(hef, configure_params)[0]
                network_group_params = network_group.create_params()

                # vstream params
                input_vstreams_params = InputVStreamParams.make(
                    network_group, format_type=FormatType.FLOAT32
                )
                output_vstreams_params = OutputVStreamParams.make(
                    network_group, format_type=FormatType.FLOAT32
                )

                HefInference.models_pool[self.model_id] = {
                    "hef": hef,
                    "network_group": network_group,
                    "network_group_params": network_group_params,
                    "input_vstreams_params": input_vstreams_params,
                    "output_vstreams_params": output_vstreams_params,
                    "input_info": [n.name for n in hef.get_input_vstream_infos()],
                    "output_infos": hef.get_output_vstream_infos(),
                }
            except Exception as e:
                HefInference.model_num -= 1
                raise ValueError(f"Error loading model {getattr(self, 'model_id', '?')}: {e}")

    @classmethod
    def _activate_model(cls, model_id):
        # 僅允許單執行緒進入（切換與 context 進出都在鎖內）
        from hailo_platform import InferVStreams
        m = cls.models_pool[model_id]

        # 關掉舊的（若存在）
        if cls.infer_pipeline is not None:
            try:
                cls.infer_pipeline.__exit__(None, None, None)
            finally:
                cls.infer_pipeline = None
        if cls.network_context is not None:
            try:
                cls.network_context.__exit__(None, None, None)
            finally:
                cls.network_context = None

        # 啟動新的
        cls.network_context = m["network_group"].activate(m["network_group_params"])
        cls.infer_pipeline = InferVStreams(
            m["network_group"],
            m["input_vstreams_params"],
            m["output_vstreams_params"],
        )
        cls.network_context.__enter__()
        cls.infer_pipeline.__enter__()
        cls.active_model_id = model_id

    def switch_model(self):
        # 使用 class-level 鎖，避免和推論並行
        with HefInference._lock:
            if self.model_id not in HefInference.models_pool:
                raise ValueError(f"Model {self.model_id} not found in pool")
            if self.model_id == HefInference.active_model_id:
                return
            HefInference._activate_model(self.model_id)

    def __call__(self, input_data):
        # 同樣鎖起來：保證不會在別人切換時推論，反之亦然
        with HefInference._lock:
            # 確保 active model 正確
            if self.model_id != HefInference.active_model_id: self.switch_model()
            return HefInference.infer_pipeline.infer(input_data)

    def close(self):
        # 關閉也鎖一下，避免 race
        with HefInference._lock:
            try:
                if HefInference.infer_pipeline is not None:
                    HefInference.infer_pipeline.__exit__(None, None, None)
                    HefInference.infer_pipeline = None
                if HefInference.network_context is not None:
                    HefInference.network_context.__exit__(None, None, None)
                    HefInference.network_context = None
                if HefInference.target is not None:
                    HefInference.target.release()
                    HefInference.target = None
                HefInference.active_model_id = None
            except Exception:
                # 關閉階段通常不 raise，避免卡住上層
                pass