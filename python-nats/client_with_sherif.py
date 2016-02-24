#!/usr/bin/env python

import time
import sys

from nats.client import NatsClient

NATS_URI = "nats://nats:nats@127.0.0.1:4222"


def get_time():
    return str(int(round(time.time() * 1000)))

#TODO Program currently exist in the right condition however, occasionally the
#     following message appears: "[error] Connection closed since ."
def main():
    try:
        # parameter declarations
        user_id = "0"
        #subscribe_list = ["1", "2"]
        subscribe_list = ["0"]
        max_messages = 5
        # messsage format
        #     "depart_uid depart_time arrival_uid arrival_time"
        received_message_list = []

        # start nats process
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)
        print nats.stat.query()

        # subscribe callback function
        #     incoming msg format= "user_id time_stamp message_number"
        def subscribe_blk(msg):
            print "[SUB]: received \"{}\"".format(msg)
            
            # split funciton was not working correctly so the msg string is being 
            # stored in a variable
            received_message_str = str(msg)
            split_message =  received_message_str.split(" ")

            # extract and store the message number/max messages that will be sent
            message_number = int(split_message[2])
            #max_message = int(split_message[3])
            # extract the message information and add id/timestamp to message
            final_message = split_message[0] + " " + split_message[1] + " " + user_id + " " + get_time()
            # store message in memory
            received_message_list.append(final_message)

            # determine if the last message has come in
            if message_number >= max_messages:
                # write recieved_message_list to file
                print '\nTotal messages recieved by user ' + str(user_id) + ':'
                for i in received_message_list:
                    print i

                # stop the nats process to exit the code cleanly
                time.sleep(1)    # prevent "[error] Connection closed since ." message
                nats.stop()

        # subscribe to every user in the subscribe list
        for ID in subscribe_list:
            sid = nats.subscribe(ID, subscribe_blk)

        # publish messages and wait between each publish
        for i in range(max_messages):
            nats.publish(user_id, user_id + " " + get_time() + " " + str(i + 1))
            print "[PUB]: publishing message " + str(i + 1)
            time.sleep(.2)     #TODO make this a random variable with a min of 200 ms

    except KeyboardInterrupt, ex:
        print "Keyboard Interrupt Detected. Exiting Program..."
        sys.exit(0)

if __name__ == "__main__":
    main()
