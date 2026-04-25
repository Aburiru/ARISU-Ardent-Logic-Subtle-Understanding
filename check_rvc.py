import sys
import torch
import os
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RVC_Check")

print(f"Python version: {sys.version}")
print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")

try:
    from rvc_python.infer import RVCInference
    print("✅ rvc-python is installed.")
except ImportError:
    print("❌ rvc-python is NOT installed.")
    sys.exit(1)

model_path = "rvc_models/arisu.pth"
index_path = "rvc_models/arisu.index"

print(f"Model exists: {os.path.exists(model_path)}")
print(f"Index exists: {os.path.exists(index_path)}")

if os.path.exists(model_path):
    try:
        print("Attempting to initialize RVCInference...")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        rvc_inference = RVCInference(device=device)
        rvc_inference.load_model(model_path)
        print("✅ RVC Model loaded successfully!")
        
        # We won't run a full inference yet unless we have a sample file, 
        # but loading the model confirms the core dependencies are working.
    except Exception as e:
        print(f"❌ Failed to initialize RVC: {e}")
else:
    print("❌ Cannot test RVC: Model file missing.")
