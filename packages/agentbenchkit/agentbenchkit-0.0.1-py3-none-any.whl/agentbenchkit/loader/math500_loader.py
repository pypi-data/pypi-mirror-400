from typing import Any

from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader
from datasets import load_dataset

@register_loader("Math-500")
class MathLoader(BaseDatasetLoader):
    def __init__(self):
        try:
            math = load_dataset("HuggingFaceH4/MATH-500")
            self.dataset = math["test"]
        except Exception as e:
            print(f"Failed to load 'Math' from Hugging Face: {e}")
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        example = self.dataset[idx]
        question = example["problem"]
        correct_answer = example["answer"]
        task = example["subject"]
        level = example["level"]
        text = f"{task}_{level}"

        return {
            "image":"",
            "question": question,
            "correct_answer": correct_answer,
            "task_name": text,
            "sample_id": f"Math_{idx}"
        }
