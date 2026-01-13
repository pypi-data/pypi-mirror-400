"""
This module provides functions for grading and categorizing agent answers for exact match question
"""
import re
from collections import defaultdict
from enum import Enum, auto
from agentbenchkit.evaluator import register_match_function,register_grader_function


# Define the four grading categories
class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()

# A set of valid MCQ options, from 'partial_acc.py'
MCQ_OPTIONS = {"A", "B", "C", "D", "E"}


def clean_answer(answer_str):
    """
    Cleans and standardizes an answer string.
    This logic is ported directly from 'scripts/partial_acc.py'.

    Returns:
    - "ERROR" if the answer is an error string or invalid.
    - "A", "B", "C", "D", or "E" if it's a valid MCQ format.
    - The cleaned, uppercase string otherwise (e.g., "FORD").
    """
    if isinstance(answer_str, int):
        return answer_str
    if not isinstance(answer_str, str):
        return "ERROR"

    cleaned = answer_str.strip().upper()

    # --- 1. Check for errors FIRST ---
    if "ERROR" in cleaned or "FAILED" in cleaned or answer_str == "NO_ANSWER":
        return "ERROR"

    # --- 2. Check for MCQ format ---
    # Regex from partial_acc.py [cite: `scripts/partial_acc.py` line 31]
    match = re.search(r"\(?([A-E])\)?\.?$", cleaned)
    if match:
        return match.group(1)  # Return the part inside the parentheses

    # Fallback for simple single-letter answers
    if len(cleaned) == 1 and cleaned in MCQ_OPTIONS:
        return cleaned

    # --- 3. Return the full string if it's not an error or MCQ ---
    # e.g., "A CAR", "FORD", "E. THE IMAGE..."
    return cleaned

@register_match_function("exact_match")
def exact_match_results(all_results):
    total_samples = 0
    correct_samples = 0
    task_totals = defaultdict(int)
    task_corrects = defaultdict(int)
    exceptions = {}
    for item in all_results:
        try:
            correct_answer = item.get("correct_answer")
            agent_answer = item.get("agent_answer")
            correct_answer = clean_answer(correct_answer)
            agent_answer_cleaned = clean_answer(agent_answer)
            task = item.get("task", "unknown_task")

            is_correct = agent_answer_cleaned== correct_answer
            total_samples += 1
            task_totals[task] += 1
            if is_correct:
                correct_samples += 1
                task_corrects[task] += 1
        except Exception as e:
            if str(e) not in exceptions:
                exceptions[str(e)] = [item.get('index')]
            else:
                exceptions[str(e)].append(item.get['index'])
            print(f"Warning: Skipping malformed result item {item.get('index', '')}: {e}")

    total_accuracy = correct_samples / total_samples * 100
    result_nums = {"all": total_accuracy}
    correct_samples_dict = {"all": correct_samples}
    result_total = {"all": total_samples}
    for k in task_totals.keys():
        task_accuracy = task_corrects[k] / task_totals[k] * 100
        result_nums[k] = task_accuracy
        result_total[k] = task_totals[k]
        correct_samples_dict[k] = task_corrects[k]
    return [
        {"type":"metric","result_name": "accuracy","result_nums": result_nums},
        {"type":"count","result_name":"correct_samples", "result_nums":correct_samples_dict},
        {"type":"count","result_name":"total_samples", "result_nums":result_total},
        {"type":"exceptions", "result_name":"exceptions", "result_nums": exceptions}
    ]

@register_grader_function("exact_match")
def exact_match(agent_answer, correct_answer) -> Grade:
    cleaned_agent = clean_answer(agent_answer)
    cleaned_correct = clean_answer(correct_answer)

    # Category 1: Agent answer was an error
    if cleaned_agent == "ERROR":
        return Grade.ERROR

    # Category 2: Correct answer IS an MCQ
    if   cleaned_correct  in MCQ_OPTIONS:
        # Agent also gave a valid MCQ answer
        if cleaned_agent in MCQ_OPTIONS:
            if cleaned_agent == cleaned_correct:
                return Grade.CORRECT
            else:
                return Grade.WRONG

        # Agent gave a non-MCQ answer (e.g., "FORD")
        else:
            return Grade.NO_ANSWER

    # Category 3: Correct answer is NOT an MCQ (e.g., "FORD")
    else:
        # We perform a direct string match.
        if cleaned_agent == cleaned_correct:
            return Grade.CORRECT
        else:
            # This includes cases where the agent said "A" to a non-MCQ
            # or just the wrong string (e.g., "CHEVY" vs "FORD").
            return Grade.WRONG

