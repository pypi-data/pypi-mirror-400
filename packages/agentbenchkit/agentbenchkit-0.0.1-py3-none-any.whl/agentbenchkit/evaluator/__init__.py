from typing import Protocol
import os
import importlib


match_functions_registry  = {}
match_logger_registry = {}

def _auto_import_match_functions():
    package_dir = os.path.dirname(__file__)
    if not os.path.exists(package_dir):
        return
    for file_name in os.listdir(package_dir):
        if file_name.endswith(".py") and not file_name.startswith("_"):
            module_name = os.path.splitext(file_name)[0]
            module_path = os.path.join(package_dir, file_name)
            try:
                module = importlib.import_module(f".{module_name}", package="agentbenchkit.evaluator")
            except Exception as e:
                print(f"Failed to import module {module_path}: {e}")


class MatchFunction(Protocol):
    def __call__(all_results:list[dict]) -> list[dict]:
        ...

class MatchLogger(Protocol):
    def __call__(agent_answer, correct_answer):
        ...

def print_match_function():
    """
        Print all registered match functions
    """
    print(list(match_functions_registry.keys()))

def get_match_function(name: str) -> MatchFunction:
    """
        Get a registered match function by name.
    """
    return match_functions_registry.get(name)

def register_match_function(name: str):
    """
        Evaluate benchmark results and calculate metrics.
            Args:
                all_results: List of result items containing:
                    - item["agent_answer"]: actual answer from agent
                    - item["correct_answer"]: correct answer from benchmark
                    - item["task"]: task category
            Returns:
                Dictionary with evaluation results:
                    {{"result_name": "example metric", "result_nums": {"all": 99, "task1": 98, ...}}}
    """
    def decorator(func: MatchFunction):
        if name in match_functions_registry:
            raise ValueError(f"Match function {name} is already registered.")
        match_functions_registry[name] = func
        return func
    return decorator

def get_grader_function(name: str) -> MatchLogger:
    """
        Get a registered logger function by name.
    """
    return match_logger_registry.get(name)

def register_grader_function(name: str):
    """
        Register a logger function.
    """
    def decorator(func: MatchLogger):
        match_logger_registry[name] = func
        return func
    return decorator

_auto_import_match_functions()
__all__ = ["print_match_function", "get_match_function", "register_match_function", "get_grader_function", "register_grader_function"]