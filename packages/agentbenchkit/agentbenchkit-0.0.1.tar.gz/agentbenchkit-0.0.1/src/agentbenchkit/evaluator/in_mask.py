from collections import defaultdict
from PIL import Image
from agentbenchkit.evaluator import register_match_function, register_grader_function
from .exact_match import Grade
import re


def clean_answer(answer_str):
        # 使用正则表达式提取坐标
    numbers = re.findall(r'-?\d+\.?\d*', answer_str)
    if len(numbers) >= 2:
        try:
            x = float(numbers[0])
            y = float(numbers[1])
            # 保持浮点数格式以支持相对坐标
            return [x, y]
        except ValueError:
            return answer_str
    else:
        return answer_str

def judge_answer(agent_answer, correct_answer):
    mask_image = correct_answer
    width, height = mask_image.size
    if isinstance(agent_answer, list) and len(agent_answer) == 2:
        x,y = agent_answer
        if x < 0 or x >= mask_image.width or y < 0 or y >= mask_image.height:
            return False
        x = int(x * width)
        y = int(y * height)
        if mask_image.getpixel((x,y))== 255:
            return True
    return False


@register_match_function("in_mask")
def in_mask_match(all_results):
    total_samples  = 0
    correct_samples = 0
    task_totals = defaultdict(int)
    task_corrects = defaultdict(int)
    exceptions = {}
    for item in all_results:
        try:
            correct_answer = item.get("correct_answer")
            agent_answer = item.get("agent_answer")
            agent_answer_cleaned = clean_answer(agent_answer)

            if judge_answer(agent_answer_cleaned, correct_answer):
                correct_samples += 1
                task_corrects[item.get("task", "unknown_task")] += 1
            total_samples += 1
            task_totals[item.get("task", "unknown_task")] += 1
        except Exception as e:
            if str(e) not in exceptions:
                exceptions[str(e)] = [item.get('index')]
            else:
                exceptions[str(e)].append(item.get('index'))
            print(f"Warning: Skipping malformed result item {item.get('index', '')}: {e}")

    result_nums = {"all": correct_samples / total_samples*100}
    result_samples = {"all": total_samples}
    correct_samples = {"all": correct_samples}
    for k in task_totals.keys():
        result_nums[k] = task_corrects[k] / task_totals[k]*100
        correct_samples[k] = task_corrects[k]
        result_samples[k] = task_totals[k]

    return [
        {"type": "metric", "result_name": "accuracy", "result_nums": result_nums},
        {"type": "count", "result_name": "total_samples", "result_nums": result_samples},
        {"type": "count", "result_name": "correct_samples", "result_nums": correct_samples},
        {"type": "exceptions", "result_name": "exceptions", "result_nums": exceptions}
    ]

@register_grader_function("in_mask")
def in_mask_grader(agent_answer, correct_answer):
    agent_answer_cleaned = clean_answer(agent_answer)
    try:
        if judge_answer(agent_answer_cleaned, correct_answer):
            return Grade.CORRECT
        else:
            return Grade.WRONG
    except Exception:
        return Grade.ERROR



