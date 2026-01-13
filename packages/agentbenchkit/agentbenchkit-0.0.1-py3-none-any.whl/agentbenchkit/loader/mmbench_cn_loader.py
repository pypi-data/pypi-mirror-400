import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MMBench_CN")
class MMBenchCN(BaseDatasetLoader):
    """Loads the 'lmms-lab/MMBench_CN' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/MMBench_CN' (dev split)...")
            self.dataset =load_dataset("lmms-lab/MMBench_CN", "default", split="dev")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/MMBench_CN': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MMBench_CN dataset."""
        example = self.dataset[idx]

        question_temp = example["question"]
        hint = example["hint"]
        image = example["image"]
        category = example["category"]
        l2_category = example["L2-category"]

        if image is None:
            images = []
        else:
            images = [image]

        options = ""
        if example["A"] != "nan":
            options += f"A. {example['A']}\n"
        if example["B"] != "nan":
            options += f"B. {example['B']}\n"
        if example["C"] != "nan":
            options += f"C. {example['C']}\n"
        if example["D"] != "nan":
            options += f"D. {example['D']}\n"
            
        if hint == "nan":
            question =  f"{question_temp}\n\n{options} \n"
        else:
            question =  f"{hint}\n{question_temp}\n\n{options} \n"

        answer = example["answer"]

        return {
            "image": images,
            "question": question,
            "correct_answer": answer,
            "task_name": f"{category}|{l2_category}",
            "sample_id": f"mmbench_cn_{idx}",
        }
