from .base import BaseDatasetLoader
from agentbenchkit.loader import register_loader
from datasets import load_dataset, concatenate_datasets
import logging

logger = logging.getLogger(__name__)

@register_loader("RefSpatialBench")
class RefSpatialBenchLoader(BaseDatasetLoader):
    CONFIGS = [
        "location", "placement","unseen"
    ]
    def __init__(self):
        logger.info("Loading RefSpatialBench dataset...")
        all_datasets = []
        try:
            for config in self.CONFIGS:
                logger.info(f"Loading RefSpatialBench subtask: {config}")
                ds = load_dataset("BAAI/RefSpatial-Bench", split= config)
                all_datasets.append(ds)
            self.dataset = concatenate_datasets(all_datasets)
            logger.info(f"Successfully loaded RefSpatialBench dataset with {len(self.dataset)} samples.")
        except Exception as e:
            logger.error("Failed to load RefSpatialBench dataset: %s", e)
            raise

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        example = self.dataset[idx]
        prompt = example["prompt"]
        suffix = example["suffix"]
        question = prompt + suffix

        return {
            "image": [example["image"]],
            "question": question,
            "correct_answer": example["mask"],
            "task_name": "difficulty_"+str(example["step"]),
            "sample_id": f"refspatialbench_{idx}",
        }
