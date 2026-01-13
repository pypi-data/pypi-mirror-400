from pycocoevalcap.bleu.bleu import Bleu
from pycocoevalcap.rouge.rouge import Rouge
from pycocoevalcap.cider.cider import Cider

from agentbenchkit.evaluator import register_match_function, register_grader_function

from enum import Enum, auto
"""
This is a evaluator for Natural Language Generation(NLG) tasks by pycocoevalcap.
In this evaluator BLEU(4), ROUGE and CIDEr is used to evaluate the NLG performance.
"""

class Grade(Enum):
    NONE = auto()

@register_match_function("nlg_score")
def compute_nlg_scores(all_results):
    coco_gt = {}
    coco_pred = {}
    total_coco_gt = {}
    total_coco_pred = {}

    task_name = []
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        task = item.get("task", "unknown_task")
        if task not in task_name:
            task_name.append(task)
            coco_gt[task] = {}
            coco_pred[task] = {}
        
        id = int(item.get("index")) + 1
        if isinstance(correct_answer, str):
            coco_gt[task][str(id)] = [correct_answer]
            total_coco_gt[str(id)] = [correct_answer]
        elif isinstance(correct_answer, list):
            coco_gt[task][str(id)] = correct_answer
            total_coco_gt[str(id)] = correct_answer
        else:
            raise ValueError("correct_answer must be a string or a list of strings")
        
        if isinstance(agent_answer, str):
            coco_pred[task][str(id)] = [agent_answer]
            total_coco_pred[str(id)] = [agent_answer]
        elif isinstance(agent_answer, list):
            coco_pred[task][str(id)] = agent_answer
            total_coco_pred[str(id)] = agent_answer
        else:
            raise ValueError("agent_answer must be a string or a list of strings")
    results = []

    score, scores = Bleu(4).compute_score(total_coco_gt, total_coco_pred)
    for idx, (total_score, sample_score) in enumerate(zip(score, scores)):
        result = {}
        result['type'] = "metric"
        result['result_name'] = f"Bleu_{idx + 1}"
        result['result_nums'] =  {"all": total_score * 100}
        results.append(result)

    score, scores = Rouge().compute_score(total_coco_gt, total_coco_pred)
    results.append({"type": "metric", "result_name": "ROUGE_L", "result_nums": {"all": score * 100}})

    score, scores = Cider().compute_score(total_coco_gt, total_coco_pred)
    results.append({"type": "metric", "result_name": "CIDEr", "result_nums": {"all": score * 100}})

    for task in task_name:
        score, scores = Bleu(4).compute_score(coco_gt[task], coco_pred[task])
        
        for idx, (_score, _) in enumerate(zip(score, scores)):
            results[idx]["result_nums"][task] = _score * 100

        score, scores = Rouge().compute_score(coco_gt[task], coco_pred[task])
        results[4]["result_nums"][task] = score * 100

        score, scores = Cider().compute_score(coco_gt[task], coco_pred[task])
        results[5]["result_nums"][task] = score * 100

    return results


@register_grader_function("nlg_score")
def nlg_score_grade(agent_answer, correct_answer) -> Grade:
    # gt = {}
    # pred = {}
    # if isinstance(correct_answer, str):
    #     gt["1"] = [correct_answer]
    # if isinstance(agent_answer, str):
    #     pred["1"] = [agent_answer]
    # result = ""
    # score, scores = Bleu(4).compute_score(gt, pred)
    # result += f"Bleu_1: {score[0] * 100:.2f} "
    # result += f"Bleu_2: {score[1] * 100:.2f} "
    # result += f"Bleu_3: {score[2] * 100:.2f} "
    # result += f"Bleu_4: {score[3] * 100:.2f} "
    # score, scores = Rouge().compute_score(gt, pred)
    # result += f"ROUGE_L: {score * 100:.2f} "
    # score, scores = Rouge().compute_score(gt, pred)
    # result += f"CIDEr: {score * 100:.2f}"
    return Grade.NONE
