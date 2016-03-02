#!/usr/bin/env python

import argparse, sys
import tornado.ioloop
import tornado.gen
import time

from nats.io.client import Client as NATS

def show_usage():
  print("pub SUBJECT [-m MAX_MESSAGES]")
  print("")
  print("Example:")
  print("")
  print("pub hello -m 10000")

def show_usage_and_die():
  show_usage()
  sys.exit(1)

def get_time():
    return str(int(round(time.time() * 1000)))

@tornado.gen.coroutine
def publisher():
    parser = argparse.ArgumentParser()

    # e.g. nats-pub hello -d "world" -s nats://127.0.0.1:4222 -s nats://127.0.0.1:4223
    parser.add_argument("subject", default="hello", nargs="?")
    parser.add_argument("-m", "--maxmsg", default="10000")

    args = parser.parse_args()

    time.sleep(5)
    print 'User', args.subject, "starting to publish" 

    nc = NATS()
    try:
        servers = ["nats://127.0.0.1:4222"]
        opts = { "servers": servers }
        yield nc.connect(**opts)

        for i in range(int(args.maxmsg)):
            message_data = args.subject + " " + get_time() + " " + str(i + 1)
            yield nc.publish(args.subject, message_data)
        yield nc.flush()
    except Exception, e:
        print(e)
        show_usage_and_die()

if __name__ == "__main__":
    tornado.ioloop.IOLoop.instance().run_sync(publisher)
