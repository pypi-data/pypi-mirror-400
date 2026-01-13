import Levenshtein
from agentbenchkit.evaluator import register_match_function, register_grader_function
import numpy as np

from enum import Enum, auto
class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()

@register_match_function("ocrbench_eval")
def compute_ocrbench_eval(all_results):
    correct = {"all": 0}
    total = {"all": 0}
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        task = item.get("task", "unknown_task")
        if task not in correct:
            correct[task] = 0
            total[task] = 0
        total[task] += 1
        total["all"] += 1
        if isinstance(correct_answer, str):
            if task == 'Handwritten Mathematical Expression Recognition':
                answer = correct_answer.strip().replace('\n',' ').replace(' ', '')
                predict = agent_answer.strip().replace('\n',' ').replace(' ', '')
            else:
                answer = correct_answer.lower().strip().replace(' ', '')
                predict = agent_answer.lower().strip().replace(' ', '')
            if answer in predict:
                correct[task] += 1
                correct["all"] += 1
        elif isinstance(correct_answer, list):
            if task == 'Handwritten Mathematical Expression Recognition':
                for j in range(len(correct_answer)):
                    answer = correct_answer[j].strip().replace('\n',' ').replace(' ', '')
                    predict = agent_answer.strip().replace('\n',' ').replace(' ', '')
                    if answer in predict:
                        correct[task] += 1
                        correct["all"] += 1
                        break
            else:
                for j in range(len(correct_answer)):
                    answer = correct_answer[j].lower().strip().replace(' ', '')
                    predict = agent_answer.lower().strip().replace(' ', '')
                    if answer in predict:
                        correct[task] += 1
                        correct["all"] += 1
                        break
    accuracy = {}
    for key in correct.keys():
        accuracy[key] = correct[key] / total[key]

    return [{"type":"count","result_name": "correct_nums","result_nums": correct},
            {"type":"metric","result_name": "accuracy","result_nums": accuracy}]
    


@register_grader_function("ocrbench_eval")
def ocrbench_eval_grader(prediction, ground_truths) -> Grade:
    if isinstance(ground_truths, str):
        answer = ground_truths.lower().strip().replace(' ', '')
        predict = prediction.lower().strip().replace(' ', '')
        if answer in predict:
            return Grade.CORRECT
    elif isinstance(ground_truths, list):
        for j in range(len(ground_truths)):
            answer = ground_truths[j].lower().strip().replace(' ', '')
            predict = prediction.lower().strip().replace(' ', '')
            if answer in predict:
                return Grade.CORRECT
            break
    else:
        return Grade.ERROR
    
    return Grade.WRONG