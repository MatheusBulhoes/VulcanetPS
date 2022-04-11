# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


"""
An example client. Run simpleserv.py first before running this.
"""

import json
from twisted.internet import reactor, protocol


# a client protocol


class EchoClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        data = input().split()
        y = {"command" : data[0], "id" : data[1]}
        self.transport.write(json.dumps(y).encode('utf-8'))

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        print(data)
        y = json.loads(data.decode("utf-8"))
        print(y["response"])
        self.connectionMade()

    def connectionLost(self, reason):
        print("connection lost")


class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()


# this connects the protocol to a server running on port 5678
def main():
    f = EchoFactory()
    reactor.connectTCP("localhost", 5678, f)
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == "__main__":
    main()
