import logging
import os
import threading
import time
from collections import defaultdict

import redis

import k3utfjson

logger = logging.getLogger(__name__)

# redis is thread safe

# NOTE: fork may duplicate file descriptor that confuses connection pool.
_pid_client = defaultdict(dict)
_lock = threading.RLock()


def get_client(ip_port):
    """
    Return a process-wise singleton redis client, which is an instance of `redis.StrictRedis`.

    Redis client returned is shared across the entire process and will not be
    re-created.
    It is also safe to use if a process fork and inherited opened socket file-descriptors.
    :param ip_port: could be a port number in `int` or `long` to get or create a
    client connecting to localhost.
    It can also be tuple of `(ip, port)`.
    :return: an instance of `redis.StrictRedis`.
    """
    ip_port = normalize_ip_port(ip_port)

    pid = os.getpid()

    with _lock:
        o = _pid_client[ip_port]

        if pid not in o:
            o[pid] = redis.StrictRedis(*ip_port)

    return _pid_client[ip_port][pid]


def wait_serve(ip_port, timeout=5):
    """
    Wait for at most `timeout` seconds until redis start serving request.
    It is useful when start a redis server.
    :param ip_port: tuple of `(ip, port)` or a single int/long number as port.
    :param timeout: specifies max waiting time, in seconds.
    :return: Nothing
    """
    t = time.time() + timeout

    rcl = get_client(ip_port)

    while time.time() < t:
        try:
            rcl.hget("foo", "foo")
            logger.info("redis is ready: " + repr(ip_port))
            return

        except redis.ConnectionError as e:
            logger.info("can not connect to redis: " + repr(ip_port) + " " + repr(e))
            time.sleep(0.1)
            continue
    else:
        logger.error("can not connect to redis: " + repr(ip_port))
        raise
    # if redis does not respond in `timeout` seconds.


class RedisChannel(object):
    """
    send message `data` through `channel`.
    `channel` is a list in redis.
    `peer` is "client" or "server".

    send is a rpush operation that adds an item to the end of a list.
    recv is a lpop operation that pops an item from the start of a list.
    """

    other_peer = {
        "client": "server",
        "server": "client",
    }

    def __init__(self, ip_port, channel, peer, timeout=None):
        """
        `redisutil.RedisChannel(ip_port, channel, peer, timeout=None)`

        Create a redis list based channel for cross process communication.

        See [redis-list-command](https://redis.io/commands#list).

        Initializing this class does **NOT** create a socket connecting to redis or
        create any data in redis.

        A channel support duplex communication.
        Thus in redis it creates two lists for each channel for two way communication:
        `<channel>/client` and `<channel>/server`.

        Client side uses `<channel>/client` to send message.
        Server side uses `<channel>/server` to send message.

        A client should initialize `RedisChannel` with argument `peer` set to `client`.
        A server should initialize `RedisChannel` with argument `peer` set to `server`.
        :param ip_port: tuple of `(ip, port)` or a single int/long number as port.
        :param channel: specifies the name of the channel to create.
        A channel should be in URI form, starting with `/`, such as: `/asyncworker/image-process`
        `channel` can also be a tuple of string:
        `('asyncworker', 'image-process')` will be converted to `/asyncworker/image-process`.
        :param peer: specifies this instance is a client or a server.
        It can be `"client"` or `"server"`.
        :param timeout: the expire time of the channel, in second.
        If it is `None`, the channel exists until being cleaned.
        """
        assert peer in self.other_peer

        self.ip_port = normalize_ip_port(ip_port)
        self.rcl = get_client(self.ip_port)

        # convert ['a', 'b'] to '/a/b'
        if isinstance(channel, (list, tuple)):
            channel = "/" + "/".join(channel)

        self.channel = channel
        self.peer = peer.lower()
        self.send_list_name = "/".join([self.channel, self.peer])
        self.recv_list_name = "/".join([self.channel, self.other_peer[self.peer]])
        self.timeout = timeout

    def send_msg(self, data):
        """
        Send data. `data` is json-encoded in redis list.
        :param data: any data type that can be json encoded.
        :return: Nothing
        """
        j = k3utfjson.dump(data)
        self.rcl.rpush(self.send_list_name, j)

        if self.timeout is not None:
            self.rcl.expire(self.send_list_name, self.timeout)

    def recv_msg(self):
        """
        Receive one message.
        If there is no message in this channel, it returns `None`.
        :return: data that is loaded from json. Or `None` if there is no message in channel.
        """
        v = self.rcl.lpop(self.recv_list_name)
        if v is None:
            return None

        return k3utfjson.load(v)

    def brecv_msg(self, timeout=0):
        """
        Block to receive one message.
        If there is no message in this channel,
        then block for `timeout` seconds or until
        a value was pushed to the channel.

        :param timeout: seconds of the block time.
        If it is `0`, then block until a message is available.

        :return: data that is loaded from json. Or `None` if timeout.
        """
        v = self.rcl.blpop(self.recv_list_name, timeout=timeout)
        if v is None or len(v) != 2:
            return None

        # v is a tuple, (key, value)
        _, value = v

        return k3utfjson.load(value)

    def recv_last_msg(self):
        """
        Similar to `RedisChannel.recv_msg` except it returns only the last message it
        sees and removes all previous messages from this channel.
        :return: data that is loaded from json. Or `None` if there is no message in channel.
        """
        last = None
        while True:
            v = self.rcl.lpop(self.recv_list_name)
            if v is None:
                return k3utfjson.load(last)

            last = v

    def brecv_last_msg(self, timeout=0):
        """
        Similar to `RedisChannel.recv_last_msg` except it blocks for `timeout`
        seconds if the channel is empty.
        :param timeout: seconds of the block time.
        If it is `0`, then block until a message is available.
        :return: data that is loaded from json. Or `None` if timeout.
        """
        msg = self.brecv_msg(timeout=timeout)
        if msg is None:
            return None

        last = self.recv_last_msg() or msg

        return last

    def peek_msg(self):
        """
        Similar to `RedisChannel.recv_msg` except it does not remove the message it
        returned.
        :return: data that is loaded from json. Or `None` if there is no message in channel.
        """
        v = self.rcl.lindex(self.recv_list_name, 0)
        if v is None:
            return None

        return k3utfjson.load(v)

    def rpeek_msg(self):
        """
        Similar to `RedisChannel.peek_msg`
        except it gets message from the tail of the channel.
        :return: JSON decoded message. Or `None` if there is no message in channel.
        """
        v = self.rcl.lindex(self.recv_list_name, -1)
        if v is None:
            return None

        return k3utfjson.load(v)

    def list_channel(self, prefix):
        """
        List all channel names those start with `prefix`.
        :param prefix: specifies what channel to list. `prefix` must starts with '/', ends with '/'.
        :return: a list of channel names.
        """
        if isinstance(prefix, (list, tuple)):
            _prefix = "/" + "/".join(prefix) + "/"
        else:
            _prefix = prefix

        if not _prefix.startswith("/"):
            raise ValueError('prefix must starts with "/", but:' + repr(prefix))

        if _prefix.endswith("*"):
            raise ValueError('prefix must NOT ends with "*", but:' + repr(prefix))

        if not _prefix.endswith("/"):
            raise ValueError('prefix must ends with "/", but:' + repr(prefix))

        _prefix = _prefix + "*"
        channels = self.rcl.keys(_prefix)

        rst = []
        for c in channels:
            for k in self.other_peer:
                k = "/" + k
                if c.endswith(k.encode()):
                    c = c[: -len(k)]
                    break
            else:
                logger.info("not a channel: " + repr(c))
                continue

            if c not in rst:
                rst.append(c)

        return sorted(rst)


def normalize_ip_port(ip_port):
    if isinstance(ip_port, int):
        ip_port = ("127.0.0.1", ip_port)

    return ip_port
