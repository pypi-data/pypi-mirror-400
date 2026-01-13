import inspect
import sys
from collections import deque
from typing import List, Tuple, Dict, Optional

# 定义进程类型
Process = Tuple[str, int, int]


def fcfs(pro: List[Process]) -> List[Dict]:
    """
    先来先服务 (FCFS) 调度算法实现。

    :param pro: 进程列表，每个元素为 (进程名, 到达时间, 服务时间)
    :type pro: List[Process]

    :return: 每个进程的调度结果，包含进程名、到达时间、服务时间、开始时间和完成时间
    :rtype: List[Dict]
    """
    # 按到达时间排序（FCFS）
    pro.sort(key=lambda x: x[1])

    current_time = 0
    result = []

    for name, arrival, service in pro:
        # 如果CPU空闲，推进时间到该进程到达
        start_time = max(current_time, arrival)
        completion_time = start_time + service

        result.append({
            "process": name,
            "arrival": arrival,
            "service": service,
            "start": start_time,
            "completion": completion_time
        })

        current_time = completion_time

    return result


def sjf(pro: List[Process]) -> List[Dict]:
    """
    短作业优先 (SJF) 调度算法实现。

    :param pro: 进程列表，每个元素为 (进程名, 到达时间, 服务时间)
    :type pro: List[Process]

    :return: 每个进程的调度结果，包含进程名、到达时间、服务时间、开始时间和完成时间
    :rtype: List[Dict]
    """
    pro = sorted(pro, key=lambda x: x[1])
    time = 0
    finished = []
    ready = []
    idx = 0
    n = len(pro)

    while len(finished) < n:
        # 加入已到达的进程
        while idx < n and pro[idx][1] <= time:
            ready.append(pro[idx])
            idx += 1

        if not ready:
            time = pro[idx][1]
            continue

        # 按服务时间最短排序
        ready.sort(key=lambda x: x[2])
        name, arrival, service = ready.pop(0)

        start = time
        finish = start + service
        time = finish

        finished.append({
            "process": name,
            "arrival": arrival,
            "service": service,
            "start": start,
            "completion": finish
        })

    return finished


def hrrn(pro: List[Process]) -> List[Dict]:
    """
    高响应比优先 (HRRN) 调度算法实现。

    :param pro: 进程列表，每个元素为 (进程名, 到达时间, 服务时间)
    :type pro: List[Process]

    :return: 每个进程的调度结果，包含进程名、到达时间、服务时间、开始时间和完成时间
    :rtype: List[Dict]
    """
    pro = sorted(pro, key=lambda x: x[1])
    time = 0
    finished = []
    ready = []
    idx = 0
    n = len(pro)

    while len(finished) < n:
        while idx < n and pro[idx][1] <= time:
            ready.append(pro[idx])
            idx += 1

        if not ready:
            time = pro[idx][1]
            continue

        # 计算响应比
        def response_ratio(_p):
            _, _arrival, _service = _p
            wait = time - _arrival
            return (wait + _service) / _service

        ready.sort(key=response_ratio, reverse=True)
        name, arrival, service = ready.pop(0)

        start = time
        finish = start + service
        time = finish

        finished.append({
            "process": name,
            "arrival": arrival,
            "service": service,
            "start": start,
            "completion": finish
        })

    return finished


def round_robin(pro: List[Process], quantum: int) -> List[Dict]:
    """
    时间片轮转 (Round Robin) 调度算法实现。

    :param pro: 进程列表，每个元素为 (进程名, 到达时间, 服务时间)
    :type pro: List[Process]
    :param quantum: 时间片大小
    :type quantum: int

    :return: 每个进程的调度结果，包含进程名、到达时间、服务时间、开始时间和完成时间
    :rtype: List[Dict]
    """
    pro = sorted(pro, key=lambda x: x[1])
    queue = deque()
    time = 0
    idx = 0
    n = len(pro)

    remaining = {p[0]: p[2] for p in pro}
    arrival_map = {p[0]: p[1] for p in pro}
    start_time = {}
    completion = {}

    while queue or idx < n:
        # 加入到达的进程
        while idx < n and pro[idx][1] <= time:
            queue.append(pro[idx][0])
            idx += 1

        if not queue:
            time = pro[idx][1]
            continue

        current = queue.popleft()

        if current not in start_time:
            start_time[current] = time

        exec_time = min(quantum, remaining[current])
        time += exec_time
        remaining[current] -= exec_time

        # 执行过程中到达的新进程
        while idx < n and pro[idx][1] <= time:
            queue.append(pro[idx][0])
            idx += 1

        if remaining[current] > 0:
            queue.append(current)
        else:
            completion[current] = time

    return [
        {
            "process": name,
            "arrival": arrival_map[name],
            "service": next(p[2] for p in pro if p[0] == name),
            "start": start_time[name],
            "completion": completion[name]
        }
        for name in start_time
    ]


def translate_logical_address(
    logical_addr: int,
    page_size: int,
    page_table: Dict[int, Tuple[int, Optional[int]]]
) -> Dict:
    """
    将逻辑地址翻译为物理地址。

    :param logical_addr: 逻辑地址
    :type logical_addr: int
    :param page_size: 页面大小（字节）
    :type page_size: int
    :param page_table: 页号 -> (存在位, 物理块号)
    :type page_table: Dict[int, Tuple[int, Optional[int]]]

    :return: 包含页号、偏移量、物理块号、物理地址和是否缺页的字典
    :rtype: Dict
    """
    page_no = logical_addr // page_size
    offset = logical_addr % page_size

    entry = page_table.get(page_no)
    if entry is None or entry[0] == 0:
        return {
            "page_no": f"0X{page_no:X}",
            "offset": f"0X{offset:X}",
            "block_no": None,
            "physical_addr": None,
            "fault": True
        }

    block_no = entry[1]
    physical_addr = block_no * page_size + offset

    return {
        "page_no": f"0X{page_no:X}",
        "offset": f"0X{offset:X}",
        "block_no": f"0X{block_no:X}",
        "physical_addr": f"0X{physical_addr:X}",
        "fault": False
    }


def show_help():
    """
    显示当前模块中所有函数的文档说明（docstring）。
    """
    current_module = sys.modules[__name__]

    print("=" * 60)
    print("Available Functions and Documentation")
    print("=" * 60)

    for name, obj in inspect.getmembers(current_module, inspect.isfunction):
        # 只显示当前模块中定义的函数，过滤掉导入的
        if obj.__module__ != __name__:
            continue

        print(f"\nFunction: {name}")
        print("-" * (10 + len(name)))

        doc = inspect.getdoc(obj)
        if doc:
            print(doc)
        else:
            print("No documentation available.")
