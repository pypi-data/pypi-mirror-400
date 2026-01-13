import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MathVision")
class MathVision(BaseDatasetLoader):
    """Loads the 'MathLLMs/MathVision' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'MathLLMs/MathVision' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("MathLLMs/MathVision", split="test")
        except Exception as e:
            logger.error("Failed to load 'MathLLMs/MathVision': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the  dataset."""
        example = self.dataset[idx]

        options = example["options"]
        question_temp = example["question"]

        if len(options)  == 0:
            question = question_temp + "\nAnswer the question using a single word or phrase."
        else:
            ids = [chr(65 + i) for i in range(len(options))]
            options = [f"{id}. {option}" for id, option in zip(ids, options)]
            question =  f"{question_temp}\n\n{'\n'.join(options)} \nAnswer with the option's letter from the given choices directly."

        answer = example["answer"]
        image = example["decoded_image"]
        task_name = example["subject"]

        return {
            "image": [image],
            "question": question,
            "correct_answer": answer,
            "task_name": task_name,  # Dataset has no specific category field
            "sample_id": f"mathvision_{idx}",
        }
