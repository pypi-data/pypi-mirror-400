#!/usr/bin/env python
# coding: utf-8

import logging
import socket

import k3awssign
from k3confloader import conf
import k3http
import k3utfjson

logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 2


class RedisProxyError(Exception):
    """
    The base class of other exceptions of `RedisProxyClient`.
    It is a subclass of `Exception`.
    """

    pass


class SendRequestError(RedisProxyError):
    """
    It is a subclass of `redisutil.RedisProxyError`.
    Raise if failed to send request to redis proxy server.
    """

    pass


class KeyNotFoundError(RedisProxyError):
    """
    It is a subclass of `redisutil.RedisProxyError`.
    Raise if key not found (redis proxy server return a `404`).
    """

    pass


class ServerResponseError(RedisProxyError):
    """
    It is a subclass of `redisutil.RedisProxyError`.
    Raise if http-status not in `(200, 404)` return from redis proxy server.

    """

    pass


def _proxy(func):
    def _wrapper(self, verb, retry, *args):
        all_hosts = [self.hosts]
        if self.proxy_hosts is not None:
            all_hosts += self.proxy_hosts

        rst = None
        err_list = []
        if verb == "GET":
            for hosts in all_hosts:
                try:
                    return func(self, hosts, verb, retry, *args)
                except RedisProxyError as e:
                    err_list.append(e)
            else:
                raise err_list[-1]

        else:
            for hosts in all_hosts:
                rst = func(self, hosts, verb, retry, *args)

        return rst

    return _wrapper


def _retry(func):
    def _wrapper(self, hosts, verb, retry, *args):
        retry = retry or 0
        err_list = []
        for _ in range(retry + 1):
            for ip, port in hosts:
                self.ip = ip
                self.port = port

                try:
                    return func(self, verb, *args)

                except (k3http.HttpError, socket.error) as e:
                    logger.exception(
                        "{e} while send request to redis proxy with {ip}:{p}".format(e=repr(e), ip=ip, p=port)
                    )
                    err_list.append(e)

        else:
            raise SendRequestError(repr(err_list[-1]))

    return _wrapper


class SetAPI(object):
    def __init__(self, cli, redis_op, mtd_info):
        self.cli = cli
        self.redis_op = redis_op.upper()
        self.http_mtd = mtd_info[0]
        self.args_count = mtd_info[1]
        self.opts = list(mtd_info[2]) + ["retry"]

    def api(self, *args, **argkv):
        mtd_args = []

        for idx in range(self.args_count):
            if idx < len(args):
                mtd_args.append(args[idx])

            else:
                left_cnt = self.args_count - len(mtd_args)
                opt_name = self.opts[-left_cnt]
                mtd_args.append(argkv.get(opt_name, None))

        retry = mtd_args.pop()

        qs = {}
        # retry in opts, but it is not in qs
        qs_keys = list(self.opts[:-1])
        while len(qs_keys) > 0:
            qs[qs_keys.pop()] = mtd_args.pop()

        body = None
        if self.http_mtd == "PUT":
            body = k3utfjson.dump(mtd_args.pop())

        path = [self.redis_op] + mtd_args

        return self.cli._api(self.http_mtd, retry, path, body, qs)


class RedisProxyClient(object):
    """
     redis operation, http method, count of args, optional args name

     ### RedisProxyClient.delete
     Delete the specified key.
     Do nothing if the key doesn’t exist.

     **arguments**:
     `key`:specifies the key to redis.
     `retry`:try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: None
     ###  RedisProxyClient.get
     Get the value with `key`. Raise a `redisutil.KeyNotFoundError` if the key doesn’t exist.

    `retry`:try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: the value at `key`.

     ### RedisProxyClient.hdel

     Delete the specified `hashkey` in the specified `hashname`.
     Raise a `redisutil.KeyNotFoundError` if it doesn’t exist.

     **arguments**:
     `hashname`:specifies the hash name to redis.

     `hashkey`:specifies the hash key to redis.

     `retry`:try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: None

     ###  RedisProxyClient.set

     Set the value at `key` to `val`.
     **arguments**:
     `key`: specifies the key to redis.
     `val`: specifies the value to redis.
     `expire`: the expire time on `key` in msec. Defaults to `None`.
     `retry`: try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: nothing

     ###  RedisProxyClient.hget

     Return the value of `haskkey` within the `haskname`.
     Raise a `redisutil.KeyNotFoundError` if it doesn’t exist.

     **arguments**:
     `hashname`: specifies the hash name to redis.
     `hashkey`: specifies the hash key to redis.
     `retry`: try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: the value of `hashkey` within the `hashname`.

     ###  RedisProxyClient.hset

     Set `hashkey` to `val` within `hashname`.

     **arguments**:

     `hashname`: specifies the hash name to redis.

     `hashkey`: specifies the hash key to redis.

     `val`: specifies the value to redis.

     `expire`: the expire time on `hashkey` within `hashname` in msec. Defaults to `None`.

     `retry`: try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: nothing

     ###  RedisProxyClient.hkeys

     Return the list of keys within `hashname`.
     Raise a `redisutil.KeyNotFoundError` if the `hashname` doesn’t exist.

     **arguments**:

     `hashname`: specifies the hash name to redis.

     `retry`: try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: a `list` contains all the keys.

     ###  RedisProxyClient.hvals

     Return the list of values within `hashname`.
     Raise a `redisutil.KeyNotFoundError` if the `hashname` doesn’t exist.

     **arguments**:

     `hashname`: specifies the hash name to redis.

     `retry`: try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: a `list` contains all the values.

     ###  RedisProxyClient.hgetall

     Return a dict of the hash’s name/value pairs.
     Raise a `redisutil.KeyNotFoundError` if the `hashname` doesn’t exist.

     **arguments**:

     `hashname`:specifies the hash name to redis.

     `retry`:try to send request for another N times while failed to send request.
     By default, it is `0`.

     **return**: a `dict` of the hash’s name/value pairs.
    """

    methods = {
        # get(key, retry=0)
        "get": ("get", "GET", 2, ()),
        # set(key, val, expire=None, retry=0)
        "set": ("set", "PUT", 4, ("expire",)),
        # hget(hashname, hashkey, retry=0)
        "hget": ("hget", "GET", 3, ()),
        # hset(hashname, hashkey, val, expire=None, retry=0)
        "hset": ("hset", "PUT", 5, ("expire",)),
        # hkeys(hashname, retry=0)
        "hkeys": ("hkeys", "GET", 2, ()),
        # hvals(hashname, retry=0)
        "hvals": ("hvals", "GET", 2, ()),
        # hgetall(hashname, retry=0)
        "hgetall": ("hgetall", "GET", 2, ()),
        # delete(key, retry=0)
        "delete": ("del", "DELETE", 2, ()),
        # hdel(hashname, key, retry=0)
        "hdel": ("hdel", "DELETE", 3, ()),
    }

    def __init__(self, hosts, proxy_hosts=None, nwr=None, ak_sk=None, timeout=None):
        """
        A client for redis proxy server.
        :param hosts: a `tuple` each element is a `(ip, port)`, retry with next addr while failed to use prev one.
        :param proxy_hosts: a `tuple` each element is `hosts`, as the backup hosts.
        :param nwr: `tuple` of `(n, w, r)`, count of replicas, count of write, count of read.
        If it is `None`, `config.rp_cli_nwr` is used.
        :param ak_sk: tuple` of `(access_key, secret_key)` to sign the request.
        If it is `None`, `config.rp_cli_ak_sk` is used.
        :param timeout: timeout of connecting redis proxy server in seconds. Defaults to `None`.
        """
        self.hosts = hosts
        self.proxy_hosts = proxy_hosts

        if nwr is None:
            nwr = conf.rp_cli_nwr

        if ak_sk is None:
            ak_sk = conf.rp_cli_ak_sk

        self.n, self.w, self.r = nwr
        self.access_key, self.secret_key = ak_sk

        self.timeout = timeout or DEFAULT_TIMEOUT
        self.ver = "/redisproxy/v1"

        for mtd_name, mtd_info in self.methods.items():
            api_obj = SetAPI(self, mtd_info[0], mtd_info[1:])
            setattr(self, mtd_name, api_obj.api)

    def _sign_req(self, req):
        sign_payload = True if "body" in req else False
        signer = k3awssign.Signer(self.access_key, self.secret_key)
        sign_ctx = signer.add_auth(req, query_auth=True, sign_payload=sign_payload)
        logger.debug("signing details: {ctx}".format(ctx=sign_ctx))

    def _make_req_uri(self, params, qs):
        path = [self.ver]
        path.extend(params)

        qs_list = [
            "n={n}".format(n=self.n),
            "w={w}".format(w=self.w),
            "r={r}".format(r=self.r),
        ]
        for k, v in qs.items():
            if v is None:
                continue

            qs_list.append("{k}={v}".format(k=k, v=v))

        return "{p}?{qs}".format(p="/".join(path), qs="&".join(qs_list))

    def _req(self, req):
        if "headers" not in req:
            req["headers"] = {
                "host": "{ip}:{port}".format(ip=self.ip, port=self.port),
            }

        elif "host" not in req["headers"]:
            req["headers"]["host"] = "{ip}:{port}".format(ip=self.ip, port=self.port)

        body = req.get("body", None)
        if body is not None:
            req["headers"]["Content-Length"] = len(body)

        self._sign_req(req)

        cli = k3http.Client(self.ip, self.port, self.timeout)
        cli.send_request(req["uri"], method=req["verb"], headers=req["headers"])
        if body is not None:
            cli.send_body(req["body"])

        cli.read_response()
        res = cli.read_body(None)

        msg = "Status:{s} req:{req} res:{res} server:{ip}:{p}".format(
            s=cli.status, req=repr(req), res=repr(res), ip=self.ip, p=self.port
        )

        if cli.status == 404:
            raise KeyNotFoundError(msg)

        elif cli.status != 200:
            raise ServerResponseError(msg)

        return res

    @_proxy
    @_retry
    def _api(self, verb, path, body, qs):
        req = {
            "verb": verb,
            "uri": self._make_req_uri(path, qs),
        }

        if body is not None:
            req["body"] = body

        if verb == "GET":
            rst = self._req(req)
            return k3utfjson.load(rst)

        else:
            self._req(req)
