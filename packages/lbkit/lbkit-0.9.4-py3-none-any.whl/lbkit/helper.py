import os
import yaml
import unittest
from xml.dom import minidom, Node

class Helper():
    @staticmethod
    def get_node_value(dom: Node, name, default=None):
        node: minidom.Attr = dom.attributes.get(name)
        if node is None:
            if default is None:
                raise Exception("Parse node failed, abort")
            return default
        return node.childNodes[0].nodeValue.strip()

    def read_yaml(file: str, key, default=None):
        if not os.path.isfile(file):
            return default
        fd = open(file, "r")
        try:
            data = yaml.load(fd, Loader=yaml.FullLoader)
            for split in key.split("/", -1):
                data = data.get(split)
                if data is None:
                    return default
            return data
        except:
            return default


generate_sig_chars = [
    "y", "b", "n", "q", "i", "u", "x", "t", "h",
    "d", "v", "s", "o", "g"]


class SigInvalidException(Exception):
    pass

def _validate_glib_signature(sig_str, sigs):
    if len(sigs) == 0:
        raise SigInvalidException(f"String {sig_str} is not a valid signature str")
    if sigs[0] in generate_sig_chars:
        if len(sigs) > 1:
            return _validate_glib_signature(sig_str, sigs[1:])
        return
    if sigs[0] == "a":
        return _validate_glib_signature(sig_str, sigs[1:])
    if sigs[0] in ["(", "{"]:
        next_chr = ")"
        if sigs[0] == "{":
            next_chr = "}"

        cnt = 0
        next_pos = -1
        for i, c in enumerate(sigs):
            if c == sigs[0]:
                cnt += 1
            elif c == next_chr:
                cnt -= 1
            if cnt == 0:
                next_pos = i
                break
        # 未找到下一个右括号
        if next_pos == -1:
            raise SigInvalidException(f"String {sig_str} is not a valid signature str")
        # 元组()之间可以为空
        if sigs[0] == '(' and next_pos == 1:
            return
        if sigs[0] == "{":
            # 字典至少需要两个字符
            if next_pos < 3:
                raise SigInvalidException(f"String {sig_str} is not a valid signature str")
            # 字典第一个签名必须是简单类型
            if sigs[1] not in generate_sig_chars:
                raise SigInvalidException(f"String {sig_str} is not a valid signature str")
        _validate_glib_signature(sig_str, sigs[1:next_pos])
        sigs = sigs[next_pos + 1:]
        if not sigs:
            return
        _validate_glib_signature(sig_str, sigs)
        return

    # '}' 和 ')'及其它字符起始的认为是非法字符
    raise SigInvalidException(f"String {sig_str} is not a valid signature str")


def validate_glib_signature(sig_str):
    _validate_glib_signature(sig_str, list(sig_str))


class TestSignatureValidateClass(unittest.TestCase):
    def test_validate_glib_signature(self):
        validate_glib_signature("as")

if __name__ == "__main__":
    unittest.main()