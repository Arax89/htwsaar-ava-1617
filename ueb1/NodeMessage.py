import json
import sys
from enum import Enum, unique


@unique
class MsgTypes(Enum):
    Control = "control"
    Application = "application"
    Unknown = "unknown"


class NodeMessage:
    msgtype = None
    __msg__ = None
    __sender__ = None
    __receiver__ = None
    __jsonmsg__ = None

    def __init__(self, msgtype: MsgTypes = None, msg: str = None, sender: int = None, receiver: int = None,
                 jsonmsg=None):
        self.msgtype = msgtype
        self.__msg__ = msg
        self.__sender__ = sender
        self.__receiver__ = receiver
        self.__jsonmsg__ = jsonmsg

    def decode(self):
        try:
            self.__jsonmsg__ = json.loads(self.__jsonmsg__)
            # Set Message
            self.__msg__ = self.__jsonmsg__["Msg"]
            # Set Sender
            self.__sender__ = self.__jsonmsg__["Sender"]
            # Set Receiver
            self.__receiver__ = self.__jsonmsg__["Receiver"]
            # Set Message Type
            if self.__jsonmsg__["MsgType"] == MsgTypes.Control.value:
                self.msgtype = MsgTypes.Control
            elif self.__jsonmsg__["MsgType"] == MsgTypes.Application.value:
                self.msgtype = MsgTypes.Application
            else:
                self.msgtype = MsgTypes.Unknown
        except json.JSONDecodeError as err:
            print("Couldn't decode message", file=sys.stderr)
            print(err)

    def encode(self):
        data = {}
        data['MsgType'] = self.msgtype.value
        data['Msg'] = self.__msg__
        data['Sender'] = self.__sender__
        data['Receiver'] = self.__receiver__
        self.__jsonmsg__ = json.dumps(data)
        return self.__jsonmsg__.encode()

    def getMessage(self):
        self.decode()
        return self.__msg__

    def getSender(self):
        return int(self.__sender__)

    def __str__(self):
        return "From: " + str(self.__sender__) + ", To: " + str(self.__receiver__) + ", MsgType: " + str(
            self.msgtype) + ", Msg: " + str(self.__msg__)
