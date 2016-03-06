#!/usr/bin/env python

import argparse, sys
import tornado.ioloop
import tornado.gen
import time
import subprocess

from nats.io.client import Client as NATS

def show_usage():
  print("client INPUT_FILE [-d DATA] [-m MAX_MESSAGES]")
  print("")
  print("Example:")
  print("")
  print("client hello -d world -m 10000")

def show_usage_and_die():
  show_usage()
  sys.exit(1)

# This function is resposible for calculating the current time in UTC
def get_time():
    return str(int(round(time.time() * 1000)))

def main():
    parser = argparse.ArgumentParser()

    # e.g. nats-pub hello -d "world" -s nats://127.0.0.1:4222 -s nats://127.0.0.1:4223
    parser.add_argument("user_string", default="0,0", nargs="?")
    parser.add_argument("-m", "--maxmsg", default="1000")
    parser.add_argument("-d", "--dirname")

    args = parser.parse_args()

    subscribe_list = str(args.user_string).split(",")
    user_id = subscribe_list.pop(0)
    sub_jobs_list = []

    for sub_id in subscribe_list:
        sub_job = subprocess.Popen(["/home/zhangso/ece476_project/good-python-nats/sub.py", sub_id, "-o", user_id, "-m", args.maxmsg, "-d", args.dirname])
        sub_jobs_list.append(sub_job)
    pub_job = subprocess.Popen(["/home/zhangso/ece476_project/good-python-nats/pub.py", user_id, "-m", args.maxmsg])

    for sub_job in sub_jobs_list:
        sub_job.wait()
    pub_job.wait()

if __name__ == "__main__":
    main()
