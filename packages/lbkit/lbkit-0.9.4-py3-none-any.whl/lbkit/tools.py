"""任务基础类"""
import shutil
import subprocess
import inspect
import os
import sys
import tempfile
import requests
import shlex
import hashlib
import re
from lbkit.log import Logger
from lbkit import errors
from lbkit.misc import Color


class Tools(object):
    """基础工具类"""
    def __init__(self, log_name: str, log_dir: str=".temp"):
        self.log_dir = os.path.realpath(log_dir)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_name = os.path.join(self.log_dir, f"{log_name}.log")
        self.log: Logger = Logger(log_name)

    class _Tee:
        """同时写入文件和终端的类"""
        def __init__(self, file_obj, verbose: bool):
            self.file = file_obj
            self.verbose = verbose
            self.memory = ""
            self.stdout = sys.stdout
            self.stderr = sys.stderr

        def writef(self, data):
            self.file.write(data)

        def write(self, data):
            # 同时写入文件和终端
            self.memory += data
            self.file.write(data)
            if self.verbose:
                self.stdout.write(data)

        def fileno(self):
            return self.file.fileno()

        def flush(self):
            self.file.flush()
            if self.verbose:
                self.stdout.flush()

    @staticmethod
    def _real_command(shell: str):
        if not isinstance(shell, str):
            raise errors.ArgException("Command {} must be string, get: {}".format(shell, type(shell)))
        cmd = shlex.split(shell)
        if len(cmd) == 0 or len(cmd[0].strip()) == 0:
            raise errors.ArgException("Command is empty")
        for c in cmd:
            if not isinstance(c, str):
                raise errors.ArgException("Command {} with type error, must be string, get: {}"
                                          .format(c, type(shell)))
        if cmd[0].find("./") >= 0:
            raise errors.ArgException("Command {} can't be relative path")
        which_cmd = shutil.which(cmd[0])
        if which_cmd is None:
            raise errors.NotFoundException(f"Command {cmd[0]} not found")
        cmd[0] = which_cmd
        if cmd[0] == shutil.which("sudo"):
            raise errors.ArgException("Can't run command with sudo, get: {}".format(shell))
        return cmd

    def exec(self, cmd: str, verbose=False, ignore_error = False, sensitive=False, log_prefix="", **kwargs):
        """执行命令，输出同时写入日志文件和终端"""
        stack = inspect.stack()[1]
        file = os.path.basename(stack.filename)
        line = stack.lineno
        echo_cmd = kwargs.get("echo_cmd", True)
        log_name = kwargs.get("log_name", self.log_name)
        uptrace = kwargs.get("uptrace", 0) + 1
        show_cmd = "***" if sensitive else cmd
        if log_prefix:
            show_cmd = "(" + log_prefix + ") " + show_cmd

        if os.environ.get("VERBOSE", False):
            verbose = True
        fd = os.fdopen(os.open(log_name, os.O_APPEND | os.O_CREAT | os.O_RDWR), "a+")
        # 使用 _Tee 类同时写入文件和终端
        msg = "{}>>>>{} {}\n".format(Color.GREEN, Color.RESET_ALL, show_cmd)
        tee = self._Tee(fd, verbose)
        if echo_cmd:
            sys.stdout.write(msg)
        tee.writef(msg)
        real_cmd = self._real_command(cmd)
        result = subprocess.Popen(real_cmd, stdout=tee, stderr=tee, universal_newlines=True)
        tee.flush()
        fd.close()
        if result is None:
            raise errors.RunCommandException(f"Run command {show_cmd} failed")
        result.communicate()
        if result.returncode == 0:
            return result
        if not ignore_error:
            msg = f"{file}:{line} > Run command ({show_cmd}) failed, log file is {log_name}"
            if not verbose:
                self.log.warn(f">>>>>>>>>> '{show_cmd}' LOG START", uptrace=uptrace)
                sys.stdout.write(tee.memory)
                sys.stdout.flush()
                self.log.warn(f"<<<<<<<<<< '{show_cmd}' LOG END", uptrace=uptrace)
            raise errors.RunCommandException(msg)
        else:
            msg = f"{file}:{line} > Run command ({show_cmd}) failed but ignore error"
        self.log.warn(msg, uptrace=uptrace)
        return result

    def pipe(self, cmds: list[str], ignore_error=False, out_file = None, **kwargs):
        uptrace = kwargs.get("uptrace", 0) + 1
        if not isinstance(cmds, list):
            raise errors.ArgException("Command ({}) with type error, only list[str] can be accepted".format(cmds))
        if out_file and os.path.isfile(out_file):
            fp = open(out_file, "w")
            fp.close()
        stdin = None
        for cmd in cmds:
            self.log.debug("{}>>>>{} {}".format(Color.GREEN, Color.RESET_ALL, cmd), uptrace=uptrace)
            stdout = tempfile.TemporaryFile("w+b")
            real_cmd = self._real_command(cmd)
            ret = subprocess.Popen(real_cmd, stdout=stdout, stdin=stdin)
            if ret is None:
                raise errors.RunCommandException(f"Run command {real_cmd[0]} failed")
            ret.communicate()
            if ret.returncode != 0:
                error_log = "Run command ({}) failed, error: {}".format(cmd, ret.stderr)
                error_log = kwargs.get("error_log", error_log)
                if ignore_error:
                    if error_log:
                        self.log.info(error_log)
                    return
                raise errors.RunCommandException(error_log)
            if stdin:
                stdin.close()
            stdin = stdout
            stdin.seek(0)

        stdin.seek(0)
        output = stdin.read()
        if out_file:
            with open(out_file, "w+b") as fp:
                fp.write(output)
        stdin.close()
        return output

    def run(self, cmd, ignore_error=False, stdout=None, stderr=None, **kwargs):
        uptrace = kwargs.get("uptrace", 0) + 1
        capture_output = kwargs.get("capture_output", True)
        self.log.debug("{}>>>>{} {}".format(Color.GREEN, Color.RESET_ALL, cmd), uptrace=uptrace)
        real_cmd = self._real_command(cmd)
        check = False if ignore_error else True
        if stdout or stderr:
            return subprocess.run(real_cmd, check=check, stdout=stdout, stderr=stderr, encoding="utf-8")
        else:
            return subprocess.run(real_cmd, capture_output=capture_output, check=check, encoding="utf-8")

    @staticmethod
    def file_digest_sha256(filename):
        """计算文件的sha256值"""
        sha256 = hashlib.sha256()
        fp = open(filename, "rb")
        while True:
            data = fp.read(65536)
            if len(data) == 0:
                break
            sha256.update(data)
        fp.close()
        return sha256.hexdigest()

    def download(self, url, dst_file, sha256sum = None):
        """下载文件"""
        self.log.info("Start download %s", url, uptrace=2)
        is_local = False
        if url.startswith("file://"):
            path = url[7:]
            shutil.copyfile(path, dst_file)
            is_local = True
        if os.path.isfile(dst_file):
            digest = self.file_digest_sha256(dst_file)
            if sha256sum is None or digest == sha256sum:
                return
            if is_local:
                raise errors.DigestNotMatchError(f"File {dst_file} with sha256 error, need: {sha256sum}, get: {digest}")
            os.unlink(dst_file)
        verify = os.environ.get("HTTPS_VERIFY", True)
        if verify:
            response = requests.get(url, timeout=30, verify=True)
        else:
            response = requests.get(url, timeout=30)
        fp = open(dst_file, "wb")
        fp.write(response.content)
        fp.close()
        digest = self.file_digest_sha256(dst_file)
        if sha256sum is None or digest == sha256sum:
            self.log.info("Download %s successfully", url, uptrace=2)
            return
        raise errors.DigestNotMatchError(f"File {dst_file} with sha256 error, need: {sha256sum}, get: {digest}")

def hump2underline(hunp_str):
    # 匹配正则，匹配小写字母和大写字母的分界位置
    p = re.compile(r'([a-z]|\d)([A-Z])')
    # 这里第二个参数使用了正则分组的后向引用
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub