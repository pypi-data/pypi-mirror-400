import base64
import io
import logging
from typing import Any

from datasets import load_dataset
from PIL import Image
from agentbenchkit.loader import register_loader
from .base import BaseDatasetLoader

logger = logging.getLogger(__name__)

@register_loader("EmbSpatialBench")
class EmbSpatialBenchLoader(BaseDatasetLoader):
    """Loads the Phineas476/EmbSpatial-Bench dataset."""

    def __init__(self):
        try:
            # --- THIS IS THE FIX ---
            # The repository contains multiple .json files with different schemas.
            # We must explicitly tell it which file to use for our "test" split
            # to avoid the schema conflict error.
            data_files = {"test": "embspatial_bench.json"}

            self.dataset = load_dataset(
                "Phineas476/EmbSpatial-Bench", data_files=data_files, split="test"
            )
            # --- END FIX ---

        except Exception as e:
            logger.error("Failed to load 'Phineas476/EmbSpatial-Bench' from Hugging Face: %s", e)
            raise

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        """Fetches and maps a sample from the EmbSpatial-Bench dataset."""
        example = self.dataset[idx]

        # 1. Handle the Base64 image
        image_b64_string = example["image"]
        image_bytes = base64.b64decode(image_b64_string)
        image = Image.open(io.BytesIO(image_bytes))

        # 2. Get the question, stripping any extra quotes
        question_text: str = example["question"].strip("'\"")

        # 3. Get the answer options (list of strings)
        options_list: list[str] = example["answer_options"]

        # 4. Get the correct answer *letter*
        # 'answer' is an integer index (e.g., 0, 1, 2, 3)
        correct_answer_index: int = example["answer"]
        options_map = ["A", "B", "C", "D"]
        correct_answer: str = options_map[correct_answer_index]

        # 5. Get the task name ('relation')
        task_name: str = example["relation"]

        # 6. Get the unique ID
        sample_id: str = example["question_id"]

        # 7. Combine the question and options with A/B/C/D prefixes
        formatted_options = [
            f"(A) {options_list[0]}",
            f"(B) {options_list[1]}",
            f"(C) {options_list[2]}",
            f"(D) {options_list[3]}",
        ]
        full_question = question_text + "\n" + "\n".join(formatted_options)

        return {
            "image": image,
            "question": full_question,
            "correct_answer": correct_answer,  # Now "A", "B", "C", or "D"
            "task_name": task_name,
            "sample_id": sample_id,
        }
