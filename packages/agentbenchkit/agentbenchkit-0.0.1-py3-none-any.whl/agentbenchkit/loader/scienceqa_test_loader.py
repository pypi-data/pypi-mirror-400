import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("ScienceQA_TEST")
class ScienceQATest(BaseDatasetLoader):
    """Loads the 'derek-thomas/ScienceQA' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'derek-thomas/ScienceQA' (test split)...")
            self.dataset =load_dataset("derek-thomas/ScienceQA", split="test")
        except Exception as e:
            logger.error("Failed to load 'derek-thomas/ScienceQA': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the ScienceQA dataset."""
        example = self.dataset[idx]

        options = example["choices"]
        question_temp = example["question"]
        hint = example["hint"]
        image = example["image"]
        category = example["category"]

        if image is None:
            images = []
        else:
            images = [image]

        ids = [chr(65 + i) for i in range(len(options))]
        options = [f"{id}. {option}" for id, option in zip(ids, options)]
        
        if hint == "":
            question =  f"{question_temp}\n\n{'\n'.join(options)}"
        else:
            question =  f"{hint}\n{question_temp}\n\n{'\n'.join(options)}"

        answer = ids[int(example["answer"])]

        return {
            "image": images,
            "question": question,
            "correct_answer": answer,
            "task_name": category,  # Dataset has no specific category field
            "sample_id": f"scienceqa_test_{idx}",
        }
