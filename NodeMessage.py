import json
from enum import Enum, unique


@unique
class MsgTypes(Enum):
    Control = "control"
    Application = "application"
    Unknown = "unknown"


class NodeMessage:

    def __init__(self, msgtype: MsgTypes =None, msg=None, sender=None, receiver=None, jsonmsg=None):
        self.msgtype = msgtype
        self.msg = msg
        self.sender = sender
        self.receiver = receiver
        self.jsonmsg = jsonmsg

    def decode(self):
        try:
            self.jsonmsg = json.loads(self.jsonmsg)
            # Set Message
            self.msg = self.jsonmsg["Msg"]
            # Set Sender
            self.sender = self.jsonmsg["Sender"]
            # Set Message Type
            if self.jsonmsg["MsgType"] == MsgTypes.Control.value:
                self.msgtype = MsgTypes.Control
            elif self.jsonmsg["MsgType"] == MsgTypes.Application.value:
                self.msgtype = MsgTypes.Application
            else:
                self.msgtype = MsgTypes.Unknown
        except json.JSONDecodeError as err:
            print("Couldn't decode message")
            print(err)

    def encode(self):
        data = {}
        data['MsgType'] = self.msgtype.value
        data['Msg'] = self.msg
        data['Sender'] = self.sender
        data['Receiver'] = self.receiver
        self.jsonmsg = json.dumps(data)
