import json
import os
import dotenv

dotenv.load_dotenv()
memory_file_path = os.getenv("MEMORY_FILE_PATH")

memories = json.load(open(memory_file_path, "r"))

for memory in memories:
    if memory["embedding"] is not None:
        del memory["embedding"]

with open(memory_file_path, "w") as f:
    json.dump(memories, f, indent=2)

