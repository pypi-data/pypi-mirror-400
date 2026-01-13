"""
This module provides functions for grading and categorizing agent answers for exact match question
"""
import re
from collections import defaultdict
from enum import Enum, auto
from agentbenchkit.evaluator import register_match_function,register_grader_function
import numpy as np

# Define the four grading categories
class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()

# A set of valid MCQ options, from 'partial_acc.py'
MCQ_OPTIONS = [chr(ord('A') + i) for i in range(56)]


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
    match = re.search(r"\(?([A-Z])\)?\.?$", cleaned)
    if match:
        return match.group(1)  # Return the part inside the parentheses

    # Fallback for simple single-letter answers
    if len(cleaned) == 1 and cleaned in MCQ_OPTIONS:
        return cleaned

    # --- 3. Return the full string if it's not an error or MCQ ---
    # e.g., "A CAR", "FORD", "E. THE IMAGE..."
    return cleaned

@register_match_function("exact_match_2l")
def exact_match_2l_results(all_results):
    total = []
    task_l1 = {}
    task_l2 = {}
    exceptions = {}
    for item in all_results:
        try:
            correct_answer = item.get("correct_answer")
            agent_answer = item.get("agent_answer")
            correct_answer = clean_answer(correct_answer)
            agent_answer_cleaned = clean_answer(agent_answer)
            task = item.get("task", "unknown_task")
            if task == "unknown_task":
                print(f"warning: item{item["index"]} no task found in result item")
                continue
            task_split = task.split("|")
            if len(task_split) != 2:
                print(f"warning: item{item["index"]} task not in expected format, formatted should be like: class-l1|class-l2")
                continue
            if task_split[0] not in task_l1:
                task_l1[task_split[0]] = []
            if task_split[1] not in task_l2:
                task_l2[task_split[1]] = []
            if agent_answer_cleaned== correct_answer:
                total.append(1)
                task_l1[task_split[0]].append(1)
                task_l2[task_split[1]].append(1)
            else:
                total.append(0)
                task_l1[task_split[0]].append(0)
                task_l2[task_split[1]].append(0)
            
        except Exception as e:
            if str(e) not in exceptions:
                exceptions[str(e)] = [item.get('index')]
            else:
                exceptions[str(e)].append(item.get['index'])
            print(f"Warning: Skipping malformed result item {item.get('index', '')}: {e}")

    total_accuracy = np.mean(np.array(total)) * 100
    result_nums = {"all": total_accuracy}

    for k in task_l1.keys():
        task_accuracy = np.mean(np.array(task_l1[k])) * 100
        result_nums["l1-" + k] = task_accuracy

    for k in task_l2.keys():
        task_accuracy = np.mean(np.array(task_l2[k])) * 100
        result_nums["l2-" + k] = task_accuracy

        
    return [
        {"type":"metric","result_name": "accuracy","result_nums": result_nums},
    ]

@register_grader_function("exact_match_2l")
def exact_match_2l(agent_answer, correct_answer) -> Grade:
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

