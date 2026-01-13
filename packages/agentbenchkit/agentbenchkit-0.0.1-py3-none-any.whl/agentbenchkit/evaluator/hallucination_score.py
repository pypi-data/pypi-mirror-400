from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from agentbenchkit.evaluator import register_match_function, register_grader_function
import warnings
from enum import Enum, auto
"""
This is an evaluator for vllm hallucination dataset. 
The model's response is required to be yes/no.
"""

class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()


@register_match_function("hallucination_score")
def compute_hallucination_score(all_results):
    y_true = []
    y_pred = []
    y_true_task = {}
    y_pred_task = {}
    task_name = []
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        task = item.get("task", "unknown_task")
        if task not in y_true_task.keys():
            y_true_task[task] = []
            y_pred_task[task] = []
            task_name.append(task)
            
        if isinstance(correct_answer, str) and isinstance(agent_answer, str):
            if correct_answer.lower() in ["yes", "no"] and agent_answer.lower() in ["yes", "no"]:
                if correct_answer.lower() == "yes":
                    y_true.append(1)
                    y_true_task[task].append(1)
                else:
                    y_true.append(0)
                    y_true_task[task].append(0)

                if agent_answer.lower() == "yes":
                    y_pred.append(1)
                    y_pred_task[task].append(1)
                else:
                    y_pred.append(0)
                    y_pred_task[task].append(0)
            else:
                warnings.warn(f'skip {item["index"]} because the correct answer or agent answer is not a yes/no choice.')
        else:
            warnings.warn(f'skip {item["index"]} because the correct answer or agent answer is not a string.')
        
                    
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, pos_label=1)
    recall = recall_score(y_true, y_pred, pos_label=1)
    f1 = f1_score(y_true, y_pred, pos_label=1)

    results = []
    results.append({"type": "metric", "result_name": "accuracy", "result_nums": {"all": accuracy * 100}})
    results.append({"type": "metric", "result_name": "precision", "result_nums": {"all": precision * 100}})
    results.append({"type": "metric", "result_name": "recall", "result_nums": {"all": recall * 100}})
    results.append({"type": "metric", "result_name": "f1", "result_nums": {"all": f1 * 100}})

    for task in task_name:
        accuracy = accuracy_score(y_true_task[task], y_pred_task[task])
        precision = precision_score(y_true_task[task], y_pred_task[task], pos_label=1)
        recall = recall_score(y_true_task[task], y_pred_task[task], pos_label=1)
        f1 = f1_score(y_true_task[task], y_pred_task[task], pos_label=1)
        results[0]["result_nums"][task] = accuracy * 100
        results[1]["result_nums"][task] = precision * 100
        results[2]["result_nums"][task] = recall * 100
        results[3]["result_nums"][task] = f1 * 100

    return results


@register_grader_function("hallucination_score")
def hallucination_score_grade(agent_answer, correct_answer) -> Grade:
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