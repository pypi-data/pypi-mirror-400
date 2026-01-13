import Levenshtein
from agentbenchkit.evaluator import register_match_function, register_grader_function
import numpy as np

from enum import Enum, auto
"""
This is a evaluator for Natural Language Generation (NLG) tasks or OCR.
Compare the similarity of two strings using the Levenshtein edit distance.
"""

class Grade(Enum):
    NONE = auto()

@register_match_function("anls_score")
def compute_anls_score(all_results):
    anls_task_score = {}
    anls_total_score = []
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        task = item.get("task", "unknown_task")
        if isinstance(correct_answer, str):
            correct_answer = [correct_answer]
        if task not in anls_task_score.keys():
            anls_task_score[task] = []
        score = anls_score(agent_answer, correct_answer)
        anls_task_score[task].append(score)
        anls_total_score.append(score)
    
    result_nums = {"all": np.average(np.array(anls_total_score))}
    for k, v in anls_task_score.items():
        result_nums[k] = np.average(np.array(v))

    return [{"type":"metric","result_name": "anls","result_nums": result_nums}]
    

def anls_score(prediction: str, ground_truths: list[str]) -> float:
    if not isinstance(ground_truths, (list, tuple)):
        ground_truths = [ground_truths]
    
    prediction = ' '.join(prediction.strip().lower().split())
    ground_truths = [' '.join(gt.strip().lower().split()) for gt in ground_truths]

    scores = []
    for gt in ground_truths:
        if len(gt) == 0 and len(prediction) == 0:
            score = 1.0
        elif len(gt) == 0 or len(prediction) == 0:
            score = 0.0
        else:
            lev_dist = Levenshtein.distance(prediction, gt)
            norm_dist = lev_dist / max(len(prediction), len(gt))
            score = 1.0 - norm_dist
        scores.append(score)
    
    return max(scores)*100  # 取最匹配的参考答案

@register_grader_function("anls_score")
def anls_grader(prediction, ground_truths) -> Grade:
    return Grade.NONE