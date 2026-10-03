import os 
from transformers import AutoTokenizer

class Tokenizer:
    def __init__(self, model_name: str = "gemma-4-26b-a4b-qat"):
        self.local_model_path = os.path.join(os.path.dirname(__file__), "models", model_name)
        if os.path.exists(self.local_model_path):
            print(f"Loading tokenizer from {self.local_model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.local_model_path, local_files_only=True)
        else:
            raise FileNotFoundError(f"Tokenizer model file not found at {self.local_model_path}. Please ensure the tokenizer model is available.")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a given text."""
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)