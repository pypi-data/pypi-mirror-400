import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MathVerse_Testmini")
class MathVerse(BaseDatasetLoader):
    """Loads the 'AI4Math/MathVerse' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'AI4Math/MathVerse' (test split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset = load_dataset("AI4Math/MathVerse", "testmini", split="testmini")
        except Exception as e:
            logger.error("Failed to load 'AI4Math/MathVerse': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MathVerse dataset."""
        example = self.dataset[idx]
        # options = example["options"]
        task_type = example["problem_version"]
        metadata = example["metadata"]
        subject = metadata.get("subject", "unknown")

        image_list = []
        if task_type != "Text Only":
            image_list.append(example["image"])
        
        question = ""
        if task_type != "Vision Only":
            question_temp = example["question"]
            question =  f"{question_temp} \nAnswer with the option's letter from the given choices directly."

        answer = example["answer"]

        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": answer,
            "task_name": f"{task_type}|{subject}",  # Dataset has no specific category field
            "sample_id": f"mathverse_{idx}",
        }
