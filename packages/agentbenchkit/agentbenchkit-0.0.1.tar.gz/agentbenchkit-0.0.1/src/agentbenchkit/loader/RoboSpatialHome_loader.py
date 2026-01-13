from huggingface_hub.constants import HF_TOKEN_PATH

from .base import BaseDatasetLoader
from agentbenchkit.loader import register_loader
import logging
logger = logging.getLogger(__name__)
from datasets import load_dataset, concatenate_datasets


@register_loader("RoboSpatial")
class RoboSpatialLoader(BaseDatasetLoader):
    CONFIGS =  ["context", "compatibility", "configuration"]

    def __init__(self):
        logger.info("Loading RoboSpatial dataset...")
        all_datasets = []
        for config in self.CONFIGS:
            logger.info(f"Loading RoboSpatial subtask: {config}")
            ds = load_dataset("chanhee-luke/RoboSpatial-Home", split= config)
            all_datasets.append(ds)
        self.dataset = concatenate_datasets(all_datasets)
        logger.info(f"Successfully loaded RoboSpatial dataset with {len(self.dataset)} samples.")

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        example = self.dataset[idx]

        return {
            "image": [example["img"]],
            "question": example['question'],
            "correct_answer": example["mask"],
            "task_name": example['category'],
            "sample_id": f"robo_spatial_{idx}",
        }