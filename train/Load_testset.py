from datasets import load_dataset
import os

# Login using e.g. `huggingface-cli login` to access this dataset
ds = load_dataset("prithivMLmods/Human-vs-NonHuman")

# Сохраняем каждый сплит в отдельный CSV файл внутри папки "output_data"
output_dir = "output_data"
os.makedirs(output_dir, exist_ok=True)

for split in ds.keys():
    ds[split].to_csv(os.path.join(output_dir, f"{split}.csv"), index=False)