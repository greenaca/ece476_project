import time
import sys
import multiprocessing

from nats.client import NatsClient

NATS_URI = "nats://nats:nats@127.0.0.1:4222"

#def user(user_id):
#    print user_id
#    return

def main(user_id):
    try:
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)

        print "user_id = %d" % user_id
        #print nats.stat.query()

        #def request_blk(msg):
        #     print "[SUB]: {}".format(msg)
        #     print nats.stat.query()
        #     nats.stop()

        #def subscribe_blk(msg, reply):
        #     print "[PUB]: {}".format(msg)
        #     nats.publish(reply, "ME ME ME")

        for i in range(5):
             sid = nats.subscribe(i)

        #nats.request("job", "wait, who can do this job", request_blk)
        print nats.stat.query()

    except KeyboardInterrupt, ex:
        print "ByeBye."
        sys.exit(0)

if __name__ == '__main__':
    #main()
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=main, args=(i,))
        jobs.append(p)
        p.start()


