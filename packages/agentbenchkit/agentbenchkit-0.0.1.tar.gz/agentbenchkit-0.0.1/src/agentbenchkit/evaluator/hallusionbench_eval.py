from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from agentbenchkit.evaluator import register_match_function, register_grader_function
import warnings
from enum import Enum, auto
import numpy as np
"""
This is a evaluator for HallusionBench Dataset.
HallusionBench dataset is a yes/no type selection dataset. 
Each question has figure_id and question_id.
If you want to use this evaluator on other datasets, the datasets must be organized in the same manner as the MME dataset.
And make sample_id like format "hallusionbench_{subcategory}_{set_id}_{figure_id}_{question_id}_{idx}".
HallusionBench dataset: https://huggingface.co/datasets/lmms-lab/HallusionBench

This evaluator will calculate aAcc, fAcc and qAcc.
aAcc: accuracy of all questions
fAcc: Group samples by identical figure_id within the same subcategory and set_id. 
      Increment the count by 1 if all questions within a group are answered correctly. 
      The accuracy is calculated as Count / Total number of groups.
qAcc: Group samples by identical question_id within the same subcategory and set_id. 
      Increment the count by 1 if all questions within a group are answered correctly. 
      The accuracy is calculated as Count / Total number of groups.
"""
class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()


@register_match_function("hallusionbench_eval")
def compute_hallusionbench_eval(all_results):
    total_correct = []
    figure_correct = {}
    question_correct = {}
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        task = item.get("task", "unknown_task")
        sample_id = item.get("sample_id", "unknown_sample_id")
        if sample_id == "unknown_sample_id":
            warnings.warn(f"sample_id is unknown for item {item['index']}.")
            continue
        sample_id_split = sample_id.split("_")
        #  f"hallusionbench_{subcategory}_{set_id}_{figure_id}_{question_id}_{idx}",
        if len(sample_id_split) != 6:
            warnings.warn(f"sample_id format for item {item['index']} is wrong.")
            continue
        _, subcategory, set_id, figure_id, question_id, idx = sample_id_split
        figure_id = f"{subcategory}_{set_id}_{figure_id}"
        question_id = f"{subcategory}_{set_id}_{question_id}"

        if figure_id not in figure_correct.keys():
            figure_correct[figure_id] = []
        if question_id not in question_correct.keys():
            question_correct[question_id] = []
            
        if isinstance(correct_answer, str) and isinstance(agent_answer, str):
            if correct_answer.lower() in ["yes", "no"] and agent_answer.lower() in ["yes", "no"]:
                if correct_answer.lower() == agent_answer.lower():
                    total_correct.append(1)
                    figure_correct[figure_id].append(1)
                    question_correct[question_id].append(1)
                else:
                    total_correct.append(0)
                    figure_correct[figure_id].append(0)
                    question_correct[question_id].append(0)
            else:
                warnings.warn(f'skip {item["index"]} because the correct answer or agent answer is not a yes/no choice.')
        else:
            warnings.warn(f'skip {item["index"]} because the correct answer or agent answer is not a string.')
    aAcc = np.mean(np.array(total_correct)) * 100
    fAcc = np.mean([np.all(x) for x in figure_correct.values()]) * 100
    qAcc = np.mean([np.all(x) for x in question_correct.values()]) * 100
    overall = (aAcc + fAcc + qAcc) / 3
    result_nums = {"aAcc": aAcc, "fAcc": fAcc, "qAcc": qAcc, "all": overall}

    results = []
    results.append({"type": "metric", "result_name": "accuracy", "result_nums": result_nums})

    return results


@register_grader_function("hallusionbench_eval")
def hallusionbench_eval_grade(agent_answer, correct_answer) -> Grade:
    if isinstance(correct_answer, str) and isinstance(agent_answer, str):
        if correct_answer.lower() in ["yes", "no"] and agent_answer.lower() in ["yes", "no"]:
            if correct_answer.lower() == agent_answer.lower():
                return Grade.CORRECT
            else:
                return Grade.WRONG
        else:
            return Grade.ERROR
    else:
        return Grade.ERROR