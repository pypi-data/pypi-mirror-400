import logging
from typing import Any

from datasets import load_dataset, concatenate_datasets

from .base import BaseDatasetLoader
from agentbenchkit.loader import register_loader

logger = logging.getLogger(__name__)

@register_loader("Blink")
class BlinkBenchLoader(BaseDatasetLoader):
    """Loads the Blink-Bench dataset from the Hugging Face hub."""
    CONFIGS = [
        "Art_Style", "Counting", "Forensic_Detection", "Functional_Correspondence",
        "IQ_Test", "Jigsaw", "Multi-view_Reasoning", "Object_Localization",
        "Relative_Depth", "Relative_Reflectance", "Semantic_Correspondence",
        "Spatial_Relation", "Visual_Correspondence", "Visual_Similarity"
    ]
    def __init__(self):  # Added **kwargs to ignore unused args
        try:
            all_datasets = []
            for config in self.CONFIGS:
                logger.info(f"Loading BLINK subtask: {config}")
                ds = load_dataset("BLINK-Benchmark/BLINK", config, split="test")
                # 添加子任务名称列
                all_datasets.append(ds)

            # 合并所有子任务
            self.dataset = concatenate_datasets(all_datasets)
            logger.info(f"Successfully loaded BLINK val set with {len(self.dataset)} samples.")
        except Exception as e:
            logger.error("Failed to load BLINK-Benchmark/BLINK from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx : int) -> dict[str, Any]:
        """Fetches and maps a sample from the Blink dataset."""
        example = self.dataset[idx]
        image_list = []
        for i in range(1,5):
            img_key = f"image_{i}"
            if img_key not in example or example[img_key] is None:
                break
            image_list.append(example[img_key])
        task = example["sub_task"]
        question = example["prompt"]
        correct_answer = example["answer"]

        return {
            "image": image_list,
            "question": str(question) ,
            "correct_answer": correct_answer,
            "task_name": task,
            "sample_id": f"Blink_{idx}"
        }