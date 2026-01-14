import os
import requests
from .config import MODEL_DIR, MODEL_PATH

# Live GitHub Release URL
MODEL_URL = "https://github.com/NotShubham1112/pixel-ai/releases/download/v0.1.0/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"

def download_model_if_needed():
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_DIR, exist_ok=True)
        print(f"Downloading Pixel-AI model from {MODEL_URL}...")
        try:
            r = requests.get(MODEL_URL, stream=True, timeout=30)
            r.raise_for_status()
            
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0
            
            with open(MODEL_PATH, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            done = int(50 * downloaded / total_size)
                            print(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB", end="")
            
            print("\nDownload complete!")
        except Exception as e:
            if os.path.exists(MODEL_PATH):
                os.remove(MODEL_PATH)
            print(f"\nError downloading model: {e}")
            print("Please check your internet connection and the MODEL_URL in utils.py")
    else:
        print(f"Model already exists at {MODEL_PATH}")
