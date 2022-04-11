# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import json, cmd
from twisted.internet import reactor, protocol

class Operator:
    def __init__(self, id):
        self.id = id
        self.state = "available"
        self.call = ""

    def getId(self):
        return self.id

    def getCall(self):
        return self.call

    def isAvailable(self):
        if(self.state == "available"):
            return 1
        return 0

    def ring(self, call):
        self.call = call
        self.state = "ringing"

    def answer(self):
        self.state = "busy"
        return self.call

    def reject(self):
        self.state = "available"
        return self.call
    
    def finish(self):
        busy = False
        if(self.state == "busy"):
            busy = True
        self.state = "available"
        return busy

class Queue:
    def __init__(self):
        self.v = []

    def empty(self):
        return (len(self.v) == 0)

    def getFirst(self):
        return self.v[0]

    def enqueue(self, call):
        self.v.append(call)

    def dequeue(self):
        return self.v.pop(0)

    def remove(self, call):
        try:
            self.v.remove(call)
            return True
        except:
            return False

class CallCenter(cmd.Cmd):
    prompt = '(CallCenter)'
    q = Queue()
    ops = []

    def __init__(self):
        for i in range(2):
            self.ops.append(Operator(chr(i+65)))
        super(CallCenter, self).__init__()

    def call(self, call):
        for i in self.ops:
            if(i.isAvailable()):
                i.ring(call)
                self.callPrint("Call " + call + " ringing for operator " + i.getId())
                return True
        return False

    def enqueue(self, call):
        self.q.enqueue(call)
        self.callPrint("Call " + call + " waiting in queue")

    def dequeue(self):
        while(not self.q.empty()):
            if(self.call(self.q.getFirst())):
                self.q.dequeue()
            else:
                return

    def do_call(self, call):
        self.callPrint("Call " + call + " received")
        if(not self.call(call)):
            self.enqueue(call)

    def do_answer(self, op):
        for i in self.ops:
            if(i.getId() == op):
                call = i.answer()
                self.callPrint("Call " + call + " answered by operator " + i.getId())
                return

    def do_reject(self, op):
        for i in self.ops:
            if(i.getId() == op):
                call = i.reject()
                self.callPrint("Call " + call + " rejected by operator " + i.getId())
                self.call(call)
                break
        self.dequeue()

    def do_hangup(self, call):
        if(self.q.remove(call)):
            self.callPrint("Call " + call + " missed")
        for i in self.ops:
            if(i.getCall() == call):
                ans = i.finish()
                if(ans):
                    self.callPrint("Call " + call + " finished and operator " + i.getId() + " available")
                else:
                    self.callPrint("Call " + call + " missed")
        self.dequeue()
        
    def callPrint(self, data):
        print(data)

class Echo(protocol.Protocol, CallCenter):
    """This is just about the simplest possible protocol"""

    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        y = json.loads(data)
        self.onecmd(y["command"]+" "+y["id"])

    def callPrint(self, data):
        y = {"response" : data}
        self.transport.write(json.dumps(y).encode('utf-8'))


def main():
    """This runs the protocol on port 5678"""
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(5678, factory)
    reactor.run()


# this only runs if the module was *not* imported
if __name__ == "__main__":
    main()
