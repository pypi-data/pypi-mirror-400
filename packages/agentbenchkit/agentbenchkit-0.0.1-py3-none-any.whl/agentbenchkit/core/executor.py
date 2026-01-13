import asyncio
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_executor(num_processes: int):
    if num_processes <=1 :
        return AsyncSequentialExecutor()
    else:
        return RayExecutor(num_processes)

class Executor:
    def execute(self, func, tasks: dict):
        raise NotImplementedError


class AsyncSequentialExecutor(Executor):
    def execute(self, func, task: dict):
        logger.info(f"Running task sequentially")
        async def run_task():
            data_indices = task["data_indices"]
            config = task["config"]
            # 使用 await 调用异步函数
            result = await func(config, data_indices=data_indices)
            return result
        return asyncio.run(run_task())


class RayExecutor(Executor):
    def __init__(self, num_processes: int = 2):
        self.num_processes = num_processes

    def execute(self, func, task: dict):
        import ray
        project_root = Path(__file__).resolve().parents[3]
        project_root = os.path.join(project_root, "agentbenchkit")

        ray.init(runtime_env={
        "PYTHONPATH": [project_root],  # 将项目根目录添加到 Python 路径
        "working_dir": project_root,# 设置工作目录
            "excludes": [
                "data/",  # 排除数据目录
                "results/",  # 排除结果目录
                ".venv/",  # 排除 Python 虚拟环境
                "__pycache__/",
                "*.log",
                "*.zip",
                "notebooks/",
            ]
            },
        )
        data_indices = task["data_indices"]
        self.num_processes = min(self.num_processes, len(data_indices))
        logger.info(f"Running tasks in parallel with {self.num_processes} workers.")
        config = task["config"]
        try:
            # 分配任务给多个worker
            chunk_size = (len(data_indices) -1+ self.num_processes) // self.num_processes
            parts = [data_indices[i:i + chunk_size] for i in range(0, len(data_indices), chunk_size)]

            futures = []
            for i, part in enumerate(parts):
                if part:
                    @ray.remote
                    def wrapper(function,config,data_indices: list):
                        import asyncio
                        return asyncio.run(function(config=config,  data_indices=data_indices))
                    futures.append(wrapper.remote(func,config, data_indices=part))            # 收集结果
            results = ray.get(futures)
            flatten_results = []
            for result in results:
                flatten_results.extend(result)
            return flatten_results
        except Exception as e:
            logger.error(f"Error running ray tasks: {e}")
            raise
        finally:
            ray.shutdown()