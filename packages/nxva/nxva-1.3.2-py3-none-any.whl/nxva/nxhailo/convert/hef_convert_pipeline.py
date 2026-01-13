import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple

import numpy as np

from nxva.nxhailo.utils import make_quant_dataset
from nxva.yolo.yolo import YOLOOptions, YOLOToolBox


class HefConvertPipeline:
    def __init__(self, 
                 model_name: str,
                 model_type: str,
                 project_dir: Union[str, Path],
                 weights_path: Union[str, Path],
                 img_size: int = 640,
                 output_dir: Optional[Union[str, Path]] = None,
                 num_calib: int = 1000,
                 yolo_version: str = "yolo11",
                 yolo_task: str = "detect",
                 profile_key: str = "m",
                 device: str = "cpu",
                 fp16: bool = False,
                 hw_arch: str = "hailo8l",
                 start_node_names: Optional[List[str]] = None,
                 config_dict: Optional[Dict] = None,
                 model_script: Optional[str] = None):
        """
        Initialize the Hef Convert Pipeline.
        
        Args:
            model_name: Name of the model
            model_type: Type of model ('yolo', 'ir', 'osnet', 'multi_model')
            project_dir: Root directory for the project
            weights_path: Path to .pt weights file
            img_size: Image size
            output_dir: Output directory (optional, defaults to project_dir/model_name)
            num_calib: Number of calibration images
            yolo_version: YOLO version string (e.g. 'yolo11', 'yolov5')
            yolo_task: YOLO task ('detect', 'pose', etc)
            profile_key: Profile key for end node lookup (e.g. 'm', 's')
            device: Device to run torch on
            nc: Number of classes
            class_names: Dictionary of class names
            fp16: Use fp16
            hw_arch: Hailo hardware architecture
            start_node_names: List of start node names for conversion
            config_dict: Optional configuration dictionary to override defaults
            model_script: Optional model script to override generated one
        """
        self.model_name = model_name
        self.model_type = model_type
        self.project_dir = Path(project_dir)
        self.weights_path = Path(weights_path)
        self.img_size = img_size
        self.output_dir = Path(output_dir) if output_dir else self.project_dir / self.model_name
        self.num_calib = num_calib
        self.yolo_version = yolo_version
        self.yolo_task = yolo_task
        self.profile_key = profile_key
        self.device = device
        self.class_names = class_names
        self.fp16 = fp16
        self.hw_arch = hw_arch
        self.start_node_names = start_node_names or []
        self.config_dict = config_dict
        self.model_script = model_script

        self.options = YOLOOptions(
            version=self.yolo_version,
            task=self.yolo_task,
            weights=str(self.weights_path),
            size=self.img_size,
            device=self.device,
            fp16=self.fp16
        )
        
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_calibration_dataset(self, data_path: list, max_num: int = None) -> Tuple[np.ndarray, int]:
        """Create calibration dataset for quantization."""
        calib_dataset = make_quant_dataset(
            data_path, 
            img_size=self.img_size, 
            output_dir=str(self.output_dir), 
            max_num=max_num
        )
        print(f"Calibration dataset shape: {calib_dataset.shape}")
        print(f"Max value: {np.max(calib_dataset)}")
        print(f"Min value: {np.min(calib_dataset)}")
        return calib_dataset, calib_dataset.shape[0]

    def convert_pt_to_onnx(self) -> Path:
        """Convert PyTorch model to ONNX format."""
        if not self.weights_path.exists():
            raise ValueError(f"Weights file {self.weights_path} does not exist")
        
        print(f"Weights file {self.weights_path} exists")
        
        toolbox = YOLOToolBox(self.options)
        onnx_output_path = self.output_dir / f"{self.model_name}.onnx"
        
        toolbox.export(
            shape=(1, 3, self.img_size, self.img_size),
            dynamic=False,
            output_path=str(onnx_output_path),
            task='torch2onnx'
        )
        
        return onnx_output_path

    def get_model_script_and_transform(self):
        """Get model script and transform method based on model type."""
        model = self.model_type
        version = self.yolo_version
        task = self.yolo_task
        num_calib = self.num_calib

        if model == 'ir':
            from nxva.nxhailo.calib_transform import ir_transform
            model_script = f"model_optimization_config(calibration, calibset_size={num_calib})\n"
            transform_method = [ir_transform]
            
        elif model == 'osnet':
            from nxva.nxhailo.calib_transform import reid_transform
            model_script = (
                f"model_optimization_config(calibration, calibset_size={num_calib})\n"
                "pre_quantization_optimization(global_avgpool_reduction, layers=model/avgpool5, division_factors=[4, 4])\n"
                "pre_quantization_optimization(global_avgpool_reduction, layers=model/avgpool7, division_factors=[4, 4])\n"
            )
            transform_method = [reid_transform]
    
        elif model == 'yolo':
            from nxva.nxhailo.calib_transform import yolo_transform
            model_script = f"model_optimization_config(calibration, calibset_size={num_calib})\n"
            transform_method = [yolo_transform]
            if 'v5' in version and task == 'pose':
                from nxva.nxhailo.calib_transform import v5_pose_transform
                model_script = f"model_optimization_config(calibration, calibset_size={num_calib})\n"
                transform_method = [v5_pose_transform]
    
        elif model == 'multi_model':
            from nxva.nxhailo.calib_transform import yolo_transform
            model_script = (
                "performance_param(compiler_optimization_level=max)\n"
                f"model_optimization_config(calibration, calibset_size={num_calib})\n"
                "model1_v5s_224/input_layer1/normalization1 = normalization([0.0, 0.0, 0.0], [255.0, 255.0, 255.0])\n"
                "model2_v5s_224/input_layer1/normalization1 = normalization([0.0, 0.0, 0.0], [255.0, 255.0, 255.0])\n"
                "model3_v5s_512/input_layer1/normalization1 = normalization([0.0, 0.0, 0.0], [255.0, 255.0, 255.0])\n"
            )
            transform_method = [yolo_transform]
        else:
            raise ValueError(f"Model type '{model}' not supported")
        
        return model_script, transform_method

    def convert_onnx_to_hef(self):
        """Convert ONNX model to Hailo HEF format."""
        from nxva.nxhailo.axcl_convert import AxclConverter
        
        config_dict = {
            "model_configs": {
                f"{self.model_name}": [self.yolo_version.upper(), self.yolo_task, self.profile_key],
            },
            "root_dir": str(self.project_dir),
            "enable_normalization_script": False,
            "custom_calib_paths": [str(self.output_dir / "calib_set.npy")],
        }
        
        if self.config_dict:
            config_dict.update(self.config_dict)
        
        model_script, transform_method = self.get_model_script_and_transform()
        
        if self.model_script is not None:
             model_script = self.model_script

        convert_pipeline = AxclConverter(config_dict)
        convert_pipeline.run(
            hw_arch=self.hw_arch, 
            transform_method=transform_method, 
            start_node_names=self.start_node_names, 
            model_script=model_script,
            min_calib=self.num_calib
        )

    def run(self, data_path: list, max_images_per_dataset: int = 300, force_dataset: bool = False, force_onnx: bool = False, force_hef: bool = False):
        """
        Run the full conversion pipeline.
        
        Args:
            data_path: List of paths (globs) for calibration data
            num_calib_dataset: Number of images to use for calibration dataset creation
            force_dataset: Force recreation of calibration dataset
            force_onnx: Force regeneration of ONNX
            force_hef: Force regeneration of HEF
        """
        # Step 1: Create calibration dataset
        has_dataset = (self.output_dir / "calib_set.npy").exists()
        if not has_dataset or force_dataset:
            self.create_calibration_dataset(data_path, max_num=max_images_per_dataset)
        
        # Step 2: Convert PyTorch to ONNX
        has_onnx = (self.output_dir / f"{self.model_name}.onnx").exists()
        if not has_onnx or force_onnx:
            self.convert_pt_to_onnx()
        
        # Step 3: Convert ONNX to HEF
        has_hef = (self.output_dir / f"{self.model_name}_{self.model_name}.hef").exists() # AXCLConvert output pattern might need check.
        # AXCLConvert saves to output_folder/{_join(model_names)}.hef. Here model_names is one element.
        # So it should be f"{self.model_name}.hef"
        # Wait, AXCLConvert: output_folder = root_dir / model_names joined /
        # hef_filename = model_names joined .hef
        
        # In AXCLConvert:
        # self.output_folder = f"{self.root_dir}/{'_'.join(self.model_names)}/"
        # hef_filename = f"{'_'.join(self.model_names)}.hef"
        
        # Here model_name is passed as key in config dict: { f"{self.model_name}": ... }
        # So model_names list has one entry: self.model_name.
        # So output folder is root_dir / self.model_name /
        # hef file is self.model_name.hef inside that folder.
        
        hef_path = self.output_dir / f"{self.model_name}.hef"
        
        if not hef_path.exists() or force_hef:
            self.convert_onnx_to_hef()
