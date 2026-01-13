import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MMTBenchmark")
class MMTBenchmark(BaseDatasetLoader):
    """Loads the 'lmms-lab/MMT-Benchmark' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/MMT-Benchmark' (val split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("lmms-lab/MMT-Benchmark", split="val")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/MMT-Benchmark': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MMT-Benchmark dataset."""
        example = self.dataset[idx]

        question_temp = example["question"] + "\n\n"
        if example["A"] is not None:
            question_temp += f"A. {example['A']}\n"
        if example["B"] is not None:
            question_temp += f"B. {example['B']}\n"
        if example["C"] is not None:
            question_temp += f"C. {example['C']}\n"
        if example["D"] is not None:
            question_temp += f"D. {example['D']}\n"
        if example["E"] is not None:
            question_temp += f"E. {example['E']}\n"
        if example["F"] is not None:
            question_temp += f"F. {example['F']}\n"
        if example["G"] is not None:
            question_temp += f"G. {example['G']}\n"
        if example["H"] is not None:
            question_temp += f"H. {example['H']}\n"
        if example["I"] is not None:
            question_temp += f"I. {example['I']}\n"
        question =  question_temp # + "\nAnswer with the option's letter from the given choices directly."

        answer = example["answer"]

        category = example["category"]
        l2_category = example["l2-category"]

        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": answer,
            "task_name": f"{category}|{l2_category}",  # Dataset has no specific category field
            "sample_id": f"mmt_benchmark_{idx}",
        }
