import os
import yaml
from typing import List, Dict, Optional

import numpy as np
from .utils import make_quant_dataset, load_end_node_config, get_end_node_names_from_dict
    


class AxclConverter:
    """
    ModelConvertPipeline handles multi-model Hailo ONNX conversion, join, normalization, calibration, and compilation.

    Supports automatic join of multiple models, optional insertion of normalization script,
    per-model end_node_names, calibration data handling, and HEF output.
    Configuration is loaded from YAML file (end_node.yaml) or can be provided via custom_end_node_list.

    Attributes:
        model_names (List[str]): List of model names, must match order of end_node_names_list.
        root_dir (str): Root directory for models.
        end_node_names_list (List[List[str]]): List of end_node_names for each model.
        enable_normalization_script (bool): Whether to insert normalization script.
        onnx_paths (List[str]): Internal list of ONNX file paths.
        calib_paths (List[str]): Internal list of calibration data file paths.
        runners (List[ClientRunner]): List of runners for each model.
        r_main (ClientRunner): Main runner after join.
        output_folder (str): Output folder for HEF file.
        convert_table (Dict): Dictionary containing model conversion configurations loaded from YAML.
        custom_calib_paths (Optional[List[str]]): Custom calibration dataset paths for each model.
        custom_end_node_list (Optional[List[List[str]]]): Custom end_node_names for each model.
        end_node_yaml_path (str): Path to the YAML configuration file.
    """
    
    
    def __init__(self, config_dict: Dict):
        """
        Initialize ModelPipeline.

        Args:
            config_dict (Dict): Complete configuration dictionary containing:
                - model_configs: Dict mapping model_name to [model_type, task, profile_key]
                  For traditional models: [model_type, task, profile_key] (e.g., ["YOLOV5", "detect", "m"])
                  For EMBED models: ["EMBED", model_name, ""] (e.g., ["EMBED", "osnet", ""])
                - root_dir: Root directory for models
                - enable_normalization_script: Whether to insert normalization script (optional, default True)
                - custom_calib_paths: Optional list of custom calibration dataset paths for each model
                - custom_end_node_list: Optional list of custom end_node_names for each model
                - end_node_yaml_path: Optional path to end_node.yaml file (default: "end_node.yaml")
        """
        # Extract model configurations
        self.model_configs = config_dict.get('model_configs', {})
        self.model_names = list(self.model_configs.keys())
        
        # Extract other configurations
        self.root_dir = config_dict.get('root_dir', '')
        self.enable_normalization_script = config_dict.get('enable_normalization_script', True)
        self.custom_calib_paths = config_dict.get('custom_calib_paths', None)
        self.custom_end_node_list = config_dict.get('custom_end_node_list', None)
        self.end_node_yaml_path = config_dict.get('end_node_yaml_path', 'end_node.yaml')
        
        # Validate custom_calib_paths if provided
        if self.custom_calib_paths is not None:
            if len(self.custom_calib_paths) != len(self.model_names):
                raise ValueError("custom_calib_paths length must match number of models")
        
        # Validate custom_end_node_list if provided
        if self.custom_end_node_list is not None:
            if len(self.custom_end_node_list) != len(self.model_names):
                raise ValueError("custom_end_node_list length must match number of models")
        
        # Initialize internal attributes
        self.convert_table = self._load_convert_table()
        self.end_node_names_list = self._build_end_node_names_list()
        self.onnx_paths = []
        self.calib_paths = []
        self.runners = []
        self.r_main = None
        self.output_folder = f"{self.root_dir}/{'_'.join(self.model_names)}/"


    def _load_convert_table(self) -> Dict:
        """
        Load convert table from YAML file.
        
        Returns:
            Dict: Convert table dictionary loaded from YAML file.
        
        Raises:
            FileNotFoundError: If YAML file is not found and no fallback is available.
        """
        # Load from YAML file
        yaml_config = load_end_node_config(self.end_node_yaml_path)
        if yaml_config is not None:
            return yaml_config
        else:
            # If YAML file is not found, raise an error since we no longer have CONVERT_TABLE fallback
            raise FileNotFoundError(f"YAML configuration file '{self.end_node_yaml_path}' not found. Please ensure the file exists and contains the required model configurations.")
    
    def _build_end_node_names_list(self) -> List[List[str]]:
        """
        Build end_node_names_list from either custom list or YAML configuration.
        
        Returns:
            List[List[str]]: List of end_node_names for each model.
        """
        # If custom_end_node_list is provided, use it directly
        if self.custom_end_node_list is not None:
            return self.custom_end_node_list
        
        # Otherwise, build from YAML configuration
        end_node_names_list = []
        for model_name in self.model_names:
            model_type, task, profile_key = self.model_configs[model_name]
            end_node_names = get_end_node_names_from_dict(self.convert_table, model_type, task, profile_key)
            end_node_names_list.append(end_node_names)
        return end_node_names_list

    def check_file_exists(self, file_path: str):
        """
        Check if a file exists. Raise FileNotFoundError if not found.

        Args:
            file_path (str): Path to check.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

    def translate_models(self, hw_arch = 'hailo8l': str, start_node_names = []: List[str]):
        """
        Translate all ONNX models and create corresponding ClientRunner objects.
        Checks for ONNX and calibration file existence.
        Supports custom calibration dataset paths for each model.
        """
        from hailo_sdk_client import ClientRunner

        if len(self.model_names) != len(self.end_node_names_list):
            raise ValueError("model_names and end_node_names_list must have the same length.")
        
        for idx, (name, end_node_names) in enumerate(zip(self.model_names, self.end_node_names_list)):
            onnx_path = f"{self.root_dir}/{name}/{name}.onnx"
            print(f"onnx_path: {onnx_path}")
            
            # Use custom calib path if provided, otherwise use default path
            if self.custom_calib_paths is not None:
                calib_path = self.custom_calib_paths[idx]
            else:
                calib_path = f"{self.root_dir}/{name}/calib_set.npy"
            
            self.check_file_exists(onnx_path)
            self.check_file_exists(calib_path)
            self.onnx_paths.append(onnx_path)
            self.calib_paths.append(calib_path)
            runner = ClientRunner(hw_arch=hw_arch)
            runner.translate_onnx_model(onnx_path, start_node_names=start_node_names, end_node_names=end_node_names)
            self.runners.append(runner)

    def join_models(self):
        """
        Join all runners into a single main runner.
        For the first join, rename both runners' "model" scope to their respective model names.
        For subsequent joins, keep existing scopes and rename the new runner's "model" scope.
        """
        from hailo_sdk_client.exposed_definitions import JoinAction
        self.r_main = self.runners[0]
        if len(self.runners) > 1:
            # First join: rename both runners' "model" scope
            scope1 = {"model": self.model_names[0]}
            scope2 = {"model": self.model_names[1]}
            self.r_main.join(self.runners[1], scope1_name=scope1, scope2_name=scope2, join_action=JoinAction.NONE)
            
            # Subsequent joins: keep existing scopes, rename new runner's "model" scope
            for idx in range(2, len(self.runners)):
                scope1 = {name: name for name in self.model_names[:idx]}
                scope2 = {"model": self.model_names[idx]}
                self.r_main.join(self.runners[idx], scope1_name=scope1, scope2_name=scope2, join_action=JoinAction.NONE)
        print('----- Join Finished.-----')

    def add_normalization(self):
        """
        Insert normalization script if enabled.
        Format: all norm nodes joined by comma, then assigned to one normalization.
        """
        if not self.enable_normalization_script:
            return
        norm_nodes = []
        for i, name in enumerate(self.model_names, 1):
            norm_nodes.append(f"{name}/norm{i}")
        alls = ", ".join(norm_nodes) + " = normalization([0.0, 0.0, 0.0], [255.0, 255.0, 255.0])"
        self.r_main.load_model_script(alls)

    def add_model_script(self, model_script: str):
        self.r_main.load_model_script(model_script)

    def optimize_full_precision(self):
        """
        Run full precision optimization on the main runner.
        """
        self.r_main.optimize_full_precision()

    def calibrate_and_optimize(self, transform_method: list, min_calib: int = None):
        """
        Load all calibration data and run quantization optimization.
        Uses up to 5000 samples, aligned across all models.
        """

        calibs = [transform(np.load(path)) for path, transform in zip(self.calib_paths, transform_method)]
        if isinstance(min_calib, int):
            min_calib = min_calib
        else:
            min_calib = min(len(c) for c in calibs)
        if len(self.runners) > 1:
            calib_dict = {f"{name}/input_layer1": c[:min_calib] for name, c in zip(self.model_names, calibs)}
            print("calib_dict keys:", calib_dict.keys())
            self.r_main.optimize(calib_dict)
        else:
            self.r_main.optimize(calibs[0])

    def compile_and_save(self):
        """
        Compile the main runner and save the HEF file to output_folder.
        """
        hef = self.r_main.compile()
        os.makedirs(self.output_folder, exist_ok=True)
        hef_filename = f"{'_'.join(self.model_names)}.hef"
        hef_path = os.path.join(self.output_folder, hef_filename)
        with open(hef_path, "wb") as f:
            f.write(hef)
        print(f"HEF file saved to: {hef_path}")

    def run(self, hw_arch: str, transform_method: list, start_node_names: list, model_script: str, min_calib: int = None):
        """
        Run the full pipeline: translate, join, normalization, optimize, calibrate, and compile.
        """
        self.translate_models(hw_arch, start_node_names)
        self.join_models()
        self.add_normalization()
        if model_script is not None:
            self.add_model_script(model_script)
        self.optimize_full_precision()
        self.calibrate_and_optimize(transform_method, min_calib)
        self.compile_and_save()



