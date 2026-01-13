import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("AI2D")
class AI2D(BaseDatasetLoader):
    """Loads the 'lmms-lab/ai2d' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/ai2d' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("lmms-lab/ai2d", split="test")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/ai2d': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the AI2D dataset."""
        example = self.dataset[idx]

        options = example["options"]
        ids = [chr(65 + i) for i in range(len(options))]
        options = [f"{id}. {option}" for id, option in zip(ids, options)]

        question_temp = example["question"]
        # question =  f"{question_temp}\n\n{'\n'.join(options)} \nAnswer with the option's letter from the given choices directly."
        question =  f"{question_temp}\n\n{'\n'.join(options)}"

        answer = ids[int(example["answer"])]

        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": answer,
            "task_name": "ai2d",  # Dataset has no specific category field
            "sample_id": f"ai2d_{idx}",
        }
