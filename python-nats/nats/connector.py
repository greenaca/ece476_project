'''\
Class Connector:
    - connection between client and nats server;

Attributes;
    - conn_opts: connection options, including auth parameters;
    - sock :  socket
    - connected: conection status;
    - data_recv: data receive thread, waiting for data from nats server;
    - pending: pending messages record;

'''

from nats.error import NatsConnectException
from nats.common import Common
from gevent.socket import (socket, wait_read)
from gevent.socket import error as socket_error
import threading

class Connector(object):
    "connector class"

    #default nats connection options.
    _DEFAULT_CONN_OPTS = {
        "user": "nats",
        "pswd": "nats", #pass in nats server
        "verbose" : True,
        "pedantic" : True,
        "ssl_required" : False
    }

    def __init__(self, **options):
        self.conn_opts = {}
        for (kwd, default) in self._DEFAULT_CONN_OPTS.items():
            if kwd in options:
                value = options[kwd]
            else:
                value = default
            self.conn_opts[kwd] = value
        self.conn_opts['user'], self.conn_opts['pass'], self.host, self.port = \
                     Common.parse_address_info(options.get("uris"))
        self.sock = socket()
        self.connected = False
        self.callback = options['callback']
        self.data_recv = threading.Thread(target=self._waiting_data)
        self.pending = []

    def open(self):
        '''\
        connect to nats server, the socket will use default gevent paramters :
            - family = AF_INET
            - type = SOCKE_STREAM
            - protocol = auto detect

        Params:
        =====
        host: nats server ip address;
        port: nats server listen port;

        Returns:
        =====
        client: nats connection;
        error: error destription if exists;
        '''
        try:
            self.sock.settimeout(3)
            self.sock.connect((self.host, self.port))
            self._on_connected()
        except socket_error, err:
            print err.message
        except Exception, err:
            print err.message

    def flush_pending(self):
        "flush pending data of current connection."

        if not self.connected or not self.pending:
            return
        try:
            self.sock.sendall("".join(self.pending))
            self.pending = None
        except socket_error, err:
            self._on_connection_lost(err.message)
        except Exception, err:
            self._on_connection_lost(err.message)

    def close(self):
        'close the connection'
        if self.pending:
            self.flush_pending()
        self._on_connection_lost("USER_STOPPED")

    def wait_data(self):
        'wait data from server'
        self.data_recv.setDaemon(True)
        self.data_recv.start()

    def  _waiting_data(self):
        'waiting for data from nats server'

        while self.connected:
            try:
                wait_read(self.sock.fileno())
                data = self.sock.recv(1024)
            except socket_error, ex:
                self._on_connection_lost(ex.message)
                return
            except Exception, ex:
                self._on_connection_lost(ex.message)
                return
            self.callback(data)

    def _on_connected(self):
        '''\
        actions when connect to nats server, actions as below:
        1. setup a ping timer for detect the connectivity of connection;
        2. setup a data receiver for listening the socket;
        '''
        self.connected = True
        self.data_recv.start()
        print "Connected to Nats <{}:{}>".format(self.host, self.port)

    def _on_connection_lost(self, reason):
        '''\
        action if connection losted, actions including:
        1. cancel data receiver; (@2014-04-06)
        2. cancel ping timer; (@2014-04-06)
        '''
        self.connected = False
        try:
            self.sock.shutdown(1)
        except socket_error, ex:
            print ex.message
            if ex == 'EBADF':
                pass
            else:
                print ex.message
        try:
            if reason == 'USER_STOPPED':
                pass
            else:
                raise NatsConnectException(
                    "Connection closed since {}.".format(reason))
        except NatsConnectException, ex:
            print ex.message

    def get_connection_options(self):
        'get the connection options'
        return self.conn_opts

    def send_command(self, command, priority=False):
        '''\
        send command to nats server;

        Params:
        =====
        command: the command string;
        priority: command priority;
        '''
        if not self.pending:
            self.pending = []
        if not priority:
            self.pending.append(command)
        if priority:
            self.pending.insert(0, command)
        self.flush_pending()
