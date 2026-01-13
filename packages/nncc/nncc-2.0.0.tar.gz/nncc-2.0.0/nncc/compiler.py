import os
import ctypes
import json
import torch
import torch.nn as nn
from safetensors.torch import save_file, save

# Load Shared Library
_lib = None

def _load_lib():
    global _lib
    if _lib is not None:
        return _lib
    
    
    # Locate the packaged compiled library
    lib_name = "nncc.dll" if os.name == "nt" else "libnncc.so"
    
    # 1. Check inside the package (relative to this file)
    package_lib = os.path.join(os.path.dirname(__file__), lib_name)
    
    # 2. Check current directory or root (dev mode fallbacks)
    dev_lib = os.path.abspath(lib_name)
    root_lib = os.path.join(os.path.dirname(os.path.dirname(__file__)), lib_name)

    candidates = [package_lib, dev_lib, root_lib]
    
    lib_path = None
    for p in candidates:
        if os.path.exists(p):
            lib_path = p
            break
            
    if not lib_path:
        # Fallback to checking pure import for extension if we revert to that
        try:
            import importlib.util
            spec = importlib.util.find_spec("nncc._libnncc")
            if spec and spec.origin:
                lib_path = spec.origin
        except ImportError:
            pass

    if not lib_path:
        raise ImportError(f"Could not find library '{lib_name}'. Ensure package is installed correctly.")

    try:
        _lib = ctypes.CDLL(lib_path)
    except OSError as e:
        raise ImportError(f"Could not load extension at {lib_path}: {e}")
    
    # Configure signatures
    
    # char* nncc_compile(const char* name, const char* nnmodel_json, const void* safe_data, size_t safe_len, size_t* out_len)
    _lib.nncc_compile.argtypes = [
        ctypes.c_char_p, # name
        ctypes.c_char_p, # nnmodel_json
        ctypes.c_void_p, # safe_data
        ctypes.c_size_t, # safe_len
        ctypes.POINTER(ctypes.c_size_t) # out_len
    ]
    _lib.nncc_compile.restype = ctypes.POINTER(ctypes.c_char)
    
    # void nncc_free(void* ptr)
    _lib.nncc_free.argtypes = [ctypes.c_void_p]
    _lib.nncc_free.restype = None

    return _lib

# Export Helper (Copied and adapted from scripts/export_model.py)
def _get_layer_info(name: str, module: nn.Module, input_shape: list) -> dict:
    layer = {"name": name}
    
    if isinstance(module, nn.Linear):
        layer["op"] = "gemm"
        layer["weights"] = {
            "weight": f"{name}.weight",
            "bias": f"{name}.bias" if module.bias is not None else None
        }
        layer["output_shape"] = [input_shape[0], module.out_features]
        
    elif isinstance(module, nn.Conv2d):
        layer["op"] = "conv2d"
        layer["weights"] = {
            "weight": f"{name}.weight",
            "bias": f"{name}.bias" if module.bias is not None else None
        }
        layer["kernel_size"] = [module.kernel_size[0], module.kernel_size[1]]
        layer["stride"] = [module.stride[0], module.stride[1]]
        layer["padding"] = [module.padding[0], module.padding[1]]
        layer["groups"] = module.groups
        h_out = (input_shape[2] + 2 * module.padding[0] - module.kernel_size[0]) // module.stride[0] + 1
        w_out = (input_shape[3] + 2 * module.padding[1] - module.kernel_size[1]) // module.stride[1] + 1
        layer["output_shape"] = [input_shape[0], module.out_channels, h_out, w_out]
        
    elif isinstance(module, nn.MaxPool2d):
        layer["op"] = "maxpool2d"
        ks = module.kernel_size if isinstance(module.kernel_size, tuple) else (module.kernel_size, module.kernel_size)
        st = module.stride if isinstance(module.stride, tuple) else (module.stride, module.stride)
        layer["kernel_size"] = list(ks)
        layer["stride"] = list(st)
        h_out = (input_shape[2] - ks[0]) // st[0] + 1
        w_out = (input_shape[3] - ks[1]) // st[1] + 1
        layer["output_shape"] = [input_shape[0], input_shape[1], h_out, w_out]
    
    elif isinstance(module, nn.AvgPool2d):
        layer["op"] = "avgpool2d"
        ks = module.kernel_size if isinstance(module.kernel_size, tuple) else (module.kernel_size, module.kernel_size)
        st = module.stride if isinstance(module.stride, tuple) else (module.stride, module.stride)
        layer["kernel_size"] = list(ks)
        layer["stride"] = list(st)
        h_out = (input_shape[2] - ks[0]) // st[0] + 1
        w_out = (input_shape[3] - ks[1]) // st[1] + 1
        layer["output_shape"] = [input_shape[0], input_shape[1], h_out, w_out]

    elif isinstance(module, nn.AdaptiveAvgPool2d):
        layer["op"] = "global_avgpool"
        layer["output_shape"] = [input_shape[0], input_shape[1], 1, 1]
        
    elif isinstance(module, nn.ReLU):
        layer["op"] = "relu"
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.ReLU6):
        layer["op"] = "relu6"
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.Sigmoid):
        layer["op"] = "sigmoid"
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.Tanh):
        layer["op"] = "tanh"
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.Softmax):
        layer["op"] = "softmax"
        layer["axis"] = module.dim if module.dim is not None else -1
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.BatchNorm2d):
        layer["op"] = "batchnorm"
        layer["weights"] = {
            "weight": f"{name}.weight",
            "bias": f"{name}.bias",
            "running_mean": f"{name}.running_mean",
            "running_var": f"{name}.running_var"
        }
        layer["epsilon"] = module.eps
        layer["output_shape"] = input_shape
    elif isinstance(module, nn.Flatten):
        layer["op"] = "flatten"
        layer["output_shape"] = [input_shape[0], -1]
    elif isinstance(module, nn.Dropout):
        layer["op"] = "dropout"
        layer["output_shape"] = input_shape
    else:
        return None
        
    if "weights" in layer:
        layer["weights"] = {k: v for k, v in layer["weights"].items() if v is not None}
        
    return layer

def _export_in_memory(model: nn.Module, sample_input: torch.Tensor, output_name: str):
    """
    Export model architecture and weights to memory.
    Returns: (json_str, safetensors_bytes)
    """
    model.eval()
    
    layers = []
    input_shape = list(sample_input.shape)
    prev_output = "input"
    current_shape = input_shape
    
    for name, module in model.named_modules():
        if name == "" or isinstance(module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
            continue
            
        # Clean name for C identifier compatibility (simple check)
        clean_name = name.replace(".", "_")
        
        layer = _get_layer_info(clean_name, module, current_shape)
        if layer:
            layer["inputs"] = [prev_output]
            layers.append(layer)
            prev_output = clean_name
            current_shape = layer["output_shape"]
    
    # Resolve flatten shapes
    for layer in layers:
        if layer["op"] == "flatten" and layer["output_shape"][1] == -1:
            idx = layers.index(layer)
            if idx > 0:
                prev_shape = layers[idx - 1]["output_shape"]
                flat_size = 1
                for d in prev_shape[1:]: flat_size *= d
                layer["output_shape"] = [prev_shape[0], flat_size]
    
    model_def = {
        "name": output_name,
        "inputs": [{"name": "input", "dtype": "float32", "shape": input_shape}],
        "outputs": [{"name": prev_output, "dtype": "float32", "shape": current_shape}],
        "layers": layers
    }
    
    json_str = json.dumps(model_def)
    
    # Save weights to bytes
    tensors = {k: v for k, v in model.state_dict().items()}
    
    # Correct iteration
    layers = []
    input_shape = list(sample_input.shape)
    prev_output = "input"
    current_shape = input_shape

    for name, module in model.named_modules():
        if name == "" or isinstance(module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
            continue
            
        # Sanitize name for C identifier
        json_name = name.replace(".", "_") 
        
        layer = _get_layer_info(name, module, current_shape)
        if layer:
            layer["inputs"] = [prev_output]
            layers.append(layer)
            prev_output = layer["name"]
            current_shape = layer["output_shape"]

    # Flatten fix again
    for layer in layers:
        if layer["op"] == "flatten" and layer["output_shape"][1] == -1:
            idx = layers.index(layer)
            if idx > 0:
                prev_shape = layers[idx - 1]["output_shape"]
                flat_size = 1
                for d in prev_shape[1:]: flat_size *= d
                layer["output_shape"] = [prev_shape[0], flat_size]

    model_def = {
        "name": output_name,
        "inputs": [{"name": "input", "dtype": "float32", "shape": input_shape}],
        "outputs": [{"name": prev_output, "dtype": "float32", "shape": current_shape}],
        "layers": layers
    }
    
    json_str = json.dumps(model_def)
    safetensors_bytes = save(tensors)
    
    return json_str.encode('utf-8'), safetensors_bytes

def compile(model: nn.Module, sample_input: torch.Tensor, name: str = "model") -> str:
    """
    Compile PyTorch model to C code.
    
    Args:
        model: PyTorch nn.Module
        sample_input: Example input tensor
        name: Name for the model (prefix for C functions)
        
    Returns:
        String containing generated C code.
    """
    lib = _load_lib()
    
    # Export to memory
    json_bytes, safe_bytes = _export_in_memory(model, sample_input, name)
    
    # Call C API
    # char* nncc_compile(const char* name, const char* nnmodel_json, const void* safe_data, size_t safe_len, size_t* out_len)
    
    out_len = ctypes.c_size_t(0)
    c_name = name.encode('utf-8')
    # json_bytes is already bytes (char*)
    # safe_bytes is bytes (void*)
    
    ptr = lib.nncc_compile(c_name, json_bytes, safe_bytes, len(safe_bytes), ctypes.byref(out_len))
    
    if not ptr:
        raise RuntimeError("nncc compilation failed")
        
    try:
        # Copy string to Python
        data = ctypes.string_at(ptr, out_len.value)
        return data.decode('utf-8')
    finally:
        lib.nncc_free(ptr)

def compile_to_file(model: nn.Module, sample_input: torch.Tensor, filename: str, name: str = "model"):
    """Compile model and save to file."""
    code = compile(model, sample_input, name)
    with open(filename, "w") as f:
        f.write(code)
