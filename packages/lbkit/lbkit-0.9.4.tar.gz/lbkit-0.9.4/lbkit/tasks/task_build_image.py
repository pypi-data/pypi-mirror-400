"""环境准备"""
import os
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger
from lbkit.tasks.image_maker.make_rockchip_image import TaskMakeRockchipImage
from lbkit.tasks.image_maker.make_qemu_image import TaskMakeQemuImage

log = Logger("build_image")

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class TaskClass(Task):
    def run(self):
        """任务入口"""
        maker = TaskMakeRockchipImage(self.config, self.name)
        if maker.available():
            maker.run()
            return 0
        maker = TaskMakeQemuImage(self.config, self.name)
        if maker.available():
            maker.run()
            return 0
        return -1

if __name__ == "__main__":
    config = Config()
    build = TaskClass(config, "test")
    build.run()