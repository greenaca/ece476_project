#!/usr/bin/env python

import time
import sys
import random

from nats.client import NatsClient
from datetime import datetime


NATS_URI = "nats://nats:nats@127.0.0.1:4222"
#NATS_URI = "nats://nats:nats@146.148.76.9:4222"

# This function is resposible for calculating the current time in UTC
#TODO this might not be the best method, can be changed.
def get_time():
    return str(int(round(time.time() * 1000)))
    #return (datetime.datetime.utcnow() - datetime.datetime(2016, 1, 1)).total_seconds()

# Main function that drives the main functionality of the client code.
#
# Command Line Usage:
#     ./client_with_sherif.py max_messages this_user_id,sub_id_0,sub_id_1, ... ,sub_id_n
#
#TODO change program name
def main():
    try:
        if len(sys.argv) != 3:
           error_str = "ERROR: Command Line Argument Mismatch."
           error_str += "\n       Usage: "
           error_str += "./client_with_sherif.py max_messages this_user_id,sub_id_0,sub_id_1, ... ,sub_id_n"
           sys.exit(error_str)

        # parameter declarations
        max_messages = int(sys.argv[1])          # Max messages this user will publish
        subscribe_list = sys.argv[2].split(",")  # List of the users that this user is subscribed to
        user_id = subscribe_list.pop(0)          # This user"s ID
        received_message_list = []               # List of the messages that have been received
        completed_user_list = []                 # List of subscribed users who have finished publishing
        publish_is_complete = False              # Boolean to determine if the publishing is complete
	filename = "nats_run_" + user_id + "_" + get_time() + ".txt"  #Filename of message data for the user_id

        # start nats process
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)
        print nats.stat.query()

        if subscribe_list != []: 
            # subscribe callback function
            def subscribe_blk(msg):
                print "[SUB]: received \"{}\"".format(msg)
                
                #NOTE: split funciton was not working correctly so the msg string is being 
                #      stored in a variable
                    #
                # reveived_message_str= "user_id time_stamp message_number"
                received_message_str = str(msg)
                split_message =  received_message_str.split(" ")
    
                message_number = int(split_message[2])
                
                # final_message = "publish_id sent_time my_id received_time"
                final_message = split_message[0] + " " + split_message[1] + " " + user_id + " " + get_time()
                received_message_list.append(final_message)
    
                # determine if the last message for that has been sent
                if (message_number % 5000) == 0: 
                    #completed_user_list.append(split_message[0])
                    #print "[SUB]: user " + str(user_id) + " finished publishing"
    
                    # check if all of the subcribed users have completed publishing
                    #if completed_user_list == subscribe_list: 
                        #print "\n[SUB]: all messages received:"
                    
                    fd = open(filename, "a")
    
                    for i in received_message_list:
                        print >> fd, "\t" + i
                        
                    fd.close
                    del received_message_list[:]
                        
                    if publish_is_complete:
                        # stop the nats process to exitsthe code cleanly
                        print "\nStopping NATS process..."
                        time.sleep(1)    # prevent "[error] Connection closed since ." message
                        nats.stop()
    
            # subscribe to every user in the subscribe list
            for ID in subscribe_list:
                sid = nats.subscribe(ID, subscribe_blk)
    
        # publish messages and wait between each publish
        for i in range(max_messages):
            nats.publish(user_id, user_id + " " + get_time() + " " + str(i + 1))
            print "[PUB]: publishing message " + str(i + 1)
            rand_num = random.expovariate(1/9.8) + .2  #Random exponential variable with a min of 200 ms
            time.sleep(rand_num)
		

        publish_is_complete = True
        if completed_user_list == subscribe_list:
            # stop the nats process to exit the code cleanly
            print "\nStopping NATS process..."
            time.sleep(1)    # prevent "[error] Connection closed since ." message
            nats.stop()

    except KeyboardInterrupt, ex:
        print "Keyboard Interrupt Detected. Exiting Program..."
        sys.exit(0)

if __name__ == "__main__":
    main()
