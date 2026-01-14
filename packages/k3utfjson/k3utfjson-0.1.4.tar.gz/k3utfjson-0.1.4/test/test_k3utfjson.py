import os
import unittest

import k3ut
import k3utfjson
import json

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestUTFJson(unittest.TestCase):
    def test_load(self):
        self.assertEqual(None, k3utfjson.load(None))
        self.assertEqual({}, k3utfjson.load("{}"))

        # load unicode, result in utf-8

        self.assertEqual("我", k3utfjson.load('"\\u6211"'))
        self.assertEqual(str, type(k3utfjson.load('"\\u6211"')))

        # unicode and string in a dictionary.

        obj = '{"a": "\u6211", "b": "1"}'
        rst = k3utfjson.load(obj)

        self.assertEqual({"a": b"\xe6\x88\x91".decode("utf-8"), "b": "1"}, rst)
        self.assertEqual(str, type(rst["a"]))
        self.assertEqual(str, type(rst["b"]))

        # load utf-8, result in str

        rst = k3utfjson.load(b'"\xe6\x88\x91"')
        self.assertEqual("我", rst)
        self.assertEqual(str, type(rst))

        # load gbk, result in str, in gbk encoding

        gbk = b'"\xb6\xd4\xd5\xbd\xc6\xbd\xcc\xa8\xb9\xd9\xb7\xbd\xd7\xee\xd0\xc2\xb0\xe6"'
        self.assertEqual("对战平台官方最新版", k3utfjson.load(gbk, encoding="gbk"))
        self.assertEqual(str, type(k3utfjson.load(gbk, encoding="gbk")))

        # load any

        s = '"\xbb"'
        rst = k3utfjson.load(s)
        self.assertEqual("\xbb", rst)
        self.assertEqual(str, type(rst))

    def test_load_backslash_x_encoded(self):
        s = '"\x61"'
        self.assertEqual("a", k3utfjson.load(s))

        s = '"\x61"'
        self.assertEqual("a", k3utfjson.load(s))

        s = b'"\xe6\x88\x91"'
        self.assertEqual("我", k3utfjson.load(s))

        self.assertRaises(json.JSONDecodeError, k3utfjson.load, '"\\"')
        self.assertRaises(json.JSONDecodeError, k3utfjson.load, '"\\x"')
        self.assertRaises(json.JSONDecodeError, k3utfjson.load, '"\\x6"')

    def test_load_decode(self):
        self.assertEqual("我", k3utfjson.load('"我"'))
        self.assertEqual("我", k3utfjson.load('"我"', encoding="utf-8"))
        self.assertEqual(str, type(k3utfjson.load('"我"', encoding="utf-8")))

        self.assertEqual({"a": "我"}, k3utfjson.load('{"a": "\\u6211"}'))
        self.assertEqual({"a": "我"}, k3utfjson.load('{"a": "我"}', encoding="utf-8"))
        self.assertEqual({"a": "我"}, k3utfjson.load('{"a": "我"}'))
        self.assertEqual({"a": "我"}, k3utfjson.load('{"a": "我"}'))
        self.assertEqual(["我"], k3utfjson.load('["我"]'))

    def test_dump(self):
        self.assertEqual("null", k3utfjson.dump(None))
        self.assertEqual("{}", k3utfjson.dump({}))

        self.assertRaises(TypeError, k3utfjson.dump, b"\xe6\x88\x91", encoding=None)
        self.assertRaises(TypeError, k3utfjson.dump, {b"\xe6\x88\x91": 1}, encoding=None)
        self.assertRaises(TypeError, k3utfjson.dump, {1: b"\xe6\x88\x91"}, encoding=None)
        self.assertRaises(TypeError, k3utfjson.dump, [b"\xe6\x88\x91"], encoding=None)
        self.assertRaises(TypeError, k3utfjson.dump, [(b"\xe6\x88\x91",)], encoding=None)

        self.assertEqual('"\\u6211"', k3utfjson.dump("我", encoding=None))
        self.assertEqual('"' + b"\xb6\xd4".decode("gbk") + '"', k3utfjson.dump("对", encoding="gbk"))
        self.assertEqual('"' + b"\xe6\x88\x91".decode("utf-8") + '"', k3utfjson.dump("我", encoding="utf-8"))

        self.assertEqual('"' + b"\xe6\x88\x91".decode("utf-8") + '"', k3utfjson.dump("我"))
        self.assertEqual('"' + b"\xe6\x88\x91".decode("utf-8") + '"', k3utfjson.dump("我"))

        # by default unicode are encoded

        self.assertEqual(
            '{"' + b"\xe6\x88\x91".decode("utf-8") + '": "' + b"\xe6\x88\x91".decode("utf-8") + '"}',
            k3utfjson.dump({"我": "我"}),
        )
        self.assertEqual(
            '{"' + b"\xe6\x88\x91".decode("utf-8") + '": "' + b"\xe6\x88\x91".decode("utf-8") + '"}',
            k3utfjson.dump({"我": "我"}),
        )
        self.assertEqual(
            '{"' + b"\xe6\x88\x91".decode("utf-8") + '": "' + b"\xe6\x88\x91".decode("utf-8") + '"}',
            k3utfjson.dump({"我": "我"}),
        )
        self.assertEqual(
            '{"' + b"\xe6\x88\x91".decode("utf-8") + '": "' + b"\xe6\x88\x91".decode("utf-8") + '"}',
            k3utfjson.dump({"我": "我"}),
        )
        self.assertEqual('["' + b"\xe6\x88\x91".decode("utf-8") + '"]', k3utfjson.dump(("我",)))

        self.assertEqual('{"\\u6211": "\\u6211"}', k3utfjson.dump({"我": "我"}, encoding=None))

        self.assertEqual('"\\""', k3utfjson.dump('"'))

        # encoded chars and unicode chars in one string
        self.assertEqual(
            "/aaa\xe7\x89\x88\xe6\x9c\xac/jfkdsl\x01",
            k3utfjson.load('"\\/aaa\xe7\x89\x88\xe6\x9c\xac\\/jfkdsl\\u0001"'),
        )

        self.assertEqual('{\n  "我": "我"\n}', k3utfjson.dump({"我": "我"}, indent=2))
        self.assertEqual('{\n    "我": "我"\n}', k3utfjson.dump({"我": "我"}, indent=4))
