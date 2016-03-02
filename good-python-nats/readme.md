# NATS - Tornado based Python 2 Client

A Python async client for the [NATS messaging system](https://nats.io).

[![License MIT](https://img.shields.io/npm/l/express.svg)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/nats-io/python-nats.svg?branch=master)](http://travis-ci.org/nats-io/python-nats)
[![GitHub release](https://img.shields.io/badge/release-v0.2.2-cafe12.svg)](https://github.com/nats-io/python-nats/releases/tag/v0.2.2)

## Supported platforms

Should be compatible with following versions of [Python](https://www.python.org/)
using [Tornado 4.2+](https://github.com/tornadoweb/tornado/tree/v4.2.0)
with [gnatsd](https://github.com/nats-io/gnatsd) as the server:

- 2.7.x
- 2.6.x

## Getting Started

```bash
git clone https://github.com/nats-io/python-nats
cd python-nats

# Only dependency is Tornado so it must be installed first: 
pip install tornado

# OR using pip
pip install -r requirements.txt

python setup.py install
```

## Basic Usage

```python
# coding: utf-8
import tornado.ioloop
import tornado.gen
import time
from datetime import datetime
from nats.io.utils  import new_inbox
from nats.io.client import Client as NATS

@tornado.gen.coroutine
def main():
    nc = NATS()

    # Establish connection to the server.
    options = { "verbose": True, "servers": ["nats://127.0.0.1:4222"] }
    yield nc.connect(**options)

    def discover(msg=None):
        print("[Received]: %s" % msg.data)

    sid = yield nc.subscribe("discover", "", discover)

    # Only interested in 2 messages.
    yield nc.auto_unsubscribe(sid, 2)
    yield nc.publish("discover", "A")
    yield nc.publish("discover", "B")

    # Following two messages won't be received.
    yield nc.publish("discover", "C")
    yield nc.publish("discover", "D")

    # Request/Response
    def help_request_handler(msg):
        print("[Received]: %s" % msg.data)
        nc.publish(msg.reply, "OK, I can help!")

    # Susbcription using distributed queue
    yield nc.subscribe("help", "workers", help_request_handler)

    try:
        # Expect a single request and timeout after 500 ms
        response = yield nc.timed_request("help", "Hi, need help!", 500)
        print("[Response]: %s" % response.data)
    except tornado.gen.TimeoutError, e:
        print("Timeout! Need to retry...")

    # Customize number of responses to receive
    def many_responses(msg=None):
        print("[Response]: %s" % msg.data)

    yield nc.request("help", "please", expected=2, cb=many_responses)

    # Publish inbox
    my_inbox = new_inbox()
    yield nc.subscribe(my_inbox)
    yield nc.publish_request("help", my_inbox, "I can help too!")

    loop = tornado.ioloop.IOLoop.instance()
    yield tornado.gen.Task(loop.add_timeout, time.time() + 1)
    try:
        start = datetime.now()
        # Make roundtrip to the server and timeout after 1000 ms
        yield nc.flush(1000)
        end = datetime.now()
        print("Latency: %d µs" % (end.microsecond - start.microsecond))
    except tornado.gen.TimeoutError, e:
        print("Timeout! Roundtrip too slow...")

if __name__ == '__main__':
    tornado.ioloop.IOLoop.instance().run_sync(main)
```

## Clustered Usage

```python
# coding: utf-8
import tornado.ioloop
import tornado.gen
from datetime import timedelta
from nats.io.client import Client as NATS
from nats.io.errors import ErrConnectionClosed

@tornado.gen.coroutine
def main():
    nc = NATS()

    # Set pool servers in the cluster and give a name to the client
    # each with its own auth credentials.
    options = {
        "servers": [
            "nats://secret1:pass1@127.0.0.1:4222",
            "nats://secret2:pass2@127.0.0.1:4223",
            "nats://secret3:pass3@127.0.0.1:4224"
            ]
        }

    # Error callback takes the error type as param.
    def error_cb(e):
        print("Error! ", e)

    def close_cb():
        print("Connection was closed!")

    def disconnected_cb():
        print("Disconnected!")

    def reconnected_cb():
        print("Reconnected!")

    # Set callback to be dispatched whenever we get
    # protocol error message from the server.
    options["error_cb"] = error_cb

    # Called when we are not connected anymore to the NATS cluster.    
    options["close_cb"] = close_cb

    # Called whenever we become disconnected from a NATS server.
    options["disconnected_cb"] = disconnected_cb

    # Called when we connect to a node in the NATS cluster again.
    options["reconnected_cb"] = reconnected_cb

    yield nc.connect(**options)

    @tornado.gen.coroutine
    def subscriber(msg):
        yield nc.publish("pong", "pong:{0}".format(msg.data))

    yield nc.subscribe("ping", "", subscriber)

    for i in range(0, 100):
        yield nc.publish("ping", "ping:{0}".format(i))
        yield tornado.gen.sleep(0.1)

    yield nc.close()

    try:
        yield nc.publish("ping", "ping")
    except ErrConnectionClosed:
        print("No longer connected to NATS cluster.")

if __name__ == '__main__':
    tornado.ioloop.IOLoop.instance().run_sync(main)
```

## Wildcard Subscriptions

```python
# coding: utf-8
import tornado.ioloop
import tornado.gen
import time
from nats.io.client import Client as NATS

@tornado.gen.coroutine
def main():
    nc = NATS()

    yield nc.connect()

    def subscriber(msg):
        print("Msg received on [{0}]: {1}".format(msg.subject, msg.data))

    yield nc.subscribe("foo.*.baz", "", subscriber)
    yield nc.subscribe("foo.bar.*", "", subscriber)
    yield nc.subscribe("foo.>", "", subscriber)
    yield nc.subscribe(">", "", subscriber)

    # Matches all of above
    yield nc.publish("foo.bar.baz", b"Hello World")
    yield tornado.gen.sleep(1)

if __name__ == '__main__':
    tornado.ioloop.IOLoop.instance().run_sync(main)
```

## Advanced Usage

```python
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
```

## Examples

In this repo there are also included a couple of simple utilities
for subscribing and publishing messages to NATS:

```sh
    # Make a subscription to 'hello'
    $ python examples/nats-sub hello

    Subscribed to 'hello'
    [Received: hello] world

    # Send a message to hello
    $ python examples/nats-pub hello -d "world"
```

## License

(The MIT License)

Copyright (c) 2015 Apcera Inc.<br/>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to
deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
