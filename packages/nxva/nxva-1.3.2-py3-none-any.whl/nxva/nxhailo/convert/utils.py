import os
import random

import cv2
import numpy as np

from PIL import Image


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    """
    Resize image to specified dimensions while maintaining aspect ratio and padding borders.
    
    Function:
        Resize input image to specified new dimensions while maintaining original aspect ratio.
        Fill empty areas with specified color, ensuring image is a multiple of 32 pixels.
    
    Input:
        img (numpy.ndarray): Input image with shape (height, width, channels)
        new_shape (tuple | int): Target dimensions, default (640, 640)
        color (tuple): Padding color (R, G, B), default (114, 114, 114)
    
    Output:
        numpy.ndarray: Resized image with dimensions new_shape
    
    Example:
        >>> img = cv2.imread('image.jpg')  # shape (480, 640, 3)
        >>> resized = letterbox(img, new_shape=(416, 416))
        >>> print(resized.shape)  # (416, 416, 3)
    """
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    elif isinstance(new_shape, tuple):
        new_shape = new_shape
    else:
        raise TypeError(f"Unsupported type for new_shape: {type(new_shape)}")
    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    dw /= 2  # divide padding into 2 sides
    dh /= 2
    
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img

def load_end_node_config(yaml_path: str = "end_node.yaml") -> Dict:
    """
    Load end_node configuration from YAML file.
    Automatically searches for end_node.yaml in common locations if the default path fails.

    Args:
        yaml_path (str): Path to the YAML configuration file.

    Returns:
        Dict: Configuration dictionary loaded from YAML.
    """
    # List of possible paths to search for end_node.yaml
    possible_paths = [
        yaml_path,  # Use the provided path first
        "end_node.yaml",  # Current directory
        "./end_node.yaml",  # Current directory with explicit path
        "./nxva/nxva/nxhailo/end_node.yaml",  # Relative path from project root
        os.path.join(os.path.dirname(__file__), "end_node.yaml"),  # Same directory as convert.py
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "end_node.yaml"),  # Parent directory
    ]
    
    # Try each possible path
    for path in possible_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    print(f"Successfully loaded end_node.yaml from: {path}")
                    return config
        except FileNotFoundError:
            continue
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {path}: {e}")
            continue
    
    # If no path worked, print warning and return None
    print(f"Warning: Could not find end_node.yaml in any of the searched locations:")
    for path in possible_paths:
        print(f"  - {path}")
    return None

def get_end_node_names_from_dict(convert_table: Dict, model_type: str, task: str, profile_key: str) -> List[str]:
    """
    Get end_node_names for a single model profile from a dictionary.
    Supports both traditional format (YOLOV5/YOLO11) and EMBED format.

    Args:
        convert_table (Dict): Dictionary containing model conversion configurations.
        model_type (str): The model type key in dict (e.g., 'YOLOV5', 'YOLO11', 'EMBED').
        task (str): The task key in dict (e.g., 'detect' for traditional, 'osnet'/'ir'/'par' for EMBED).
        profile_key (str): Profile key (e.g., 'm', 'n') for traditional format, ignored for EMBED format.

    Returns:
        List[str]: end_node_names for the profile.
    """
    # Handle EMBED format (simplified format for models without NMS architecture)
    if model_type == 'EMBED':
        if task not in convert_table[model_type]:
            raise ValueError(f"Task '{task}' not found in EMBED section")
        return convert_table[model_type][task]
    
    # Handle traditional format (YOLOV5/YOLO11)
    if model_type not in convert_table:
        raise ValueError(f"Model type '{model_type}' not found in convert_table")
    
    if task not in convert_table[model_type]:
        raise ValueError(f"Task '{task}' not found for model type '{model_type}'")
    
    task_list = convert_table[model_type][task]
    task_dict = {}
    for entry in task_list:
        task_dict.update(entry)
    
    if profile_key not in task_dict:
        raise ValueError(f"Profile key '{profile_key}' not found in convert_table for {model_type}/{task}")
    
    return task_dict[profile_key]


def make_quant_dataset(dataset_path, img_size=320, ch=3, max_num=5000, output_dir='./'):
    """Create quantization dataset"""
    os.makedirs(output_dir, exist_ok=True)
    # images_list = [img_name for img_name in os.listdir(dataset_path) 
    #               if os.path.splitext(img_name)[1] == ".jpg"]
    import glob
    images_list = []
    if isinstance(dataset_path, list):
        for p in dataset_path:
            images_list.extend(glob.glob(p))
    else:
        images_list = glob.glob(dataset_path)

    random.shuffle(images_list)

    images_list = images_list[:max_num]
    
    calib_dataset = np.zeros((len(images_list), img_size, img_size, ch))
    error_count = 0
    error_path_list = []
    for idx, img_name in enumerate(sorted(images_list)):
        img = np.array(Image.open(img_name))
        if img.shape[-1] == 3:
            img_preproc = letterbox(img, new_shape=(img_size, img_size))
            calib_dataset[idx, :, :, :] = img_preproc
        else:
            error_path_list.append(img_name)
            error_count += 1
    print(f"error_count: {error_count}")
    print(f"error_path_list: {error_path_list}")
    
    save_data_path = os.path.join(output_dir, "calib_set.npy")
    np.save(save_data_path, calib_dataset)
    return calib_dataset