"""环境准备"""
import os
import requests
import shutil
import time
import traceback
from functools import partial

from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger
from lbkit.tools import Tools
from multiprocessing.pool import Pool, ApplyResult
from lbkit.misc import DownloadFlag

log = Logger("build_image")

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class DownloadTask():
    def __init__(self, record, dst_dir):
        self.url = record.get("url")
        self.file = record.get("file")
        self.decompress = record.get("decompress", {})
        self.dirname = self.decompress.get("dirname")
        self.strip_components = self.decompress.get("strip_components")
        self.dst = os.path.join(dst_dir, self.file)
        self.dst = os.path.realpath(self.dst)
        if not self.dst.startswith(dst_dir):
            raise Exception(f"Download {self.file} failed because file contain relative paths")
        dir = os.path.dirname(self.dst)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        self.sha256 = record.get("sha256")
        self.verify = record.get("verify", True)

    def start(self):
        last = time.time()
        if os.path.isfile(self.dst):
            calc_sha = Tools.file_digest_sha256(self.dst)
            # 需要校验hash且hash不一致时删除文件
            if self.sha256 != "any":
                if self.sha256 != calc_sha:
                    os.unlink(self.dst)
                else:
                    return
            else:
                url, hash = DownloadFlag.read(self.dst)
                # flash标志文件记录的url、hash一致时无需重复下载
                if  url == self.url and hash == calc_sha:
                    return
        print(f"Start downloading {self.file} from {self.url}")
        DownloadFlag.clean(self.dst)
        req = requests.get(self.url, stream=True, verify=self.verify, timeout=30)
        req.raise_for_status()
        total_size = int(req.headers.get('content-length', 0))
        total_down = 0
        fp = open(self.dst, 'wb')
        for chunk in req.iter_content(chunk_size=16384):
            if chunk:
                fp.write(chunk)
                total_down += len(chunk)
                now = time.time()
                # 每30秒打印一次进度
                if now - last > 30:
                    print(f"File {self.dst} is downloading, downloaded {total_down} / {total_size} ")
                    last = now
        fp.close()
        calc_sha = Tools.file_digest_sha256(self.dst)
        if self.sha256 != "any" and calc_sha != self.sha256:
            os.unlink(self.dst)
            raise Exception(f"File {self.file} downloaded but sha256 not match, need: {self.sha256}, get: {calc_sha}")
        DownloadFlag.create(self.dst, self.url, calc_sha)


def download_filed(error, pool: Pool):
    print(f"download file failed, error: {str(error)}")
    pool.terminate()


class TaskClass(Task):
    def run(self):
        records = self.config.get_manifest_config("download", [])
        if not records:
            return
        tasks: dict[str, DownloadTask] = {}
        temps: list[DownloadTask] = []
        for rec in records:
            task =  DownloadTask(rec, self.config.download_path)
            temps.append(task)
            if not os.path.isfile(task.dst):
                with open(task.dst, "w+") as _:
                    pass
        for task in temps:
            if not task.url.startswith("file://"):
                if tasks.get(task.file):
                    raise Exception(f"manifest.yml configuration error, file {task.file} repeatedly")
                tasks[task.file] = task
                continue
            DownloadFlag.clean(task.dst)
            src = task.url[7:]
            # 源文件不存在
            if not os.path.isfile(src):
                raise Exception(f"Download failed, file {task.url} not exist")
            if os.path.isfile(task.dst):
                os.unlink(task.dst)
            shutil.copyfile(src, task.dst)
            calc_hash = self.tools.file_digest_sha256(task.dst)
            DownloadFlag.create(task.dst, task.url, calc_hash)
        pool = Pool()
        results: list[(ApplyResult, DownloadTask)] = []
        for _, task in tasks.items():
            ec = partial(download_filed, pool=pool)
            result = pool.apply_async(task.start, error_callback=ec)
            results.append((result, task))
        pool.close()
        pool.join()
        for result in results:
            if not result[0].ready():
                raise Exception(f"Download file {result[1].file} failed")
            try:
                result[0].get()
            except:
                log.error("Download with exception")
                traceback.print_exc()
                return -1
        for task in temps:
            if not task.decompress:
                continue
            dirname = os.path.join(self.config.download_path, task.dirname)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            cmd = f"tar -xf {task.dst} -C {dirname}"
            if task.strip_components:
                cmd += f" --strip-components={task.strip_components}"
            self.exec(cmd)
        return 0


if __name__ == "__main__":
    config = Config()
    build = TaskClass(config, "test")
    build.run()