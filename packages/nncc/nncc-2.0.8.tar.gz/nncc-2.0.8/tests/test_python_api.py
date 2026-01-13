import os
import sys
import torch
import torch.nn as nn
import numpy as np
import subprocess

# Add project root to path to import nncc
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import nncc

def create_model():
    return nn.Sequential(
        nn.Flatten(),
        nn.Linear(10, 5),
        nn.ReLU(),
        nn.Linear(5, 2),
        nn.Softmax(dim=-1)
    )

def test_api():
    print("Testing nncc Python API...")
    
    # 1. Create model
    model = create_model()
    sample_input = torch.randn(1, 1, 10) # 1x1x10 input (flattened to 10)
    
    # 2. Compile to C string
    print("\n[1/3] Compiling model to C code string...")
    try:
        c_code = nncc.compile(model, sample_input, name="test_api_model")
        print(f"  Success! Generated {len(c_code)} bytes of C code.")
        if "void test_api_model_inference" not in c_code:
            print("  ERROR: Generated code missing inference function")
            return False
    except Exception as e:
        print(f"  ERROR: Compilation failed: {e}")
        return False
        
    # 3. Save to file and compile with GCC
    print("\n[2/3] Verifying generated code validity...")
    with open("test_api_gen.c", "w") as f:
        f.write(c_code)
        
    wrapper_code = """
    #include <stdio.h>
    #define TEST_API_MODEL_IMPLEMENTATION
    #include "test_api_gen.c"
    
    int main() {
        float input[10] = {0};
        float output[2] = {0};
        test_api_model_inference(input, output);
        printf("%f %f\\n", output[0], output[1]);
        return 0;
    }
    """
    
    with open("test_api_wrapper.c", "w") as f:
        f.write(wrapper_code)
        
    # Compile
    cmd = ["gcc", "-O2", "-o", "test_api_runner.exe", "test_api_wrapper.c", "-lm"]
    print(f"  Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: GCC Compilation failed:\n{result.stderr}")
        return False
        
    print("  Success! Code compiled.")
    
    # 4. Run it
    print("\n[3/3] Running inference...")
    result = subprocess.run(["./test_api_runner.exe"], capture_output=True, text=True)
    if result.returncode != 0:
         print(f"  ERROR: Execution failed: {result.stderr}")
         return False
         
    print(f"  Output: {result.stdout.strip()}")
    print("\nAPI Test PASSED!")
    return True

if __name__ == "__main__":
    if test_api():
        sys.exit(0)
    else:
        sys.exit(1)
