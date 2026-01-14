import os

BASE_DIR = os.path.expanduser("~/.pixel_ai")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_NAME = "pixel_ai_gguf.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

# LLM parameters
MAX_TOKENS = 256
TEMPERATURE = 0.7
