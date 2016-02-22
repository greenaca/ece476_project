import time
import sys

from nats.client import NatsClient
from datetime import datetime

# server ip to connect to
NATS_URI = "nats://nats:nats@127.0.0.1:4222"

def main():
    try:

	uid_text = "UID1 :: MSG :: "

        nats = NatsClient(uris=NATS_URI) # prints version info
        nats.start() # connects to server
        time.sleep(1)

        print nats.stat.query() # gives first 'status'

	# subscribe to a particular id
        def subscribe_blk(msg, reply):
	    dt = datetime.utcnow().strftime(".%Y.%m.%d.%H.%M.%S.%f.")
	    print("[dt_on_r]: " + dt)
	    r_timestamp = dt.split('.')
            s_timestamp = msg.split('.')
            print "{}".format(msg)
	    print(r_timestamp)
	    print(s_timestamp)
	    time_data = ["years", "months", "days", "hours", "minutes", "seconds", "ms"]
	    for i in range(1, 8):
	    	print(str(int(r_timestamp[i]) - int(s_timestamp[i])) + " " + time_data[i-1])

	print("here6")

        # subscribe to 'job' tag
	sid = nats.subscribe("job", subscribe_blk) 

	print("sid: " + str(sid))

	pub_text = ""
	for i in range(0, 10):
	    	dt = " (" + datetime.utcnow().strftime(".%Y.%m.%d.%H.%M.%S.%f.") + ")"
		pub_text = "[dt_on_p]: " + dt + uid_text
        	rid = nats.publish("job", pub_text)
		time.sleep(4)
		# print("rid: " + str(rid))
		
        print nats.stat.query()
	print("here9")
        # nats.stop()

    except KeyboardInterrupt, ex:
        print "ByeBye."
        sys.exit(0)

if __name__ == '__main__':
    main()
