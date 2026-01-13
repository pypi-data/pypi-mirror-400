import logging
from typing import Any

from datasets import load_dataset
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("MathVista")
class MathVista(BaseDatasetLoader):
    """Loads the 'AI4Math/MathVista' dataset from the Hugging Face hub."""

    def __init__(self):
        try:
            logger.info("Loading 'AI4Math/MathVista' (testmini split)...")
            # The dataset only has a 'test' split
            # load_dataset("lmms-lab/RealWorldQA")
            self.dataset =load_dataset("AI4Math/MathVista", split="testmini")
        except Exception as e:
            logger.error("Failed to load 'AI4Math/MathVista': %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the MathVista dataset."""
        example = self.dataset[idx]
        question_temp = example["question"]
        task_name = example["metadata"]["category"] + "-" + example["question_type"]

        question = ""
        
        if example["question_type"] == "free_form":
            answer = example["answer"]
            # if example["answer_type"] == "integer":
                
            # elif example["answer_type"] == "float":
            
            # elif example["answer_type"] == "text":
            if example["metadata"]["language"] == "english":
                question = question_temp + "\nAnswer the question using a single word or phrase."
            elif example["metadata"]["language"] == "chinese":
                question = question_temp + "\n使用一个词或短语回答."

        elif example["question_type"] == "multi_choice":
            options = example["choices"]
            answer = example["answer"]
            id = options.index(answer)
            ids = [chr(65 + i) for i in range(len(options))]
            options = [f"{id}. {option}" for id, option in zip(ids, options)]
            if example["metadata"]["language"] == "english":
                question =  f"{question_temp}\n\n{'\n'.join(options)} \nAnswer with the option's letter from the given choices directly."
            elif example["metadata"]["language"] == "chinese":
                question =  f"{question_temp}\n\n{'\n'.join(options)} \n直接回答选定选项的字母."
            answer = ids[id]

        return {
            "image": [example["decoded_image"]],
            "question": question,
            "correct_answer": answer,
            "task_name": task_name,  # Dataset has no specific category field
            "sample_id": f"mathvista_{idx}",
        }
