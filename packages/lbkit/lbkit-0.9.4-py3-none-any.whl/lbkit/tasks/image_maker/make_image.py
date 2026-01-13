"""环境准备"""
import os
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task


class TaskMakeImage(Task):
    def available(self):
        return False

    def run(self):
        return

if __name__ == "__main__":
    config = Config()
    build = TaskMakeImage(config, "test")
    build.run()