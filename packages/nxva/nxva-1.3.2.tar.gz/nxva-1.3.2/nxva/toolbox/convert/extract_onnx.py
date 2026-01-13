import argparse
import numpy as np

import onnx
from onnx import helper, TensorProto
import onnx.shape_inference
from onnx.utils import extract_model

def show_onnx(input_path):
    """
    Display input tensor information of an ONNX model.
    
    This function loads an ONNX model and prints out the details of all input tensors,
    including their names, shapes, and element types. Useful for inspecting model
    structure before processing or conversion.
    
    Args:
        input_path (str): Path to the input ONNX model file
        
    Example output:
        images [1, 3, 512, 512] 1
        (name: images, shape: [1, 3, 512, 512], element_type: 1 which is float32)
    """
    m = onnx.load(input_path)
    for i in m.graph.input:
        t = i.type.tensor_type
        shape = [d.dim_value for d in t.shape.dim]
        elem_type = t.elem_type  # Usually 1=float32
        print(i.name, shape, elem_type)


def truncate_onnx(input_onnx, output_onnx, target_nodes, new_output_names=None):
    """
    Extract a subgraph from an ONNX model and rename output tensors.
    
    This function performs two main operations:
    1. Extracts a subgraph from the input ONNX model, keeping only the specified
       input and output nodes (truncating the model at the target nodes)
    2. Renames the output tensors to sequential names ("1", "2", "3", ...) for
       easier identification and use in downstream processing
    
    The extraction process creates a new ONNX model that contains only the nodes
    necessary to compute the target output nodes from the input nodes. This is
    useful for model optimization, debugging, or creating intermediate models.
    
    Args:
        input_onnx (str): Path to the input ONNX model file
        output_onnx (str): Path where the extracted model will be saved
        target_nodes (list): List of target node names (node.name) that will become
                            the outputs of the extracted model
        new_output_names (list, optional): List of new output names. If None,
                                          uses sequential names "1", "2", "3"...
    
    Note:
        Currently hardcoded to use "images" as input tensor name. The output file
        path is also hardcoded to "../model/yolov5m_512_truncated.onnx"
    """
    # Must be the actual input tensor name in the graph
    inputs = ["images"]

    # Method A: Extract model directly using file paths
    # This creates a new ONNX model containing only nodes needed to compute
    # the target_nodes from the inputs
    extract_model(input_onnx, output_onnx, input_names=inputs, output_names=target_nodes)

    # Optional: Validate the extracted model
    onnx.checker.check_model(onnx.load(output_onnx))
    
    # ======================
    # Load the extracted model for renaming
    model = onnx.load(output_onnx)

    # Iterate through all nodes and rename output tensor names
    # Replace target node names with sequential numbers ("1", "2", "3", ...)
    idx = 0
    for node in model.graph.node:
        for i, out in enumerate(node.output):
            if out in target_nodes:
                idx += 1
                node.output[i] = f"{idx}"

    # Also modify graph.output (because output names need to be synchronized)
    # Update the formal output definitions in the graph
    idx = 0
    for i, out in enumerate(model.graph.output):
        name = out.name
        if name in target_nodes:
            idx += 1
            model.graph.output[i].name = f"{idx}"

    # Save to new file
    onnx.save(model, "../model/yolov5m_512_truncated.onnx")

    # Validate the final model
    onnx.checker.check_model("../model/yolov5m_512_truncated.onnx")
    print("✅ renamed ok!")






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ONNX toolbox utilities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Command: show_onnx
    show_parser = subparsers.add_parser("show", help="Show ONNX model input information")
    show_parser.add_argument("input_path", type=str, help="Path to input ONNX model")
    
    # Command: extract_and_rename
    extract_parser = subparsers.add_parser("extract", help="Extract and rename ONNX model")
    extract_parser.add_argument("input_onnx", type=str, help="Path to input ONNX model")
    extract_parser.add_argument("output_onnx", type=str, help="Path to output ONNX model")
    extract_parser.add_argument("--target-nodes", nargs="+", required=True,
                               help="List of target node names to extract")
    extract_parser.add_argument("--new-output-names", nargs="+", default=None,
                               help="Optional list of new output names. If not provided, uses '1', '2', '3'...")
    
    args = parser.parse_args()
    
    if args.command == "show":
        show_onnx(args.input_path)
    elif args.command == "extract":
        truncate_onnx(
            input_onnx=args.input_onnx,
            output_onnx=args.output_onnx,
            target_nodes=args.target_nodes,
            new_output_names=args.new_output_names
        )
    else:
        parser.print_help()


# python3 onnx_toolbox.py show ../model/yolov5m_512.onnx
# python3 onnx_toolbox.py extract ../model/yolov5m_512.onnx ../model/yolov5m_512_truncated.onnx --target-nodes /model/model.24/m.0/Conv /model/model.24/m.1/Conv /model/model.24/m.2/Conv


