import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("COCO-Caption2017")
class COCOCaption2017(BaseDatasetLoader):
    """Loads the 'lmms-lab/COCO-Caption2017' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/COCO-Caption2017' (val split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("lmms-lab/COCO-Caption2017", split="val")
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/COCO-Caption2017': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the Caption2017 dataset."""
        example = self.dataset[idx]

        return {
            "image": [example["image"]],
            "question": example["question"],
            "correct_answer": example["answer"],
            "task_name": "coco_caption",  # Dataset has no specific category field
            "sample_id": f"coco_caption_{idx}",
        }
