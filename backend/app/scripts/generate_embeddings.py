from app.services.embeddings import get_embedding
import json
import os
import dotenv

dotenv.load_dotenv()
memory_file_path = os.getenv("MEMORY_FILE_PATH")

memories = json.load(open(memory_file_path, "r"))

for memory in memories:
    if "embedding" not in memory:
        memory["embedding"] = get_embedding(memory["content"])

with open(memory_file_path, "w") as f:
    json.dump(memories, f, indent=2)



