#! /usr/bin/env python3

import importlib
import os
import time
import traceback
import sys
import psutil

from multiprocessing import Process
from multiprocessing import Manager
from lbkit.errors import LiteBmcException
from lbkit.tools import Tools
from lbkit.tasks.config import Config
from lbkit.utils.env_detector import EnvDetector
import lbkit.misc as misc
from lbkit.misc import load_yml_with_json_schema_validate

# 任务失败状态
TASK_STATUS_FAILED = "Failed"
TASK_STATUS_SUCCED = "succed"
TASK_STATUS_EXCEPT = "Except"
TASK_STATUS_RUNNING = "Runing"
tool = Tools("executor")
log = tool.log
manager = Manager()
status_dict = manager.dict()
status_lock = manager.Lock()


def wait_finish(target_name, wait_list):
    """
    等待任务结束
    """
    if not wait_list:
        return True
    start_time = time.time()
    cnt = 0
    while True:
        finish = True
        time.sleep(0.1)
        for work_name in wait_list:
            cur_time = time.time()
            key = target_name + "/" + work_name
            status = status_dict.get(key)
            if status is None:
                log.warn(f"等待不存在的任务{key}。如果要等待一个任务，这个任务必须在当前任务之前运行，否则触发异常")
                return False
            if status == TASK_STATUS_SUCCED:
                continue
            if status == TASK_STATUS_FAILED or status == TASK_STATUS_EXCEPT:
                return False
            finish = False
            # 每等待60s打印一次日志
            if int(cur_time - start_time) >= 60:
                start_time = time.time()
                cnt += 60
                log.info("目标 {} 正在等待任务: {}, 当前已等待 {} 秒".format(target_name, work_name, cnt))
            break
        if finish:
            return True


class TaskExecutor():
    '''
    '''
    def __init__(self, target_name, work, config: Config):
        super().__init__()
        self.work = work
        self.config: Config = config
        self.target_name = target_name
        self.work_name = self.work.get("task", "")
        self.status_key = target_name + "/" + self.work_name
        chunks = self.work_name.split(".", -1)
        if len(chunks) == 1:
            self.task_path = ""
            self.work_name = chunks[1]
        else:
            self.task_path = "lbkit.tasks." + chunks[0]
            self.work_name = chunks[1]
        self.exception = None

    def load_class(self):
        if not self.task_path:
            return None
        log.debug("工作路径: {}".format(self.task_path))
        work_py_file = importlib.import_module(self.task_path)
        return getattr(work_py_file, "TaskClass")

    def run(self):
        '''
        功能描述：执行任务
        '''
        work_name = self.work_name
        log.debug(f"任务{self.status_key}已就绪")
        ret = wait_finish(self.target_name, self.work.get("wait"))
        if not ret:
            log.debug(f"任务{self.status_key}等待的其它任务发生错误")
            return -1
        work_class = self.load_class()
        # 如果未指定类时，不需要执行
        if work_class is not None:
            work_x = work_class(self.config, work_name)
            # work配置项和target配置项
            work_config = self.work.get("config")
            work_x.deal_conf(work_config)
            with status_lock:
                status = status_dict.get(self.status_key)
                if status is None:
                    status_dict[self.status_key] = TASK_STATUS_RUNNING
            if status is None:
                # 创建进程并且等待完成或超时
                ret = work_x.run()
                if ret is not None and ret != 0:
                    return -1
            else:
                # 不需要创建进程，等待任务执行完成即可
                wait_list = []
                wait_list.append(work_name)
                ret = wait_finish(self.target_name, wait_list)
                if not ret:
                    log.debug(f"任务{self.status_key}等待的其它任务发生错误")
                    return -1

            log.debug(f"任务 {work_name} 开始安装步骤")

        # 创建子任务
        ret = exec_works(self.work.get("subtasks", []), self.config, os.cpu_count())
        ret = ret and exec_works(self.work.get("seqtasks", []), self.config, 1)
        if not ret:
            status_dict[self.status_key] = TASK_STATUS_FAILED
            return -1

        log.success(f"任务 {work_name} 完成")
        with status_lock:
            status_dict[self.status_key] = TASK_STATUS_SUCCED
        return 0

def task_handler(te:TaskExecutor):
    try:
        ret = te.run()
    except Exception as e:
        traceback.print_exc()
        log.error(f"Task {te.status_key} exit with exceiption: {str(e)}")
        with status_lock:
            status_dict[te.status_key] = TASK_STATUS_EXCEPT
        return -1
    if ret != 0:
        with status_lock:
            status_dict[te.status_key] = TASK_STATUS_FAILED
        return -1
    else:
        with status_lock:
            status_dict[te.status_key] = TASK_STATUS_SUCCED
        return 0


class TaskInfo():
    def __init__(self, te: TaskExecutor, proc: Process):
        self.te = te
        self.proc = proc


def kill_process_and_children(pid):
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    children = parent.children(recursive=True)
    for child in children:
        child.terminate()

    parent.terminate()


def wait_tasks(tasks: dict[str, TaskInfo], alow_processes_alive=0):
    while True:
        new_results = {}
        cnt = 0
        killall = False
        for key, ti in tasks.items():
            if ti.proc.is_alive():
                new_results[key] = ti
                cnt += 1
                continue
            with status_lock:
                status = status_dict.get(ti.te.status_key)
            if status == TASK_STATUS_EXCEPT or status == TASK_STATUS_FAILED:
                killall = True
                break
        if killall:
            for _, ti in tasks.items():
                kill_process_and_children(ti.proc.pid)
            return None, False
        tasks = new_results
        if cnt > 0 and cnt >= alow_processes_alive:
            time.sleep(0.1)
        else:
            return new_results, True

def exec_works(work_list, config, processes):
    if not work_list:
        return True
    # 创建任务并等待完成
    results: dict[str, TaskInfo] = {}
    for work in work_list:
        te = TaskExecutor(config.target, work, config)
        result = Process(target=task_handler, args=(te, ))
        results[te.status_key] = TaskInfo(te, result)
        result.start()
        results, ok = wait_tasks(results, processes)
        if not ok:
            return False
    _, ok = wait_tasks(results, 0)
    return ok


def target_executor(config):
    log.info(f"创建新目标 {config.target} 构建计划表")
    manifest_target = f"{config.code_path}/targets/{config.target}.yml"
    lbkit_target = os.path.join(misc.TARGETS_DIR, config.target + ".yml")
    if os.path.isfile(manifest_target):
        target_file = manifest_target
    elif os.path.isfile(lbkit_target):
        target_file = lbkit_target
    else:
        raise Exception(f"构建目标文件 [target_]{config.target}.yml 不存在")

    # 读取配置
    work_list = load_yml_with_json_schema_validate(target_file, os.path.join(misc.TARGETS_DIR, "tdf.v1.json"))
    target_cfg = work_list.get("config", {})
    config.deal_conf(target_cfg)
    environments = work_list.get("env", {})
    for key, value in environments.items():
        log.success(f"配置环境变量 {key}: {value}")
        os.environ[key] = value
    # 打印任务清单
    log.debug(f"任务列表:{work_list}")
    # 创建任务调度器
    ret = exec_works(work_list.get("subtasks", []), config, os.cpu_count())
    ret = ret and exec_works(work_list.get("seqtasks", []), config, 1)
    return ret


class Executor(object):
    def __init__(self, env: EnvDetector):
        if not env.manifest:
            raise LiteBmcException("未找到manifest.yml配置文件，当前目录不是一个合法的产品配置仓")
        os.chdir(env.manifest.folder)

    def run(self):
        target = ""
        succ = False
        try:
            config = Config(sys.argv[2:])
            target = config.target
            succ = target_executor(config)
        except Exception as e:
            traceback.print_exc()
            raise Exception(f"任务 {target} 执行失败")
        if succ:
            log.success(f"任务 {target} 执行成功")
            return 0
        else:
            raise Exception(f"任务 {target} 执行失败")

if __name__ == "__main__":
    env = EnvDetector()
    exec = Executor(env)
    exec.run()
