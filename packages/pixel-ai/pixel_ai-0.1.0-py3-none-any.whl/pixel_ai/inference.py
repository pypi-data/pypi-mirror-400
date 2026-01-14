from llama_cpp import Llama
from .config import MODEL_PATH, MAX_TOKENS, TEMPERATURE

def run_llm():
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Please run 'pixel-ai install' first.")
        return

    model = Llama(model_path=MODEL_PATH)
    print("Pixel-AI LLM ready. Type your prompt (Ctrl+C to exit).")

    try:
        while True:
            prompt = input("\nYou: ")
            output = model(prompt, max_tokens=MAX_TOKENS, temperature=TEMPERATURE)
            print("Pixel-AI:", output['choices'][0]['text'].strip())
    except KeyboardInterrupt:
        print("\nExiting Pixel-AI...")
