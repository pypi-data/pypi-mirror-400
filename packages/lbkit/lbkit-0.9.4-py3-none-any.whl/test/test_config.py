import unittest
from lbkit.tasks.config import Config

class TestConfig(unittest.TestCase):
    def test_config_merge_config(self):
        src = "123"
        dst = "abc"
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = None
        dst = "abc"
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, dst)
        src = "123"
        dst = None
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = ["123"]
        dst = None
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = ["123"]
        dst = ["abc"]
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = []
        dst = ["abc"]
        out = Config.merge_cfg(dst, src)
        src = None
        dst = ["abc"]
        out = Config.merge_cfg(dst, src)
        src = None
        dst = []
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, dst)
        src = {"key1": "val1"}
        dst = {"key1": "val2"}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = {"key1": "val1", "key2": [123, 234]}
        dst = {"key1": "val2"}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, src)
        src = {"key2": [123, 234]}
        dst = {"key1": "val2"}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, {"key1": "val2", "key2": [123, 234]})
        src = {"key2": [123, 234]}
        dst = {"key1": "val2", "key2": [456]}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, {"key1": "val2", "key2": [123, 234]})
        src = {"key2": [123, 234]}
        dst = {"key1": "val2", "key2": []}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, {"key1": "val2", "key2": [123, 234]})
        src = {"key2": [123, 234]}
        dst = {"key1": "val2", "key2": None}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, {"key1": "val2", "key2": [123, 234]})
        src = {"key2": None}
        dst = {"key1": "val2", "key2": []}
        out = Config.merge_cfg(dst, src)
        self.assertEqual(out, {"key1": "val2", "key2": []})

if __name__ == "__main__":
    unittest.main()