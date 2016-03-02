# coding: utf-8
import tornado.ioloop
import tornado.gen
import time
from nats.io.client import Client as NATS

@tornado.gen.coroutine
def main():
    nc = NATS()

    # Set pool servers in the cluster and give a name to the client.
    options = {
        "name": "worker",
        "servers": [
            "nats://secret:pass@127.0.0.1:4222",
            "nats://secret:pass@127.0.0.1:4223",
            "nats://secret:pass@127.0.0.1:4224"
            ]
        }

    # Explicitly set loop to use for the reactor.
    options["io_loop"] = tornado.ioloop.IOLoop.instance()

    yield nc.connect(**options)

    @tornado.gen.coroutine
    def subscriber(msg):
        yield nc.publish("discover", "pong")

    yield nc.subscribe("discover", "", subscriber)

    while True:
        # Confirm stats to implement basic throttling logic.
        sent = nc.stats["out_msgs"]
        received = nc.stats["in_msgs"]
        delta = sent - received

        if delta > 2000:
            print("Waiting... Sent: {0}, Received: {1}, Delta: {2}".format(sent, received, delta))
            yield tornado.gen.sleep(1)

        if nc.stats["reconnects"] > 10:
            print("[WARN] Reconnected over 10 times!")

        for i in range(1000):
            yield nc.publish("discover", "ping")

if __name__ == '__main__':
    tornado.ioloop.IOLoop.instance().run_sync(main)
