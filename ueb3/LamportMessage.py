import json
from enum import Enum, unique


@unique
class MsgTypes(Enum):
    Acknowledge = "Acknowledge"
    Request = "Request"
    Ready = "Ready"
    Register = "Register"
    Reply = "Reply"
    Release = "Release"
    Remove = "Remove"
    Terminate = "Terminate"


class LamportMessage:
    msgtype = None
    time_stamp = None
    jsonmsg = None
    sender = None
    receiver = None
    request_timestamp = None

    def __init__(self, sender=None, msgtype: MsgTypes = None, timestamp: int = None, request_timestamp: int = None,
                 jsonMsg=None):
        self.sender = sender
        self.msgtype = msgtype
        self.time_stamp = timestamp
        self.jsonmsg = jsonMsg
        self.request_timestamp = request_timestamp

    def decodeLamport(self):
        try:
            self.jsonmsg = json.loads(self.jsonmsg)
            if self.jsonmsg["Timestamp"] != None:
                self.time_stamp = int(self.jsonmsg["Timestamp"])
            if self.jsonmsg["Request_Timestamp"] != None:
                self.request_timestamp = int(self.jsonmsg["Request_Timestamp"])
            if self.jsonmsg["Sender"] != None:
                self.sender = int(self.jsonmsg["Sender"])
            if self.jsonmsg["MsgType"] == MsgTypes.Request.value:
                self.msgtype = MsgTypes.Request
            elif self.jsonmsg["MsgType"] == MsgTypes.Acknowledge.value:
                self.msgtype = MsgTypes.Acknowledge
            elif self.jsonmsg["MsgType"] == MsgTypes.Reply.value:
                self.msgtype = MsgTypes.Reply
            elif self.jsonmsg["MsgType"] == MsgTypes.Release.value:
                self.msgtype = MsgTypes.Release
            elif self.jsonmsg["MsgType"] == MsgTypes.Ready.value:
                self.msgtype = MsgTypes.Ready
            elif self.jsonmsg["MsgType"] == MsgTypes.Remove.value:
                self.msgtype = MsgTypes.Remove
            elif self.jsonmsg["MsgType"] == MsgTypes.Register.value:
                self.msgtype = MsgTypes.Register
            else:
                self.msgtype = MsgTypes.Terminate
        except json.JSONDecodeError as err:
            print(err)

    def encodeLamport(self):
        data = {}
        data['Sender'] = self.sender
        data['MsgType'] = self.msgtype.value
        data['Timestamp'] = self.time_stamp
        data['Request_Timestamp'] = self.request_timestamp
        self.jsonmsg = json.dumps(data)
        return self.jsonmsg.encode()

    def __str__(self):
        return "Sender=" + str(self.sender) + ", MsgType=" + str(self.msgtype.value) + ", TS=" + str(self.time_stamp)
