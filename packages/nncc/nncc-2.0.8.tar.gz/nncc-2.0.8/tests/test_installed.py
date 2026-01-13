import nncc
import torch
import torch.nn as nn
import subprocess
import os

def test_installed():
    print("Testing INSTALLED nncc package...")
    print(f"nncc version: {nncc.__version__}")
    print(f"nncc path: {nncc.__file__}")

    model = nn.Sequential(nn.Linear(4, 2))
    input_data = torch.randn(1, 4)
    
    try:
        c_code = nncc.compile(model, input_data)
        print(f"Success! Generated {len(c_code)} bytes.")
    except Exception as e:
        print(f"FAILED: {e}")
        return False
        
    return True

if __name__ == "__main__":
    if test_installed():
        print("Installed package verification passed.")
    else:
        exit(1)
