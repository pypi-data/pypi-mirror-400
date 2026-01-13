import logging
from typing import Any

from datasets import load_dataset

from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("CVBench")
class CVBenchLoader(BaseDatasetLoader):
    """Loads the CV-Bench dataset from the Hugging Face hub."""

    def __init__(self):  # Added **kwargs to ignore unused args
        try:
            cv_bench = load_dataset("nyu-visionx/CV-Bench")
            self.dataset = cv_bench["test"]
        except Exception as e:
            logger.error("Failed to load 'nyu-visionx/CV-Bench' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the CV-Bench dataset."""
        example = self.dataset[idx]

        image = example["image"]  # Already a PIL Image
        question = example["prompt"]
        correct_answer = example["answer"]
        task_name = example["task"]
        sample_id = f"cvbench_{idx}"  # Add prefix

        return {
            "image": [image],
            "question": question,
            "correct_answer": correct_answer,
            "task_name": task_name,
            "sample_id": sample_id,
        }
