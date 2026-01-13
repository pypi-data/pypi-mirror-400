#!/usr/bin/env python3
"""
test_nncc.py - End-to-end test for nncc

This script:
1. Creates a simple PyTorch model
2. Exports it to .safetensors + .nnmodel format
3. Runs nncc to generate C code
4. Compiles the generated C code
5. Runs inference in both PyTorch and C
6. Compares outputs to verify correctness

Requirements:
    pip install torch safetensors numpy
"""

import os
import sys
import json
import struct
import subprocess
import numpy as np

try:
    import torch
    import torch.nn as nn
    from safetensors.torch import save_file
except ImportError:
    print("Please install required packages:")
    print("  pip install torch safetensors numpy")
    sys.exit(1)


# =============================================================================
# Export Function (same as README)
# =============================================================================

def export_to_nncc(model, sample_input, output_name="model"):
    """Export PyTorch model to nncc format."""
    model.eval()
    save_file(model.state_dict(), f"{output_name}.safetensors")
    
    layers = []
    input_shape = list(sample_input.shape)
    prev_layer = "input"
    current_shape = input_shape
    
    for name, module in model.named_modules():
        if name == "" or isinstance(module, (nn.Sequential, nn.ModuleList)):
            continue
        
        layer = {"name": name.replace(".", "_"), "inputs": [prev_layer]}
        
        if isinstance(module, nn.Linear):
            layer["op"] = "gemm"
            layer["weights"] = {"weight": f"{name}.weight"}
            if module.bias is not None:
                layer["weights"]["bias"] = f"{name}.bias"
            current_shape = [current_shape[0], module.out_features]
            layer["output_shape"] = current_shape
        elif isinstance(module, nn.ReLU):
            layer["op"] = "relu"
        elif isinstance(module, nn.Softmax):
            layer["op"] = "softmax"
            layer["axis"] = -1
        elif isinstance(module, nn.Flatten):
            layer["op"] = "flatten"
            flat_size = 1
            for d in current_shape[1:]:
                flat_size *= d
            current_shape = [current_shape[0], flat_size]
            layer["output_shape"] = current_shape
        else:
            continue
        
        layers.append(layer)
        prev_layer = layer["name"]
    
    model_def = {
        "name": output_name,
        "inputs": [{"name": "input", "dtype": "float32", "shape": input_shape}],
        "outputs": [{"name": prev_layer, "dtype": "float32", "shape": current_shape}],
        "layers": layers
    }
    
    with open(f"{output_name}.nnmodel", "w") as f:
        json.dump(model_def, f, indent=2)
    
    return model_def


# =============================================================================
# Test Runner
# =============================================================================

def create_test_model():
    """Create a simple MLP for testing."""
    model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(784, 128),
        nn.ReLU(),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Linear(64, 10),
        nn.Softmax(dim=-1)
    )
    return model


def generate_test_wrapper(model_name, input_size, output_size):
    """Generate a C test wrapper that reads input and writes output."""
    return f'''
#include <stdio.h>
#include <stdlib.h>

#define MODEL_IMPLEMENTATION
#include "{model_name}.c"

int main(int argc, char** argv) {{
    if (argc != 3) {{
        fprintf(stderr, "Usage: %s <input.bin> <output.bin>\\n", argv[0]);
        return 1;
    }}
    
    float input[{input_size}];
    float output[{output_size}];
    
    // Read input
    FILE* fin = fopen(argv[1], "rb");
    if (!fin) {{ perror("Cannot open input"); return 1; }}
    fread(input, sizeof(float), {input_size}, fin);
    fclose(fin);
    
    // Run inference
    model_inference(input, output);
    
    // Write output
    FILE* fout = fopen(argv[2], "wb");
    if (!fout) {{ perror("Cannot open output"); return 1; }}
    fwrite(output, sizeof(float), {output_size}, fout);
    fclose(fout);
    
    return 0;
}}
'''


def run_test():
    """Run the complete end-to-end test."""
    print("=" * 60)
    print("nncc End-to-End Test")
    print("=" * 60)
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # Find nncc executable
    if os.name == 'nt':
        nncc_exe = os.path.join(project_dir, "nncc.exe")
    else:
        nncc_exe = os.path.join(project_dir, "nncc")
    
    if not os.path.exists(nncc_exe):
        print(f"ERROR: nncc executable not found at {nncc_exe}")
        print("Please build nncc first:")
        print("  gcc -Wall -std=c99 -O2 -o nncc src/*.c -lm")
        return False
    
    # Use a test subdirectory
    test_dir = os.path.join(project_dir, "test_output")
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)
    print(f"\nTest directory: {test_dir}")
    
    # Step 1: Create and export model
    print("\n[1/6] Creating test model...")
    model = create_test_model()
    sample_input = torch.randn(1, 1, 28, 28)
    model_def = export_to_nncc(model, sample_input, "test_model")
    print(f"  - Model: {len(list(model.modules()))-1} layers")
    print(f"  - Input shape: {sample_input.shape}")
    
    # Step 2: Run PyTorch inference
    print("\n[2/6] Running PyTorch inference...")
    test_input = torch.randn(1, 1, 28, 28)
    with torch.no_grad():
        pytorch_output = model(test_input).numpy().flatten()
    print(f"  - PyTorch output: [{pytorch_output[0]:.6f}, {pytorch_output[1]:.6f}, ...]")
    
    # Step 3: Generate C code with nncc
    print("\n[3/6] Generating C code with nncc...")
    result = subprocess.run(
        [nncc_exe, "test_model.safetensors", "test_model.nnmodel", "-o", "test_model.c", "-v"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR: nncc failed:\n{result.stderr}\n{result.stdout}")
        return False
    print(f"  - Generated: test_model.c")
    
    # Step 4: Create test wrapper and compile
    print("\n[4/6] Compiling generated code...")
    input_size = int(np.prod(sample_input.shape))
    output_size = pytorch_output.shape[0]
    
    wrapper_code = generate_test_wrapper("test_model", input_size, output_size)
    with open("test_wrapper.c", "w") as f:
        f.write(wrapper_code)
    
    compile_result = subprocess.run(
        ["gcc", "-O2", "-o", "test_runner.exe" if os.name == 'nt' else "test_runner", "test_wrapper.c", "-lm"],
        capture_output=True, text=True
    )
    if compile_result.returncode != 0:
        print(f"  ERROR: Compilation failed:\n{compile_result.stderr}")
        # Show generated code for debugging
        print("\n  Generated C code snippet:")
        with open("test_model.c") as f:
            lines = f.readlines()[:50]
            for i, line in enumerate(lines, 1):
                print(f"  {i:3}: {line.rstrip()}")
        return False
    print("  - Compiled: test_runner")
    
    # Step 5: Run C inference
    print("\n[5/6] Running C inference...")
    
    # Write input as binary
    test_input_flat = test_input.numpy().flatten()
    with open("input.bin", "wb") as f:
        for val in test_input_flat:
            f.write(struct.pack('f', val))
    
    runner = "test_runner.exe" if os.name == 'nt' else "./test_runner"
    run_result = subprocess.run(
        [runner, "input.bin", "output.bin"],
        capture_output=True, text=True
    )
    if run_result.returncode != 0:
        print(f"  ERROR: C inference failed:\n{run_result.stderr}")
        return False
    
    # Read output
    with open("output.bin", "rb") as f:
        c_output = np.frombuffer(f.read(), dtype=np.float32)
    print(f"  - C output: [{c_output[0]:.6f}, {c_output[1]:.6f}, ...]")
    
    # Step 6: Compare outputs
    print("\n[6/6] Comparing outputs...")
    max_diff = np.max(np.abs(pytorch_output - c_output))
    mean_diff = np.mean(np.abs(pytorch_output - c_output))
    
    print(f"  - Max difference: {max_diff:.8f}")
    print(f"  - Mean difference: {mean_diff:.8f}")
    
    # Allow small numerical differences
    tolerance = 1e-5
    if max_diff < tolerance:
        print(f"\n✓ TEST PASSED: Outputs match within tolerance ({tolerance})")
        return True
    else:
        print(f"\n✗ TEST FAILED: Outputs differ more than tolerance ({tolerance})")
        print("\nPyTorch output:", pytorch_output)
        print("C output:", c_output)
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
