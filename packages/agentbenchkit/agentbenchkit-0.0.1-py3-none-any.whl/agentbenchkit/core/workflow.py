import importlib
import os
import sys
from typing import Callable, List, Union
import requests
from langfuse import Langfuse, propagate_attributes
from agentbenchkit.loader import get_dataset_loader
from agentbenchkit.recorder import get_online_recorder, get_results_recorder, get_benchmark_answer_recorder, print_evaluation_results
from agentbenchkit.evaluator import get_match_function, get_grader_function
from agentbenchkit.core.executor import get_executor
import logging
from PIL import Image
from omegaconf import OmegaConf
import json
from pathlib import Path
from .utils import get_default_helper, ConfigManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BenchmarkConfig:
    def __init__(self, dataloader, agent, state_builder, result_parser,evaluator, results_dir, grader,  benchmark):
        self.dataloader = dataloader
        self.agent = agent
        self.state_builder = state_builder
        self.result_parser = result_parser
        self.evaluator = evaluator
        self.results_dir = results_dir
        self.grader = grader
        self.benchmark = benchmark


async def _run_single_question(example, config: BenchmarkConfig):
    state = config.state_builder(example)
    agent = config.agent
    try:
        if isinstance(config.agent, str):
            raw_answer = requests.post(config.agent, state)
        else:
            agent = agent()
            if hasattr(agent, "graph"):
                if hasattr(agent, "invoke_config"):
                    raw_answer = await agent.graph.ainvoke(state, config=agent.invoke_config)
                else:
                    raw_answer = await agent.graph.ainvoke(state)
            else:
                raw_answer = await agent.ainvoke(state)
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raw_answer = str(e)[:100]
    return raw_answer

async def run_benchmark_task(config: BenchmarkConfig, data_indices: list):
    results = []
    recorder = get_online_recorder()
    for i, idx in enumerate(data_indices):
        try:
            example = config.dataloader[idx]
            question = example["question"]
            correct_answer = example["correct_answer"]
            if isinstance(correct_answer, Image.Image):
                correct_answer = "file"
            task_name = example["task_name"]
            sample_id = example["sample_id"]
        except Exception as e:
            logger.error(f"Error processing example {idx}: {e}")
            continue

        result_data = {
            "index": idx,
            "task": task_name,
            "question": question,
            "correct_answer": correct_answer,
            "agent_answer": "Error: Skipped (Agent run failed)",
            "sample_id": sample_id
        }
        if recorder is not None:
            if isinstance(recorder, Langfuse):
                with recorder.start_as_current_span(
                        name=f"{sample_id}_{task_name}", input={"question": question}
                )as current_span:
                    with propagate_attributes(tags=[task_name, sample_id]):
                        raw_answer = await _run_single_question(example, config)
                    logger.info(f"sample_{sample_id}")
                    logger.info(raw_answer)

                    raw_parser = config.result_parser(raw_answer)
                    if isinstance(raw_parser, str):
                        agent_answer = raw_parser
                    elif isinstance(raw_parser, dict):
                        if raw_parser.get("answer") is None:
                            raise ValueError("Invalid result_parser output, output single String or a dict at least contain one 'answer' key")
                        for k,v in raw_parser.items():
                            if k == "answer":
                                agent_answer = v
                            else:
                                result_data[k] = v
                    else:
                        raise ValueError("Invalid result_parser output, output single String or a dict at least contain one 'answer' key")

                    result_data["agent_answer"] = agent_answer
                    results.append(result_data)
                    grader = config.grader
                    grade = grader(correct_answer, example["correct_answer"])
                    current_span.score(
                        name="correctness",
                        value=grade.name,  # Use the enum name
                        data_type="CATEGORICAL",
                        comment=f"Agent: {agent_answer} | Correct: {correct_answer}",
                    )

                    current_span.update(
                        output={
                            "agent_answer": agent_answer,
                        },
                        metadata={
                            "task_name": task_name,
                            "sample_id": sample_id,
                            "correct_answer": correct_answer if not isinstance(correct_answer, Image.Image) else "file",
                            "agent_answer": agent_answer,
                        },
                    )
                recorder.flush()
        else:
            try:
                raw_answer = await _run_single_question(example, config)
                logger.info(raw_answer)
            except Exception as e:
                logger.error(f"Error running agent: {e}")
                raw_answer = e
            raw_parser = config.result_parser(raw_answer)
            if isinstance(raw_parser, str):
                agent_answer = raw_parser
            elif isinstance(raw_parser, dict):
                for k, v in raw_parser.items():
                    if raw_parser.get("answer") is None:
                        raise ValueError("Invalid result_parser output, output single String or a dict at least contain one 'answer' key")
                    if k == "answer":
                        agent_answer = v
                    else:
                        result_data[k] = v
            else:
                raise ValueError(
                    "Invalid result_parser output, output single String or a dict at least contain one 'answer' key")
            result_data["agent_answer"] = agent_answer
            results.append(result_data)
    return results

def load_builder_from_config(builder):
    module_path, func_name = builder.split(".",1)
    if module_path in sys.modules:
        module = sys.modules[module_path]
    else:
        module = importlib.import_module(module_path)

    builder_func = getattr(module, func_name)
    return builder_func

class BenchmarkRunner:
    def __init__(self,
                 agent: Callable | str,
                 loader_name: str,
                 state_builder: Callable = None,
                 result_parser: Callable=None,
                 evaluator: Union[str, List[str]]= None,
                 num_workers: int=1):
        """
        Define a benchmark runner instance,run benchmark task by .run()
        :param agent: your own agent/llm builder or an api address string
        :param loader_name: predefined or your registered loader name
        :param state_builder:  your registered state builder
        :param result_parser: your registered result parser
        :param evaluator: predefined or your registered evaluator name
        :param num_workers: working process
        """
        if agent is None:
            raise ValueError("Please provide either agent/llm build function or api address")
        self.build_agent = agent
        if loader_name is None:
            raise ValueError("Please provide the name of the benchmark to be tested")
        self.dataloader = get_dataset_loader(loader_name)
        self.benchmark = loader_name
        if state_builder is None or result_parser is None:
            default_state_builder, default_result_parser = get_default_helper(loader_name)
            state_builder = state_builder or default_state_builder
            result_parser = result_parser or default_result_parser
        self.state_builder = state_builder
        self.result_parser = result_parser
        self.executor = get_executor(num_workers)
        if isinstance(evaluator, list) and len(evaluator) > 1:
            logger.info(f"Using multiple evaluators: {evaluator}")
            self.evaluator = [get_match_function(item) for item in evaluator]
        else:
            if evaluator is None or len(evaluator) == 0:
                current_dir = Path(__file__).parent.parent
                file_path = current_dir / 'loader' / 'default_evaluator.json'
                with open(file_path, "r", encoding="utf-8") as f:
                    default_eval = json.load(f)
                if loader_name in default_eval.keys():
                    evaluator = default_eval[loader_name]["evaluator"]
                    logger.info(f"Using default evaluator for {loader_name}: {evaluator}")
                else:
                    evaluator = "exact_match"
                    logger.info(
                        f"No default evaluator is configured for {loader_name}, use default evaluator {evaluator}")
            self.evaluator = [get_match_function(evaluator)] if isinstance(evaluator, str) else [get_match_function(evaluator[0])]

        self.grader = get_grader_function(evaluator[0])
        if self.grader is None and os.getenv("LANGFUSE_HOST"):
            raise ValueError(f"Grader for {evaluator}is not registered, langfuse cannot be activated, "
                             f"either implement the function remove langfuse environment setting")
        self.print = True

    @classmethod
    def from_config(cls, config_path):
        """
        initialize a benchmark runner from a yaml file
        :param config_path: path to yaml file
        """
        if not os.path.exists(config_path):
            raise ValueError(f"Config file for running benchmark {config_path} does not exist")
        config = OmegaConf.load(config_path)
        # 加载配置文件中的测试对象
        test_object = config.test_object
        if test_object.type is None:
            raise ValueError("test_object.type is None")
        elif test_object.type in ["agent","llm"]:
            test_object_loaded = load_builder_from_config(test_object.builder)
        elif test_object.type == "api":
            test_object_loaded = test_object.address
        else:
            raise ValueError(f"Unknown test_object.type: {test_object.type}, available choices are 'agent','llm' or 'api'")

        runners  = []
        results = config.results
        results_path = results.path
        #加载配置文件中的benchmark集（）
        for benchmark in config.benchmarks:
            loader_name = benchmark.name

            module_path, func_name = benchmark.state_builder.split(".", 1)
            try:
                if module_path in sys.modules:
                    module = sys.modules[module_path]
                else:
                    module = importlib.import_module(module_path)
                state_builder = getattr(module, func_name)
            except ModuleNotFoundError :
                raise ValueError(f"Module {module_path} not found")
            except AttributeError:
                raise ValueError(f"Function {func_name} not found in module {module_path}")

            module_path, func_name = benchmark.result_parser.split(".", 1)
            try:
                if module_path in sys.modules:
                    module = sys.modules[module_path]
                else:
                    module = importlib.import_module(module_path)
                result_parser = getattr(module, func_name)
            except ModuleNotFoundError :
                raise ValueError(f"Module {module_path} not found")
            except AttributeError:
                raise ValueError(f"Function {func_name} not found in module {module_path}")

            if benchmark.get("evaluator") is None:
                evaluator = None
            elif len(benchmark.evaluator) == 0:
                evaluator = None
            else:
                evaluator = benchmark.evaluator

            num_workers = benchmark.get("num_workers", 1)
            limit = benchmark.get("limit", None)
            index_list = benchmark.get("indices", None)

            runner = BenchmarkRunner(test_object_loaded, loader_name, state_builder, result_parser, evaluator, num_workers)
            runner.print = False
            runners.append(runner)
            runner.run(results_path, limit, index_list)
        logging.getLogger().handlers[0].flush()
        print("\n -------------------")
        print("Results for benchmarks")
        for benchmark in config.benchmarks:
            print_evaluation_results(results_path, benchmark.name)


    def run(self, results_dir, limit: int=None, indices:list[int]=None):
        """
        run specified indices or first limit number of benchmark and save result into results_dir
        :param results_dir: results will be saved to this dir
        :param limit: if limit is None, run all questions
        :param indices: specified indices and has a higher priority to param 'limit'
        """
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)
        all_indices = list(range(len(self.dataloader)))

        if indices is not None:
            # 使用指定索引
            all_indices = [i for i in indices if i < len(self.dataloader)]
            logger.info(f"Running on specified indices: {len(all_indices)} samples")
        elif limit is not None:
            # 使用前limit个样本
            all_indices = all_indices[:limit]
            logger.info(f"Running on first {limit} samples")
        else:
            logger.info(f"Running on all {len(all_indices)} samples")

        # 创建配置对象
        config = BenchmarkConfig(
            dataloader=self.dataloader,
            agent=self.build_agent,
            state_builder=self.state_builder,
            result_parser=self.result_parser,
            results_dir=results_dir,
            evaluator=self.evaluator,
            grader = self.grader,
            benchmark=self.benchmark
        )

        task = {"config": config, "data_indices": all_indices}
        results = self.executor.execute(run_benchmark_task, task)
        get_benchmark_answer_recorder(results, results_dir, f"{self.benchmark}_results")
        get_results_recorder(results_dir, config, self.print)

    def evaluate_by_result_file(self, results_dir: str):
        config = BenchmarkConfig(
            dataloader=self.dataloader,
            agent=self.build_agent,
            state_builder=self.state_builder,
            result_parser=self.result_parser,
            results_dir=results_dir,
            evaluator=self.evaluator,
            grader=self.grader,
            benchmark=self.benchmark
        )
        get_results_recorder(results_dir, config)


    def evaluate(self,
                 result_file:  str,
                 results_dir:  str,
                 evaluator: str = None):
        """evaluate by result json file directly

           result_file: the path of result json file
           results_dir: the path of results directory, final result will be saved at results_dir/results.json
           evaluator: the evaluator function
        """
        import os
        if os.path.exists(result_file):
            with open(result_file, "r", encoding="utf-8") as f:
                all_results = json.load(f)
        else:
            raise FileNotFoundError(f"Result file {result_file} not found")
        
        match_function = get_match_function(evaluator)
        result_list = match_function(all_results)
        results_path = f"{results_dir}/results.json"
        print("\n--- Benchmark Results ---")
        for item in result_list:
            if item["type"] == "exceptions":
                continue
            if item["type"] == "metric":
                result_name = item["result_name"]
                overall_result = item["result_nums"]["all"]
                print(f"{result_name}:            {overall_result:6.2f}%")
            if item["type"] == "count":
                result_name = item["result_name"]
                overall_result = item["result_nums"]["all"]
                print(f"{result_name}:            {overall_result}")

        print("\n--- Benchmark Results by Task ---")
        # --- Print Task-Specific Results ---
        for item in result_list:
            result_name = item["result_name"]
            if item["type"] == "exceptions":
                continue
            if item["type"] == "metric":
                for k in item["result_nums"].keys():
                    if k != "all":
                        print(f"{result_name} for {k}:          {item['result_nums'][k]:6.2f}%")
            if item["type"] == "count":
                for k in item["result_nums"].keys():
                    if k != "all":
                        print(f"{result_name} for {k}:          {item['result_nums'][k]}")
        print("\n--- Benchmark Exceptions ---")
        for item in result_list:
            if item["type"] == "exceptions":
                print(f"Exceptions: {item['result_nums']}")
        with open(results_path, "w") as f:
            json.dump(result_list, f, indent=2)
        print(f"Results saved to {results_path}")
