#!/usr/bin/env python

import subprocess
import sys

def main():
    if len(sys.argv) != 3:
           error_str = "ERROR: Command Line Argument Mismatch."
           error_str += "\n       Usage: "
           error_str += "./main_parser.py max_messages input_file"
           sys.exit(error_str)

    max_messages = sys.argv[1]
    input_file = sys.argv[2]

    user_dictionary = {}

    # open file and store each user's sub list
    for line in open(input_file):
        relation = line.strip().split(',')
        if relation[0] not in user_dictionary:
            user_dictionary[relation[0]] = []
        user_dictionary[relation[0]].append(relation[1])

    # execute the client script for each user
    for user in user_dictionary:
        arg_str = user + ',' + ','.join(user_dictionary[user])
        subprocess.Popen(["./client_with_sherif.py", max_messages, arg_str])

if __name__ == '__main__':
    main()

    
