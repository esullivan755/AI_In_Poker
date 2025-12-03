# run only after running download_pokerbench.py
import os
import json
import random

RAW_PATH = "data/raw/train.jsonl"

# load random PokerBench episode and print key fields
def load_random_sample(path):
    with open(path, "r") as f:
        lines = f.readlines()
    return json.loads(random.choice(lines))

def main():
    sample = load_random_sample(RAW_PATH)

    for k, v in sample.items():
        print(f"{k}:\n{v}\n{'-'*40}")

if __name__ == "__main__":
    main()
