import base64
import json
from io import BytesIO
from pathlib import Path
from langchain_core.messages import HumanMessage
import re
from agentbenchkit.core.prompt import PROMPT_MCQ, PROMPT_YN


class ConfigManager:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        current_dir = Path(__file__).parent.parent
        file_path = current_dir / 'loader' / 'default_evaluator.json'
        with open(file_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def get_default_type(self, benchmark_name: str) -> str:
        config = self.config.get(benchmark_name, None)
        if config is None:
            return ""
        return config.get("Type")

    def get_metadata(self, benchmark_name: str) -> dict:
        return self.config.get(benchmark_name, {})

_config_manager = ConfigManager()

def pil_to_base64(image):
    buffered_image = BytesIO()
    image.save(buffered_image, format="PNG")
    img_str = base64.b64encode(buffered_image.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"


def _create_default_llm_state_builder(benchmark_name:str, custom_prompt: str=None):
    def state_builder(example):
        try:
            image_urls = []
            for item in example["image"]:
                if item is not None:
                    b64_url = pil_to_base64(item)
                    image_urls.append(b64_url)
        except Exception as e:
            raise ValueError(f"Failed to process image: {e}") from e
        human_content = []
        for image in image_urls:
            human_content.append({"type": "image_url", "image_url": {"url": image}})
        human_content.append({"type": "text", "text": example["question"]})

        if custom_prompt is not None:
            human_content.append({"type": "text", "text": custom_prompt})
        else:
            type = _config_manager.get_default_type(benchmark_name)
            if type == "MCQ":
                human_content.append({"type": "text", "text": PROMPT_MCQ})
            elif type == "Judge":
                human_content.append({"type": "text", "text": PROMPT_YN})

        return [HumanMessage(content=human_content)]
    return state_builder

def _create_default_llm_result_parser(benchmark_name:str):
    def result_parser(raw_answer):
        content = raw_answer.content
        type = _config_manager.get_default_type(benchmark_name)
        if type == "MCQ":
            patterns = [
                r'([A-Z])\.',
                r'\(([A-Z])\)'
            ]
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return match.group(1)
        if type == "Judge":
            judge_match = re.search(r'\b(yes|no)\b', content.lower())
            if judge_match:
                return judge_match.group(1)
        return content
    return result_parser

def get_default_helper(benchmark_name:str, custom_prompt: str=None, builder_type: str="llm"):
    if builder_type == "llm":
        return _create_default_llm_state_builder(benchmark_name, custom_prompt), _create_default_llm_result_parser(benchmark_name)
    else:
        raise ValueError("Invalid builder_type")







