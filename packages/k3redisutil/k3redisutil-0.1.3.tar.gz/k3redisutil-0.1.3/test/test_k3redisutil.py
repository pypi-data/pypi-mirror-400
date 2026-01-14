import mock
import os
import sys
import time
import unittest
import urllib.parse

from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

import k3redisutil
import k3thread
import k3utdocker
import k3ut
import k3utfjson

dd = k3ut.dd

redis_tag = "redis:7-alpine"

redis_port = 6379


class TestRedis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        k3utdocker.pull_image(redis_tag)

    def setUp(self):
        self.containers = [
            ("redis-0", redis_tag, "192.168.52.40"),
            ("redis-1", redis_tag, "192.168.52.41"),
        ]
        self.docker_name = "redis-0"
        self.ip = "192.168.52.40"

        k3utdocker.create_network()

        for args in self.containers:
            k3utdocker.start_container(*(args + ("",)))
            dd("started redis in docker: " + repr(args))

            k3redisutil.wait_serve((args[2], redis_port))

        self.rcl = k3redisutil.get_client((self.ip, redis_port))

    def tearDown(self):
        for args in self.containers:
            dd("remove_container: " + args[0])
            k3utdocker.remove_container(args[0])

    def test_set_get(self):
        hname = "foo"

        rst = self.rcl.hset(hname, "a", "1")
        dd("hset rst:", rst)

        rst = self.rcl.hget(hname, "a")
        dd("hget rst:", rst)

        self.assertEqual(b"1", rst)


class TestRedisRecreate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        k3utdocker.pull_image(redis_tag)

    def setUp(self):
        self.containers = [
            ("redis-0", redis_tag, "192.168.52.40"),
            ("redis-1", redis_tag, "192.168.52.41"),
        ]

        # for single redis cases:
        self.docker_name = "redis-0"
        self.ip = "192.168.52.40"
        self.is_child = False

        k3utdocker.create_network()

        for args in self.containers:
            k3utdocker.start_container(*(args + ("",)))
            dd("started redis in docker: " + repr(args))

            k3redisutil.wait_serve((args[2], redis_port))

        self.rcl = k3redisutil.get_client((self.ip, redis_port))

    def tearDown(self):
        # do not tear down in child process
        if self.is_child:
            return

        for args in self.containers:
            dd("remove_container: " + args[0])
            k3utdocker.remove_container(args[0])

    def test_recreate_client(self):
        hname = "foo"

        pid = os.fork()

        dd("my pid:", os.getpid())

        if pid == 0:
            # child
            self.is_child = True
            rcl = k3redisutil.get_client((self.ip, redis_port))
            rcl.hset(hname, "a", "5")

            rcl.close()
        else:
            # parent

            os.waitpid(pid, 0)
            dd("child pid quit: " + repr(pid))

            rst = self.rcl.hget(hname, "a")

            dd("redis hget rst:", rst)

            self.assertEqual(b"5", rst)


class TestRedisProxyClient(unittest.TestCase):
    response = {}
    request = {}
    access_key = "test_accesskey"
    secret_key = "test_secretkey"

    def setUp(self):
        self.addr = ("127.0.0.1", 22038)
        self.proxy_addr = ("127.0.0.1", 22039)

        self.response["http-status"] = 200

        def _start_http_svr():
            self.http_server = HTTPServer(self.addr, HttpHandle)
            self.http_server.serve_forever()

        def _start_proxy_http_svr():
            self.proxy_http_server = HTTPServer(self.proxy_addr, HttpHandle)
            self.proxy_http_server.serve_forever()

        k3thread.start(_start_http_svr)
        k3thread.start(_start_proxy_http_svr)
        time.sleep(0.1)

        self.cli = k3redisutil.RedisProxyClient([self.addr])
        self.n = self.cli.n
        self.w = self.cli.w
        self.r = self.cli.r

    def tearDown(self):
        self.http_server.shutdown()
        self.http_server.server_close()
        self.proxy_http_server.shutdown()
        self.proxy_http_server.server_close()

    def test_proxy_get(self):
        cli = k3redisutil.RedisProxyClient([self.addr], proxy_hosts=[[self.proxy_addr]])

        res = cli.get("foo")
        time.sleep(0.1)
        exp_res = {"foo": 1, "bar": 2}
        self.assertDictEqual(exp_res, res)

        self.http_server.shutdown()
        self.http_server.server_close()
        res = cli.get("foo")
        time.sleep(0.1)
        self.assertDictEqual(exp_res, res)

        self.response["http-status"] = 404
        self.assertRaises(k3redisutil.KeyNotFoundError, cli.get, "foo")

        self.response["http-status"] = 500
        self.assertRaises(k3redisutil.ServerResponseError, cli.get, "foo")

        self.proxy_http_server.shutdown()
        self.proxy_http_server.server_close()
        self.assertRaises(k3redisutil.SendRequestError, cli.get, "foo")

    def test_proxy_set(self):
        cli = k3redisutil.RedisProxyClient([self.addr], proxy_hosts=[[self.proxy_addr]])
        # expect no exception
        cli.set("foo", "bar")

        self.response["http-status"] = 500
        self.assertRaises(k3redisutil.ServerResponseError, cli.set, "foo", "bar")

        self.response["http-status"] = 200
        self.proxy_http_server.shutdown()
        self.proxy_http_server.server_close()
        self.assertRaises(k3redisutil.SendRequestError, cli.set, "foo", "bar")

        self.http_server.shutdown()
        self.http_server.server_close()
        self.assertRaises(k3redisutil.SendRequestError, cli.set, "foo", "bar")

    def test_send_request_failed(self):
        # close http server
        self.tearDown()

        self.assertRaises(k3redisutil.SendRequestError, self.cli.get, "foo")
        self.assertRaises(k3redisutil.SendRequestError, self.cli.set, "foo", "bar")

        self.assertRaises(k3redisutil.SendRequestError, self.cli.hget, "foo", "bar")
        self.assertRaises(k3redisutil.SendRequestError, self.cli.hset, "foo", "bar", "xx")

        self.assertRaises(k3redisutil.SendRequestError, self.cli.hkeys, "foo")
        self.assertRaises(k3redisutil.SendRequestError, self.cli.hvals, "foo")
        self.assertRaises(k3redisutil.SendRequestError, self.cli.hgetall, "foo")

        self.assertRaises(k3redisutil.SendRequestError, self.cli.delete, "foo")
        self.assertRaises(k3redisutil.SendRequestError, self.cli.hdel, "foo", "bar")

    def test_not_found(self):
        self.response["http-status"] = 404
        self.assertRaises(k3redisutil.KeyNotFoundError, self.cli.get, "foo")
        self.assertRaises(k3redisutil.KeyNotFoundError, self.cli.hget, "foo", "bar")
        self.assertRaises(k3redisutil.KeyNotFoundError, self.cli.hkeys, "foo")
        self.assertRaises(k3redisutil.KeyNotFoundError, self.cli.hvals, "foo")
        self.assertRaises(k3redisutil.KeyNotFoundError, self.cli.hgetall, "foo")

    def test_server_response_error(self):
        cases = (
            201,
            302,
            403,
            500,
        )

        for status in cases:
            self.response["http-status"] = status
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.get, "foo")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hget, "foo", "bar")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.set, "foo", "val")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hset, "foo", "bar", "val")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hkeys, "foo")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hvals, "foo")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hgetall, "foo")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.delete, "foo")
            self.assertRaises(k3redisutil.ServerResponseError, self.cli.hdel, "foo", "bar")

    def test_get(self):
        cases = (("foo", None), ("bar", 1), ("123", 2), ("foobar123", 3))

        for key, retry_cnt in cases:
            res = self.cli.get(key, retry_cnt)
            time.sleep(0.1)

            exp_path = "{ver}/GET/{k}".format(ver=self.cli.ver, k=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

            exp_res = {
                "foo": 1,
                "bar": 2,
            }
            self.assertDictEqual(exp_res, res)

    def test_hget(self):
        cases = (
            ("hname1", "hval1"),
            ("hname2", "hval2"),
            ("hname3", "hval3"),
            ("hname4", "hval4"),
        )

        for hname, hkey in cases:
            res = self.cli.hget(hname, hkey)
            time.sleep(0.1)

            exp_path = "{ver}/HGET/{hn}/{hk}".format(ver=self.cli.ver, hn=hname, hk=hkey)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

            exp_res = {
                "foo": 1,
                "bar": 2,
            }

            self.assertDictEqual(exp_res, res)

    def test_set(self):
        cases = (
            ("key1", "val1", None),
            ("key2", "val2", 1),
            ("key3", "val3", 2),
            ("key4", "val4", 3),
            ("key5", 11, 4),
            ("key6", 22, 5),
        )

        for key, val, expire in cases:
            self.cli.set(key, val, expire)
            time.sleep(0.1)

            exp_path = "{ver}/SET/{k}".format(ver=self.cli.ver, k=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            if expire is not None:
                exp_qs += "&expire={e}".format(e=expire)

            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])
            self.assertEqual(k3utfjson.dump(val), TestRedisProxyClient.request["req-body"])

    def test_hset(self):
        cases = (
            ("hname1", "key1", "val1", None),
            ("hname2", "key2", "val2", 1),
            ("hname3", "key3", "val3", 2),
            ("hname4", "key4", "val4", 3),
            ("hname5", "key5", 11, 4),
            ("hname6", "key6", 22, 5),
        )

        for hname, key, val, expire in cases:
            self.cli.hset(hname, key, val, expire=expire)
            time.sleep(0.1)

            exp_path = "{ver}/HSET/{hn}/{hk}".format(ver=self.cli.ver, hn=hname, hk=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            if expire is not None:
                exp_qs += "&expire={e}".format(e=expire)

            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])
            self.assertEqual(k3utfjson.dump(val), TestRedisProxyClient.request["req-body"])

    def test_hkeys_hvals_hgetall(self):
        cases = (
            "hname1",
            "hname2",
            "hname3",
            "hname4",
        )

        for hname in cases:
            self.cli.hkeys(hname)
            time.sleep(0.1)

            exp_path = "{ver}/HKEYS/{hn}".format(ver=self.cli.ver, hn=hname)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

            self.cli.hvals(hname)
            time.sleep(0.1)

            exp_path = "{ver}/HVALS/{hn}".format(ver=self.cli.ver, hn=hname)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

            self.cli.hgetall(hname)
            time.sleep(0.1)

            exp_path = "{ver}/HGETALL/{hn}".format(ver=self.cli.ver, hn=hname)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"
            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

    def test_retry(self):
        # close http server
        self.tearDown()

        cases = (
            (None, 4),
            (0, 4),
            (1, 8),
            (2, 12),
            (3, 16),
            (4, 20),
        )

        sess = {"run_times": 0}

        def _mock_for_retry(req):
            sess["run_times"] += 1
            return req

        for retry_cnt, exp_cnt in cases:
            sess["run_times"] = 0
            with mock.patch("k3redisutil.RedisProxyClient._sign_req", side_effect=_mock_for_retry):
                try:
                    self.cli.get("foo", retry=retry_cnt)
                except Exception:
                    pass

                try:
                    self.cli.hget("foo", "bar", retry=retry_cnt)
                except Exception:
                    pass

                try:
                    self.cli.set("foo", "val", retry=retry_cnt)
                except Exception:
                    pass

                try:
                    self.cli.hset("foo", "bar", "val", retry=retry_cnt)
                except Exception:
                    pass

            self.assertEqual(exp_cnt, sess["run_times"])

    def test_delete(self):
        cases = (
            ("foo", None),
            ("bar", 1),
            ("123", 2),
            ("foobar123", 3),
        )

        for key, retry_cnt in cases:
            self.cli.delete(key, retry_cnt)
            time.sleep(0.1)

            exp_path = "{ver}/DEL/{key}".format(ver=self.cli.ver, key=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"

            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])

    def test_hdel(self):
        cases = (
            ("hashname", "key0", None),
            ("hashname", "key1", 1),
            ("hashname", "key2", 2),
            ("hashname", "key3", 3),
        )

        for hname, key, retry_cnt in cases:
            self.cli.hdel(hname, key, retry_cnt)
            time.sleep(0.1)

            exp_path = "{ver}/HDEL/{hname}/{key}".format(ver=self.cli.ver, hname=hname, key=key)
            self.assertEqual(exp_path, TestRedisProxyClient.request["req-path"])

            exp_qs = "n=3&w=2&r=2"

            self.assertIn(exp_qs, TestRedisProxyClient.request["req-qs"])


class HttpHandle(BaseHTTPRequestHandler):
    def do_PUT(self):
        length = int(self.headers.get("Content-Length"))
        rst = []

        while length > 0:
            buf = self.rfile.read(length)
            rst.append(buf.decode())
            length -= len(buf)

        path_res = urllib.parse.urlparse(self.path)

        TestRedisProxyClient.request["req-body"] = "".join(rst)
        TestRedisProxyClient.request["req-path"] = path_res.path
        TestRedisProxyClient.request["req-qs"] = path_res.query

        self.send_response(TestRedisProxyClient.response["http-status"])
        self.send_header("Content-Length", 0)
        self.end_headers()

    def do_GET(self):
        response = k3utfjson.dump(
            {
                "foo": 1,
                "bar": 2,
            }
        ).encode()

        path_res = urllib.parse.urlparse(self.path)

        TestRedisProxyClient.request["req-path"] = path_res.path
        TestRedisProxyClient.request["req-qs"] = path_res.query

        self.send_response(TestRedisProxyClient.response["http-status"])
        self.send_header("Content-Length", len(response))
        self.end_headers()

        self.wfile.write(response)

    def do_DELETE(self):
        path_res = urllib.parse.urlparse(self.path)

        TestRedisProxyClient.request["req-path"] = path_res.path
        TestRedisProxyClient.request["req-qs"] = path_res.query

        self.send_response(TestRedisProxyClient.response["http-status"])
        self.send_header("Content-Length", 0)
        self.end_headers()


def child_exit():
    # to suppress error message caused by sys.exit()
    os.close(0)
    os.close(1)
    os.close(2)

    sys.exit(0)
