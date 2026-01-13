import logging
from typing import Any

from datasets import load_dataset, concatenate_datasets
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("HallusionBench")
class HallusionBench(BaseDatasetLoader):
    """Loads the 'lmms-lab/HallusionBench' dataset from the Hugging Face hub."""

    CONFIGS = ["image", "non_image"]
    def __init__(self):
        try:
            logger.info("Loading 'lmms-lab/HallusionBench'...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            dataset_image = load_dataset("lmms-lab/HallusionBench", split="image")
            dataset_non_image = load_dataset("lmms-lab/HallusionBench", split="non_image")

            self.dataset = concatenate_datasets([dataset_image, dataset_non_image])
        except Exception as e:
            logger.error("Failed to load 'lmms-lab/HallusionBench': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the HallusionBench dataset."""
        example = self.dataset[idx]
        question = example["question"] # + '\nPlease answer yes or no.'

        if int(example["gt_answer"]) == 1:
            answer = "yes"
        else:
            answer = "no"
        subcategory = example["subcategory"]
        set_id = example["set_id"]
        figure_id = example["figure_id"]
        question_id = example["question_id"]
        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": answer,
            "task_name": example["sample_note"],  # Dataset has no specific category field
            "sample_id": f"hallusionbench_{subcategory}_{set_id}_{figure_id}_{question_id}_{idx}",
        }
