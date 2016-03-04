#!/usr/bin/env python

import subprocess
import argparse, sys
from functools import wraps
import errno
import os
import signal
import time

timeout_secs = 6300   # 1.75hrs

class TimeoutError(Exception):
    pass

def timeout(seconds=(30 + timeout_secs), error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            subprocess.call(["pkill", "-9", "python"])
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator

def show_usage():
  print("main_parser INPUT_FILE [-m MAX_MESSAGES]")
  print("")
  print("Example:")
  print("")
  print("main_parser users.txt -m 10000")

@timeout(30 + timeout_secs)
def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", nargs="?")
    parser.add_argument("-m", "--maxmsg", default="1000")

    args = parser.parse_args()

    max_messages = args.maxmsg
    input_file = args.input_file
    log_dir = "logs"
    run_time = time.strftime("%d-%m-%Y-%H-%M-%S")
    run_dir = log_dir + "/nats-run_" + run_time    # Name of directory for this run
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    os.makedirs(run_dir)

    user_dictionary = {}

    # open file and store each user"s sub list
    for line in open(input_file):
        relation = line.strip().split(",")
        if relation[0] not in user_dictionary:
            user_dictionary[relation[0]] = []
        user_dictionary[relation[0]].append(relation[1:])

    user_jobs_list = []

    # execute the client script for each user
    for user, subs in user_dictionary.iteritems():
        arg_str = user + "," + ",".join(subs[0])
        user_job = subprocess.Popen(["./client.py", arg_str, "-m", max_messages, "-d", run_dir])
        user_jobs_list.append(user_job)


    for user_job in user_jobs_list:
        user_job.wait()

if __name__ == "__main__":
    main()

    
