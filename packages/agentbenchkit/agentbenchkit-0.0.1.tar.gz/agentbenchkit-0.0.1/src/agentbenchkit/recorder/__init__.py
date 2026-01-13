import os,sys
from langfuse import get_client
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_online_recorder() :
    """
    Factory function to get the specified recorder.
    """
    pk = os.environ.get("LANGFUSE_PUBLIC_KEY")
    sk = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST")
    if pk and sk and host:
        logger.info("Using Langfuse for recording")
        return get_client()
    else:
        logger.info("Not using Langfuse for recording")
        return None

def get_benchmark_answer_recorder(results:list, results_dir: str, file_name: str):
    try:
        os.makedirs(results_dir, exist_ok=True)
        results_file_path = os.path.join(results_dir, f"{file_name}.json")
        with open(results_file_path, "w") as f:
            json.dump(results, f, indent=2)
            logger.info(f"Successfully wrote results to {results_file_path}")
    except Exception as e:
        logger.error(f"Error writing results file: {e}")

def _print_results(result_list, benchmark_name: str):
    print(f"\n--- Benchmark Results for {benchmark_name} ---")
    for item in result_list:
        if item["type"] == "exceptions":
            continue
        if item["type"] == "metric":
            result_name = item["result_name"]
            overall_result = item["result_nums"]["all"]
            print(f"{result_name:<20}: {overall_result:5.2f}%")
        if item["type"] == "count":
            result_name = item["result_name"]
            overall_result = item["result_nums"]["all"]
            print(f"{result_name:<20}: {overall_result}")

    print("\n--- Benchmark Results by Task ---")
    # --- Print Task-Specific Results ---
    for item in result_list:
        result_name = item["result_name"]
        if item["type"] == "exceptions":
            continue
        if item["type"] == "metric":
            for k in item["result_nums"].keys():
                if k != "all":
                    print(f"{f"{result_name} for {k}":<40}: {item['result_nums'][k]:5.2f}%")
        if item["type"] == "count":
            for k in item["result_nums"].keys():
                if k != "all":
                    print(f"{f"{result_name} for {k}":<40}: {item['result_nums'][k]}")
    print("\n--- Benchmark Exceptions ---")
    for item in result_list:
        if item["type"] == "exceptions":
            print(f"Exceptions: {item['result_nums']}")

def get_results_recorder(results_dir: str, config, require_printing: bool = True):
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    worker_file = os.path.join(results_dir, f"{config.benchmark}_results.json")

    if not worker_file:
        logger.error(f"Error: No result file found for {config.benchmark} in {results_dir}")
        sys.exit(1)

    try:
        with open(worker_file) as f:
            results = json.load(f)
    except Exception as e:
        logger.error(f"Warning: Could not read or parse {worker_file}: {e}")

    if not results:
        logger.error("No results were successfully loaded.")
        sys.exit(1)

    data_loader = config.dataloader
    for item in results:
        if item["correct_answer"] == "file":
            item["correct_answer"] = data_loader.__getitem__(item["index"])["correct_answer"]

    match_function = config.evaluator

    results_path = os.path.join(results_dir, f"{config.benchmark}_evaluation.json")
    logging.getLogger().handlers[0].flush()
    extend_list = []
    for item in match_function:
        result_list = item(results)
        extend_list.extend(result_list)
    if require_printing:
        _print_results(extend_list, config.benchmark)
    with open(results_path, "w") as f:
        json.dump(extend_list, f, indent=2)
    logger.info(f"Results saved to {results_path}")

def print_evaluation_results(results_dir: str, benchmark_name: str):
    worker_file = os.path.join(results_dir, f"{benchmark_name}_evaluation.json")
    if not worker_file:
        logger.error(f"Error: No result file found for {benchmark_name} in {results_dir}")
        sys.exit(1)
    with open(worker_file) as f:
        results = json.load(f)
    _print_results(results, benchmark_name)