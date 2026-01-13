import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("ERQA")
class ErqaBenchLoader(BaseDatasetLoader):
    """Loads the CV-Bench dataset from the Hugging Face hub."""

    def __init__(self):  # Added **kwargs to ignore unused args
        try:
            erqa = load_dataset("FlagEval/ERQA")
            self.dataset = erqa["test"]
        except Exception as e:
            logger.error("Failed to load 'FlagEval/ERQA' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the ERQA dataset."""
        example = self.dataset[idx]

        image = example["images"]  # Already a PIL Image
        question = example["question"]
        correct_answer = example["answer"]
        task_name = example["question_type"]
        sample_id = f"ERQA_{idx}"  # Add prefix

        return {
            "image": image,
            "question": question,
            "correct_answer": correct_answer,
            "task_name": task_name,
            "sample_id": sample_id,
        }


