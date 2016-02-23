import time
import sys
import multiprocessing

from nats.client import NatsClient

NATS_URI = "nats://nats:nats@127.0.0.1:4222"

#def subscribe(user_id):
#	sid = nats.subscribe(user_id, subscribe_blk)
#	return

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

        def subscribe(user_id):
                user_info = "id%d" % (user_id,)
                sid = nats.subscribe(user_info, subscribe_blk)
                print user_info
                print sid
		#print type(user_info)
		return

        def subscribe_blk(msg):
            print "[PUB]: {}".format(msg)
	    # add id and timestamp to msg
	    # store msg in memory		
            print nats.stat.query()

#        def subscribe(user_id):
#		user_info = "id%d" % (user_id,)
#                sid = nats.subscribe(user_info, subscribe_blk)
#		print user_info
#		print type(user_info)
#                return

        for i in range(1):
		print "in for-loop"
                jobs = []
                p = multiprocessing.Process(target=subscribe, args=(i,))
                jobs.append(p)
                p.start()

#	def subscribe(user_id):
#        	sid = nats.subscribe(user_id, subscribe_blk)
#        	return

	#for i in range(5):
	#	jobs = []
        #	p = multiprocessing.Process(target=subscribe, args=(i,))
        #	jobs.append(p)
        #	p.start()


	#sid = nats.subscribe("id0", subscribe_blk)
	#sid = nats.subscribe("id1", subscribe_blk)
	#sid = nats.subscribe("id2", subscribe_blk)


	for i in range(5):
		nats.publish("id0", "user 0: message " + str(i))
		nats.publish("id1", "user 1: message " + str(i))
		nats.publish("id2", "user 2: message " + str(i))
		print "publishing user 0: message " + str(i)
		print "publishing user 1: message " + str(i)
		print "publishing user 2: message " + str(i)
		time.sleep(2)

    except KeyboardInterrupt, ex:
        print "ByeBye."
        sys.exit(0)

if __name__ == '__main__':
#	for i in range(5):
#                jobs = []
#                p = multiprocessing.Process(target=subscribe, args=(i,))
#                jobs.append(p)
#                p.start()
    	main()
