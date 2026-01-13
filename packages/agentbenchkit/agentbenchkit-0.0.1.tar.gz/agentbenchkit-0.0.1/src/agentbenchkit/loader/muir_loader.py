import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MUIR")
class MuirBenchLoader(BaseDatasetLoader):
    """Loads the CV-Bench dataset from the Hugging Face hub."""

    def __init__(self):  # Added **kwargs to ignore unused args
        try:
            muir = load_dataset("MUIRBENCH/MUIRBENCH")
            self.dataset = muir["test"]
        except Exception as e:
            logger.error("Failed to load 'MUIRBENCH/MUIRBENCH' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MUIR dataset."""
        example = self.dataset[idx]
        task = example["task"]
        question = example["question"]
        options = example["options"]
        correct_answer = example["answer"]
        image = example["image_list"]

        option_list = ""
        for i,item in enumerate(options):
            letter = chr(ord('A') + i)
            option_list = option_list + f" {letter}.{item} "

        return {
            "image": image,
            "question": str(question) + option_list,
            "correct_answer": correct_answer,
            "task_name": task,
            "sample_id": f"MUIR_{idx}"
        }

