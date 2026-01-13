import inspect
import sys
from collections import deque
from typing import List, Tuple, Dict, Optional

import anty

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


def page_replacement_opt(page_requests: List[int], num_frames: int) -> Dict:
    """
    最佳置换算法 (OPT) 实现。
    淘汰以后最长时间不再被访问的页面。
    :param page_requests: 页面请求序列
    :type page_requests: List[int]
    :param num_frames: 内存大小（页面数量）
    :type num_frames: int
    :return: 包含算法名称、缺页次数、置换次数、访问历史的字典
    """
    frames = []
    faults = 0
    replacements = 0
    history = []

    for i in range(len(page_requests)):
        page = page_requests[i]
        hit = True
        is_replacement = False

        if page not in frames:
            hit = False
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                # 寻找以后最长时间不用的页面
                is_replacement = True
                replacements += 1
                farthest_idx = -1
                replace_idx = -1

                for f_idx, f_page in enumerate(frames):
                    try:
                        # 找到该页面下次出现的位置
                        next_use = page_requests.index(f_page, i + 1)
                    except ValueError:
                        # 以后不再使用了
                        next_use = float('inf')

                    if next_use > farthest_idx:
                        farthest_idx = next_use
                        replace_idx = f_idx

                frames[replace_idx] = page

        history.append({
            "step": i + 1, "page": page, "frames": list(frames),
            "hit": hit, "replacement": is_replacement
        })

    return {"algorithm": "OPT", "faults": faults, "replacements": replacements, "steps": history}


def page_replacement_fifo(page_requests: List[int], num_frames: int) -> Dict:
    """
    先进先出算法 (FIFO) 实现。
    淘汰最早进入内存的页面。
    :param page_requests: 页面请求序列
    :type page_requests: List[int]
    :param num_frames: 内存大小（页面数量）
    :type num_frames: int
    :return: 包含算法名称、缺页次数、置换次数、访问历史的字典
    """
    frames = []
    faults = 0
    replacements = 0
    history = []

    for i, page in enumerate(page_requests):
        hit = True
        is_replacement = False
        if page not in frames:
            hit = False
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                is_replacement = True
                replacements += 1
                frames.pop(0)  # 弹出最老的一个
                frames.append(page)

        history.append({
            "step": i + 1, "page": page, "frames": list(frames),
            "hit": hit, "replacement": is_replacement
        })

    return {"algorithm": "FIFO", "faults": faults, "replacements": replacements, "steps": history}


def page_replacement_lru(page_requests: List[int], num_frames: int) -> Dict:
    """
    最近最久未使用算法 (LRU) 实现。
    淘汰最近一段时间最久没有被访问的页面。
    :param page_requests: 页面请求序列
    :type page_requests: List[int]
    :param num_frames: 内存大小（页面数量）
    :type num_frames: int
    :return Dict: 包含算法名称、缺页次数、置换次数、访问历史的字典
    """
    frames = []  # 逻辑上：列表尾部是最近使用的
    faults = 0
    replacements = 0
    history = []

    for i, page in enumerate(page_requests):
        hit = True
        is_replacement = False
        if page in frames:
            # 命中：将页面移到末尾表示最新使用
            frames.remove(page)
            frames.append(page)
        else:
            hit = False
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                is_replacement = True
                replacements += 1
                frames.pop(0)  # 移除最久没用的（列表头）
                frames.append(page)

        history.append({
            "step": i + 1, "page": page, "frames": list(frames),
            "hit": hit, "replacement": is_replacement
        })

    return {"algorithm": "LRU", "faults": faults, "replacements": replacements, "steps": history}


def page_replacement_clock(page_requests: List[int], num_frames: int) -> Dict:
    """
    最近未用算法 (CLOCK) 实现。
    使用循环指针和访问位（use_bit）。
    :param page_requests: 页面请求序列
    :type page_requests: List[int]
    :param num_frames: 内存大小（页面数量）
    :type num_frames: int
    :return: 包含算法名称、缺页次数、置换次数、访问历史的字典
    """
    # 存储结构：[[page, use_bit], ...]
    frames_data = []
    pointer = 0
    faults = 0
    replacements = 0
    history = []

    for i, page in enumerate(page_requests):
        hit = False
        is_replacement = False

        # 检查是否命合
        for data in frames_data:
            if data[0] == page:
                hit = True
                data[1] = 1  # 命中，置访问位为1
                break

        if not hit:
            faults += 1
            if len(frames_data) < num_frames:
                # 填充阶段
                frames_data.append([page, 1])
            else:
                # 循环查找替换位
                is_replacement = True
                replacements += 1
                while True:
                    if frames_data[pointer][1] == 0:
                        # 找到访问位为0的，替换
                        frames_data[pointer] = [page, 1]
                        pointer = (pointer + 1) % num_frames
                        break
                    else:
                        # 访问位为1的清零，指针后移
                        frames_data[pointer][1] = 0
                        pointer = (pointer + 1) % num_frames

        history.append({
            "step": i + 1,
            "page": page,
            "frames": [d[0] for d in frames_data],
            "hit": hit,
            "replacement": is_replacement
        })

    return {"algorithm": "CLOCK", "faults": faults, "replacements": replacements, "steps": history}


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


def print_process(table: List[Process], quantum: int = 4):
    """
    打印进程调度结果。
    :param table: 进程列表，每个元素为 (进程名, 到达时间, 服务时间)
    :param quantum: 时间片大小
    :return: None
    """
    for func in [fcfs, sjf, hrrn, lambda x: round_robin(x, quantum)]:
        result = func(table)
        print(f"{func.__name__} scheduling:")
        print("\n".join(map(str, sorted(result, key=lambda x: ord(x["process"])))))
        print("-" * 60)

def print_page_replace(page_list: List[int], page_size: int):
    """
    打印页面置换结果。
    :param page_list: 页面请求序列
    :param page_size: 页面大小（字节）
    :return: None
    """
    for func in [page_replacement_opt, page_replacement_fifo, page_replacement_lru, page_replacement_clock]:
        res = func(page_list, page_size)
        print(f"{res['algorithm']} replacement: {res['replacements']}")


def print_translation(logical_addresses: List[int], page_size: int, page_table: List[Optional[int]]):
    """
    打印逻辑地址翻译结果。
    :param logical_addresses: 逻辑地址列表
    :param page_size: 页面大小（K字节）
    :param page_table: 按照顺序的物理块号列表[None, 0x1000, 0x2000, None, 0x3000, 0x4000, None]
    :return: None
    """
    page_table = {i: (1 if v is not None else 0, v) for i, v in enumerate(page_table)}
    for addr in logical_addresses:
        res = translate_logical_address(addr, page_size * 1024, page_table)
        print(res)


