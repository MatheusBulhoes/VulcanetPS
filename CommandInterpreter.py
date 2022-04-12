import json, cmd
from twisted.internet import reactor, protocol

class Client(protocol.Protocol, cmd.Cmd):
    def do_call(self, call):
        return

    def do_answer(self, op):
        return

    def do_reject(self, op):
        return

    def do_hangup(self, call):
        return

    def default(self, line):
        raise Exception()

    def connectionMade(self):
        self.readData()

    def readData(self):
        try:
            data = input(">>> ").split()
            self.onecmd(data[0]+' '+data[1])
            y = {"command" : data[0], "id" : data[1]}
            self.transport.write(json.dumps(y).encode('utf-8'))
        except:
            print("invalid command")
            self.readData()

    def dataReceived(self, data):
        try:
            y = json.loads(data.decode("utf-8"))
            print(y["response"])
        except:
            res = data.decode("utf-8").split("}{")
            y = json.loads(res[0]+'}')
            print(y["response"])
            y = json.loads('{'+res[1])
            print(y["response"])
        self.readData()
            
    def connectionLost(self, reason):
        print("connection lost")


class Factory(protocol.ClientFactory):
    protocol = Client

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()

def main():
    f = Factory()
    reactor.connectTCP("localhost", 5678, f)
    reactor.run()

if __name__ == "__main__":
    main()
