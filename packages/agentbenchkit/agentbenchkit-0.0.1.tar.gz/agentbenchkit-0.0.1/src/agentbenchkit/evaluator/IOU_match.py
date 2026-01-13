from collections import defaultdict
import re
from agentbenchkit.evaluator import register_match_function,register_grader_function
from agentbenchkit.evaluator.exact_match import Grade


# IOU_Calculation for BBox
def clean_answer(answer_str):
    if isinstance(answer_str, list):
        return answer_str
    if not isinstance(answer_str, str):
        return "ERROR"+str(answer_str)
    answer_str = answer_str.strip()
    numbers = re.findall(r'-?\d+', answer_str)
    # 检查是否正好有4个数字
    if len(numbers) == 4:
        bbox = [int(num) for num in numbers]
        # 验证坐标合理性 (x2 > x1 且 y2 > y1)
        if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
            return bbox
        else:
            return "ERROR"
    else:
        return "ERROR"

def calculate_iou(agent_answer:list[int], correct_answer:list[int]):
    """
       计算两个边界框列表之间的交并比(IOU)

       Args:
           agent_answer: 模型预测的边界框坐标列表 [x1, y1, x2, y2]
           correct_answer: 正确的边界框坐标列表 [x1, y1, x2, y2]

       Returns:
           float: IOU值，范围在[0, 1]之间
       """
    # 获取预测框和真实框的坐标
    pred_x1, pred_y1, pred_x2, pred_y2 = agent_answer
    true_x1, true_y1, true_x2, true_y2 = correct_answer

    # 计算相交区域的坐标
    inter_x1 = max(pred_x1, true_x1)
    inter_y1 = max(pred_y1, true_y1)
    inter_x2 = min(pred_x2, true_x2)
    inter_y2 = min(pred_y2, true_y2)

    # 计算相交面积
    inter_width = max(0, inter_x2 - inter_x1)
    inter_height = max(0, inter_y2 - inter_y1)
    intersection_area = inter_width * inter_height

    # 计算各自面积
    pred_area = (pred_x2 - pred_x1) * (pred_y2 - pred_y1)
    true_area = (true_x2 - true_x1) * (true_y2 - true_y1)

    # 计算并集面积
    union_area = pred_area + true_area - intersection_area

    # 计算IOU
    if union_area == 0:
        return 0.0

    iou = intersection_area / union_area
    return iou

@register_match_function("IOU_Calculation")
def IOU_Calculation(all_results):
    """
    Calculate the IOU for each task.
    """
    total_samples = 0
    average_iou = 0
    task_totals = defaultdict(int)
    task_average_iou = defaultdict(int)
    exceptions = {}
    for item in all_results:
        try:
            correct_answer = item.get("correct_answer")
            agent_answer = item.get("agent_answer")
            task = item.get("task", "unknown_task")

            correct_answer_cleaned = clean_answer(correct_answer)
            agent_answer_cleaned = clean_answer(agent_answer)
            iou = calculate_iou(agent_answer_cleaned, correct_answer_cleaned)
            total_samples += 1
            task_totals[task] += 1

            average_iou += iou
            task_average_iou[task] += iou
        except Exception as e:
            if str(e) not in exceptions:
                exceptions[str(e)] = [item.get('index')]
            else:
                exceptions[str(e)].append(item.get['index'])
            print(f"Warning: Skipping malformed result item {item.get('index', '')}: {e}")

    result_nums = {"all": average_iou/total_samples}
    result_samples = {"all": total_samples}
    for k in task_average_iou:
        result_nums[k] = task_average_iou[k]/task_totals[k]
        result_samples[k] = task_totals[k]
    return [
        {"type": "metric", "result_name": "average_iou", "result_nums": result_nums},
        {"type": "count", "result_name": "total_samples", "result_nums": total_samples},
        {"type": "exceptions", "result_name": "exceptions", "result_nums": exceptions}
    ]

@register_match_function("IOU_Threshold")
def IOU_Threshold(all_results):
    """
    Calculate the IOU threshold for each task.
    """
    total_samples = 0
    correct_samples = 0
    task_totals = defaultdict(int)
    task_corrects = defaultdict(int)
    exceptions = {}
    for item in all_results:
        try:
            correct_answer = item.get("correct_answer")
            agent_answer = item.get("agent_answer")
            task = item.get("task", "unknown_task")
            correct_answer_cleaned = clean_answer(correct_answer)
            agent_answer_cleaned = clean_answer(agent_answer)
            if calculate_iou(agent_answer_cleaned, correct_answer_cleaned) > 0.5:
                correct_samples += 1
                task_corrects[task] += 1
            total_samples += 1
            task_totals[task] += 1
        except Exception as e:
            if str(e) not in exceptions:
                exceptions[str(e)] = [item.get('index')]
            else:
                exceptions[str(e)].append(item.get['index'])
            print(f"Warning: Skipping malformed result item {item.get('index', '')}: {e}")
    result_nums = {"all": correct_samples / total_samples*100}
    result_samples = {"all": total_samples}
    correct_samples = {"all": correct_samples}
    for k in task_totals.keys():
        result_nums[k] = task_corrects[k] / task_totals[k]*100
        correct_samples[k] = task_corrects[k]
        result_samples[k] = task_totals[k]
    return [
        {"type": "metric", "result_name": "average_iou", "result_nums": result_nums},
        {"type": "count", "result_name": "total_samples", "result_nums": total_samples},
        {"type": "count", "result_name": "correct_samples", "result_nums": correct_samples},
        {"type": "exceptions", "result_name": "exceptions", "result_nums": exceptions}
    ]

@register_grader_function("IOU_Calculation")
def IOU_Calculation_log(agent_answer, correct_answer):
    correct_answer_cleaned = clean_answer(correct_answer)
    agent_answer_cleaned = clean_answer(agent_answer)
    if agent_answer_cleaned == "ERROR":
        return "error"

    return calculate_iou(agent_answer_cleaned, correct_answer_cleaned)

@register_grader_function("IOU_Threshold")
def IOU_Threshold_log(agent_answer, correct_answer) -> Grade:
    agent_answer_cleaned = clean_answer(agent_answer)
    correct_answer_cleaned = clean_answer(correct_answer)
    if agent_answer_cleaned == "ERROR":
        return Grade.ERROR
    if calculate_iou(agent_answer_cleaned, correct_answer_cleaned) > 0.5:
        return Grade.CORRECT
    else:
        return Grade.WRONG
