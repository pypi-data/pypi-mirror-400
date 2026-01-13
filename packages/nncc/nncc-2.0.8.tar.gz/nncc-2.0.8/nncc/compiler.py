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
    
    # 1. Windows: DLL is packaged directly
    if os.name == "nt":
        dll_path = os.path.join(os.path.dirname(__file__), "nncc.dll")
        if os.path.exists(dll_path):
            try:
                _lib = ctypes.CDLL(dll_path)
                # Success, skip below
                return _setup_signatures(_lib)
            except OSError:
                pass

    # 2. Linux/Mac: Check for compiled extension module (via import machinery)
    try:
        import importlib.util
        spec = importlib.util.find_spec("nncc._libnncc")
        if spec and spec.origin:
             _lib = ctypes.CDLL(spec.origin)
             return _setup_signatures(_lib)
    except (ImportError, OSError):
        pass

    # 3. Fallback: Development environment (root directory)
    dev_lib_name = "nncc.dll" if os.name == "nt" else "libnncc.so"
    dev_path = os.path.abspath(dev_lib_name) # Current dir
    if not os.path.exists(dev_path):
        # Try up one level
        dev_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), dev_lib_name)
        
    if os.path.exists(dev_path):
        try:
             _lib = ctypes.CDLL(dev_path)
             return _setup_signatures(_lib)
        except OSError:
             pass

    raise ImportError("Could not load 'nncc' C library. \n"
                      "  - On Windows: Ensure nncc.dll is in the package.\n"
                      "  - On Linux/Mac: Ensure the package was compiled during install (gcc required).\n")

def _setup_signatures(lib):
    """Internal helper to set argtypes/restype"""
    lib.nncc_compile.argtypes = [
        ctypes.c_char_p, # name
        ctypes.c_char_p, # json
        ctypes.c_void_p, # safe_data
        ctypes.c_size_t, # safe_len
        ctypes.POINTER(ctypes.c_size_t) # out_len
    ]
    lib.nncc_compile.restype = ctypes.c_void_p # Returns char* (but c_void_p prevents auto-conversion to string/int)
    
    lib.nncc_free.argtypes = [ctypes.c_void_p]
    lib.nncc_free.restype = None
    
    return lib

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
    Returns: (json_bytes, safetensors_bytes)
    """
    model.eval()
    
    # Single pass: extract layers and track shapes
    layers = []
    input_shape = list(sample_input.shape)
    prev_output = "input"
    current_shape = input_shape
    
    for name, module in model.named_modules():
        if name == "" or isinstance(module, (nn.Sequential, nn.ModuleList, nn.ModuleDict)):
            continue
        
        layer = _get_layer_info(name, module, current_shape)
        if layer:
            layer["inputs"] = [prev_output]
            layers.append(layer)
            prev_output = layer["name"]
            current_shape = layer["output_shape"]
    
    # Resolve flatten shapes (requires second dimension to be computed)
    for layer in layers:
        if layer["op"] == "flatten" and layer["output_shape"][1] == -1:
            idx = layers.index(layer)
            if idx > 0:
                prev_shape = layers[idx - 1]["output_shape"]
                flat_size = 1
                for d in prev_shape[1:]:
                    flat_size *= d
                layer["output_shape"] = [prev_shape[0], flat_size]
    
    # Build final model definition
    model_def = {
        "name": output_name,
        "inputs": [{"name": "input", "dtype": "float32", "shape": input_shape}],
        "outputs": [{"name": prev_output, "dtype": "float32", "shape": current_shape}],
        "layers": layers
    }
    
    json_str = json.dumps(model_def)
    
    # Export weights
    tensors = {k: v for k, v in model.state_dict().items()}
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
        # Provide diagnostic information for debugging
        json_preview = json_bytes[:500].decode('utf-8', errors='replace')
        raise RuntimeError(
            f"nncc compilation failed.\n"
            f"  Model name: {name}\n"
            f"  JSON preview (first 500 chars):\n{json_preview}..."
        )

        
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
