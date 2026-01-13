import logging
from typing import Any

from datasets import load_dataset

from . import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MMBench_EN")
class MMBenchEnLoader(BaseDatasetLoader):
    """Loads the MMBenchEn dataset from the Hugging Face hub."""

    def __init__(self, ):  # Added **kwargs to ignore unused args
        try:
            MMBenchEn_dataset = load_dataset("lmms-lab/MMBench_EN")
            self.dataset = MMBenchEn_dataset["dev"]
        except Exception as e:
            logger.error("Failed to load 'MMBenchEn/MMBenchEn' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MMBenchEn dataset."""
        example = self.dataset[idx]

        # if example["image2"] is None:
        image = example["image"]  # Already a PIL Image
        question = example["question"]
        category = example["category"]
        l2category = example["l2-category"]
        hint = example["hint"]

        options_str = ""
        if example["A"] != "nan":
            options_str += f"A.{example['A']}\n"
        if example["B"] != "nan":
            options_str += f"B.{example['B']}\n"
        if example["C"] != "nan":
            options_str += f"C.{example['C']}\n"
        if example["D"] != "nan":
            options_str += f"D.{example['D']}\n"
        if hint == "nan":
            question = f"{question}\n{options_str}"
        else:
            question = f"{hint}\n{question}\n{options_str}"
        correct_answer = example["answer"]
        
        sample_id = f"MMBenchEn_{idx}"  # Add prefix
        task_name = f"{category}|{l2category}"
        return {
            "image": [image],
            "question": question,
            "correct_answer": correct_answer,
            "task_name": task_name,
            "sample_id": sample_id,
        }
