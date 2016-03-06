#!/usr/bin/env python

import argparse, sys
import tornado.ioloop
import tornado.gen
import time

from nats.io.client import Client as NATS

def show_usage():
    print("sub SUBJECT -o ORIGINAL [-m MAX_MESSAGES]")

def show_usage_and_die():
    show_usage()
    sys.exit(1)

# This function is resposible for calculating the current time in UTC
def get_time():
    return str(int(round(time.time() * 1000)))

@tornado.gen.coroutine
def subscribe():
    received_message_list = []

    # Parse the command line arguments
    parser = argparse.ArgumentParser()

    # e.g. nats-sub hello -s nats://127.0.0.1:4222
    parser.add_argument("subject", default="hello", nargs="?")
    parser.add_argument("-o", "--original", default="hello", nargs="?")
    parser.add_argument("-m", "--maxmsg", default=10000, type=int)
    parser.add_argument("-d", "--dirname")

    # Parse!
    args = parser.parse_args()

    file_time = time.strftime("%d-%m-%Y-%H-%M-%S")
    filename = "nats-run_" +\
               args.subject + "-" + args.original + "_" +\
               file_time + ".txt"  #Filename of message data for the user_id
    completed_user_list = []                 # List of subscribed users who have finished publishing

    # Create client and connect to server
    nc = NATS()
    servers = ["nats://146.148.76.9:4222"]
    #servers = ["nats://127.0.0.1:4222"]
    opts = { "servers": servers }
    yield nc.connect(**opts)

    def handler(msg):
        #print("[Received: {0}] {1}".format(msg.subject, msg.data))

        sub_time = get_time()
        received_message_str = str(msg.data)
        split_message = received_message_str.split(" ")
        message_number = int(split_message[2])
        final_message = split_message[0] + " " +\
                        split_message[1] + " " +\
                        args.original + " " +\
                        sub_time
        received_message_list.append(final_message)

        if message_number == args.maxmsg:
            fd = open(args.dirname + "/" + filename, "a")
            for i in received_message_list:
                print >> fd, i
            fd.close
            del received_message_list[:]
                    
            tornado.ioloop.IOLoop.instance().stop()

    print("Subscribed to '{0}'".format(args.subject))
    future = nc.subscribe(args.subject, "", handler)
    sid = future.result()

if __name__ == "__main__":
    subscribe()
    tornado.ioloop.IOLoop.instance().start()
