import os
import json
from tqdm import tqdm

RAW_DIR = "data/raw"
OUT_DIR = "data/processed"
os.makedirs(OUT_DIR, exist_ok=True)

def convert_split(split_name):
    raw_path = os.path.join(RAW_DIR, f"{split_name}.jsonl")
    out_path = os.path.join(OUT_DIR, f"{split_name}.jsonl")

    if not os.path.exists(raw_path):
        return

    with open(raw_path, "r") as f_in, open(out_path, "w") as f_out:
        for line in tqdm(f_in, desc=f"{split_name}"):
            item = json.loads(line)

            instruction = item.get("instruction", "").strip()
            output = item.get("output", "").strip()

            new_item = {
                "input": instruction,
                "target": output
            }

            f_out.write(json.dumps(new_item) + "\n")

def main():
    possible_splits = ["train", "validation", "test"]

    for split in possible_splits:
        convert_split(split)

if __name__ == "__main__":
    main()
