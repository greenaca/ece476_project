#!/usr/bin/env python

import subprocess
import argparse, sys

def show_usage():
  print("main_parser INPUT_FILE [-m MAX_MESSAGES]")
  print("")
  print("Example:")
  print("")
  print("main_parser users.txt -m 10000")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_file", nargs="?")
    parser.add_argument("-m", "--maxmsg", default="1000")

    args = parser.parse_args()

    max_messages = args.maxmsg
    input_file = args.input_file

    user_dictionary = {}

    # open file and store each user"s sub list
    for line in open(input_file):
        relation = line.strip().split(",")
        if relation[0] not in user_dictionary:
            user_dictionary[relation[0]] = []
        user_dictionary[relation[0]].append(relation[1:])

    #user_jobs_list = []

    # execute the client script for each user
    for user, subs in user_dictionary.iteritems():
        arg_str = user + "," + ",".join(subs[0])
        user_job = subprocess.Popen(["./client.py", arg_str, "-m", max_messages])
        user_jobs_list.append(user_job)


    for user_job in user_jobs_list:
        user_job.wait()

if __name__ == "__main__":
    main()

    
