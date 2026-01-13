from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from agentbenchkit.evaluator import register_match_function, register_grader_function
from enum import Enum, auto
"""
This is a evaluator for MME Dataset.
The MME dataset is a yes/no type of selection dataset. 
Each question is organized in pairs and in sequence. 
If you want to use this evaluator on other datasets, the datasets must be organized in the same manner as the MME dataset.
MME Dataset: https://huggingface.co/datasets/lmms-lab/MME

This evaluator will calculate the sum of accuracy and accuracy+ as the final result.
Accuracy is calculated as the number of correctly answered questions divided by the total number of questions.
Accuracy+ is calculated as follows: for each pair of questions, if both questions in the pair are answered correctly, it counts as 1; then, the total count of such correctly answered pairs is divided by the total number of question pairs.
"""

class Grade(Enum):
    CORRECT = auto()
    WRONG = auto()
    NO_ANSWER = auto()  # Answer was not in the expected A-E format
    ERROR = auto()

eval_type_dict = {
    "Perception": ["existence", "count", "position", "color", "posters", "celebrity", "scene", "landmark", "artwork", "OCR"],
    "Cognition": ["commonsense_reasoning", "numerical_calculation", "text_translation", "code_reasoning"]
}


class calculate_metrics:
    def divide_chunks(self, l, n=2):
        # looping till length l
        for i in range(0, len(l), n): 
            yield l[i:i + n]
        
        return 

    def parse_pred_ans(self, pred_ans):
        pred_label = None
        if pred_ans in ["yes", "no"]:
            pred_label = pred_ans
        else:
            prefix_pred_ans = pred_ans[:4]

            if "yes" in prefix_pred_ans:
                pred_label = "yes"
            elif "no" in prefix_pred_ans:
                pred_label = "no"
            else:
                pred_label = "other"

        return pred_label


    def compute_metric(self, gts, preds):
        assert len(gts) == len(preds)

        label_map = {
            "yes": 1,
            "no": 0,
            "other": -1,
        }
        
        gts = [label_map[x] for x in gts]
        preds = [label_map[x] for x in preds]

        acc = accuracy_score(gts, preds) 

        clean_gts = []
        clean_preds = []
        other_num = 0 
        for gt, pred in zip(gts, preds):
            if pred == -1:
                other_num += 1
                continue
            clean_gts.append(gt)
            clean_preds.append(pred)
        

        conf_mat = confusion_matrix(clean_gts, clean_preds, labels=[1,0])
        precision = precision_score(clean_gts, clean_preds, average='binary')
        recall = recall_score(clean_gts, clean_preds, average='binary')
        tp, fn = conf_mat[0]
        fp, tn = conf_mat[1]

        metric_dict = dict()
        metric_dict = {
            "TP": tp,
            "FN": fn,
            "TN": tn,
            "FP": fp,
            "precision": precision,
            "recall": recall,
            "other_num": other_num,
            "acc": acc,
        }

        return metric_dict


    def process_result(self, lines):

        model_score_dict = dict()
        for eval_type, task_name_list in eval_type_dict.items():
            # print("===========", eval_type, "===========")
           
            scores = 0
            task_score_dict = dict()

            for task_name in task_name_list:
                if task_name not in lines.keys() or len(lines[task_name]) == 0:
                    continue

                # task_txt = os.path.join(results_dir, task_name + ".txt")
                # lines = open(task_txt, 'r', encoding="utf-8").readlines()
                chunk_lines = list(self.divide_chunks(lines[task_name])) # one image corresponds to two questions
                
                img_num = len(chunk_lines)
                task_other_ans_num = 0
                task_score = 0
                acc_plus_correct_num = 0
                gts = []
                preds = []

                for img_items in chunk_lines:
                    assert len(img_items) == 2
                    img_correct_num = 0

                    for img_item in img_items:
                        img_name, question, gt_ans, pred_ans = img_item.split("\t")

                        gt_ans = gt_ans.lower()
                        pred_ans = pred_ans.lower()

                        assert gt_ans in ["yes", "no"] # gt can only be yes or no.

                        pred_ans = self.parse_pred_ans(pred_ans)
                        assert pred_ans in ["yes", "no", "other"]

                        gts.append(gt_ans)
                        preds.append(pred_ans)
                        
                        if gt_ans == pred_ans:
                            img_correct_num += 1
                        
                        if pred_ans not in ["yes", "no"]:
                            task_other_ans_num += 1

                    if img_correct_num == 2:
                        acc_plus_correct_num += 1

                # cal TP precision acc, etc.
                metric_dict = self.compute_metric(gts, preds)
                acc_plus = acc_plus_correct_num / img_num
                metric_dict["acc_plus"] = acc_plus
                
                
                for k, v in metric_dict.items():
                    if k in ["acc", "acc_plus"]:
                        task_score += v*100
                
                task_score_dict[task_name] = task_score
                
                scores += task_score
            
            model_score_dict[eval_type] = scores
            model_score_dict.update(task_score_dict)
            # print("total score:", scores, "\n")
            # for task_name, score in task_score_dict.items():
                # print("\t", task_name, " score:", score)
            # print("\n")
        
        return model_score_dict

@register_match_function("mme_score")
def calculate_mme_score(all_results):
    cal = calculate_metrics()
    lines = {}
    for item in all_results:
        correct_answer = item.get("correct_answer")
        agent_answer = item.get("agent_answer")
        question = item.get("question", "unknown_task")
        sample_id = item.get("sample_id", "unknown_id")
        task = item.get("task", "unknown_task")
        if sample_id == "unknown_id":
            print(f"warning: sample_id is unknown for {question} {correct_answer} {agent_answer}")
            continue
        if task == "unknown_task":
            print(f"warning: task is unknown for {question} {correct_answer} {agent_answer}")
            continue
        if task not in lines:
            lines[task] = []
        lines[task].append(f"{sample_id}\t{question}\t{correct_answer}\t{agent_answer}")
    model_score_dict = cal.process_result(lines)
    overall = 0
    for k, v in eval_type_dict.items():
        overall += model_score_dict[k]
    result_nums = {"all": overall}
    result_nums.update(model_score_dict)
    return [
        {"type": "metric", "result_name": "accuracy+accuracy_plus", "result_nums": result_nums}
    ]



@register_grader_function("mme_score")
def mme_score_grade(agent_answer, correct_answer) -> Grade:
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

