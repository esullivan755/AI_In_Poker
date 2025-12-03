import os
from datasets import load_dataset
from tqdm import tqdm
import json

DATA_DIR = os.path.join("data", "raw")
os.makedirs(DATA_DIR, exist_ok=True)

# save huggingface dataset json
def save_jsonl(dataset_split, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in tqdm(dataset_split, desc=f"Saving {path}"):
            f.write(json.dumps(item) + "\n")

def main():
    dataset_name = "RZ412/PokerBench"
    dataset = load_dataset(dataset_name)

    for split in dataset.keys():
        out_path = os.path.join(DATA_DIR, f"{split}.jsonl")
        save_jsonl(dataset[split], out_path)

if __name__ == "__main__":
    main()
