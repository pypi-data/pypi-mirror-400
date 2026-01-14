import k3redisutil
import time

# Using redis as a duplex cross process communication channel pool.

# client and server with the same channel name "/foo" is a pair
c = k3redisutil.RedisChannel(6379, "/foo", "client")
s = k3redisutil.RedisChannel(6379, "/foo", "server")

c.send_msg("c2s")
s.send_msg("s2c")

# list channels
print(c.list_channel("/"))  # ["/foo"]
print(s.recv_msg())  # c2s
print(c.recv_msg())  # s2c

cli = k3redisutil.RedisProxyClient([("127.0.0.1", 2222), ("192.168.0.100", 222)])

cli.set("k1", "v1", retry=1)
cli.set("k2", "v2", expire=1000)  # msec

print(cli.get("k1", retry=2))
# out: 'v1'

print(cli.get("k2"))
# out: 'v2'

time.sleep(1)
cli.get("k2")
# raise a 'redisutil.KeyNotFoundError' because it is timeout

cli.hset("hashname1", "k3", "v3")
cli.hset("hashname2", "k4", "v4", expire=1000)

print(cli.hget("hashname1", "k3"))
# out: 'v3'

print(cli.hget("hashname2", "k4"))
# out: 'v4'

time.sleep(1)
cli.hget("hashname2", "k4")
# raise a 'redisutil.KeyNotFoundError' because it is timeout
