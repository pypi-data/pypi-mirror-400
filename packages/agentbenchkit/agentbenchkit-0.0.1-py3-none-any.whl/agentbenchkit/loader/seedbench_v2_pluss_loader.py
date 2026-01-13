import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("SEED-Bench-2-Plus")
class SEEDBench2Plus(BaseDatasetLoader):
    """Loads the 'doolayer/SEED-Bench-2-Plus' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'doolayer/SEED-Bench-2-Plus' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("doolayer/SEED-Bench-2-Plus", split="test")
        except Exception as e:
            logger.error("Failed to load 'doolayer/SEED-Bench-2-Plus': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the SEED-Bench-2-Plus dataset."""
        example = self.dataset[idx]
        question = example["question"] + "\n\n"
        question += f"A. {example['choice_A']}\n"
        question += f"B. {example['choice_B']}\n"
        question += f"C. {example['choice_C']}\n"
        question += f"D. {example['choice_D']}\n"
        # question += "Answer with the option's letter from the given choices directly."

        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["answer"],
            "task_name": example["question_image_type"],  # Dataset has no specific category field
            "sample_id": f"seed_bench_v2_plus_{idx}",
        }
