from typing import Any

from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader
from datasets import load_dataset

@register_loader("Squad")
class SquadLoader(BaseDatasetLoader):
    def __init__(self):
        try:
            squad = load_dataset("rajpurkar/squad")
            self.dataset = squad["validation"]
        except Exception as e:
            print(f"Failed to load 'squad' from Hugging Face: {e}")
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        example = self.dataset[idx]
        context = example["context"]
        question = example["question"]
        correct_answer = example["answers"]["text"]
        task = example["title"]

        text = f"Given the context:{context}, answer the following question:{question}"

        return {
            "image":"",
            "question": text,
            "correct_answer": correct_answer,
            "task_name": task,
            "sample_id": f"Squad_{idx}"
        }