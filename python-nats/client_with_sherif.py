import time
import sys

from nats.client import NatsClient

NATS_URI = "nats://nats:nats@127.0.0.1:4222"

# This example code will not exit cleanly so you will have to kill
# the process
def main():
    try:
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)

        print nats.stat.query()

	# msg = "depart_uid depart_time arrival_uid arrival_time
	# This works right now. But we want each of these subscriptions
	# have their own process.
	#
	# subprocess psudocode:
        #	def subscribe_blk(msg):
	#	    add id and timestamp to msg
	#	    store msg in memory		
	#
        #	sid = nats.subscribe("userID", subscribe_blk)
	#	
        def subscribe_blk(msg):
	    #incoming message format: userID time_stamp msg#
            print "[PUB]: {}".format(msg)
	    # add id and timestamp to msg
	    # store msg in memory		
            for i in range(10):
	        print s


        sid = nats.subscribe("id0", subscribe_blk)
        sid = nats.subscribe("id1", subscribe_blk)
        sid = nats.subscribe("id2", subscribe_blk)


	for i in range(1):
		nats.publish("id0", "user 0: message " + str(i))
		nats.publish("id1", "user 1: message " + str(i))
		nats.publish("id2", "user 2: message " + str(i))
		print "publishing user 0: message " + str(i)
		print "publishing user 1: message " + str(i)
		print "publishing user 2: message " + str(i)
		time.sleep(.2)

    except KeyboardInterrupt, ex:
        print "ByeBye."
        sys.exit(0)

if __name__ == '__main__':
    main()
