"""GITEE API"""
import os
import argparse
import inspect
import requests
import json
import re
from argparse import ArgumentParser
from lbkit import errors
from lbkit.tools import Tools
from argparse import RawTextHelpFormatter

tools = Tools("comp_build")
log = tools.log
cwd = os.getcwd()
lb_cwd = os.path.split(os.path.realpath(__file__))[0]

class GiteeArgument(object):
    def __init__(self, option_str, help_info, default=None, required=False, action=None):
        self.option_str = option_str
        self.help_info = help_info
        self.default = default
        self.required = required
        self.action = action

class GiteeCommandInfo(object):
    def __init__(self, name, desc, callback_name):
        self.name = name
        self.desc = desc
        self.callback_name = callback_name
        self.args: list[GiteeArgument] = []
        self.args.append(GiteeArgument("--token", help_info="user's private token", default=None))
        self.args.append(GiteeArgument("--repo", help_info="repository name", default=None))
        self.args.append(GiteeArgument("--owner", help_info="repository owner", default=None))

class Gitee():
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(
            description="Build component", formatter_class=RawTextHelpFormatter)
        sub_parser = parser.add_subparsers(help="sub-commands help")
        cmd_map = {}
        for key, value in self.__class__.__dict__.items():
            if key.endswith("_args") and isinstance(value, staticmethod):
                method = getattr(Gitee, key)
                info: GiteeCommandInfo = method()
                sub:ArgumentParser = sub_parser.add_parser(info.name, help=info.desc)
                for arg in info.args:
                    sub.add_argument(arg.option_str, help=arg.help_info, default=arg.default, required=arg.required, action=arg.action)
                cmd_map[info.name] = info

        self.options = parser.parse_args(args)
        self.token = None
        self.repo = None
        self.owner = None
        # 处理公共的参数
        self.parse_public_argument()
        sub_cmd = args[0]
        info: GiteeCommandInfo = cmd_map.get(sub_cmd)
        if info is None:
            raise errors.LiteBmcException(f"Command {sub_cmd} not found")
        for member in inspect.getmembers(self, predicate=inspect.ismethod):
            if member[0] != info.callback_name:
                continue
            try:
                return member[1]()
            except json.JSONDecodeError as e:
                raise errors.RunCommandException("Json decode failed") from e
            except Exception as e:
                raise errors.HttpRequestException(f"Request failed, repo: {self.owner}/{self.repo}, method: {info.callback_name}") from e
        raise errors.RunCommandException(f"Request failed, repo: {self.owner}/{self.repo}, method {info.callback_name} not found")

    def parse_public_argument(self):
        self.token = os.environ.get("GITEE_TOKEN")
        if self.options.token is not None:
            self.token = self.options.token
        if self.token is None:
            raise errors.ArgException("Call gitee failed, you must set environment GITEE_TOKEN or run command with --token option")
        self.check_parameter_format("token", f"^[a-z0-9]+$", self.token)

        self.owner = os.environ.get("giteeTargetNamespace")
        if not self.owner:
            self.owner = os.environ.get("giteeSourceNamespace")
        if self.options.owner is not None:
            self.owner = self.options.owner
        if self.owner is None:
            raise errors.ArgException("Call gitee failed, you must set environment giteeTargetNamespace or run command with --owner option")
        self.check_parameter_format("owner", f"^[a-z0-9_a-z-]+$", self.owner)

        self.repo = os.environ.get("giteeTargetRepoName")
        if not self.repo:
            self.repo = os.environ.get("giteeSourceRepoName")
        if self.options.repo is not None:
            self.repo = self.options.repo
        if self.repo is None:
            raise errors.ArgException("Call gitee failed, you must set environment giteeTargetRepoName or run command with --repo option")
        self.check_parameter_format("repo", f"^[a-z0-9_a-z-]+$", self.repo)

    @staticmethod
    def check_parameter_format(name, regex, value):
        if re.match(regex, value) is None:
            raise errors.ArgException(f"Call gitee failed, The {name} does not satisfy the regular expression {regex}")

    @staticmethod
    def pr_add_label_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("add_label", "Add a new label for special PR", "pr_add_label")
        info.args.append(GiteeArgument("--label", help_info="label name, sparate with ',' if you want add multiple labels", required=True))
        info.args.append(GiteeArgument("--id", help_info="PR id", required=True))
        info.args.append(GiteeArgument("--replace", help_info="delete all labels before add", action="store_true"))
        return info

    def pr_add_label(self):
        self.check_parameter_format("label", "^[a-z0-9A-Z.\-,]+$", self.options.label)
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/labels?access_token={self.token}"
        body = self.options.label.split(",")
        resp = requests.post(url, json=body)
        if resp.status_code != 201:
            raise errors.HttpRequestException(f"Add label failed, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}, code: {resp.status_code}")
        log.info(f"Add label {self.options.label} successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")
        if not self.options.replace:
            return
        body = json.loads(resp.content)
        wait_delete_labels = []
        for label in body:
            name = label.get("name")
            if name != self.options.label:
                wait_delete_labels.append(name)
        if len(wait_delete_labels):
            req = ",".join(wait_delete_labels)
            url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/labels/{req}?access_token={self.token}"
            resp = requests.delete(url)
            if resp.status_code == 204:
                log.info(f"Delete labels({req}) successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")

    @staticmethod
    def pr_del_label_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("del_label", "Delete a label for special PR", "pr_del_label")
        info.args.append(GiteeArgument("--label", help_info="label name, sparate with ',' if you want delete multiple labels", required=True))
        info.args.append(GiteeArgument("--id", help_info="PR id", required=True))
        return info

    def pr_del_label(self):
        self.check_parameter_format("label", "^[a-z0-9A-Z.\-,]+$", self.options.label)
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/labels/{self.options.label}?access_token={self.token}"
        resp = requests.delete(url)
        if resp.status_code == 204:
            log.info(f"Delete labels({self.options.label}) successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")

    @staticmethod
    def pr_add_comment_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("add_comment", "Add comments with special content", "pr_add_comment")
        info.args.append(GiteeArgument("--comment", help_info="comment", required=True))
        info.args.append(GiteeArgument("--id", help_info="PR id", default=None))
        info.args.append(GiteeArgument("--sha", help_info="COMMIT sha", default=None))
        return info

    def pr_add_comment(self):
        if self.options.id is not None:
            self.check_parameter_format("id", "^[0-9]+$", self.options.id)
            url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/comments"
            body = {
                "access_token": self.token,
                "body": self.options.comment
            }
            resp = requests.post(url, json=body)
            if resp.status_code != 201:
                raise errors.HttpRequestException(f"Add comment {self.options.comment} failed, repo: {self.owner}/{self.repo}.git, " +
                                                  f"PR: {self.options.id}, status code: {resp.status_code}")
            body = json.loads(resp.content)
            id = body.get("id")
            log.info(f"Add comment {self.options.comment} successfully, comment id: {id} repo: {self.owner}/{self.repo}.git, " +
                     f"PR: {self.options.id}")
        if self.options.sha is not None:
            self.check_parameter_format("id", "^[0-9a-fA-F]{40}$", self.options.sha)
            url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/commits/{self.options.sha}/comments"
            body = {
                "access_token": self.token,
                "body": self.options.comment
            }
            resp = requests.post(url, json=body)
            if resp.status_code != 201:
                raise errors.HttpRequestException(f"Add comment {self.options.comment} failed. repo: {self.owner}/{self.repo}.git, " +
                                                  f"SHA: {self.options.sha}, status code: {resp.status_code}")
            body = json.loads(resp.content)
            id = body.get("id")
            log.info(f"Add comment {self.options.comment} successfully, comment id: {id} repo: {self.owner}/{self.repo}.git, " +
                     f"SHA: {self.options.sha}")

    @staticmethod
    def pr_del_comment_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("del_comment", "Delete comments with special content", "pr_del_comment")
        info.args.append(GiteeArgument("--comment", help_info="comment", required=True))
        info.args.append(GiteeArgument("--id", help_info="PR id", required=True))
        return info

    def pr_del_comment(self):
        self.check_parameter_format("id", "^[0-9]+$", self.options.id)
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/comments"
        get_url = url + f"?access_token={self.token}&page=1&per_page=100"
        response = requests.get(get_url)
        body = json.loads(response.content)
        if not isinstance(body, list):
            raise errors.HttpRequestException("Get all comment failed, not a list return")
        for content in body:
            id = content.get("id")
            if id is None:
                raise errors.HttpRequestException("Get invalid comment id")
            body = content.get("body")
            if body.strip() != self.options.comment:
                continue
            url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/comments/{id}?access_token={self.token}"
            resp = requests.delete(url)
            if resp.status_code != 204:
                raise errors.HttpRequestException(f"Delete comment {id} failed, code: {resp.status_code}")
            log.info(f"Delete comment {body} successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")

    @staticmethod
    def pr_set_test_state_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("set_test_state", "Set test OK", "pr_set_test_state")
        info.args.append(GiteeArgument("--id", help_info="PR id", required=True))
        return info

    def pr_set_test_state(self):
        self.check_parameter_format("id", "^[0-9]+$", self.options.id)
        body = {
            "access_token": self.token
        }
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/test"
        resp = requests.post(url, json=body)
        if resp.status_code != 204:
            raise errors.HttpRequestException(f"Set test OK failed, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}, code: {resp.status_code}")
        log.info(f"Set test OK successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")

    @staticmethod
    def pr_reset_test_state_args() -> GiteeCommandInfo:
        info = GiteeCommandInfo("reset_test_state", "Reset test state", "pr_reset_test_state")
        info.args.append(GiteeArgument("--id", help_info="PR id", required=True))
        return info

    def pr_reset_test_state(self):
        self.check_parameter_format("id", "^[0-9]+$", self.options.id)
        body = {
            "access_token": self.token
        }
        url = f"https://gitee.com/api/v5/repos/{self.owner}/{self.repo}/pulls/{self.options.id}/testers"
        resp = requests.patch(url, json=body)
        if resp.status_code != 200:
            raise errors.HttpRequestException(f"Reset test status failed, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}, code: {resp.status_code}")
        log.info(f"Reset test state successfully, repo: {self.owner}/{self.repo}.git, pr: {self.options.id}")
