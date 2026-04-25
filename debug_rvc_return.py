import os
import torch
import numpy as np
from rvc_python.infer import RVCInference

# Initialize
device = "cuda:0" if torch.cuda.is_available() else "cpu"
rvc = RVCInference(device=device)
model_path = "rvc_models/arisu.pth"
rvc.load_model(model_path)

# Mock a call to see what audio_opt looks like
# We'll use a dummy input if we don't have one, but we likely have temp files.
print(f"Current parameters: f0up_key={rvc.f0up_key}, f0method={rvc.f0method}")

# Test with internal call
try:
    # This is what infer_file does internally
    model_info = rvc.models[rvc.current_model]
    file_index = model_info.get("index", "")
    
    print("Calling vc_single...")
    # Using a fake path just to see the catch block or return type if it gets far
    # Actually, let's look at the return of a successful pipeline call if possible.
    # But wait, the source says 'return audio_opt' or 'return info, (None, None)'
    # If it fails, it returns a TUPLE: (info, (None, None))
    # That explains the error! 'tuple' object has no attribute 'dtype'
except Exception as e:
    print(f"Error: {e}")
